if __name__=="__main__":
    from AnyQt.QtWidgets import QMainWindow,QApplication
    from AnyQt.QtCore import QUrl
    import sys
    from pygui.runtimetrend import RuntimeTrend
    
    app = QApplication(sys.argv)
    home = RuntimeTrend( )
    home.show( )
    app.exec()