"""
    Worker - multiprocessing based worker
    
    Message based interface
    =======================
    
    Message format
    --------------
    
    [msg_type, ...]
    
    Message types
    -------------
    
    The message types beginning with ":" are reserved.
    
    To worker:
     - [":quit"]
  
    @author: jldupont

    Created on 2010-03-03
"""
__all__=["WorkerClass", "WorkerManager"]

from Queue import Empty
from multiprocessing import Process, Queue

class WorkerClass(Process):
    """
    Callbacks:
    - "beforeRun()"
    - "beforeQuit()"
    
    @param timeout: float in seconds 
    """
    def __init__(self, name, timeout=0.1):
        Process.__init__(self)
        self.name=name
        self.timeout=timeout
        self.qin=Queue()
        self.qout=Queue()
        self.quit=False
        
    def rxFromWorker(self, block=False):
        try:          
            msg=self.qout.get_nowait()# block, self.timeout)
        except Empty: msg=None
        return msg
        
    def txToWorker(self, *p):
        """
        Transmit to Worker
        
        Parameters: either (msg) or (mtype, msg)
        """
        #print "txToWorker: ", p
        if len(p) == 1:
            self.qin.put(*p)
        else:
            mtype=p[0]
            msg=p[1]
            self.qin.put([mtype].extend(msg))
        
    def rxMsg(self, block=False):
        """ Get message
            Defaults to 'non-blocking'
        """
        try:          
            msg=self.qin.get(block, self.timeout)
            try: 
                if msg[0]==":quit":
                    self._quit()
            except: pass
        except Empty: msg=None
        return msg
        
    def txMsg(self, mtype, msg):
        """ Non-blocking transmit message
        """
        self.qout.put([mtype, msg])
        
    def _quit(self):
        if hasattr(self, "beforeQuit"):
            self.beforeQuit()
        self.quit=True
        
    def run(self):
        if hasattr(self, "beforeRun"):
            self.beforeRun()
            
        self.doRun()
        
    def doRun(self):
        raise RuntimeError("'WorkerClass.doRun' must be subclassed")


## ==========================================================================



class WorkerManagerClass(object):
    """ Manages the lifecycle of Workers
    """
    def __init__(self):
        self.cleaners=[]
    
    def terminate(self, w):
        c=WorkerCleaner(w)
        c.start()
        self.cleaners.extend([c])
        self._gc()
        
    def _gc(self):
        newlist=[]
        for cleaner in self.cleaners:
            if not cleaner.is_alive():
                del cleaner
            else:
                newlist.extend([cleaner])
        self.cleaners=newlist
    

WorkerManager=WorkerManagerClass()


## ==========================================================================



from threading import Thread

class WorkerCleaner(Thread):
    """ Takes care of cleaning-up a Worker
    
    @param worker: worker instance
    @param timeout: maximum timeout (in seconds) to wait for a worker to terminate
    """
    def __init__(self, worker, timeout=5):
        Thread.__init__(self)
        self.w=worker
        self.timeout=timeout
    
    def run(self):
        self.w.txToWorker([":quit"])
        self.w.join(self.timeout)
        if self.w.is_alive():
            self.w.terminate()
            


## ==========================================================================


if __name__=="__main__":
    from time import sleep
    
    class Worker(WorkerClass):
        def __init__(self, name):
            WorkerClass.__init__(self, name)
            
        def beforeRun(self):
            print "Worker.beforeRun"
        def beforeQuit(self):
            print "Worker.beforeQuit" ## won't show most probably
            
        def doRun(self):
            print "Worker.doRun"            
            while not self.quit:
                msg=self.rxMsg()
                if msg is not None:
                    print "Worker: rx msg: ", msg
                sleep(0.5)
                
        
    w=Worker("test")
    w.start()
    
    WorkerManager.terminate(w)
        
    
