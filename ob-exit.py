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
        dialog = ExitDialog(ExitGUI(), ExitPresenter())
        dialog.show()
        sys.exit(app.exec_())


class ExitDialog(QObject):

    def __init__(self, view, presenter, parent=None):
        super(ExitDialog, self).__init__(parent)
        presenter.setParent(view)

        view.logout.connect(presenter.logout)
        view.reboot.connect(presenter.reboot)
        view.poweroff.connect(presenter.poweroff)

        self._view = view

    def show(self):
        self._view.show()


class ExitGUI(QDialog):

    logout = pyqtSignal()
    reboot = pyqtSignal()
    poweroff = pyqtSignal()

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

    def _signalLogout(self):
        self.logout.emit()

    def _signalReboot(self):
        self.reboot.emit()

    def _signalPoweroff(self):
        self.poweroff.emit()


class ExitPresenter(QObject):
    def __init__(self, parent=None):
        super(ExitPresenter, self).__init__(parent)

    def logout(self):
        subprocess.call(['openbox', '--exit'])

    def reboot(self):
        subprocess.call(['dbus-send', '--system', '--print-reply',
                         '--dest=org.freedesktop.ConsoleKit',
                         '/org/freedesktop/ConsoleKit/Manager',
                         'org.freedesktop.ConsoleKit.Manager.Restart'])

    def poweroff(self):
        subprocess.call(['dbus-send', '--system', '--print-reply',
                         '--dest=org.freedesktop.ConsoleKit',
                         '/org/freedesktop/ConsoleKit/Manager',
                         'org.freedesktop.ConsoleKit.Manager.Stop'])


if __name__ == '__main__':
    main()
