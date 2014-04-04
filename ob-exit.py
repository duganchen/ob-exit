#!/usr/bin/env python

from sip import setapi
setapi("QDate", 2)
setapi("QDateTime", 2)
setapi("QTextStream", 2)
setapi("QTime", 2)
setapi("QVariant", 2)
setapi("QString", 2)
setapi("QUrl", 2)

from PyQt4.QtGui import QApplication, QDialog, QHBoxLayout, QPushButton
from PyQt4.QtCore import QObject, QSharedMemory, pyqtSignal
import subprocess
import sys


def main():
    app = QApplication(sys.argv)

    # Prevent more than one instance from running at once
    lock = QSharedMemory('ob-exit')
    if lock.create(1):
        view = ExitGUI()
        presenter = ExitPresenter(lock, view)
        view.logout.connect(presenter.logout)
        view.reboot.connect(presenter.reboot)
        view.poweroff.connect(presenter.poweroff)
        view.closed.connect(presenter.releaseLock)
        view.show()
        sys.exit(app.exec_())


class ExitGUI(QDialog):

    logout = pyqtSignal()
    reboot = pyqtSignal()
    poweroff = pyqtSignal()

    closed = pyqtSignal()

    def __init__(self, parent=None):
        super(ExitGUI, self).__init__(parent)
        self.setWindowTitle(self.tr('Exit?'))

        layout = QHBoxLayout()

        cancelButton = QPushButton(self.tr('&Cancel'))
        cancelButton.clicked.connect(self.reject)
        layout.addWidget(cancelButton)

        logoutButton = QPushButton(self.tr('&Logout'))
        logoutButton.clicked.connect(self._signalLogout)
        layout.addWidget(logoutButton)

        rebootButton = QPushButton(self.tr('&Reboot'))
        rebootButton.clicked.connect(self._signalReboot)
        layout.addWidget(rebootButton)

        poweroffButton = QPushButton(self.tr('&Poweroff'))
        poweroffButton.clicked.connect(self._signalPoweroff)
        layout.addWidget(poweroffButton)

        self.setLayout(layout)

    def closeEvent(self, event):
        self.closed.emit()
        super(ExitGUI, self).closeEvent(event)

    def _signalLogout(self):
        self.logout.emit()

    def _signalReboot(self):
        self.reboot.emit()

    def _signalPoweroff(self):
        self.poweroff.emit()


class ExitPresenter(object):
    def __init__(self, lock, view):
        self.__lock = lock
        self.__view = view

    def logout(self):
        self.releaseLock()
        subprocess.call(['openbox', '--exit'])

    def reboot(self):
        self.releaseLock()
        subprocess.call(['dbus-send', '--system', '--print-reply',
                         '--dest=org.freedesktop.ConsoleKit',
                         '/org/freedesktop/ConsoleKit/Manager',
                         'org.freedesktop.ConsoleKit.Manager.Restart'])

    def poweroff(self):
        self.releaseLock()
        subprocess.call(['dbus-send', '--system', '--print-reply',
                         '--dest=org.freedesktop.ConsoleKit',
                         '/org/freedesktop/ConsoleKit/Manager',
                         'org.freedesktop.ConsoleKit.Manager.Stop'])

    def releaseLock(self):

        # If we're releasing the lock, we're locking the UI while we close
        # it.
        self.__view.setEnabled(False)

        # Release the lock that prevents more than one instance from running at
        # a time. Note that this is slightly more complex than in C++, due to
        # the lack of a delete operator.
        self.__lock.deleteLater()
        QApplication.processEvents()


if __name__ == '__main__':
    main()
