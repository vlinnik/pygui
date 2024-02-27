from pygui.app import GUIApp

app = GUIApp('./tests/gui.yaml')
home = app.window('Home')

app.expose( globals() )

app.exec()

