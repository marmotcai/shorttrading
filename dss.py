
import stock



class dss():

    def __init__(self, obj):

        self.stock_obj = obj


    def Decision(self, marketinfos):

        def buy(marketinfo):
            if (self.stock_obj.s.get_capital_quota() > 80): # 占用资金超过80%，不继续买入
                return
            price_diff = self.stock_obj.s.qi.average_price - marketinfo.now # 最新价格和均价的价格差，作为判断因素
            if (not self.stock_obj.s.qi.cost) or (price_diff > 0.03):

                if (price_diff <= 0):
                    price_diff = 0.01
                volume = round(self.stock_obj.s.startinfo.minimum_volume * price_diff, 0)
                self.stock_obj.bid("buy", marketinfo, volume) # 下买单

        def sell(marketinfo):
            if (self.stock_obj.s.get_tradable() <= 0):
                print("没有可卖出额度")
                return

            if (self.stock_obj.s.get_capital_quota() < 50):
                return

            price_diff = marketinfo.now - self.stock_obj.s.qi.buy_cost
            if (not self.stock_obj.s.qi.cost) or (price_diff > 0.03):
                self.stock_obj.bid("sell", marketinfo, self.stock_obj.s.startinfo.minimum_volume)  # 下卖单

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

        self.stock_obj.s.qi.update_average_price(marketinfos)

        buy(marketinfos)

    #    if (self.stock_obj.s.get_tradable() > 0): # 判断是否还有卖出额度
    #        sell(marketinfos)

        print("最新价格：" + str(marketinfos.now) + " 当前均价：" + str(self.stock_obj.s.qi.average_price))
        print("当前资金用量：" + str(self.stock_obj.s.get_capital_quota()) + "%")
        print("当天可卖出：" + str(self.stock_obj.s.get_tradable()))
        print("当天买入：" + str(self.stock_obj.s.qi.buy_volume) + " 卖出：" + str(self.stock_obj.s.qi.sell_volume))
        print("区间存量：" + str(self.stock_obj.s.qi.get_interval_volume()))
        print("区间收益：" + str(self.stock_obj.s.qi.get_interval_income()))
        print("当前成本:" + str(self.stock_obj.s.qi.cost) + " 数量:" + str(self.stock_obj.s.qi.volume))
        print("当前买入成本:" + str(self.stock_obj.s.qi.buy_cost) + " 数量:" + str(self.stock_obj.s.qi.buy_volume))
        print("当前卖出成本:" + str(self.stock_obj.s.qi.sell_cost) + " 数量:" + str(self.stock_obj.s.qi.sell_volume))

        self.stock_obj.s.update()

        #########################################################################################
