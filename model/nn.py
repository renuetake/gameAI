import numpy as np
import tensorflow as tf
import nnhelper
import nnmodel
from nnconfig import *

"""
get_qvalues
    Inputで受け取ったパスの画像を状態とした時のQ値を出力する

Inputs
----------
image_paths : list string [フレーム数]
    状態となる各画像のpathが格納されている

initialize : bool
    default : False
    モデルの初期化を行うかどうか, Trueならば行う

Outputs
----------
qvalues : np.array np.float32 [アクション数]
    各行動のQ値
"""
def get_qvalues(image_paths, initialize=False):
    # 画像の準備(状態)
    s_t = nnhelper.images2array(image_paths)

    with tf.Graph().as_default():
        # Q値の算出
        x = np.asarray([s_t])
        y = tf.nn.softmax(nnmodel.inference(x, 1.0))

        # 保存の準備
        saver = tf.train.Saver()
        # セッションの作成
        sess = tf.Session()
        # セッションの開始及び初期化
        sess.run(tf.global_variables_initializer())

        # モデルの読み込み
        if initialize == True:
            saver.restore(sess, CHECKPOINT)

        # 実行
        qvalues = sess.run(y)

        return qvalues