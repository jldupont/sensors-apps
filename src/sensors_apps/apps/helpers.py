"""
    @author: jldupont

    Created on 2010-03-03
"""
import os
import gtk #@UnresolvedImport

class AppIcon(object):
    
    PATHS=[ "/usr/share/icons/"
            , "/./"
            , "/./../../gnome/"
           ]
    
    def __init__(self, file_name):
        self.filename=file_name
        self.curdir=os.path.abspath( os.path.dirname(__file__) )
    
    def _iter(self):
        for path in self.PATHS:
            rpath=path.replace("/./", "%s/" % self.curdir)
            apath=os.path.abspath(rpath)
            cpath="%s/%s" % (apath, self.filename)
            yield cpath
    
    def getIconPixBuf(self):
        for path in self._iter():
            print "path: ", path
            try:    
                pixbuf = gtk.gdk.pixbuf_new_from_file( path )
                break
            except: 
                continue

        return pixbuf.scale_simple(24,24,gtk.gdk.INTERP_BILINEAR)

