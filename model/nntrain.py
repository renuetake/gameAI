import random
import numpy as np
import tensorflow as tf
import nn
import nnmodel
import nnhelper
from nnconfig import *

def make_mini_batch_list(states, rewards):
    """
    make_mini_batch_list
        ミニバッチを生成する

    Inputs
    ----------
    states : np.array float [None(状態数), フレーム数, width, height]
        学習に使う全ての状態ごとの各画像のnp.arrayが格納されている

    rewards : list float [None(状態数)]
        statesと対になりその報酬が格納されている

    Outputs
    ----------
    mini_batch_list : list [ミニバッチ数, BATCH_SIZE, 2(入力データ np.array np.float32 [IMAGE_SIZE * IMAGE_SIZE * フレーム数], 教師データ np.array np.float32 [ACTION_NUM])]
        ミニバッチのリスト, 入力と教師データの対がバッチサイズごとにまとめられて, さらにそれらをリストでラップしている
    """
    mini_batch_list = []
    mini_batch = []
    for t in range(states.shape[0] - 1):
        s_t0 = nnhelper.resize_images(states[t])
        s_t1 = nnhelper.resize_images(states[t + 1])
        q_next = nn.get_qvalues(s_t1)
        mask = np.zeros(CLASS_NUM)
        mask[q_next.argmax] = 1
        expQ = (mask * rewards[t]) + (mask * GAMMA) * q_next
        mini_batch.append([s_t0, expQ])
        if t % BATCH_SIZE == BATCH_SIZE - 1:
            mini_batch_list.append(mini_batch)
            mini_batch = []
        
    return mini_batch_list

def train(states, rewards):
    """
    train
        学習を行う

    Inputs
    ----------
    states : np.array float [None(状態数), フレーム数, width, hight]
        学習に使う全ての状態ごとの各画像のnp.arrayが格納されている

    rewards : list float [None(状態数)]
        statesと対になりその報酬が格納されている

    Outputs
    ----------
        なし
    """

    with tf.Graph().as_default():
        # dropout率
        keep_prob = tf.placeholder(tf.float32)
        # 画像データ
        x = tf.placeholder(tf.float32, [None, INPUT_NEURONS])
        # 教師データ
        t = tf.placeholder(tf.float32, [None, CLASS_NUM])
        # 出力データ
        y = nnmodel.inference(x, keep_prob)
        # 誤差出力
        loss_values = nnmodel.loss(y, t)
        # 学習
        train_step = nnmodel.training(loss_values)

        # 保存の準備
        saver = tf.train.Saver()
        
        with tf.Session() as sess:
            saver.restore(sess, CHECKPOINT)

            # 学習
            for epoch in range(EPOCH_SIZE):
                # バッチ生成
                mini_batch_list = make_mini_batch_list(states, rewards)
                random.shuffle(mini_batch_list)
                for mini_batch in mini_batch_list:
                    # 状態sで期待されるQ値expected_qvaluesが出力されるように重みを調整
                    sess.run(train_step, feed_dict={x: mini_batch[0], t: mini_batch[1], keep_prob: 0.5})
                    # 1epoch毎に学習データに対して精度を出す
                    # train_loss = sess.run(loss_values, feed_dict={x: batch[0], t: batch[1], keep_prob: 1.0})
                    # print(f'[epoch {epoch+1:02d}] oss={train_loss:12.10f}')

            # 完成したモデルを保存する
            saver.save(sess, CHECKPOINT)