
from AnyQt.QtWidgets import QLabel,QWidget
from AnyQt.QtCore import QUrl,QTimer,Property,Signal,Slot
from AnyQt.QtGui import QMovie,QPixmap
from enum import Flag,auto
from AnyQt import USED_API

if USED_API=='pyqt6':
    from AnyQt.QtCore import pyqtEnum as Q_FLAGS
else:
    from AnyQt.QtCore import Q_FLAGS
    
class PlaybackHint(Flag):
    Nothing = auto()
    Ceaseless = auto()
    Rewind = auto()
    StartOnShow = auto()
    Bounce = auto()

class Animation(QLabel):
    PlaybackHint = PlaybackHint
    
    Q_FLAGS(PlaybackHint)
        
    Ceaseless = PlaybackHint.Ceaseless    
    StartOnShow = PlaybackHint.StartOnShow
    Rewind = PlaybackHint.Rewind
    Bounce = PlaybackHint.Bounce
    
            
    def __init__(self, parent: QWidget=None, *args, **kwargs):
        self._hint = PlaybackHint(PlaybackHint.Nothing)
        self._movie = None
        self._touched = False
        self._source = QUrl( )
        super(Animation, self).__init__(parent,*args, **kwargs)

    @Slot(QUrl)
    def setSource(self, url: QUrl ):
        self._source = url
        if url.scheme()=='qrc':
            file = ':'+url.path()
        else:
            file = url.toLocalFile( )
        _preview = QPixmap()
        if not _preview.load( file ):
            pass
        if self._movie:
            self._movie.frameChanged.disconnect()
            
        self._movie = QMovie( file )
        self._movie.setCacheMode(QMovie.CacheMode.CacheAll)
        self._movie.frameChanged.connect( self._frameChanged )
        
        self.resize(_preview.size())
        if self._movie.isValid():
            self.setMovie(self._movie)
            self._movie.jumpToNextFrame()
        else:
            self.setPixmap(_preview)
            
    def getSource(self)->QUrl:
        return self._source
    
    def getPlaybackHints(self)->PlaybackHint:
        return self._hint
    
    def setPlaybackHints(self,hint: PlaybackHint):
        self._hint = hint
        pass
    
    @Slot(bool)
    def setRunning(self,running: bool):
        if not self._movie: return
        
        if running:
            self._movie.start()
        else:
            self._movie.stop( )
            self._frameChanged(self._movie.currentFrameNumber())
            # if PlaybackHint.Bounce in PlaybackHint(self._hint) and self._movie.currentFrameNumber()>0:
            #     self._movie.jumpToFrame( self._movie.currentFrameNumber()-1 )
        
    def isRunning(self) -> bool:
        if not self._movie: return False
        return self._movie.state()==QMovie.MovieState.Running

    def _frameChanged(self,frame: int):
        if PlaybackHint.Bounce in PlaybackHint(self._hint) and frame>0 and self._movie.state()==QMovie.MovieState.NotRunning:
            QTimer.singleShot(self._movie.nextFrameDelay(), lambda: self._movie.jumpToFrame( frame-1 ))
        if PlaybackHint.Ceaseless in PlaybackHint(self._hint) and self._movie.state()==QMovie.MovieState.NotRunning and frame!=0:
            if frame<self._movie.frameCount( ):
                QTimer.singleShot(self._movie.nextFrameDelay(), lambda: self._movie.jumpToFrame( frame+1 ))
            else:
                QTimer.singleShot(self._movie.nextFrameDelay(), lambda: self._movie.jumpToFrame( 0 ))
            
            

    def isTouched(self)->bool:
        return self._touched 
        
    def mousePressEvent(self, event):
        if (self._movie.currentImage().pixel(event.pos()) & 0xFF00000)>0:
            self._touched = True
            self.touched.emit( self._touched)
    
    def mouseReleaseEvent(self,event):
        self._touched = False 
        self.touched.emit( self._touched  )
            
    touched = Signal(bool,arguments=['on'])
    touch   = Property(bool, isTouched, notify = touched)
    source  = Property(QUrl,getSource,setSource)
    running = Property(bool,isRunning,setRunning)
    playbackHints = Property(PlaybackHint,getPlaybackHints,setPlaybackHints)
