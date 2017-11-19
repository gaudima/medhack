import sys

from PyQt5.QtGui import QGuiApplication
from PyQt5.QtQml import QQmlApplicationEngine
from app.dialog import *

if __name__ == "__main__":
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine(parent=app)
    dialog = Dialog(parent=app)
    ctx = engine.rootContext()
    ctx.setContextProperty("dialog", dialog)
    engine.load(QUrl("qml/main.qml"))
    exit(app.exec_())



