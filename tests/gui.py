from pygui.app import GUIApp,logging

logging.basicConfig( level=logging.DEBUG )
app = GUIApp('./tests/gui.yaml')
home = app.window('Home')

app.expose( globals() )

app.exec()

