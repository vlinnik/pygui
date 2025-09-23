#!/usr/bin/python3

from qtpy.QtGui import QIcon
from qtpy.QtDesigner import QPyDesignerCustomWidgetPlugin

try:
    from pygui.animation import Animation,PlaybackHint
    class __AnimationPlugin(QPyDesignerCustomWidgetPlugin):

        def __init__(self, parent=None):
            super().__init__(parent)

            self.initialized = False

        def initialize(self, core):
            if self.initialized:
                return

            self.initialized = True

        def isInitialized(self):
            return self.initialized

        def createWidget(self, parent):
            return Animation(parent)

        def name(self):
            return "Animation"

        def group(self):
            return "PYGUI"

        def icon(self):
            return QIcon()

        def toolTip(self):
            return ""

        def whatsThis(self):
            return ""

        def isContainer(self):
            return True

        def includeFile(self):
            return "pygui.animation"
except:
    import traceback; traceback.print_exc();

try:
    from pygui.runtimetrend import RuntimeTrend
    class __RuntimeTrendPlugin(QPyDesignerCustomWidgetPlugin):

        def __init__(self, parent=None):
            super().__init__(parent)

            self.initialized = False

        def initialize(self, core):
            if self.initialized:
                return

            self.initialized = True

        def isInitialized(self):
            return self.initialized

        def createWidget(self, parent):
            return RuntimeTrend(parent)

        def name(self):
            return "RuntimeTrend"

        def group(self):
            return "PYGUI"

        def icon(self):
            return QIcon()

        def toolTip(self):
            return ""

        def whatsThis(self):
            return ""

        def isContainer(self):
            return False

        def includeFile(self):
            return "pygui.runtimetrend"
except:
    pass
    
if __name__=="__main__":
    from qtpy.QtWidgets import QMainWindow,QApplication
    from qtpy.QtCore import QUrl
    import sys
    from pygui.animation import Animation,PlaybackHint
    
    app = QApplication(sys.argv)
    home = QMainWindow( )
    ani = Animation( home )
    ani.setSource( QUrl.fromLocalFile("/tmp/dcement.mng"))
    ani.setPlaybackHints(PlaybackHint.Bounce)
    home.resize(ani.size())

    ani.touched.connect( ani.setRunning )

    home.show( )

    app.exec()