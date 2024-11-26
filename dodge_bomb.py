import os
import random
import sys
import time
import pygame as pg

# 定数定義
WIDTH, HEIGHT = 1100, 650
DELTA: dict[int, tuple[int, int]] = {
    pg.K_UP: (0, -5),
    pg.K_DOWN: (0, +5),
    pg.K_LEFT: (-5, 0),
    pg.K_RIGHT: (+5, 0),
}

# 現在のディレクトリを変更
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def check_bound(rct: pg.Rect) -> tuple[bool, bool]:
    """
    引数で与えられたRectが画面の中か外かを判定する。

    Args:
        rct (pg.Rect): 判定対象のRect（こうかとんまたは爆弾）。

    Returns:
        tuple[bool, bool]: 真理値タプル（横方向, 縦方向）。
                           画面内ならTrue、画面外ならFalse。
    """
    yoko, tate = True, True
    if rct.left < 0 or WIDTH < rct.right:
        yoko = False
    if rct.top < 0 or HEIGHT < rct.bottom:
        tate = False
    return yoko, tate


def game_over(screen: pg.Surface) -> None:
    """
    ゲームオーバー画面を表示し、5秒後に終了する。

    Args:
        screen (pg.Surface): ゲーム画面のSurface。
    """
    font = pg.font.Font(None, 80)
    text = font.render("Game Over", True, (255, 255, 255))
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))

    # 泣いているこうかとんの画像をロード
    cry_kk_img = pg.transform.rotozoom(pg.image.load("fig/8.png"), 0, 1.5)

    # ブラックアウト画面を描画
    screen.fill((0, 0, 0))
    screen.blit(text, text_rect)
    offset_x = 25
    screen.blit(cry_kk_img,
                 (text_rect.left - offset_x - cry_kk_img.get_width(),
                   text_rect.centery - cry_kk_img.get_height() // 2))
    screen.blit(cry_kk_img,
                 (text_rect.right + offset_x,
                   text_rect.centery - cry_kk_img.get_height() // 2))
    pg.display.update()

    # 5秒間表示
    time.sleep(5)


def main() -> None:
    """
    ゲームのメインループを実行する。
    """
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200

    # 爆弾の初期設定
    bb_img = pg.Surface((20, 20))  # 爆弾用の空Surface
    pg.draw.circle(bb_img, (255, 0, 0), (10, 10), 10)  # 爆弾円を描く
    bb_img.set_colorkey((0, 0, 0))  # 四隅の黒を透過させる
    bb_rct = bb_img.get_rect()  # 爆弾Rectの抽出
    bb_rct.centerx = random.randint(0, WIDTH)
    bb_rct.centery = random.randint(0, HEIGHT)
    vx, vy = +5, +5  # 爆弾速度ベクトル

    clock = pg.time.Clock()
    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return

        # 衝突判定
        if kk_rct.colliderect(bb_rct):
            game_over(screen)
            return  # ゲームオーバー後に終了

        screen.blit(bg_img, [0, 0])

        # こうかとんの移動
        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        for key, tpl in DELTA.items():
            if key_lst[key]:
                sum_mv[0] += tpl[0]
                sum_mv[1] += tpl[1]
        kk_rct.move_ip(sum_mv)

        # こうかとんが画面外なら元の場所に戻す
        if check_bound(kk_rct) != (True, True):
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1])
        screen.blit(kk_img, kk_rct)

        # 爆弾の移動
        bb_rct.move_ip(vx, vy)
        yoko, tate = check_bound(bb_rct)
        if not yoko:  # 横にはみ出てる
            vx *= -1
        if not tate:  # 縦にはみ出てる
            vy *= -1
        screen.blit(bb_img, bb_rct)

        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
