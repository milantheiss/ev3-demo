#!/usr/bin/env python3
import logging

from radar_app_client import RadarAppClient
import threading
from time import sleep
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QBrush, QFont
from PyQt5.QtWidgets import QApplication, QMainWindow
import sys

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)s %(threadName)s %(name)s %(message)s")
logger = logging.getLogger('RADAR APP CONTROLLER')
logger.setLevel(logging.DEBUG)

distanz_in_pxl = 0


def start_radar_application():
    global distanz_in_pxl
    app = QApplication(sys.argv)
    is_closed = False
    window = Window(width=500, height=1000)
    while True:
        sleep(1000 / (60 * 1000))
        app.processEvents()
        window.update()
        if window.is_closed:
            break


class RadarAppController:
    _distance_data = None

    def __init__(self):
        self.radar_app_client = RadarAppClient(self)
        logger.info("App Controler created. Press enter to start requesting Data")
        input()
        self._distance_data_updated = False
        threading.Thread(target=self.start_requesting).start()
        threading.Thread(target=start_radar_application).start()

    def request_data(self):
        self.radar_app_client.send_server_request("GET", "distance_data")

    def start_requesting(self):
        while True:
            self._distance_data_updated = False
            threading.Thread(target=self.request_data).start()
            while self._distance_data_updated is False:
                sleep(0.5)

    def process_response(self, response):
        global distanz_in_pxl
        if response.get("methode") == "RESPONSE":
            if response.get("description") == "distance data":
                try:
                    distanz_in_pxl = int(response.get("value")) * 5
                except ValueError:
                    logger.error("Error while casting response into int. Current value of distance data: %s",
                                 distanz_in_pxl/5)
                self._distance_data_updated = True


class Window(QMainWindow):
    def __init__(self, xpos=0, ypos=30, width=600, height=800):
        super().__init__()
        self.xPos = xpos
        self.yPos = ypos
        self.height = height
        self.width = width

        self.setWindowTitle("EV3 Radar")

        self.is_closed = False

        self.setGeometry(self.xPos, self.yPos, self.width, self.height)
        self.setFixedSize(self.width, self.height)

        self.black_rect_width = self.width - 200
        self.black_rect_height = self.height - 100
        self.black_rect_xpos = 50
        self.black_rect_ypos = 50

        self.show()

    def paintEvent(self, e):
        global distanz_in_pxl
        painter = QPainter(self)
        painter.setBrush(QBrush(Qt.darkGray, Qt.SolidPattern))
        painter.drawRect(0, 0, self.width, self.height)

        painter.setBrush(QBrush(Qt.black, Qt.SolidPattern))
        painter.drawRect(self.black_rect_xpos, self.black_rect_ypos, self.black_rect_width, self.black_rect_height)

        painter.setBrush(QBrush(Qt.red, Qt.SolidPattern))
        if 0 < distanz_in_pxl < (self.black_rect_height - 15):
            painter.drawRect(50, self.height - 62 - distanz_in_pxl, self.black_rect_width, 10)
        else:
            painter.drawRect(50, self.height - 62 - self.black_rect_height + 15, self.black_rect_width, 10)

        painter.setPen(Qt.white)
        painter.setFont(QFont('Decorative', 30))

        painter.drawText(50, 40, "Mindstorm EV3 Radar")
        painter.setFont(QFont('Decorative', 15))

        self.draw_distanz(e, painter)
        self.draw_skala(e, painter)

    def draw_distanz(self, event, painter):
        for i in range(0, int((self.black_rect_height / 50))):
            text_x = (self.black_rect_width + 10 + self.black_rect_xpos)
            text_y = self.black_rect_ypos + self.black_rect_height - (50 * i)

            painter.drawText(text_x, text_y, "%s cm" % (i * 10))

    def draw_skala(self, event, painter):

        painter.setBrush(QBrush(Qt.white, Qt.SolidPattern))
        skala_x = self.black_rect_width + 30
        for i in range(0, int((self.black_rect_height / 50))):
            skala_y = self.black_rect_ypos + self.black_rect_height - (50 * i) - 8
            painter.drawRect(skala_x, skala_y, 25, 2)

        for i in range(0, int((self.black_rect_height / 10))):
            skala_y = self.black_rect_ypos + self.black_rect_height - (10 * i) - 8
            painter.drawRect(skala_x, skala_y, 20, 1)

    def closeEvent(self, e):
        self.is_closed = True


if __name__ == "__main__":
    app_controller = RadarAppController()
