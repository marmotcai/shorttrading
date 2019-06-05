
import datetime


def istringtime():  # 判断是否交易日
    date = datetime.datetime.now()
    day = date.weekday()
    if (day > 4):
        return 0

    am_time1 = datetime.datetime.strptime(str(datetime.datetime.now().date()) + '9:25', '%Y-%m-%d%H:%M')
    am_time2 = datetime.datetime.strptime(str(datetime.datetime.now().date()) + '11:35', '%Y-%m-%d%H:%M')
    pm_time1 = datetime.datetime.strptime(str(datetime.datetime.now().date()) + '12:55', '%Y-%m-%d%H:%M')
    pm_time2 = datetime.datetime.strptime(str(datetime.datetime.now().date()) + '15:05', '%Y-%m-%d%H:%M')

    if date >= am_time1 and date <= am_time2:
        return 1
    if date >= pm_time1 and date <= pm_time2:
        return 1

    return 0

class startinfos: # 启动信息
    def __init__(self):
        self.stock_name = "" # 股票名称
        self.stock_code = 0 # 股票代码
        self.minimum_profit = 300 # 单次交易最小盈利值
        self.minimum_volume = 1000 # 单次交易数量
        self.maximum_capital = 1000000 # 动用最大资金
        self.old_position = 50000 # 存量老股，用于T+0
        self.premium_space = round(self.minimum_profit / self.minimum_volume, 2)

    def set_stock_code(self, stock_code):
        self.stock_code = stock_code

    def set_minimum_profit(self, profit):
        self.minimum_profit = profit
        self.premium_space = round(self.minimum_profit / self.minimum_volume, 2)

    def set_minimum_volume(self, volume):
        self.minimum_volume = volume
        self.premium_space = round(self.minimum_profit / self.minimum_volume, 2)

    def set_maximum_capital(self, capital):
        self.maximum_capital = capital

    def set_old_position(self, old_position):
        self.old_position = old_position

class orders: # 交易信息
    def __init__(self):
        self.code = 0 # 代码
        self.type = -1 # 交易类型 0：卖出 1：买入
        self.time = 0 # 委托时间s
        self.price = 0 # 委托价格
        self.volume = 0 # 委托数量
        self.marketinfo = 0 # 当前行情信息
        self.charge = 0 # 手续费

class marketinfos: # 行情信息
    def __init__(self):
        self.buy = 0  # 竞买价
        self.sell = 0  # 竞卖价
        self.now = 0  # 现价
        self.open = 0  # 开盘价
        self.close = 0  # 昨日收盘价
        self.high = 0  # 今日最高价
        self.low = 0  # 今日最低价
        self.bid1 = 0  # 买一价
        self.bid1_volume = 0  # 买一量
        self.ask1 = 0  # 卖一价
        self.ask1_volume = 0  # 卖一量

class statistics: # 当前状态信息
    def __init__(self):
        self.startinfo = startinfos() # 启动信息
        self.marketinfo = marketinfos() # 最新行情信息
        self.position = 0 # 当前总持仓
        self.primecost = 0 # 当前总成本
        self.tolvalue = 0 # 当前市值
        self.floating_income = 0  # 浮动收益，代表市值和成本差
        self.interval_income = 0  # 区间收益，代表波段操作收益
        self.buy_charge = 0   # 买入总税费
        self.sell_charge = 0   # 卖出总税费
        self.current_cost = 0 # 持仓成本单价
        self.bid = {}  # 下单记录
        self.buy_order = {}  # 买入记录
        self.buy_count = 0  # 买入次数
        self.sell_order = {}  # 卖出记录
        self.sell_count = 0  # 卖出次数

    def get_quota(self): # 判断资金余量
        return round(self.primecost / self.startinfo.maximum_capital, 2)

    #########################################################################################


    def get_state_htmlitem(self):
        stateinfo = ""

        if not istringtime():
            stateinfo += "<div>" + str(self.startinfo.stock_name) + " (" + self.startinfo.stock_code + ") 休市中</div>"
        else:
            stateinfo += "<div>" + str(self.startinfo.stock_name) + " (" + self.startinfo.stock_code + ")</div>"

        stateinfo += "<div>当前价格: " + str(self.marketinfo.now) + "</div>"
        stateinfo += "<div>成本单价: " + str(self.current_cost) + "</div>"
        stateinfo += "<div>总持仓: " + str(self.position) + "</div>"
        stateinfo += "<div>成本: " + str(self.primecost) + "</div>"
        stateinfo += "<div>市值: " + str(self.tolvalue) + "</div>"
        stateinfo += "<div>买入总税费: " + str(self.buy_charge) + "</div>"
        stateinfo += "<div>卖出总税费: " + str(self.sell_charge) + "</div>"
        stateinfo += "<div>当前买入单: " + str(self.buy_order.__len__()) + "/" + str(self.buy_count) + "</div>"
        stateinfo += "<div>当前卖出单: " + str(self.sell_order.__len__()) + "/" + str(self.sell_count) + "</div>"
        stateinfo += "<div>交易次数: " + str(self.bid.__len__()) + "</div>"

        if (self.floating_income > 0):
            stateinfo += "<div>浮动盈亏: <span style=\"color:red;\">" + str(self.floating_income) + "</span></div>"
        else:
            stateinfo += "<div>浮动盈亏: <span style=\"color:green;\">" + str(self.floating_income) + "</span></div>"

        if (self.interval_income > 0):
            stateinfo += "<div>波段盈亏: <span style=\"color:red;\">" + str(self.interval_income) + "</span></div>"
        else:
            stateinfo += "<div>波段盈亏: <span style=\"color:green;\">" + str(self.interval_income) + "</span></div>"

        income = round(self.floating_income + self.interval_income, 2)
        if (income > 0):
            stateinfo += "<div>总盈亏: <span style=\"color:red;\">" + str(income) + "</span></div>"
        else:
            stateinfo += "<div>总盈亏: <span style=\"color:green;\">" + str(income) + "</span></div>"

        return stateinfo

class calc:  # 计算工具类

    def __init__(self, statistics):
        self.s = statistics # 当前状态信息

    #########################################################################################

    def calc_cost(self, type, price, volume):
        charge = self.calc_charge(type, price, volume)
        primecost = (self.s.current_cost * self.s.position) + (price * volume) + charge # 总成本

        return round(primecost / (self.s.position + volume), 3)

    def calc_profit(self, buy, sell, volume): # 计算区间收益
        charge_buy = self.calc_charge("buy", buy, volume)
        charge_sell = self.calc_charge("sell", sell, volume)

        profit = volume * (sell - buy) - charge_buy - charge_sell

        return round(profit, 2)

    def calc_charge(self, type, price, volume): # 计算费率

        def charge_buy(price, volume):
            total_sum = price * volume
            commission = round(total_sum * 0.03) / 100  # 佣金
            if (commission < 5): commission = 5

            transfer = 0
            if (int(self.s.startinfo.stock_code) >= 600000):
                transfer = round(volume * 0.06) / 100  # 过户费

            stamp = 0
            total_charge = round((commission + transfer + stamp) * 100) / 100

            return total_charge

        #########################################################################################

        def charge_sell(price, volume):
            total_sum = price * volume
            commission = round(total_sum * 0.03) / 100  # 佣金
            if (commission < 5): commission = 5

            transfer = 0
            if (int(self.s.startinfo.stock_code) >= 600000):  # 只有沪市收取
                transfer = round(volume * 0.06) / 100  # 过户费

            stamp = round(total_sum * 0.1) / 100  # 印花税

            total_charge = round((commission + transfer + stamp) * 100) / 100

            return total_charge

        charge = {'buy': charge_buy,
                  'sell': charge_sell}

        c = charge[type]

        return round(c(price, volume), 2)

    #########################################################################################
