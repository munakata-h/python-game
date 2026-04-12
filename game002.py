import pygame
import sys
import os
import random

# 1. 初期設定
pygame.init()
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("図形描画版：飛行機 vs お化け (Advanced)")

# 色の定義
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
PURPLE = (200, 100, 255)
EYE_COLOR = (50, 50, 50)

# --- スコア読み込み ---
def load_score():
    if os.path.exists("score.txt"):
        with open("score.txt", "r") as f:
            try:
                return int(f.read().strip())
            except:
                return 0
    return 0

# --- 【関数】飛行機を描く ---
def draw_player(surface, x, y):
    pygame.draw.polygon(surface, GREEN, [(x + 25, y), (x, y + 40), (x + 50, y + 40)])
    pygame.draw.rect(surface, GREEN, (x + 5, y + 25, 40, 8))
    pygame.draw.polygon(surface, GREEN, [(x + 25, y + 35), (x + 15, y + 45), (x + 35, y + 45)])

# --- 【関数】お化けを描く ---
def draw_enemy(surface, x, y):
    pygame.draw.ellipse(surface, PURPLE, (x, y, 40, 45))
    for i in range(3):
        pygame.draw.circle(surface, PURPLE, (x + 10 + (i * 10), y + 40), 8)
    pygame.draw.circle(surface, WHITE, (x + 12, y + 15), 5)
    pygame.draw.circle(surface, WHITE, (x + 28, y + 15), 5)
    pygame.draw.circle(surface, EYE_COLOR, (x + 12, y + 15), 2)
    pygame.draw.circle(surface, EYE_COLOR, (x + 28, y + 15), 2)

# --- 変数設定 ---
score = load_score()
player_x = 375
player_y = 530
player_speed = 6
player_rect = pygame.Rect(player_x, player_y, 50, 50)

bullets = []        # プレイヤーの弾
enemy_bullets = []  # 敵の弾
enemies = []
for i in range(8):
    for j in range(3):
        enemies.append(pygame.Rect(i * 80 + 100, j * 60 + 50, 40, 40))

enemy_dx = 2
enemy_dy = 20
font_score = pygame.font.SysFont(None, 40)

# --- メインループ ---
clock = pygame.time.Clock()
while True:
    screen.fill(BLACK)
    player_rect.x = player_x # 当たり判定用位置更新

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                bullets.append(pygame.Rect(player_x + 22, player_y, 5, 15))

    # 自機の移動
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player_x > 0:
        player_x -= player_speed
    if keys[pygame.K_RIGHT] and player_x < 750:
        player_x += player_speed

    # 敵の移動と攻撃
    turn = False
    for e in enemies:
        e.x += enemy_dx
        if e.x <= 0 or e.x >= 760:
            turn = True
        
        # 攻撃ロジック：低い確率でお化けが玉を撃つ
        if random.random() < 0.005: # 約0.5%の確率
            enemy_bullets.append(pygame.Rect(e.x + 18, e.y + 40, 5, 10))

    if turn:
        enemy_dx *= -1
        for e in enemies:
            e.y += enemy_dy

    # プレイヤーの弾の移動と描画
    for b in bullets[:]:
        b.y -= 8
        pygame.draw.rect(screen, RED, b)
        if b.y < 0:
            bullets.remove(b)

    # 敵の弾の移動と描画
    for eb in enemy_bullets[:]:
        eb.y += 5
        pygame.draw.rect(screen, YELLOW, eb)
        # プレイヤーとの当たり判定
        if player_rect.colliderect(eb):
            score = max(0, score - 50) # 当たると50点マイナス
            enemy_bullets.remove(eb)
        elif eb.y > SCREEN_HEIGHT:
            enemy_bullets.remove(eb)

    # 敵の描画と当たり判定
    for e in enemies[:]:
        draw_enemy(screen, e.x, e.y)
        for b in bullets[:]:
            if e.colliderect(b):
                enemies.remove(e)
                bullets.remove(b)
                score += 2 # 倒すと2点プラス
                break

    # 自機の描画
    draw_player(screen, player_x, player_y)

    # スコア表示（上部中央）
    score_text = font_score.render(f"SCORE: {score}", True, WHITE)
    text_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, 30))
    screen.blit(score_text, text_rect)

    # クリア・ゲームオーバー判定
    if not enemies:
        print(f"最終スコア: {score}")
        break
    if any(e.y > 520 for e in enemies):
        print("残念！お化けに攻め込まれました...")
        break

    pygame.display.flip()
    clock.tick(60)

# スコアを最終保存して終了
with open("score.txt", "w") as f:
    f.write(str(score))
pygame.quit()