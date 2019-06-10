
import datetime


def istringtime():  # 判断是否交易日
    date = datetime.datetime.now()
    day = date.weekday()
    if (day > 4):
        return 0

    am_time1 = datetime.datetime.strptime(str(datetime.datetime.now().date()) + '9:30', '%Y-%m-%d%H:%M')
    am_time2 = datetime.datetime.strptime(str(datetime.datetime.now().date()) + '11:30', '%Y-%m-%d%H:%M')
    pm_time1 = datetime.datetime.strptime(str(datetime.datetime.now().date()) + '13:00', '%Y-%m-%d%H:%M')
    pm_time2 = datetime.datetime.strptime(str(datetime.datetime.now().date()) + '15:00', '%Y-%m-%d%H:%M')

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

class stock: #存量股票信息
    def __init__(self):
        self.volume = 0 # 总量
        self.price = 0 # 平均单价
        self.charge = 0 # 税费

class qis: # 量化指标
    def __init__(self, statistics):
        self.s = statistics  # 当前状态信息

        self.capital = self.s.startinfo.maximum_capital # 当前资金
        self.max_price_list = 5 # 记录价格均线的历史价格数据个数
        self.last_price = [] # 最近的价格列表
        self.average_price = 0 # 平均价格

        self.volume = 0  # 当前数量
        self.cost = 0 # 当前成本

        self.buy_volume = 0 # 买入总量
        self.buy_primecost = 0 # 买入总成本
        self.buy_cost = 0 # 买入单价成本

        self.sell_volume = 0 # 卖出总量
        self.sell_primecost = 0  # 卖出总成本
        self.sell_cost = 0 # 卖出单价成本

    def get_last_price(self):
        if (self.last_price.__len__() <= 0):
            return 0
        return self.last_price[self.last_price.__len__() - 1]

    def get_tolvalue(self): # 获取当前持仓市值
        return self.volume * self.cost

    def update_average_price(self, marketinfos):
        if (self.get_last_price() == marketinfos.now):
            return

        if (self.last_price.__len__() >= self.max_price_list):
            self.last_price.pop(0)

        self.last_price.append(marketinfos.now)
        tolprice = 0
        for num in range(0, self.last_price.__len__()):
            tolprice += self.last_price[num]
        self.average_price = round((tolprice / self.last_price.__len__()), 4)
        return self.average_price

    def buy_update(self, price, volume):
        charge = self.s.calc.calc_charge("buy", price, volume)
        capital = price * volume

        self.capital -= capital
        self.capital -= charge
        self.capital = round(self.capital, 5)

        self.buy_primecost = (self.buy_volume * self.buy_cost) + capital + charge # 买入耗费总成本
        self.buy_volume += volume
        self.buy_cost = round(self.buy_primecost / (self.buy_volume), 5)

        self.s.buy_tolvolume += volume

    def sell_update(self, price, volume):
        charge = self.s.calc.calc_charge("sell", price, volume)
        capital = price * volume

        self.capital += capital
        self.capital -= charge
        self.capital = round(self.capital, 2)

        self.sell_primecost = (self.sell_volume * self.sell_cost) + capital - charge # 卖出总成本
        self.sell_volume += volume
        self.sell_cost = round(self.sell_primecost / (self.sell_volume), 5)

        self.s.sell_tolvolume += volume

    def update(self):
        self.volume = self.buy_volume - self.sell_volume
        if (self.volume != 0):
            self.cost = round((self.buy_primecost - self.sell_primecost) / self.volume, 5)
        else:
            self.cost = 0
            self.buy_cost = 0
            self.buy_volume = 0
            self.buy_primecost = 0
            self.sell_cost = 0
            self.sell_volume = 0
            self.sell_primecost = 0

    def get_interval_volume(self): # 股票存量
        return round(self.buy_volume - self.sell_volume, 0)

    def get_interval_capital(self): # 资金存量
        return round(self.capital, 2)

    def get_interval_income(self):
        interval_income = self.get_interval_capital() - self.s.startinfo.maximum_capital # 资金存量
        interval_income += self.get_interval_volume() * self.get_last_price() # 股票存量

        return round(interval_income, 2)

class orders: # 交易信息
    def __init__(self):
        self.code = 0 # 代码
        self.type = -1 # 交易类型 0：卖出 1：买入
        self.time = 0 # 委托时间s
        self.price = 0 # 委托价格
        self.volume = 0 # 委托数量
        self.marketinfo = 0 # 当前行情信息
        self.charge = 0 # 手续费

    def get_primecost(self):
        return (self.price * self.volume) + self.charge

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
    def __init__(self, startinfos):
        self.startinfo = startinfos # 启动信息
        self.marketinfo = marketinfos() # 最新行情信息
        self.position = 0 # 当前总持仓
        self.primecost = 0 # 当前总成本
        self.tolvalue = 0 # 当前市值
        self.tradable = startinfos.old_position # 可卖出交易数量
        self.buy_tolvolume = 0  # 当天买入总量
        self.sell_tolvolume = 0  # 当天卖出总量
        self.floating_income = 0  # 浮动收益，代表市值和成本差
        self.interval_income = 0  # 区间收益，代表波段操作收益
        self.last_time = datetime.datetime.now() # 记录上次的日期和时间
        self.buy_charge = 0   # 买入总税费
        self.sell_charge = 0   # 卖出总税费
        self.current_cost = 0 # 持仓成本单价
        self.bid = {}  # 下单记录
        self.buy_order = {}  # 买入记录
        self.sell_order = {}  # 卖出记录
        self.qi = qis(self)  # 量化指标信息
        self.calc = calc(self) # 计算工具类

    def update(self): # 刷新当前信息
        self.position = 0
        self.primecost = 0
        self.buy_charge = 0
        self.sell_charge = 0

        for b in self.buy_order:
            order = self.buy_order.get(b)
            self.position = self.position + order.volume  # 计算买入总持仓
            self.primecost = self.primecost + order.get_primecost()  # 计算买入总成本
            self.buy_charge = self.buy_charge + order.charge

        for b in self.sell_order:
            order = self.sell_order.get(b)
            self.position = self.position - order.volume  # 计算卖出总持仓
            self.primecost = self.primecost - order.get_primecost()  # 计算卖出总成本
            self.sell_charge = self.sell_charge + order.charge

        self.position = round(self.position, 0)
        self.primecost = round(self.primecost, 2)
        self.buy_charge = round(self.buy_charge, 2)
        self.sell_charge = round(self.sell_charge, 2)

        yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
        if (yesterday.day == self.last_time.day):
            # 跨天了，可以更新T+1相关信息
            self.tradable = self.tradable + self.position # 更新可交易持仓
            self.buy_tolvolume = 0  # 买入总量
            self.sell_tolvolume = 0  # 卖出总量

        self.last_time = datetime.datetime.now()
        return

    def get_position(self): # 获取当前持仓
        self.update()
        return self.position

    def get_primecost(self): # 获取当前持仓成本
        self.update()
        return self.primecost

    def get_tradable(self): # 获取可卖出交易数量
        return self.tradable - self.sell_tolvolume

    def get_capital_quota(self): # 计算使用资金的比例
        return round(self.qi.get_tolvalue() * 100 / self.startinfo.maximum_capital, 2)

    def get_position_quota(self): # 计算当前持仓和可交易的比例
        return round(self.qi.volume * 100 / self.tradable, 2)

    #########################################################################################

    def get_state_htmlitem(self):
        stateinfo = ""

        if not istringtime():
            stateinfo += "<div>" + str(self.startinfo.stock_name) + " (" + self.startinfo.stock_code + ") 休市中</div>"
        else:
            stateinfo += "<div>" + str(self.startinfo.stock_name) + " (" + self.startinfo.stock_code + ")</div>"

        stateinfo += "<div>当前价格: " + str(self.marketinfo.now) + "</div>"
        stateinfo += "<div>当前均价: " + str(self.qi.average_price) + "</div>"
        stateinfo += "<div>成本单价: " + str(self.qi.cost) + "</div>"
        stateinfo += "<div>总持仓: " + str(self.qi.volume) + "</div>"
        stateinfo += "<div>当前买入成本:" + str(self.qi.buy_cost) + "</div>"
        stateinfo += "<div>当前卖出成本:" + str(self.qi.sell_cost) + "</div>"
        stateinfo += "<div>当天买入：" + str(self.buy_tolvolume) + "</div>"
        stateinfo += "<div>当天卖出：" + str(self.sell_tolvolume) + "</div>"
        stateinfo += "<div>买入总税费: " + str(self.buy_charge) + "</div>"
        stateinfo += "<div>卖出总税费: " + str(self.sell_charge) + "</div>"
        stateinfo += "<div>资金可用：" + str(self.qi.capital) + "</div>"
        stateinfo += "<div>资金比例：" + str(self.get_capital_quota()) + "%" + "</div>"
        stateinfo += "<div>可卖出额度：" + str(self.get_tradable()) + "</div>"
        stateinfo += "<div>区间存量：" + str(self.qi.get_interval_volume()) + "</div>"
        stateinfo += "<div>区间收益：" + str(self.qi.get_interval_income()) + "</div>"

    #    if (self.floating_income > 0):
    #        stateinfo += "<div>浮动盈亏: <span style=\"color:red;\">" + str(self.floating_income) + "</span></div>"
    #    else:
    #        stateinfo += "<div>浮动盈亏: <span style=\"color:green;\">" + str(self.floating_income) + "</span></div>"
#
    #    if (self.interval_income > 0):
    #        stateinfo += "<div>波段盈亏: <span style=\"color:red;\">" + str(self.interval_income) + "</span></div>"
    #    else:
    #        stateinfo += "<div>波段盈亏: <span style=\"color:green;\">" + str(self.interval_income) + "</span></div>"
#
    #    income = round(self.floating_income + self.interval_income, 2)
    #    if (income > 0):
    #        stateinfo += "<div>总盈亏: <span style=\"color:red;\">" + str(income) + "</span></div>"
    #    else:
    #        stateinfo += "<div>总盈亏: <span style=\"color:green;\">" + str(income) + "</span></div>"

        return stateinfo

class calc:  # 计算工具类

    def __init__(self, statistics):
        self.s = statistics # 当前状态信息

    #########################################################################################

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
