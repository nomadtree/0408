import sys
import time

import requests

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic
from PyQt5.QtGui import QIcon

import pyupbit  # pip install pyupbit

form_class = uic.loadUiType("upbitinfo.ui")[0]

# 시그널 클래스->업비트서버에 요청을 넣어서 코인 정보를 가져오는 일을 하는 클래스
class UpbitCall(QThread):
    # 시그널 함수 선언(정의)
    coinDataSent = pyqtSignal(float, float, float, float, float, float, float, float)

    def __init__(self, ticker):
    # 시그널 클래스 객체가 선언될 때 메인윈도우에서 코인 종류(ticker)를 받아오게 설계
        super().__init__()
        self.ticker = ticker
        self.alive = True

    def run(self):
        while self.alive:  # 무한루프
            url = "https://api.upbit.com/v1/ticker"
            param = {"markets":f"KRW-{self.ticker}"}
            # "https://api.upbit.com/v1/ticker?markets=KRW-BTC"
            response = requests.get(url, params=param)

            result = response.json()

            trade_price = result[0]["trade_price"]  # 비트코인의 현재가격
            high_price = result[0]["high_price"]  # 최고가
            low_price = result[0]["low_price"]  # 최고가
            prev_closing_price = result[0]["prev_closing_price"]  # 전일종가
            trade_volume = result[0]["trade_volume"]  # 최근 거래량
            acc_trade_volume_24h = result[0]["acc_trade_volume_24h"]  # 24시간 누적 거래량
            acc_trade_price_24h = result[0]["acc_trade_price_24h"]  # 24시간 누적 거래대금
            signed_change_rate = result[0]["signed_change_rate"]  # 부호가 있는 변화율

            self.coinDataSent.emit(
                float(trade_price),
                float(high_price),
                float(low_price),
                float(prev_closing_price),
                float(trade_volume),
                float(acc_trade_volume_24h),
                float(acc_trade_price_24h),
                float(signed_change_rate)
            )
            # 업비트 api 호출 딜레이 2초
            time.sleep(2)

    def close(self):
        self.alive = False

class MainWindow(QMainWindow, form_class):  # 슬롯 클래스
    def __init__(self):
        super().__init__()
        self.setupUi(self)  # ui 불러오기
        self.setWindowTitle("비트코인 정보 프로그램 v0.9")
        self.setWindowIcon(QIcon("icon/bitcoin.png"))
        self.statusBar().showMessage("Upbit Api Application Ver 0.9")

        self.ticker = "BTC"

        self.ubc = UpbitCall(self.ticker)  # 시그널 클래스로 객체 선언
        self.ubc.coinDataSent.connect(self.fillCoinData)
        self.ubc.start()  # 시그널 클래스 run() 실행
        self.combobox_setting()  # 콤보박스 초기화 설정 함수 호출
        self.coin_comboBox.currentIndexChanged.connect(self.coin_comboBox_selected)
        # 콤보박스의 메뉴 선택 변경 이벤트가 발생했을때 호출될 함수 설정


    def combobox_setting(self):  # 코인리스트 콤보박스 설정 함수
        tickerList = pyupbit.get_tickers(fiat="KRW")  # 코인 종류(ticker list) 가져오기

        coinList = []

        # KRW- 를 제거 텍스트를 리스트로 생성
        for ticker in tickerList:
            coinList.append(ticker[4:])

        coinList.remove("BTC")  # 리스트에 btc 제거
        coinList = sorted(coinList)  # BTC를 제외한 나머지 코인리스트 오름차순으로 정렬

        coinList = ["BTC"] + coinList  # BTC 첫번째 순서가 되고 나머지 리스트는 정렬된 상태로 추가됨

        self.coin_comboBox.addItems(coinList)

    def coin_comboBox_selected(self):  # 콤보박스에서 새로운 코인 종류가 선택되었을 때 호출함수
        selected_ticker = self.coin_comboBox.currentText()  # 콤보박스에서 선택된 메뉴의 텍스트 가져오기
        self.ticker = selected_ticker  # 새롭게 선택한 코인 ticker 로 변경

        self.coin_ticker_label.setText(self.ticker)
        self.ubc.close()  # while문의 무한루프가 stop
        self.ubc = UpbitCall(self.ticker)  # 새로운 시그널 클래스 객체를 생성(새로운 ticker를 넣어서)
        self.ubc.coinDataSent.connect(self.fillCoinData)
        self.ubc.start()  # 시그널 클래스 run() 실행




    def fillCoinData(self, trade_price, high_price, low_price, prev_closing_price,
                     trade_volume, acc_trade_volume_24h, acc_trade_price_24h, signed_change_rate):
        self.trade_price.setText(f"{trade_price:,.0f}원")  # 현재가
        self.high_price.setText(f"{high_price:,.0f}원")
        self.low_price.setText(f"{low_price:,.0f}원")
        self.closing_price.setText(f"{prev_closing_price:,.0f}원")
        self.trade_volume.setText(f"{trade_volume:,.3f}개")
        self.trade_volume_24h.setText(f"{acc_trade_volume_24h:,.3f}개")
        self.trade_price_24h.setText(f"{acc_trade_price_24h:,.0f}원")
        self.change_rate.setText(f"{signed_change_rate:.2f}%")
        self.update_style()


    def update_style(self):  # 변화율이 +이면 빨간색, -이면 파란색으로 표시
        if "-" in self.change_rate.text():
            self.change_rate.setStyleSheet("background-color:blue;color:white;")
            self.trade_price.setStyleSheet("color:blue;")
        else:
            self.change_rate.setStyleSheet("background-color:red;color:white;")
            self.trade_price.setStyleSheet("color:red;")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())