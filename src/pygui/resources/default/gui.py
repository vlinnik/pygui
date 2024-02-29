from pygui.app import GUIApp

app = GUIApp()
home = app.window('Example')

app.expose( globals() )

app.exec()

