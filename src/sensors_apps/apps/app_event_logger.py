"""
    Event-Logger
    
    @author: jldupont

    Created on 2010-03-03
"""
APP_NAME="sensors-event-logger"

__all__=[]
import gtk #@UnresolvedImport

from helpers import AppIcon

from system.mbus import Bus

class AppPopupMenu:
    def __init__(self, app):
        self.item_exit = gtk.MenuItem( "exit", True)
        self.item_exit.connect( 'activate', app.exit)

        self.menu = gtk.Menu()
        self.menu.append( self.item_exit)
        self.menu.show_all()

    def show_menu(self, button, time):
        self.menu.popup( None, None, None, button, time)
        

       

class App(object):
    def __init__(self):
        
        self.popup_menu=AppPopupMenu(self)
        
        self.tray=gtk.StatusIcon()
        self.tray.set_visible(True)
        self.tray.set_tooltip(APP_NAME)
        self.tray.connect('popup-menu', self.do_popup_menu)
        
        scaled_buf = AppIcon("%s.png" % APP_NAME).getIconPixBuf()
        self.tray.set_from_pixbuf( scaled_buf )
        
    def do_popup_menu(self, status, button, time):
        self.popup_menu.show_menu(button, time)

    def exit(self, *p):
        Bus.publish("App", "%quit")


_app=App()


if __name__=="__main__":
    gtk.main()
    