import os
import random
import sys
import time
import pygame as pg

WIDTH, HEIGHT = 1100, 650  
DELTA = {
    pg.K_UP: (0, -5),
    pg.K_DOWN: (0, +5),
    pg.K_LEFT: (-5, 0),
    pg.K_RIGHT: (+5, 0),
}  # キー入力に対する移動量の辞書

os.chdir(os.path.dirname(os.path.abspath(__file__))) 

def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    """
    引数で与えられたRectが画面の中か外化を判定する
    引数: こうかとんRect or 爆弾Rect
    戻り値: 真理値タプル（横、縦）/画面内:True、画面外:False   
    """
    yoko, tate = True, True
    if obj_rct.left < 0 or WIDTH < obj_rct.right:
        yoko = False
    if obj_rct.top < 0 or HEIGHT < obj_rct.bottom:
        tate = False
    return yoko, tate


def init_bb_imgs() -> tuple[list[pg.Surface], list[int]]:
    """
    サイズの異なる爆弾Surfaceを要素としたリストと加速度リストを返す
    
    Returns:
        bb_imgs (list[pg.Surface]): 爆弾サイズに応じたSurfaceのリスト
        bb_accs (list[int]): 爆弾の加速度のリスト
    """
    bb_imgs = []
    bb_accs = [a for a in range(1, 11)]  # 加速度リスト（1〜10）
    
    # サイズが異なる爆弾Surfaceのリストを作成
    for r in range(1, 11):
        bb_img = pg.Surface((20 * r, 20 * r), pg.SRCALPHA)  # 爆弾用のSurface
        pg.draw.circle(bb_img, (255, 0, 0), (10 * r, 10 * r), 10 * r)  # 爆弾円を描画
        bb_imgs.append(bb_img)
    return bb_imgs, bb_accs  # 爆弾画像リスト（bb_imgs）と加速度リスト（bb_accs）をタプルで返す


def gameover(screen: pg.Surface) -> None:
    """
    ゲームオーバー画面を表示する
    画面をブラックアウト（半透明）
    泣いているこうかとん画像と「Game Over」の文字列を表示
    5秒間待機
    
    Args:
        screen (pg.Surface): ゲーム画面のSurface
    """
    overlay = pg.Surface((WIDTH, HEIGHT))
    overlay.fill((0, 0, 0))
    overlay.set_alpha(150)
    screen.blit(overlay, (0, 0))  # 半透明のオーバーレイを描画
    cry_kk_img = pg.transform.rotozoom(pg.image.load("fig/8.png"), 0, 1.5)  # 泣いているこうかとん画像
    font = pg.font.Font(None, 80)
    text = font.render("Game Over", True, (255, 255, 255))  # 「Game Over」の文字を描画
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    offset_x = 25
    screen.blit(text, text_rect)  # テキストを描画
    screen.blit(cry_kk_img, (text_rect.left - offset_x - cry_kk_img.get_width(),
                             text_rect.centery - cry_kk_img.get_height() // 2))  # 泣いているこうかとん（左）
    screen.blit(cry_kk_img, (text_rect.right + offset_x,
                             text_rect.centery - cry_kk_img.get_height() // 2))  # 泣いているこうかとん（右）
    pg.display.update()  # 画面を更新
    time.sleep(5)  # 5秒待機


def main() -> None:
    """
    ゲームのメインループを実行する。
    """
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))  # 画面サイズ設定
    bg_img = pg.image.load("fig/pg_bg.jpg")  # 背景画像のロード
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)  # こうかとん画像のロード
    kk_rct = kk_img.get_rect()  # こうかとんのRect取得
    kk_rct.center = 300, 200  # 初期位置設定
    
    # 爆弾の初期化
    bb_imgs, bb_accs = init_bb_imgs()  # サイズと加速度のリストを取得
    bb_rct = bb_imgs[0].get_rect()  # 爆弾の最初のRectを取得
    bb_rct.center = random.randint(0, WIDTH), random.randint(0, HEIGHT)  # 爆弾の初期位置設定
    vx, vy = +5, +5  # 爆弾の初期速度
    
    clock = pg.time.Clock()  # クロックオブジェクトの生成
    tmr = 0  # タイマーの初期化

    while True:  # ゲームループ
        for event in pg.event.get():  # イベント処理
            if event.type == pg.QUIT:   # ウィンドウの閉じるボタンが押されたら
                return  # ゲーム終了

        screen.blit(bg_img, [0, 0])  # 背景を描画

        # こうかとんと爆弾が衝突した場合
        if kk_rct.colliderect(bb_rct):  
            gameover(screen)  # ゲームオーバー画面を表示
            return  # ゲーム終了
        
        # こうかとんの移動処理
        key_lst = pg.key.get_pressed()  # キーの状態を取得
        sum_mv = [0, 0]  # こうかとんの移動量の初期化
        for key, tpl in DELTA.items():  # DELTAの辞書に基づいて移動量を加算
            if key_lst[key]:
                sum_mv[0] += tpl[0]
                sum_mv[1] += tpl[1]
        kk_rct.move_ip(sum_mv)  # こうかとんの位置を移動
        if check_bound(kk_rct) != (True, True):  # 画面外に出た場合
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1])  # 移動量を元に戻す
        screen.blit(kk_img, kk_rct)  # こうかとんの画像を描画

        # 時間経過による爆弾の拡大と加速
        idx = min(tmr // 500, 9)  # 時間に応じて爆弾のサイズを更新
        avx = vx * bb_accs[idx]  # 加速された横方向速度
        avy = vy * bb_accs[idx]  # 加速された縦方向速度
        bb_img = bb_imgs[idx]  # 現在の爆弾の画像を取得
        bb_rct = bb_img.get_rect(center=bb_rct.center)  # 爆弾の位置を更新
        bb_rct.move_ip(avx, avy)  # 爆弾の移動
        yoko, tate = check_bound(bb_rct)  # 画面内かどうか判定
        if not yoko:  # 横方向に画面外に出たら
            vx *= -1  # 逆方向に移動
        if not tate:  # 縦方向に画面外に出たら
            vy *= -1  # 逆方向に移動
        screen.blit(bb_img, bb_rct)  # 爆弾の画像を描画

        tmr += 1  # タイマーを更新
        pg.display.update()  # 画面を更新
        clock.tick(50)  # フレームレートを設定

if __name__ == "__main__":  # このファイルが直接実行されたら
    pg.init()    # Pygameの初期化
    main()     # メイン関数の実行
    pg.quit()  # Pygameの終了
    sys.exit()  # システム終了
