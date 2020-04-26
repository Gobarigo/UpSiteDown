import sys
import os
import time

from PyQt5 import QtNetwork
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWebKitWidgets import QWebView
from PyQt5.QtWidgets import QApplication


''' 
Credit for this class: 
    Author: Richard Penman
    Bitbucket: https://bitbucket.org/richardpenman/scripts/src/default/webkit_screenshot.py
'''


class Screenshot(QWebView):
    def __init__(self, proxy_type=None, proxy_addr=None, proxy_port=None):
        self.app = QApplication(sys.argv)
        QWebView.__init__(self)
        self._loaded = False
        self.loadFinished.connect(self._loadFinished)
        # Sets the proxy if any
        if proxy_addr and proxy_port and proxy_type:
            proxy = QtNetwork.QNetworkProxy()
            if proxy_type == "http":
                proxy.setType(QtNetwork.QNetworkProxy.HttpProxy)
            elif proxy_type == "socks5":
                proxy.setType(QtNetwork.QNetworkProxy.Socks5Proxy)
            proxy.setHostName(proxy_addr)
            proxy.setPort(int(proxy_port))
            QtNetwork.QNetworkProxy.setApplicationProxy(proxy)
        if not os.path.exists("./screenshots"):
            os.makedirs("./screenshots")

    def capture(self, url, output_file):
        self.load(QUrl(url))
        self.wait_load()
        frame = self.page().mainFrame()
        self.page().setViewportSize(frame.contentsSize())
        image = QImage(self.page().viewportSize(), QImage.Format_ARGB32)
        painter = QPainter(image)
        frame.render(painter)
        painter.end()
        image.save("{}/{}".format("./screenshots", output_file))

    def wait_load(self, delay=0):
        while not self._loaded:
            self.app.processEvents()
            time.sleep(delay)
        self._loaded = False

    def _loadFinished(self, result):
        self._loaded = True
