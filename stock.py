import random

import stockinfo
import dss
import datetime

import easyquotation
import time

class BaseStock():

    def __init__(self, startinfos):
        self.test = 1
        self.quotation = easyquotation.use('sina')

        self.s = stockinfo.statistics(startinfos) # 状态信息

        stock_value = self.quotation.stocks([self.s.startinfo.stock_code])[self.s.startinfo.stock_code]
        self.s.startinfo.stock_name = stock_value['name']  # 名字

        self.dss = dss.dss(self) # 决策系统对象

    #########################################################################################

    def bid(self, type, marketinfo, volume):

        #########################################################################################

        def new_order(type, price, volume):
            order = stockinfo.orders()
            order.code = self.s.startinfo.stock_code
            order.type = type
            order.price = round(price, 2)
            order.volume = volume
            order.time = datetime.datetime.now()
            order.charge = self.s.calc.calc_charge(type, price, volume)

            return order

        def bid_buy(price, volume):
            order = new_order("buy", price, volume)
            self.s.buy_order[order.price] = order
            self.s.qi.buy_update(price, volume)
            print("==> 开始下单买入,价格：" + str(price), " 数量: " + str(volume) + " 平均买入均价:" + str(self.s.qi.buy_cost))
            #self.s.buy_volume = self.s.buy_volume + volume
            #self.s.buy_charge = self.s.buy_charge + order.charge
            #self.s.buy_charge = round(self.s.buy_charge, 2)

            return order

        def bid_sell(price, volume):
            order = new_order("sell", price, volume)
            self.s.sell_order[order.price] = order
            self.s.qi.sell_update(price, volume)
            print("<== 开始下单卖出,价格：" + str(price), " 数量: " + str(volume) + " 平均卖出均价:" + str(self.s.qi.sell_cost))
            #self.s.sell_volume = self.s.sell_volume + volume
            #self.s.sell_charge = self.s.sell_charge + order.charge
            #self.s.sell_charge = round(self.s.sell_charge, 2)

            return order

        #########################################################################################

        bid = {'buy': bid_buy, 'sell': bid_sell}
        c = bid[type]

        order = c(marketinfo.now, volume)
        if order:
            order.marketinfo = marketinfo
            key = str(order.time)
            self.s.bid[key] = order # 交易记录

    #########################################################################################

    def run(self):
        # for num in range(1, 1000):
        while True:
            if (self.test <= 0) and (not stockinfo.istringtime()):
                time.sleep(30)
                continue

            stock_value = self.quotation.stocks([self.s.startinfo.stock_code])[self.s.startinfo.stock_code]

            self.s.marketinfo.buy = stock_value['buy']  # 竞买价
            self.s.marketinfo.sell = stock_value['sell']  # 竞卖价

            self.s.marketinfo.now = stock_value['now']  # 现价
            self.s.marketinfo.open = stock_value['open']  # 开盘价
            self.s.marketinfo.close = stock_value['close']  # 昨日收盘价
            self.s.marketinfo.high = stock_value['high']  # 今日最高价
            self.s.marketinfo.low = stock_value['low']  # 今日最低价
            self.s.marketinfo.bid1 = stock_value['bid1']  # 买一价
            self.s.marketinfo.bid1_volume = stock_value['bid1_volume']  # 买一量
            self.s.marketinfo.ask1 = stock_value['ask1']  # 卖一价
            self.s.marketinfo.ask1_volume = stock_value['ask1_volume']  # 卖一量
            self.s.marketinfo.date = stock_value['date']  # 日期
            self.s.marketinfo.time = stock_value['time']  # 时间

            #  测试用，随机价格
            if (self.test == 1):
                self.s.marketinfo.now = self.s.marketinfo.now + round(random.randrange(-10, 10) / 100, 2)
                self.s.marketinfo.now = round(self.s.marketinfo.now, 2)

            print("----------决策分析--------")

            self.dss.Decision(self.s.marketinfo)

            print("----------决策分析--------")

            #print("----------状态信息--------")
#
            #self.s.tolvalue = self.s.position * self.s.marketinfo.now
            #self.s.tolvalue = round(self.s.tolvalue, 2)
#
            #self.s.floating_income = round(self.s.tolvalue - self.s.primecost, 2)
#
            #print(" 当前价格：" + str(self.s.marketinfo.now) + " 成本单价: " + str(self.s.current_cost))
            #print(" 当前买入单: " + str(self.s.buy_order.__len__()) + "/" + str(self.s.qi.buy_volume) +
            #      " 当前卖出单: " + str(self.s.sell_order.__len__()) + "/" + str(self.s.qi.sell_volume) +
            #      " 交易次数: " + str(self.s.bid.__len__()))
            #print(" 总持仓: " + str(self.s.position) + " 成本: " + str(self.s.primecost) + " 市值: " + str(self.s.tolvalue) + "\r\n"
            #      + " 买入总税费: " + str(self.s.buy_charge) + " 卖出总税费: " + str(self.s.sell_charge) + "\r\n"
            #      + " 浮动盈亏: " + str(self.s.floating_income) + " 波段盈亏: " + str(self.s.interval_income))
#
            #print("----------状态信息--------")

            time.sleep(5)
