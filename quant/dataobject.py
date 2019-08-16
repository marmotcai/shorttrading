import pickle
import pandas as pd

from vendor import zsys
from vendor import zpd_talib as zta
from vendor import ztools as zt
from vendor import ztools_data as zdat
from vendor import ztools_datadown as zddown

from utils import params as my_params
from utils import utils as my_utils

################################################################################

class download():
    def __init__(self):
        print("start download data ..")

    def download_inx(self, downpath = my_params.default_datapath, filename = "inx_code.csv"):
        if my_utils.path_exists(filename) == False:
            print("inx file is not exists and exit")
            return False

        if my_utils.path_exists(downpath) == False:
            my_utils.mkdir(downpath)

        zddown.down_stk_inx(downpath, filename);
        return True

    def downlaod_stk(self, downpath = my_params.default_datapath, filename = "stk_code.csv"):
        if my_utils.path_exists(filename) == False:
            print("stk file is not exists and exit")
            return False

        if my_utils.path_exists(downpath) == False:
            my_utils.mkdir(downpath)

        xtyp = '5'
        zddown.down_stk_all(downpath, filename, xtyp)


class util():
    def __init__(self):
        pd.set_option('display.max_rows', 10)
        pd.set_option('display.width', 450)
        pd.set_option('display.float_format', zt.xfloat5)

    def get_onehot(df, k):
        return pd.get_dummies(df[k]).values

    def get_features(df, features_lst):
        return df[features_lst].values

    # 填充前一天和后一天的值
    def prepared_pre_next(df):
        df['next_open'] = df['open'].shift(-1)  # 后一天的开盘价
        df['pre_close'] = df['close'].shift(1)  # 前一天收盘价
        return df

    # 计算均值
    def prepared_avg(df):
        df['ohlc_avg'] = df[my_params.ohlc_lst].mean(axis = 1).round(2) # 当天OHLC均值
        df['dprice_max'] = df['ohlc_avg'].rolling(10).max()
        df['dprice_min'] = df['ohlc_avg'].rolling(10).min()
        df['dprice_avg'] = df['ohlc_avg'].rolling(10).mean()
        df = zdat.df_xed_nextDay(df, ksgn = 'ohlc_avg', newSgn = 'xavg', nday = 10) #10日均值
        return df

    # 计算MA均线
    def prepared_ma(df):
        return zta.mul_talib(zta.MA, df, ksgn = 'ohlc_avg', vlst = zsys.ma100Lst_var) # ma

    # 计算振幅
    def prepared_amp(df):
        df['price_range'] = df['high'].sub(df['low'])  # 当天振幅
        df['amp'] = df['price_range'].div(df['pre_close'])  # 当天振幅
        df['amp_type'] = df['amp'].apply(zt.iff3type, d0 = 0.03, d9 = 0.05, v3=3, v2=2, v1=1)  # 振幅分类器
        return df

    def prepared_next_profit(df, num = 5, count = 2, step = 5):
        for i in range(count):
            j = num + i * step
            keyname_profit = 'next_profit_' + str(j)
            df[keyname_profit] = df['close'].shift(-1 * (j)).sub(df['close'])

        return df

    def prepared_next_rate(df, num = 5, count = 2, step = 5):
        for i in range(count):
            j = num + i * step
            keyname_profit = 'next_profit_' + str(j)
            keyname_rate = 'next_rate_' + str(j)
            df[keyname_profit] = df['close'].shift(-1 * (j)).sub(df['close'])
            df[keyname_rate] = df[keyname_profit].div(df['close'])


        df['next_rate_10_type'] = df['next_rate_10'].apply(zt.iff3type, d0=0, d9=0.05, v3=3, v2=2, v1=1)  # 振幅分类器

        return df

    # 次日数据
    def prepared_next(df):
        df['next_ohlc_avg'] = df['ohlc_avg'].shift(-1)
        df['next_price_range'] = df['price_range'].shift(-1)
        df['next_amp'] = df['amp'].shift(-1)
        df['next_amp_type'] = df['amp_type'].shift(-1)
        return df

    # 其它处理
    def prepared_other(df):
        # 清除NaN值
        df = df.fillna(method='pad')
        df = df.fillna(method='bfill')
        return df

    # 处理标签数据
    def prepared_y(df, y_key, type = 'onehot'):
        # 处理标签

        df['y'] = df[y_key] # 输出

        if (type == 'onehot'):
            # 分类模式， One-Hot
            return util.get_onehot(df, 'y')
        else:
            return df['y']


    def split(df, DC):
        # 训练数据和测试数据分割
        dnum_train = len(df.index)
        dnum_test = round(dnum_train * DC)
        return df.head(dnum_test), df.tail(dnum_train - dnum_test)

################################################################################

class  train_data():

    def __init__(self, data_dir, data_file):

        self.model_type = {'rate': self.model_rate, 'amp': self.model_amp}  # 定义策略执行函数

        self.data_dir = data_dir
        self.data_file = data_file
        self.df = pd.read_csv(data_dir + data_file, index_col = 0)

    def load(self, filepath):
        f = open(filepath, 'rb')
        x = pickle.load(f)
        f.close()

        return x

    def save(self, filepath, df):
        f = open(filepath, 'wb')
        pickle.dump(df, f)
        f.close()



    def training(self, df):
        return df

    # def plot(self):

    ################################################################################

    def model_rate(self, df):
        self.df = self.df.sort_values('date')  # 日期排序

        self.df = util.prepared_pre_next(self.df)  # 前一天收盘价和后一天的开盘价
        self.df = util.prepared_next_profit(self.df, 1, 10, 1)  # 计算第5天和第10天的收益率，从第5天开始，计算2次，步长为5天
        self.df = util.prepared_next_rate(self.df, 5, 2, 5)  # 计算第5天和第10天的收益率，从第5天开始，计算2次，步长为5天
        self.df = util.prepared_avg(self.df)  # 填充均值
        self.df = util.prepared_ma(self.df)  # 填充MA均线
        self.df = util.prepared_amp(self.df)  # 填充最大振幅
        self.df = util.prepared_next(self.df)  # 填充次日数据
        self.df = util.prepared_other(self.df)  # 填充其它swi

    def model_amp(self, df):
        self.df = self.df.sort_values('date')  # 日期排序

    ################################################################################

    def prepared(self, model_type = 'rate'):
        self.model_execution = self.model_type[model_type]
        self.model_execution(self. df)

        # df = self.load(default_datadir + 'c.dat')
        # self.save(default_datadir + 'c.dat', self.df)

        #############################################################################################################

        # 分离训练和测试数据
    #   self.df_train, self.df_test = self.split(self.df, 0.6)

    #   # 构建训练特征数据
    #   other_features_lst = ohlc_lst + profit_lst # + xagv_lst + ma100_lst + other_lst
    #   self.x_train = util.get_features(self.df_train, other_features_lst)
    #   self.x_test = util.get_features(self.df_test, other_features_lst)

    #   #############################################################################################################

    #   # 构建特征，也就是结果值Y
    #   self.y_train = util.prepared_y(self.df_train, 'next_rate_10_type')
    #   self.y_test = util.prepared_y(self.df_test, 'next_rate_10_type')

        #############################################################################################################

    #   y_lst = self.y_train[0]
    #   x_lst = other_features_lst

    #   num_in, num_out = len(x_lst), len(y_lst)

    #   print('\n self.df_test.tail()', self.df_test.tail())
    #   print('\n self.x_train.shape,', self.x_train.shape)
    #   print('\n type(self.x_train),', type(self.x_train))

    #   rxn, txn = self.x_train.shape[0], self.x_test.shape[0]
    #   self.x_train, self.x_test = self.x_train.reshape(rxn, num_in, -1), self.x_test.reshape(txn, num_in, -1)
    #   print('\n x_train.shape,', self.x_train.shape)
    #   print('\n type(x_train),', type(self.x_train))

    #   print('\n num_in, num_out:', num_in, num_out)

        # mx = zks.rnn010(num_in, num_out)
        # mx = zks.lstm010(num_in, num_out)
     #   mx = zks.lstm020typ(num_in, num_out)
     #   #
     #   mx.summary()
     #   plot_model(mx, to_file = default_datadir + 'model.png')
#
     #   print('\n#4 模型训练 fit')
     #   tbCallBack = keras.callbacks.TensorBoard(log_dir = default_logdir, write_graph = True, write_images=True)
     #   tn0 = arrow.now()
     #   mx.fit(self.x_train, self.y_train, epochs = 500, batch_size = 512, callbacks = [tbCallBack])
     #   tn = zt.timNSec('', tn0, True)
#
     #   print('\n#5 模型预测 predict')
     #   tn0 = arrow.now()
     #   y_pred0 = mx.predict(self.x_test)
     #   tn = zt.timNSec('', tn0, True)
     #   y_pred = np.argmax(y_pred0, axis = 1) + 1
     #   #
     #   self.df_test['y_pred'] = zdat.ds4x(y_pred, self.df_test.index, True)
     #   self.df_test.to_csv(default_datadir + 'my.csv', index = False)
#
     #   print('NaN的数量:', self.df_test.isnull().sum().sum())
#
     #   print('\n#6 acc准确度分析')
     #   print('\nky0=10')
#
     #   dacc, dfx, a10 = ztq.ai_acc_xed2ext(self.df_test.y, self.df_test.y_pred, ky0 = 3, fgDebug = True)
#
     #   x1, x2 = self.df_test['y'].value_counts(), self.df_test['y_pred'].value_counts()
     #   zt.prx('x1', x1);
     #   zt.prx('x2', x2)

################################################################################

