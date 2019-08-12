from __future__ import print_function

import os
import math
import arrow
from IPython import display
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
from sklearn import metrics
import tensorflow as tf
from tensorflow.python.data import Dataset

import keras
import keras as ks
from keras import initializers,models,layers
from keras.preprocessing import sequence
from keras.models import Sequential,load_model
from keras.layers import Dense, Input, Dropout, Embedding, LSTM, Bidirectional,Activation,SimpleRNN,Conv1D,MaxPooling1D, GlobalMaxPooling1D,GlobalAveragePooling1D
from keras.utils import plot_model

import zsys
import zpd_talib as zta
import ztools as zt
import ztools_data as zdat
import ztools_datadown as zddown
import ztools_tq as ztq
import zai_keras as zks

################################################################################

default_datadir = './data/'
default_logdir = './data/logs/'

ohlc_lst = ['open', 'high', 'low', 'close']

ma100_lst_var = [2, 3, 5, 10, 15, 20, 25, 30, 50, 100]
ma100_lst = ['ma_2', 'ma_3', 'ma_5', 'ma_10', 'ma_15', 'ma_20', 'ma_25', 'ma_30', 'ma_50', 'ma_100']
ma200_lst_var = [2, 3, 5, 10, 15, 20, 25, 30, 50, 100, 150, 200]
ma200_lst = ['ma_2', 'ma_3', 'ma_5', 'ma_10', 'ma_15', 'ma_20','ma_30', 'ma_50', 'ma_100', 'ma_150', 'ma_200']
ma030_lst_var = [2, 3, 5, 10, 15, 20, 25, 30]
ma030_lst = ['ma_2', 'ma_3', 'ma_5', 'ma_10', 'ma_15', 'ma_20', 'ma_25', 'ma_30']

xagv_lst = ['xavg1', 'xavg2','xavg3','xavg4','xavg5','xavg6','xavg7','xavg8','xavg9']

other_lst = ['price_range', 'amp', 'amp_type']

################################################################################

def mkdir(path):
    # 去除首位空格
    path = path.strip()
    # 去除尾部 \ 符号
    path = path.rstrip("\\")
    # 判断结果
    if not os.path.exists(path):
        # 如果不存在则创建目录
        os.makedirs(path)
        return True
    else:
        return False

################################################################################

class down_data():
    def __init__(self, data_dir = default_datadir):
        self.data_dir = data_dir
        self.rss = self.data_dir + 'xday/'

        mkdir(self.rss)

    def download_inx(self, filename = "inx_index.csv"):
        finx = self.data_dir + filename
        zddown.down_stk_inx(self.rss, finx);

    def downlaod_stk(self, filename = "stk_index.csv"):
        xtyp = '5'
        finx = self.data_dir + filename;
        zddown.down_stk_all(self.rss, finx, xtyp)

################################################################################

class  train_data():

    def __init__(self, data_dir, data_file):
        self.data_dir = data_dir
        self.data_file = data_file
        self.df = pd.read_csv(data_dir + data_file, index_col = 0)

    # 填充前一天和后一天的值
    def prepared_pre_next(self, df):
        df['next_open'] = df['open'].shift(-1)  # 后一天的开盘价
        df['pre_close'] = df['close'].shift(1)  # 前一天收盘价
        return df

    # 计算均值
    def prepared_avg(self, df):
        df['ohlc_avg'] = df[ohlc_lst].mean(axis = 1).round(2) # 当天OHLC均值
        df = zdat.df_xed_nextDay(df, ksgn = 'ohlc_avg', newSgn = 'xavg', nday = 10) #10日均值
        return df

    # 计算MA均线
    def prepared_ma(self, df):
        return zta.mul_talib(zta.MA,  df, ksgn = 'ohlc_avg', vlst = zsys.ma100Lst_var) # ma

    # 计算振幅
    def prepared_amp(self, df):
        df['price_range'] = df['high'].sub(df['low'])  # 当天振幅
        df['amp'] = df['price_range'].div(df['pre_close'])  # 当天振幅
        df['amp_type'] = df['amp'].apply(zt.iff3type, d0=0.03, d9=0.05, v3=3, v2=2, v1=1)  # 振幅分类器
        return df

    # 次日数据
    def prepared_next(self, df):
        df['next_ohlc_avg'] = df['ohlc_avg'].shift(-1)
        df['next_price_range'] = df['price_range'].shift(-1)
        df['next_amp'] = df['amp'].shift(-1)
        df['next_amp_type'] = df['amp_type'].shift(-1)
        return df

    # 其它处理
    def prepared_other(self, df):
        # 清除NaN值
        df = df.fillna(method='pad')
        df = df.fillna(method='bfill')

        return df

    # 处理标签数据
    def prepared_y(self, df, y_key, type = 'onehot'):
        # 处理标签

        df['y'] = df[y_key] # 输出

        if (type == 'onehot'):
            # 分类模式， One-Hot
            return self.get_onehot(df, 'y')
        else:
            return df['y']

    def split(self, df, DC):
        # 训练数据和测试数据分割
        dnum_train = len(df.index)
        dnum_test = round(dnum_train * DC)

        return df.head(dnum_test), df.tail(dnum_train - dnum_test)

    def get_onehot(self, df, k):
        return pd.get_dummies(df[k]).values

    def get_features(self, df, features_lst):
        return df[features_lst].values

    def training(self, df):
        return df

    # def modelling(self, df):

    # def plot(self):

    def prepared(self):
        self.df = self.df.sort_values('date') #日期排序

        self.df = self.prepared_pre_next(self.df) # 前一天收盘价和后一天的开盘价
        self.df = self.prepared_avg(self.df) # 填充均值
        self.df = self.prepared_ma(self.df) # 填充MA均线
        self.df = self.prepared_amp(self.df)  # 填充最大振幅
        self.df = self.prepared_next(self.df)  # 填充次日数据
        self.df = self.prepared_other(self.df)  # 填充其它

        #############################################################################################################

        # 分离训练和测试数据
        self.df_train, self.df_test = self.split(self.df, 0.6)

        # 构建训练特征数据
        other_features_lst = ohlc_lst + xagv_lst + ma100_lst + other_lst
        self.x_train = self.get_features(self.df_train, other_features_lst)
        self.x_test = self.get_features(self.df_test, other_features_lst)

        #############################################################################################################

        # 构建特征值
        self.y_train = self.prepared_y(self.df_train, 'next_amp_type')
        self.y_test = self.prepared_y(self.df_test, 'next_amp_type')

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

        print('\nnum_in, num_out:', num_in, num_out)
        # mx = zks.rnn010(num_in, num_out)
        # mx = zks.lstm010(num_in, num_out)
        mx = zks.lstm020typ(num_in, num_out)
        #
        mx.summary()
        plot_model(mx, to_file = default_datadir + 'model.png')

        print('\n#4 模型训练 fit')
        tbCallBack = keras.callbacks.TensorBoard(log_dir = default_logdir, write_graph = True, write_images=True)
        tn0 = arrow.now()
        mx.fit(self.x_train, self.y_train, epochs = 500, batch_size = 512, callbacks = [tbCallBack])
        tn = zt.timNSec('', tn0, True)

        print('\n#5 模型预测 predict')
        tn0 = arrow.now()
        y_pred0 = mx.predict(self.x_test)
        tn = zt.timNSec('', tn0, True)
        y_pred = np.argmax(y_pred0, axis = 1) + 1
        #
        self.df_test['y_pred'] = zdat.ds4x(y_pred, self.df_test.index, True)
        self.df_test.to_csv(default_datadir + 'my.csv', index = False)

        print('NaN的数量:', self.df_test.isnull().sum().sum())

        print('\n#6 acc准确度分析')
        print('\nky0=10')

        dacc, dfx, a10 = ztq.ai_acc_xed2ext(self.df_test.y, self.df_test.y_pred, ky0 = 5, fgDebug = True)

        x1, x2 = self.df_test['y'].value_counts(), self.df_test['y_pred'].value_counts()
        zt.prx('x1', x1);
        zt.prx('x2', x2)

################################################################################

class train():
    def __init__(self, train_data):
        self.data_obj = train_data

    def training(self, num_in=1, num_out=1):
        self.model = Sequential()
        self.model.add(Dense(num_in * 4, input_dim=num_in, activation='relu'))
        self.model.add(Dense(num_out))
        #
        # mean_squared_error
        self.model.compile('adam', 'mse', metrics=['acc'])
        self.model.summary()

        # plot_model(self.model, to_file = rlog + 'mx_training.png')

        tbCallBack = keras.callbacks.TensorBoard(log_dir = default_logdir, write_graph=True, write_images=True)

        x_train, y_train = self.data_obj.df_train['max_price_range', 'ohlc_avg'].values, self.data_obj.df_train['next_range_price'].values
        x_test, y_test = self.data_obj.df_test['max_price_range', 'ohlc_avg'].values, self.data_obj.df_test['next_range_price'].values

        self.model.fit(x_train, y_train, epochs=500, batch_size=512, callbacks=[tbCallBack])

        tn0 = arrow.now()
        y_pred = self.model.predict(x_test)
        tn = zt.timNSec('', tn0, True)
        self.data_obj.df_test['y_pred'] = zdat.ds4x(y_pred, self.data_obj.df_test.index, True)
        self.data_obj.df_test.to_csv(default_logdir + 'df_tst.csv', index=False)

    def draw(self):
        df_draw = pd.DataFrame()
        df_draw['range_price_type'] = self.data_obj.df_test['range_price_type']
        df_draw['y_pred'] = self.data_obj.df_test['y_pred']
        df_draw.plot()
        plt.show()
################################################################################

def testing():
    device_name = tf.test.gpu_device_name()
    if device_name != '/device:GPU:0':
        raise SystemError('GPU device not found')
    print('Found GPU at: {}'.format(device_name))

def load(filename):
    data_obj = train_data(default_datadir, filename)
    data_obj.prepared()
    print(data_obj.df.tail(10))

    return data_obj

def init():
    # testing()
    #
    # tf.logging.set_verbosity(tf.logging.ERROR)
    # pd.options.display.max_rows = 10
    # pd.options.display.float_format = '{:.1f}'.format
    pd.set_option('display.max_rows', 10)
    pd.set_option('display.width', 450)
    pd.set_option('display.float_format', zt.xfloat5)

    mkdir(default_datadir)
    mkdir(default_logdir)

################################################################################

# down_obj = down_data(default_datadir)
# down_obj.download_inx()
# down_obj.downlaod_stk()

init()
data_obj = load("601988.csv")
# train_obj = train(data_obj)
# train_obj.training()
# train_obj.draw()

exit(0)

california_housing_dataframe = pd.read_csv("./data/california_housing_train.csv", sep=",")

# california_housing_dataframe = california_housing_dataframe.reindex(
#     np.random.permutation(california_housing_dataframe.index))

def preprocess_features(california_housing_dataframe):
  """Prepares input features from California housing data set.

  Args:
    california_housing_dataframe: A Pandas DataFrame expected to contain data
      from the California housing data set.
  Returns:
    A DataFrame that contains the features to be used for the model, including
    synthetic features.
  """
  selected_features = california_housing_dataframe[
    ["latitude",
     "longitude",
     "housing_median_age",
     "total_rooms",
     "total_bedrooms",
     "population",
     "households",
     "median_income"]]
  processed_features = selected_features.copy()
  # Create a synthetic feature.
  processed_features["rooms_per_person"] = (
    california_housing_dataframe["total_rooms"] /
    california_housing_dataframe["population"])
  return processed_features

def preprocess_targets(california_housing_dataframe):
  """Prepares target features (i.e., labels) from California housing data set.

  Args:
    california_housing_dataframe: A Pandas DataFrame expected to contain data
      from the California housing data set.
  Returns:
    A DataFrame that contains the target feature.
  """
  output_targets = pd.DataFrame()
  # Scale the target to be in units of thousands of dollars.
  output_targets["median_house_value"] = (
    california_housing_dataframe["median_house_value"] / 1000.0)
  return output_targets

def construct_feature_columns(input_features):
  """Construct the TensorFlow Feature Columns.

  Args:
    input_features: The names of the numerical input features to use.
  Returns:
    A set of feature columns
  """
  return set([tf.feature_column.numeric_column(my_feature)
              for my_feature in input_features])

def my_input_fn(features, targets, batch_size=1, shuffle=True, num_epochs=None):
    """Trains a linear regression model.

    Args:
      features: pandas DataFrame of features
      targets: pandas DataFrame of targets
      batch_size: Size of batches to be passed to the model
      shuffle: True or False. Whether to shuffle the data.
      num_epochs: Number of epochs for which data should be repeated. None = repeat indefinitely
    Returns:
      Tuple of (features, labels) for next data batch
    """

    # Convert pandas data into a dict of np arrays.
    features = {key: np.array(value) for key, value in dict(features).items()}

    # Construct a dataset, and configure batching/repeating.
    ds = Dataset.from_tensor_slices((features, targets))  # warning: 2GB limit
    ds = ds.batch(batch_size).repeat(num_epochs)

    # Shuffle the data, if specified.
    if shuffle:
        ds = ds.shuffle(10000)

    # Return the next batch of data.
    features, labels = ds.make_one_shot_iterator().get_next()
    return features, labels

def train_model(
        learning_rate,
        steps,
        batch_size,
        training_examples,
        training_targets,
        validation_examples,
        validation_targets):
    """Trains a linear regression model.

    In addition to training, this function also prints training progress information,
    as well as a plot of the training and validation loss over time.

    Args:
      learning_rate: A `float`, the learning rate.
      steps: A non-zero `int`, the total number of training steps. A training step
        consists of a forward and backward pass using a single batch.
      batch_size: A non-zero `int`, the batch size.
      training_examples: A `DataFrame` containing one or more columns from
        `california_housing_dataframe` to use as input features for training.
      training_targets: A `DataFrame` containing exactly one column from
        `california_housing_dataframe` to use as target for training.
      validation_examples: A `DataFrame` containing one or more columns from
        `california_housing_dataframe` to use as input features for validation.
      validation_targets: A `DataFrame` containing exactly one column from
        `california_housing_dataframe` to use as target for validation.

    Returns:
      A `LinearRegressor` object trained on the training data.
    """

    periods = 10
    steps_per_period = steps / periods

    # Create a linear regressor object.
    my_optimizer = tf.train.GradientDescentOptimizer(learning_rate=learning_rate)
    my_optimizer = tf.contrib.estimator.clip_gradients_by_norm(my_optimizer, 5.0)
    linear_regressor = tf.estimator.LinearRegressor(
        feature_columns=construct_feature_columns(training_examples),
        optimizer=my_optimizer
    )

    # Create input functions.
    training_input_fn = lambda: my_input_fn(training_examples,
                                            training_targets["median_house_value"],
                                            batch_size=batch_size)
    predict_training_input_fn = lambda: my_input_fn(training_examples,
                                                    training_targets["median_house_value"],
                                                    num_epochs=1,
                                                    shuffle=False)
    predict_validation_input_fn = lambda: my_input_fn(validation_examples,
                                                      validation_targets["median_house_value"],
                                                      num_epochs=1,
                                                      shuffle=False)

    # Train the model, but do so inside a loop so that we can periodically assess
    # loss metrics.
    print("Training model...")
    print("RMSE (on training data):")
    training_rmse = []
    validation_rmse = []
    for period in range(0, periods):
        # Train the model, starting from the prior state.
        linear_regressor.train(
            input_fn=training_input_fn,
            steps=steps_per_period,
        )
        # Take a break and compute predictions.
        training_predictions = linear_regressor.predict(input_fn=predict_training_input_fn)
        training_predictions = np.array([item['predictions'][0] for item in training_predictions])

        validation_predictions = linear_regressor.predict(input_fn=predict_validation_input_fn)
        validation_predictions = np.array([item['predictions'][0] for item in validation_predictions])

        # Compute training and validation loss.
        training_root_mean_squared_error = math.sqrt(
            metrics.mean_squared_error(training_predictions, training_targets))
        validation_root_mean_squared_error = math.sqrt(
            metrics.mean_squared_error(validation_predictions, validation_targets))
        # Occasionally print the current loss.
        print("  period %02d : %0.2f" % (period, training_root_mean_squared_error))
        # Add the loss metrics from this period to our list.
        training_rmse.append(training_root_mean_squared_error)
        validation_rmse.append(validation_root_mean_squared_error)
    print("Model training finished.")

    # Output a graph of loss metrics over periods.
    plt.ylabel("RMSE")
    plt.xlabel("Periods")
    plt.title("Root Mean Squared Error vs. Periods")
    plt.tight_layout()
    plt.plot(training_rmse, label="training")
    plt.plot(validation_rmse, label="validation")
    plt.legend()

    return linear_regressor


training_examples = preprocess_features(california_housing_dataframe.head(12000))
display.display(training_examples.describe())

training_targets = preprocess_targets(california_housing_dataframe.head(12000))
display.display(training_targets.describe())

validation_examples = preprocess_features(california_housing_dataframe.tail(5000))
display.display(validation_examples.describe())

validation_targets = preprocess_targets(california_housing_dataframe.tail(5000))
display.display(validation_targets.describe())

plt.figure(figsize=(13, 8))

ax = plt.subplot(1, 2, 1)
ax.set_title("Validation Data")

ax.set_autoscaley_on(False)
ax.set_ylim([32, 43])
ax.set_autoscalex_on(False)
ax.set_xlim([-126, -112])
plt.scatter(validation_examples["longitude"],
            validation_examples["latitude"],
            cmap="coolwarm",
            c=validation_targets["median_house_value"] / validation_targets["median_house_value"].max())

ax = plt.subplot(1,2,2)
ax.set_title("Training Data")

ax.set_autoscaley_on(False)
ax.set_ylim([32, 43])
ax.set_autoscalex_on(False)
ax.set_xlim([-126, -112])
plt.scatter(training_examples["longitude"],
            training_examples["latitude"],
            cmap="coolwarm",
            c=training_targets["median_house_value"] / training_targets["median_house_value"].max())
_ = plt.plot()

plt.show()

# Double-check that we've done the right thing.
print("Training examples summary:")
display.display(training_examples.describe())
print("Validation examples summary:")
display.display(validation_examples.describe())

print("Training targets summary:")
display.display(training_targets.describe())
print("Validation targets summary:")
display.display(validation_targets.describe())

correlation_dataframe = training_examples.copy()
correlation_dataframe["target"] = training_targets["median_house_value"]

correlation_dataframe.corr()
display.display(correlation_dataframe.describe())

#
# Your code here: add your features of choice as a list of quoted strings.
#
minimal_features = [
]

assert minimal_features, "You must select at least one feature!"

minimal_training_examples = training_examples[minimal_features]
minimal_validation_examples = validation_examples[minimal_features]

#
# Don't forget to adjust these parameters.
#
train_model(
    learning_rate=0.001,
    steps=500,
    batch_size=5,
    training_examples=minimal_training_examples,
    training_targets=training_targets,
    validation_examples=minimal_validation_examples,
    validation_targets=validation_targets)

minimal_features = [
  "median_income",
  "latitude",
]

minimal_training_examples = training_examples[minimal_features]
minimal_validation_examples = validation_examples[minimal_features]
#
#_ = train_model(
#    learning_rate=0.01,
#    steps=500,
#    batch_size=5,
#    training_examples=minimal_training_examples,
#    training_targets=training_targets,
#    validation_examples=minimal_validation_examples,
#    validation_targets=validation_targets)
#