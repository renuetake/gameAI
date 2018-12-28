import random
import numpy as np
import tensorflow as tf
import nn
import nnmodel
import nnhelper
from nnconfig import *

def make_mini_batch_list(all_input_paths, rewards, initialize):
    """
    make_mini_batch_list
        ミニバッチを生成する

    Inputs
    ----------
    all_input_paths : list string [None(画像の数), フレーム数]
        学習に使う全ての状態ごとの各画像のpathが格納されている

    rewards : list float [None(画像の数)]
        all_input_pathsと対になりその報酬が格納されている

    initialize : bool
        モデルの初期化を行うかどうか, Trueならば行う

    Outputs
    ----------
    mini_batch_list : list [ミニバッチ数, BATCH_SIZE, 2(入力データ np.array np.float32 [IMAGE_SIZE * IMAGE_SIZE * フレーム数], 教師データ np.array np.float32 [ACTION_NUM])]
        ミニバッチのリスト, 入力と教師データの対がバッチサイズごとにまとめられて, さらにそれらをリストでラップしている
    """
    mini_batch_list = []
    mini_batch = []
    for t in range(len(all_input_paths) - 1):
        s_t0 = nnhelper.images2array(all_input_paths[t])
        s_t1 = nnhelper.images2array(all_input_paths[t + 1])
        q_next = nn.get_qvalues(s_t1, initialize)
        mask = np.zeros(CLASS_NUM)
        mask[q_next.argmax] = 1
        expQ = (mask * rewards[t]) + (mask * GAMMA) * q_next
        mini_batch.append([s_t0, expQ])
        if t % BATCH_SIZE == BATCH_SIZE - 1:
            mini_batch_list.append(mini_batch)
            mini_batch = []
        
    return mini_batch_list

def train(all_input_paths, rewards, initialize=False):
    """
    train
        学習を行う

    Inputs
    ----------
    all_input_paths : list string [None(画像の数), フレーム数]
        学習に使う全ての状態ごとの各画像のpathが格納されている

    rewards : list float [None(画像の数)]
        all_input_pathsと対になりその報酬が格納されている

    initialize : bool
        default : False
        モデルの初期化を行うかどうか, Trueならば行う

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
        # セッションの作成
        sess = tf.Session()
        # セッションの開始及び初期化
        sess.run(tf.global_variables_initializer())

        # 学習
        for epoch in range(EPOCH_SIZE):
            # バッチ生成
            mini_batch_list = make_mini_batch_list(all_input_paths, rewards, initialize=initialize)
            random.shuffle(mini_batch_list)
            for mini_batch in mini_batch_list:
                # 状態sで期待されるQ値expected_qvaluesが出力されるように重みを調整
                sess.run(train_step, feed_dict={x: mini_batch[0], t: mini_batch[1], keep_prob: 0.5})
                # 1epoch毎に学習データに対して精度を出す
                # train_loss = sess.run(loss_values, feed_dict={x: batch[0], t: batch[1], keep_prob: 1.0})
                # print(f'[epoch {epoch+1:02d}] oss={train_loss:12.10f}')

        # 完成したモデルを保存する
        saver.save(sess, CHECKPOINT)