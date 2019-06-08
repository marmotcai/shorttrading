
import stock



class dss():

    def __init__(self, obj):

        self.stock_obj = obj
        self.income_unit = 0.03

    def Decision(self, marketinfos):

        def buy(marketinfo):
            if (self.stock_obj.s.get_capital_quota() > 80): # 占用资金超过80%，不继续买入
                print("资金用量已经超过临界值，暂时停止买入")
                return

            self.stock_obj.s.qi.update()

            price_diff = 0
            buy_volume = 0
            if (self.stock_obj.s.qi.volume < 0):
                # 存在卖空单
                price_diff = round(self.stock_obj.s.qi.sell_cost - marketinfo.now, 2)
                buy_volume = self.stock_obj.s.qi.volume * -1
                print("买空价差:" + str(price_diff))
            else:
                price_diff = round(self.stock_obj.s.qi.average_price - marketinfo.now, 2) # 最新价格和均价的价格差，作为判断因素
                buy_volume = round(self.stock_obj.s.startinfo.minimum_volume * price_diff, 0)
                print("买入价差:" + str(price_diff))

            if (price_diff > self.income_unit):
                self.stock_obj.bid("buy", marketinfo, buy_volume)  # 下买单

        def sell(marketinfo):
            if (self.stock_obj.s.get_tradable() <= 0):
                print("没有可卖出额度")
                return

            self.stock_obj.s.qi.update()

            price_diff = 0
            sell_volume = 0
            if (self.stock_obj.s.qi.volume > 0):
                # 存在买单
                price_diff = round(marketinfo.now - self.stock_obj.s.qi.buy_cost, 2)
                sell_volume = self.stock_obj.s.qi.volume
                print("卖出价差:" + str(price_diff) + " 买入成本:" + str(self.stock_obj.s.qi.buy_cost), " 存量:" + str(sell_volume))
            else:
                # 卖空操作
                price_diff = round(marketinfo.now - self.stock_obj.s.qi.average_price,2)
                sell_volume = round(self.stock_obj.s.startinfo.minimum_volume * price_diff, 0)
                print("卖空价差:" + str(price_diff))

            if (price_diff > self.income_unit):
                self.stock_obj.bid("sell", marketinfo, sell_volume)  # 下卖单

        def judge_buy(marketinfo):
            for b in self.stock_obj.s.sell_order: # 检查是否有卖出单可以买回获利的
                profit = -1 * self.stock_obj.s.calc.calc_profit(b, marketinfo.now, self.stock_obj.s.startinfo.minimum_volume)
                if (profit > self.stock_obj.s.startinfo.minimum_profit):
                    self.stock_obj.s.sell_order.pop(b)  # 从卖单列表里删除卖单
                    self.stock_obj.bid("buy", marketinfo, self.stock_obj.s.startinfo.minimum_volume)

                    self.stock_obj.s.interval_income = self.stock_obj.s.interval_income + profit  # 计算波段盈利
                    self.stock_obj.s.interval_income = round(self.stock_obj.s.interval_income, 2)
                    return

            for b in self.stock_obj.s.buy_order:
                space = round(b - marketinfo.now, 2)
                if ( abs(space) < self.stock_obj.s.startinfo.premium_space):
                    print(" 价格空间小于阈值(" + str(abs(space)) + ") 不予买入:(" + str(b) + "-" + str(marketinfo.now) + ")")
                    return

            quota = self.stock_obj.s.get_capital_quota()
            if (quota < 80): # 判断资金余量是否超过80%
                order = self.stock_obj.s.buy_order.get(marketinfo.now) # 判断这个价格是否已经买入
                if (not order):
                    self.stock_obj.bid("buy", marketinfo, self.stock_obj.s.startinfo.minimum_volume)
                    print(" 价格空间大于阈值,买入:(" + str(marketinfo.now) + "-" + str(self.stock_obj.s.startinfo.minimum_volume) + ")")

        def judge_sell(marketinfo):

            for b in self.stock_obj.s.buy_order: # 检查是否有买入单可以卖出获利的
                profit = self.stock_obj.s.calc.calc_profit(b, marketinfo.now, self.stock_obj.s.startinfo.minimum_volume)
                if (profit > self.stock_obj.s.startinfo.minimum_profit):
                    self.stock_obj.s.buy_order.pop(b)  # 从买单列表里删除买单
                    self.stock_obj.bid("sell", marketinfo, self.stock_obj.s.startinfo.minimum_volume) # 下卖单
                    self.stock_obj.s.interval_income = self.stock_obj.s.interval_income + profit  # 计算波段盈利
                    self.stock_obj.s.interval_income = round(self.stock_obj.s.interval_income, 2)
                    return
        #########################################################################################

        self.stock_obj.s.update()

        self.stock_obj.s.qi.update_average_price(marketinfos) # 刷新平均价格

        buy(marketinfos)
        sell(marketinfos)

        print("最新价格：" + str(marketinfos.now) + " 当前均价：" + str(self.stock_obj.s.qi.average_price))
        print("当前成本:" + str(self.stock_obj.s.qi.cost) + " 数量:" + str(self.stock_obj.s.qi.volume))
        print("当前买入成本:" + str(self.stock_obj.s.qi.buy_cost) + " 当前卖出成本:" + str(self.stock_obj.s.qi.sell_cost))
        print("当天买入：" + str(self.stock_obj.s.qi.buy_volume) + " 卖出：" + str(self.stock_obj.s.qi.sell_volume))
        print("资金可用：" + str(self.stock_obj.s.qi.capital), " 资金比例：" + str(self.stock_obj.s.get_capital_quota()) + "%")
        print("可卖出额度：" + str(self.stock_obj.s.get_tradable()))
        print("区间存量：" + str(self.stock_obj.s.qi.get_interval_volume()) + " 区间收益：" + str(self.stock_obj.s.qi.get_interval_income()))

        self.stock_obj.s.update()

        #########################################################################################
