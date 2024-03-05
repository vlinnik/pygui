from pygui.app import GUIApp

app = GUIApp(package=__package__,hints = [__file__] )  
home = app.window('Example')

app.expose( globals() )

app.exec()