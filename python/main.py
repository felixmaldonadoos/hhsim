# main.py
import sys
from PyQt5.QtWidgets import QApplication
from app import App

def main():
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
