from PySide6.QtWidgets import QApplication,QWidget
from PySide6.QtCore import QObject,QFile,QTimer
from PySide6.QtUiTools import QUiLoader
from pyplc.utils.subscriber import Subscriber
from pyplc.utils.bindable import Property,Expressions
from pygui.utils import QObjectPropertyBinding,QObjectSignalHandler

import logging,sys,yaml,re,os,importlib.resources as resources
from sqlalchemy import ForeignKey,String,BLOB,Boolean,create_engine,select
from sqlalchemy.orm import Session,DeclarativeBase,Mapped,mapped_column

class _Base(DeclarativeBase):
    pass

class _Variables(_Base):
    __tablename__ = "Variables"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(45))
    type: Mapped[int]
    source: Mapped[str] = mapped_column(String(45))
    address: Mapped[str] = mapped_column(String(128))
    logging: Mapped[bool] = mapped_column(Boolean)
    events: Mapped[bool] = mapped_column(Boolean)

class _Animations(_Base):
    __tablename__ = "Animations"
    id: Mapped[int] = mapped_column(primary_key=True)
    objectID: Mapped[str] = mapped_column(String(128))
    className: Mapped[str] = mapped_column(String(45))
    prop: Mapped[str] = mapped_column('property',String(45))
    data: Mapped[str] = mapped_column(String(128))

class _Signals(_Base):
    __tablename__ = "Signals"
    id: Mapped[int] = mapped_column(primary_key=True)
    objectID: Mapped[str] = mapped_column(String(128))
    className: Mapped[str] = mapped_column(String(45))
    signal: Mapped[str] = mapped_column(String(45))
    data: Mapped[str] = mapped_column(String(128))

class GUIApp(QApplication):
    log = logging.getLogger( __name__ )

    class __Slot():
        def __init__(self,code: str, app: 'GUIApp', args = [] ) -> None:
            self.code = code
            self.app = app
            self.args = args

        def __call__(self, *_):
            args = { }
            for arg in zip(self.args,_):
                args[arg[0]] = arg[1]
            exec( self.code, args, self.app.expressions)

    def __init__(self) -> None:
        GUIApp.log.info('Initialization...')
        super().__init__( sys.argv )
        self.toc = { }
        self.ini = { } 
        self.devices = { }
        self.expressions = Expressions( )

        try: 
            with open(resources.files('resources').joinpath('project.yaml')) as conf:
                self.ini = yaml.load(conf,Loader=yaml.Loader)
        except Exception as e:
            self.ini = { 'PYPLC': { } , 'Database' : '' }
            GUIApp.log.error('Problem with project.yaml: %s',e)

        if 'Workdir' in self.ini:
            try:
                os.chdir(self.ini['Workdir'])
            except Exception as e:
                self.log.error('Cant set working dir from project yaml: %s',e)

        self.log.info('Working dir is %s',os.getcwd())
        if 'PYSIDE_DESIGNER_PLUGINS' not in os.environ: os.environ['PYSIDE_DESIGNER_PLUGINS'] = os.getcwd()

        try:
            self.engine = create_engine('sqlite:///'+self.ini['Database'], echo=False)
            self.__pyplc( )
            self.__variables( )
        except Exception as e:
            self.log.error('Project initialization failed: %s',e)

    def __expand(self,expression: str)->str:
        var = re.compile(r'\${([^}]+)}')
        env = self.ini['Environment']
        for m in re.findall(var,expression):
            what = '\${' + f'{m}' + '}'
            expression = re.sub(what,env[m] if m in env else '',expression)
        return expression
    
    def __pyplc(self):
        devs = self.ini['PYPLC']
        for name in devs:
            info = devs[name]
            dev = Subscriber(info['host'],info['port'])
            timer = QTimer(self)
            timer.setInterval(info['rate'] if 'rate' in info else 200)
            timer.timeout.connect( dev )
            self.devices['PYPLC.'+name] = (dev,timer)

    def var(self,init_val=None,name: str=None):
        if isinstance(init_val, Property ):
            self.expressions.append(name,init_val)
            return init_val
        else:
            ret = Property(init_val)
            if name is not None:
                self.expressions.append(name,ret)
            return ret
        
    def expose(self,ctx: dict):
        for key in ctx:
            var = ctx[key]
            if isinstance(var,Property):
                self.var(var,key)
        for key in self.expressions.keys():
            if key not in ctx:
                ctx[key] = self.expressions.items[key]
                                
    def __variables(self):
        session = Session(self.engine)
        vars = select(_Variables).order_by(_Variables.type)
        remote = 0 
        locals= 0
        for var in session.scalars(vars):
            source = self.__expand(var.source)
            if source in self.devices:
                dev,_ = self.devices[source]
                self.var(Subscriber.subscribe(dev,var.address,var.name),var.name)
                remote+=1
            else:
                if var.type==2:
                    self.var(0.0,var.name)
                else:
                    raise ValueError
                locals+=1

        GUIApp.log.info('Variables statistics: remote/locals %d/%d',remote,locals)

    def __findChild(self,o: QObject, path: list[str] ):
        child = o.findChild(QObject, path[0] )
        if len(path)>1:
            return self.__findChild(child,path[1:])
        return child

    def animate( self,o: QObject ):
        session = Session(self.engine)
        animations = select(_Animations).where(_Animations.objectID.like(o.objectName()+'.%'))
        bindings = []
        for row in session.scalars(animations):
            child = self.__findChild(o, row.objectID.split('.')[1:])
            if child:
                if row.data in self.expressions.keys():
                    bindings.append( QObjectPropertyBinding.create(child,row.prop, self.expressions.items[row.data] ) )
                else:
                    bindings.append( QObjectPropertyBinding.create(child,row.prop, self.expressions.create(row.data),True ) )
        return bindings
    
    def scriptize(self,o: QObject):
        session = Session(self.engine)
        signals = select(_Signals).where(_Signals.objectID.like(o.objectName()+'.%'))
        scripts = []
        for row in session.scalars(signals):
            child = self.__findChild(o, row.objectID.split('.')[1:])
            if child:
                scripts.append(QObjectSignalHandler( child, row.signal, row.data ))
        return scripts
    
    def start(self, o:QObject):
        animations = self.animate(o)
        scripts = self.scriptize(o)
        self.toc[o] = (animations,scripts)
        self.log.info('Object %s started: %d/%d animations/scripts',o,len(animations),len(scripts))
    
    def stop(self,o: QObject):
        if o not in self.toc:
            GUIApp.log.warn('Stopping object that doesnt started')
            return
        self.log.info('Stopping object %s',o)
        animations,scripts = self.toc.pop(o)
        for i in animations:
            del i
        for i in scripts:
            i.stop( )
            del i
        animations.clear()
        scripts.clear()
        animations = None
        scripts = None
    
    def window(self,ui: str,show: bool = True)->QWidget:
        if ui in self.ini['Windows']:
            file = QFile(os.getcwd() + '/' + self.ini['Windows'][ui])
        else:
            file = QFile(os.getcwd() + f'/resources/ui/{ui}.ui')
        if not file.exists():
            self.log.error('Requested window %s not found',ui)
            return None
        file.open(QFile.ReadOnly)
        loader = QUiLoader()
        widget = loader.load(file)
        file.close()

        if widget is None:
            self.log.error('Cannot load widget %s',ui)
            return
        self.start(widget)
        if show:
            widget.show( )
        return widget

    def exec(self):
        GUIApp.log.info('Starting event loop...')
        for i in self.devices:
            dev,timer = self.devices[i]
            dev.connect( )
            timer.start( )
        return super().exec()
