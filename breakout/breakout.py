#! /usr/bin/env python
#coding: utf-8
import pygame
from pygame.locals import *
import numpy as np
import os
import random
import sys
import math


np.set_printoptions(threshold=np.inf)
START, PLAY, GAMEOVER = (0, 1, 2) # ゲーム状態
SCR_RECT = Rect(0, 0, 372, 384)
SC_NUM = 0

class BreakOut:
    def __init__(self):
        pygame.init()
        screen = pygame.display.set_mode(SCR_RECT.size)
        pygame.display.set_caption(u"BREAK OUT")
        # 素材のロード
        self.load_images()

        # ゲームオブジェクトを初期化
        self.init_game()
        # メインループ開始
        clock = pygame.time.Clock()
        # スクリーンショットの間隔制御のためのClock開始
        pygame.time.set_timer(pygame.USEREVENT, 30)
        while True:
                clock.tick(60)
                self.update()
                self.draw(screen)
                pygame.display.update()
                self.key_handler()
                self.get_ball_pos()

    def init_game(self):
        """ ゲームオブジェクトを初期化 """
        # ゲーム状態
        self.game_state = START
        # スプライトグループを作成して登録
        self.all = pygame.sprite.RenderUpdates()
        self.bricks = pygame.sprite.Group()  # 衝突判定用グループ
        # デフォルトスプライトグループを登録
        Paddle.containers = self.all
        Ball.containers = self.all
        Brick.containers = self.all, self.bricks

        # パドルを作成
        self.paddle = Paddle()

        # ブロックを作成
        # 自動的にbricksグループに追加される
        for x in range(1, 11):
            for y in range(1, 6):
                Brick(x, y)
        # スコアボードを作成
        self.score_board = ScoreBoard()
        # ボールを作成
        self.ball = Ball(self.paddle, self.bricks, self.score_board)

    def update(self):
        """ ゲーム状態の更新 """
        if self.game_state == PLAY:
            self.all.update()
    
    def draw(self, screen):
        """ 描画 """
        screen.fill((0, 0, 0))
        if self.game_state == START:
            # タイトルを描画
            title_font = pygame.font.SysFont(None, 30)
            title = title_font.render("BREAKOUT GAME", False, (255, 0, 0))
            screen.blit(title, ((SCR_RECT.width-title.get_width())/2, 100))
            # PUSH STARTを描画
            push_font = pygame.font.SysFont(None, 20)
            push_space = push_font.render("PUSH SPACE KEY", False, (255,255,255))
            screen.blit(push_space, ((SCR_RECT.width-push_space.get_width())/2, 300))
        elif self.game_state == PLAY:  # ゲームプレイ画面
            self.all.draw(screen)
        elif self.game_state == GAMEOVER:  # ゲームオーバー画面
            # GAME OVERを描画
            gameover_font = pygame.font.SysFont(None, 40)
            gameover = gameover_font.render("GAME OVER", False, (255,0,0))
            screen.blit(gameover, ((SCR_RECT.width-gameover.get_width())/2, 100))
            # PUSH STARTを描画
            push_font = pygame.font.SysFont(None, 20)
            push_space = push_font.render("PUSH SPACE KEY", False, (255,255,255))
            screen.blit(push_space, ((SCR_RECT.width-push_space.get_width())/2, 300))

    def key_handler(self):
        """キーハンドラー"""
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN and event.key == K_SPACE:
                if self.game_state == START:  # スタート画面でスペースを押したとき
                    self.game_state = PLAY
                elif self.game_state == GAMEOVER:  # ゲームオーバー画面でスペースを押したとき
                    self.init_game()  # ゲームを初期化して再開
                    self.game_state = PLAY
            # 一定時間毎に画面情報を取得
            if event.type == USEREVENT:
                image = self.get_image()

    def load_images(self):
        Paddle.image = load_image('paddle.png')
        Ball.image = load_image('ball.png')
        Brick.image = load_image('brick.png')

    def get_ball_pos(self):
        # ボールの位置を取得して下に落ちていたらgame_stateをGAMEOVERにする
        if self.ball.rect.top > SCR_RECT.bottom:
            self.game_state = GAMEOVER

    def get_image(self):

        # ディスプレイの情報を3次元で取得
        image = pygame.surfarray.array3d(pygame.display.get_surface())
        # 中間値法によるグレースケール
        image = np.max(image, axis = 2)/2 +np.min(image, axis = 2)/2
        # 実際のゲーム画面と同様にパドルが下、ブロックが上に配置するように返す。
        return image.T


class Paddle(pygame.sprite.Sprite):
    """ボールを打つパドル"""
    def __init__(self):
        # imageとcontainersはmain()でセットされる
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.rect = self.image.get_rect()
        self.rect.bottom = SCR_RECT.bottom  # パドルは画面の一番下
        self.rect.centerx = 185
    def update(self):
        vx = 5 # キーを押した時の移動距離
        # 押されているキーをチェック
        pressed_keys = pygame.key.get_pressed()
        # 押されているキーに応じて画像を移動
        if pressed_keys[K_LEFT]:
            self.rect.move_ip(-vx, 0)
        if pressed_keys[K_RIGHT]:
            self.rect.move_ip(vx, 0)

        self.rect.clamp_ip(SCR_RECT)  # SCR_RECT内でしか移動できなくなる

class Ball(pygame.sprite.Sprite):
    """ボール"""
    speed = 5
    angle_left = 135
    angle_right = 45
    def __init__(self, paddle, bricks, score_board):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.rect = self.image.get_rect()
        self.dx = self.dy = 0  # ボールの速度
        self.paddle = paddle  # パドルへの参照
        self.bricks = bricks  # ブロックグループへの参照
        self.update = self.start
        self.score_board = score_board
        self.hit = 0  # 連続でブロックを壊した回数
    def start(self):
        """ボールの位置を初期化"""
        # パドルの中央に配置
        self.rect.centerx = self.paddle.rect.centerx
        self.rect.bottom = self.paddle.rect.top
        # スペースキーで開始
        if pygame.key.get_pressed()[K_SPACE] == 1:
            self.dx = 0
            self.dy = -self.speed
            # update()をmove()に置き換え
            self.update = self.move
    def move(self):
        """ボールの移動"""
        self.rect.centerx += self.dx
        self.rect.centery += self.dy
        # 壁との反射
        if self.rect.left < SCR_RECT.left:  # 左側
            self.rect.left = SCR_RECT.left
            self.dx = -self.dx  # 速度を反転
        if self.rect.right > SCR_RECT.right:  # 右側
            self.rect.right = SCR_RECT.right
            self.dx = -self.dx
        if self.rect.top < SCR_RECT.top:  # 上側
            self.rect.top = SCR_RECT.top
            self.dy = -self.dy
        # パドルとの反射
        if self.rect.colliderect(self.paddle.rect) and self.dy > 0:
            self.hit = 0  # 連続ヒットを0に戻す
            # パドルの左端に当たったとき135度方向、右端で45度方向とし、
            # その間は線形補間で反射方向を計算
            x1 = self.paddle.rect.left - self.rect.width  # ボールが当たる左端
            y1 = self.angle_left  # 左端での反射方向（135度）
            x2 = self.paddle.rect.right  # ボールが当たる右端
            y2 = self.angle_right  # 右端での反射方向（45度）
            m = float(y2-y1) / (x2-x1)  # 直線の傾き
            x = self.rect.left  # ボールが当たった位置
            y = m * (x - x1) + y1
            angle = math.radians(y)
            self.dx = self.speed * math.cos(angle)
            self.dy = -self.speed * math.sin(angle)
        # ボールを落とした場合
        if self.rect.top > SCR_RECT.bottom:
            self.update = self.start  # ボールを初期状態に
            # ボールを落としたら-30点
            self.hit = 0
            self.score_board.init_score()
            BreakOut.game_state = GAMEOVER
        # ブロックを壊す
        # ボールと衝突したブロックリストを取得
        bricks_collided = pygame.sprite.spritecollide(self, self.bricks, True)
        if bricks_collided:  # 衝突ブロックがある場合
            oldrect = self.rect
            for brick in bricks_collided:  # 各衝突ブロックに対して
                # ボールが左から衝突
                if oldrect.left < brick.rect.left < oldrect.right < brick.rect.right:
                    self.rect.right = brick.rect.left
                    self.dx = -self.dx
                # ボールが右から衝突
                if brick.rect.left < oldrect.left < brick.rect.right < oldrect.right:
                    self.rect.left = brick.rect.right
                    self.dx = -self.dx
                # ボールが上から衝突
                if oldrect.top < brick.rect.top < oldrect.bottom < brick.rect.bottom:
                    self.rect.bottom = brick.rect.top
                    self.dy = -self.dy
                # ボールが下から衝突
                if brick.rect.top < oldrect.top < brick.rect.bottom < oldrect.bottom:
                    self.rect.top = brick.rect.bottom
                    self.dy = -self.dy
                # 点数を追加
                self.hit += 1
                self.score_board.add_score(self.hit * 10)
    
    def ret_ball_pos(self):
        return self.rect

class Brick(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.rect = self.image.get_rect()
        # ブロックの位置を更新
        self.rect.left = SCR_RECT.left + x * self.rect.width
        self.rect.top = SCR_RECT.top + y * self.rect.height

class ScoreBoard():
    """スコアボード"""
    def __init__(self):
        self.sysfont = pygame.font.SysFont(None, 80)
        self.score = 0
    def draw(self, screen):
        score_img = self.sysfont.render(str(self.score), True, (255,255,0))
        x = (SCR_RECT.size[0] - score_img.get_width()) / 2
        y = (SCR_RECT.size[1] - score_img.get_height()) / 2
        screen.blit(score_img, (x, y))
    def init_score(self):
        self.score = 0
    
    def add_score(self, x):
        self.score += x


def load_image(filename, colorkey=None):
    """画像をロードして画像と矩形を返す"""
    filename = os.path.join("breakout/data", filename)
    try:
        image = pygame.image.load(filename)
    except pygame.error as message:
        print("Cannot load image:", filename)
        raise SystemExit(message)
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image

if __name__ == '__main__':
    BreakOut()
