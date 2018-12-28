import tensorflow as tf
from nnconfig import *

def inference(x, keep_prob):
    """
    inference
        モデルの定義と計算

    Inputs
    ----------
    x : tensor tf.float32 [BATCH_SIZE, IMAGE * IMAGE * フレーム数]
        入力データ

    keep_prob : tensor tf.float32
        ドロップアウト率

    Outputs
    ----------
    y : tensor tf.float32 [BATCH_SIZE, 行動数]
        現在のNNの重みで出力したQ値
    """
    # 重みを標準偏差0.1の正規分布で初期化する
    def weight_variable(shape):
        initial = tf.truncated_normal(shape, stddev=0.1)
        return tf.Variable(initial)

    # バイアスを0.1の定数で初期化する
    def bias_variable(shape):
        initial = tf.constant(0.1, shape=shape)
        return tf.Variable(initial)

    # 畳み込みを行う
    def conv2d(x, W):
        # 縦横ともにストライドは1でゼロパディングを行う
        return tf.nn.conv2d(x, W, strides=[1, 1, 1, 1], padding='SAME')

    # 畳み込み層を作成する
    def conv_layer(x, filter_size, filter_in, filter_out):
        # 重み
        W = weight_variable([filter_size, filter_size, filter_in, filter_out])
        # バイアス
        b = bias_variable([filter_out])
        # 活性化関数
        return tf.nn.relu(conv2d(x, W) + b)

    # プーリング層を作成する
    def pool_layer(x, image_size):
        # MAXプーリング（カーネルサイズ2px*2px、縦横ともにストライドは2、ゼロパディング）
        h = tf.nn.max_pool(x, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')
        # 画像サイズは半分になる
        return h, int(image_size / 2)

    # 全結合層を作成する
    def dense_layer(x, dense_in, dense_out):
        # 重み
        W = weight_variable([dense_in, dense_out])
        # バイアス
        b = bias_variable([dense_out])
        # 結合
        return tf.matmul(x, W) + b

    # 平坦化されたベクトルを画像に戻す
    x_image = tf.reshape(x, [-1, IMAGE_SIZE, IMAGE_SIZE, CHANNEL_NUM])

    # 畳み込み層のフィルターサイズ 畳み込みは3px*3pxのカーネルサイズで行う
    filter_size = 3

    # 第1畳み込み層
    conv1_in = CHANNEL_NUM
    conv1_out = 32
    conv1 = conv_layer(x_image, filter_size, conv1_in, conv1_out)
    # 第1プーリング層
    pool1, out_size = pool_layer(conv1, IMAGE_SIZE)

    # 第2畳み込み層
    conv2_in = conv1_out
    conv2_out = 64
    conv2 = conv_layer(pool1, filter_size, conv2_in, conv2_out)
    # 第2プーリング層
    pool2, out_size = pool_layer(conv2, out_size)

    # 画像を平坦化してベクトルにする
    dimension = out_size * out_size * conv2_out
    x_flatten = tf.reshape(pool2, [-1, dimension])

    # 全結合層
    fc = dense_layer(x_flatten, dimension, conv2_out)
    # 活性化関数
    fc = tf.nn.relu(fc)

    # ドロップアウト
    drop = tf.nn.dropout(fc, keep_prob)

    # モデル出力
    y = dense_layer(drop, conv2_out, CLASS_NUM)

    y = tf.nn.tanh(y)

    return y

def loss(y, t):
    """
    loss
        期待されるQ値と現在のQ値との最小2乗誤差を出力

    Inputs
    ----------
    y : tensor tf.float32 [ミニバッチ数, 行動数]
        現在のNNの重みで出力したQ値

    t : tensor tf.float32 [ミニバッチ数, 行動数]
        教師データ(このQ値を出力させたい)

    Outputs
    ----------
    loss_values : tensor tf.float32 [BATCH_SIZE, 行動数]
        各現在のQ値に対しての誤差
    """
    loss_values = tf.square(t - y) / 2
    return loss_values

def training(loss_values):
    """
    training
        誤差を最小にするように重みを変更

    Inputs
    ----------
    loss_values : tensor tf.float32 [BATCH_SIZE, 行動数]
        各現在のQ値に対しての誤差

    Outputs
    ----------
    tf.train.AdamOptimizer(LEARNING_RATE).minimize(loss_values) : よくわからない
        ドキュメントリンク : https://www.tensorflow.org/api_docs/python/tf/train/AdamOptimizer
        An Operation that updates the variables in var_list. If global_step was not None, that operation also increments global_step.
    """
    # 勾配降下アルゴリズム(Adam)を用いて誤差を最小化する
    return tf.train.AdamOptimizer(LEARNING_RATE).minimize(loss_values)