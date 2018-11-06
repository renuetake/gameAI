# gameAI

## How to use Docker

Dockerで環境を構築する
```
# イメージ作成(Dockerfileがあるディレクトリで実行)
$ docker build ./ -t game_ai

# コンテナ作成
$ docker run -v $PWD:/work -itd --name game_ai_01 game_ai
```

コンテナの開始/停止
```
# コンテナの停止
$ docker stop game_ai_01

# コンテナの開始
$ docker start game_ai_01
```

Dockerで実行を行う
```
# python実行
$ docker exec -ti game_ai_01 python <filename.py>

# bashの実行
$ docker exec -ti game_ai_01 bash
```

モジュールを追加する際には、requirements.txtに記載してください
```
# ファイルを編集
$ vim requirements.txt

# コンテナを再ビルド（Dockerfileでpipを実行しています）
# 必要に応じて、イメージとコンテナを削除
$ docker rm -f game_ai_01
$ docker build ./ -t game_ai
$ docker run -v $PWD:/work -itd --name game_ai_01 game_ai
```

## Install Test

パッケージが正しくインストールされているかのテスト
```
$ docker exec -ti game_ai_01 bash
$ cd test
$ python installtest.py
```