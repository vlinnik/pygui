from PySide6.QtCore import QObject,SIGNAL,QCoreApplication,QByteArray
from pyplc.utils.bindable import Property

class QObjectPropertyBinding():
    """Привязка свойства  QObject для отображения/изменения через механизм callback функций
    display должен принимать 1 параметр display( cb: callable )
    input(value: Any) - если свойство изменяется будет вызван input с новым значением в качестве параметра
    """    
    def __init__(self,obj: QObject, prop: str, display: callable = None,input: callable = None ) -> None:
        self.connections = []
        mo = obj.metaObject()
        mp = mo.property( mo.indexOfProperty(prop) )
        if obj.inherits('QAbstractButton') and prop=='down':
            self.connections.append(obj.connect( SIGNAL('pressed()'), lambda: input( True )))
            self.connections.append(obj.connect( SIGNAL('released()'), lambda: input( False)))
        if obj.inherits('QLineEdit') and prop=='text':
            self.connections.append(obj.connect( SIGNAL('editingFinished()'),lambda: input( obj.text() )))
        elif input and mp.hasNotifySignal():
            self.connections.append(obj.connect( SIGNAL('') + mp.notifySignal().methodSignature().data().decode('ascii'), input ))
        if display:
            display( lambda value: mp.write( obj,value) )

        self.mp = mp
        self.obj = obj
    def __del__(self):
        try:
            for i in self.connections:
                self.obj.disconnect(i)
        except:
            pass    
        
    @staticmethod
    def create(obj: QObject, prop: str, target: Property, readOnly: bool=False):
        return QObjectPropertyBinding(obj,prop,target.bind,None if readOnly else target.write)

class QObjectSignalHandler():
    def __init__(self,obj: QObject, signal: str, code: str ) -> None:
        mo = obj.metaObject()
        ms = mo.method( mo.indexOfSignal(signal) )
        self.code = code
        self.obj = obj
        
        self.args = [ x[0].data().decode() if x[0].size()>0 else f'arg{x[1]}' for x in zip(list(ms.parameterNames( )),range(ms.parameterCount()))]
        self.connection = QObject.connect(obj,SIGNAL( signal ), self )
    
    def __del__(self):
        self.stop( )

    def stop(self):
        try:
            self.obj.disconnect(self.connection)
        except:
            pass

    def __call__(self, *_):
        args = { }
        for arg in zip(self.args,_):
            args[arg[0]] = arg[1]
        exec( self.code, args, QCoreApplication.instance().expressions )
        
        
