import tensorflow as tf
import numpy as np

c = np.array([[3.,4], [5.,6], [6.,7]])
step = tf.reduce_mean(c, 1)                                                                                 
with tf.Session() as sess:
    print(sess.run(step))
