"""
    @author: jldupont

    Created on 2010-03-03
"""
__all__=[]
from system.mbus import Bus

from system.worker import WorkerClass, WorkerManager
from system.amqp import AMQPCommRx  

class AmqpListenerAgent(WorkerClass):
    """
    """
    EXCH="org.sensors"
    RKEY="state.io.#"
    
    def __init__(self, config):
        WorkerClass.__init__(self, "AmqpListenerAgent")
        self.comm=None
        self.config=config
        
    def doRun(self):
        self.comm=AMQPCommRx(self.config, self.EXCH, rkey=self.RKEY, rq="q.sensors.listener")
        self.comm.connect()
        
        while not self.quit and self.comm.isOk():
            self.comm.wait()
            self.processMsgQueue()

        print "AmqpListenerAgent: exiting"
                        
    def processMsgQueue(self):
        while True:
            mtype, rkey, mdata=self.comm.gMsg()
            if mtype is None: 
                break
            self.txMsg(rkey, mdata)
        
                

        

## -------------------------------------------------------------------------
## -------------------------------------------------------------------------
        
    
class Manager(object):
    """ Manages the lifecyle of the Listener Agents
    """
    RETRY_INTERVAL=4*10
    
    def __init__(self):
        self.currentWorker=None
        self.cpc=0
        self.last_spawn_count=0
    
    def _hconfig(self, config):
        self.config=config
        self.update()
    
    def update(self):
        """ A new worker will get spawn on the next 'poll'
        """
        if self.currentWorker is not None:
            WorkerManager.terminate(self.currentWorker)
            self.currentWorker=None
    
    def maybeSpawn(self):
        if self.currentWorker is None:
            delta=self.cpc - self.last_spawn_count
            if delta >= self.RETRY_INTERVAL or self.last_spawn_count==0:
                self.currentWorker=AmqpListenerAgent(self.config)
                self.currentWorker.start()
                self.last_spawn_count=self.cpc
     
                
    def _hpoll(self, pc):
        self.cpc=pc
        
        if not self.config:
            Bus.publish(self, "%config-amqp?")

        self.maybeSpawn()
        
        if self.currentWorker is not None:
            if not self.currentWorker.is_alive():
                Bus.publish(self, "%conn-error", "warning", "Connection to AMQP broker failed")
                del self.currentWorker
                self.currentWorker = None
                
        if self.currentWorker is not None:
            self.processMsgQueue()
            
    def processMsgQueue(self):
        while True:
            msg=self.currentWorker.rxFromWorker()
            if msg is None:
                break
            try:
                mtype=msg.pop(0)
                mdata=msg.pop(0)
            except:
                Bus.publish(self, "%llog", "%msg-error", "error", "Error whilst decoding message from AMQP exchange 'org.sensors' ")
                continue

            ## e.g. "state.io.din"
            Bus.publish(self, mtype, mdata)
            
    def _hquit(self):
        self.update()

    

_mng=Manager()
Bus.subscribe("%config-amqp",  _mng._hconfig)
Bus.subscribe("%poll",         _mng._hpoll)
Bus.subscribe("%quit",         _mng._hquit)