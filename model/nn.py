import numpy as np
import tensorflow as tf
import nnhelper
import nnmodel
from nnconfig import *

def get_qvalues(image_paths):
    """
    get_qvalues
        Inputで受け取ったパスの画像を状態とした時のQ値を出力する

    Inputs
    ----------
    image_paths : list string [フレーム数]
        状態となる各画像のpathが格納されている

    Outputs
    ----------
    qvalues : np.array np.float32 [アクション数]
        各行動のQ値
    """
    # 画像の準備(状態)
    s_t = nnhelper.images2array(image_paths)

    with tf.Graph().as_default():
        # Q値の算出
        x = np.asarray([s_t])
        y = tf.nn.softmax(nnmodel.inference(x, 1.0))

        # 保存の準備
        saver = tf.train.Saver()

        # モデルの読み込み
        with tf.Session() as sess:
            ckpt = tf.train.get_checkpoint_state(CHECKPOINT_PATH)
            if ckpt:
                saver.restore(sess, CHECKPOINT)
            else:
                init = tf.initialize_all_variables()
                sess.run(init)
                saver.save(sess, CHECKPOINT)
            
            # 実行
            qvalues = sess.run(y)

        return qvalues