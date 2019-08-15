import arrow
import keras
from keras.utils import plot_model


from vendor import ztools as zt
from vendor import zai_keras as zks
from quant import dataobject as do
from quant import evaluation as eva
from utils import params as p

class model():
    def __init__(self, do):
        self.do = do # 数据对象

    def modeling(self, type = 'rate'): # 建模过程
        self.do.prepared(type)

    def building(self):

        # 分离训练和测试数据
        self.df_train, self.df_test = do.util.split(self.do.df, 0.6)

        # 构建训练特征数据
        other_features_lst = p.ohlc_lst + p.profit_lst # + xagv_lst + ma100_lst + other_lst
        self.x_train = do.util.get_features(self.df_train, other_features_lst)
        self.x_test = do.util.get_features(self.df_test, other_features_lst)

        #############################################################################################################

        # 构建特征，也就是结果值Y
        self.y_train = do.util.prepared_y(self.df_train, 'next_rate_10_type')
        self.y_test = do.util.prepared_y(self.df_test, 'next_rate_10_type')

        y_lst = self.y_train[0]
        x_lst = other_features_lst

        num_in, num_out = len(x_lst), len(y_lst)

        print('\n self.df_test.tail()', self.df_test.tail())
        print('\n self.x_train.shape,', self.x_train.shape)
        print('\n type(self.x_train),', type(self.x_train))

        rxn, txn = self.x_train.shape[0], self.x_test.shape[0]
        self.x_train, self.x_test = self.x_train.reshape(rxn, num_in, -1), self.x_test.reshape(txn, num_in, -1)
        print('\n x_train.shape,', self.x_train.shape)
        print('\n type(x_train),', type(self.x_train))

        print('\n num_in, num_out:', num_in, num_out)

        # mx = zks.rnn010(num_in, num_out)
        # mx = zks.lstm010(num_in, num_out)

        mx = zks.lstm020typ(num_in, num_out)
        mx.summary()
        plot_model(mx, to_file = p.default_datadir + 'model.png')

        print('\n#4 模型训练 fit')
        tbCallBack = keras.callbacks.TensorBoard(log_dir = p.default_logdir, write_graph = True, write_images=True)
        tn0 = arrow.now()
        mx.fit(self.x_train, self.y_train, epochs = 500, batch_size = 512, callbacks = [tbCallBack])
        tn = zt.timNSec('', tn0, True)

        eva_obj = eva.evaluation(self.do)
        eva_obj.predict(mx, self.df_test, self.x_test)
#
     #   print('\n#5 模型预测 predict')
     #   tn0 = arrow.now()
     #   y_pred0 = mx.predict(self.x_test)
     #   tn = zt.timNSec('', tn0, True)
     #   y_pred = np.argmax(y_pred0, axis = 1) + 1
     #   #
     #   self.df_test['y_pred'] = zdat.ds4x(y_pred, self.df_test.index, True)
     #   self.df_test.to_csv(p.default_datadir + 'my.csv', index = False)
##
     #   print('NaN的数量:', self.df_test.isnull().sum().sum())