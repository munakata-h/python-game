import pygame
import sys
import random
import os

# --- 1. 設定 ---
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60
LIMIT_TIME = 120
BLACK, WHITE, YELLOW, BLUE, GOLD, RED = (0,0,0), (255,255,255), (255,255,0), (0,0,255), (255,215,0), (255,50,50)
PLAYER_SPEED = 4
ENEMY_SPEED = 2.2

# 迷路レイアウト（1:壁, 0:エサ, 2:スタート）
MAZE = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,1],
    [1,0,1,1,0,1,0,1,1,1,1,1,1,0,1,0,1,1,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,1,1,0,1,1,1,0,1,1,0,1,1,1,0,1,1,0,1],
    [0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0], # ワープ通路
    [1,0,1,1,0,1,1,1,0,1,1,0,1,1,1,0,1,1,0,1],
    [1,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,1],
    [1,0,1,1,0,1,0,1,1,1,1,1,1,0,1,0,1,1,0,1],
    [1,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
]

TILE_SIZE = 40

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        def load_p(name): return pygame.transform.scale(pygame.image.load(name).convert_alpha(), (34, 34))
        self.stand_r = load_p("player_1.png")
        self.walk_r = [load_p("player_2.png"), load_p("player_3.png")]
        self.walk_l = [pygame.transform.flip(f, True, False) for f in self.walk_r]
        self.walk_u = [pygame.transform.rotate(f, 90) for f in self.walk_r]
        self.walk_d = [pygame.transform.rotate(f, -90) for f in self.walk_r]
        self.image = self.stand_r
        self.rect = self.image.get_rect(center=(x, y))
        self.hitbox = self.rect.inflate(-18, -18) 
        self.direction = pygame.Vector2(0, 0)
        self.anime_count = 0

    def update(self, walls):
        keys = pygame.key.get_pressed()
        new_dir = pygame.Vector2(0, 0)
        if keys[pygame.K_LEFT]: new_dir.x = -1
        elif keys[pygame.K_RIGHT]: new_dir.x = 1
        elif keys[pygame.K_UP]: new_dir.y = -1
        elif keys[pygame.K_DOWN]: new_dir.y = 1

        if new_dir.length() > 0:
            old_x = self.rect.x
            self.rect.x += new_dir.x * PLAYER_SPEED
            self.hitbox.center = self.rect.center
            if any(self.hitbox.colliderect(w.rect) for w in walls):
                self.rect.x = old_x
            else:
                if new_dir.x != 0: self.direction = pygame.Vector2(new_dir.x, 0)

            old_y = self.rect.y
            self.rect.y += new_dir.y * PLAYER_SPEED
            self.hitbox.center = self.rect.center
            if any(self.hitbox.colliderect(w.rect) for w in walls):
                self.rect.y = old_y
            else:
                if new_dir.y != 0: self.direction = pygame.Vector2(0, new_dir.y)

        self.hitbox.center = self.rect.center
        if self.rect.right < 0: self.rect.left = SCREEN_WIDTH
        elif self.rect.left > SCREEN_WIDTH: self.rect.right = 0

        if self.direction.length() > 0:
            self.anime_count += 1
            idx = (self.anime_count // 8) % 2
            if self.direction.x > 0: self.image = self.walk_r[idx]
            elif self.direction.x < 0: self.image = self.walk_l[idx]
            elif self.direction.y < 0: self.image = self.walk_u[idx]
            elif self.direction.y > 0: self.image = self.walk_d[idx]

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(RED)
        pygame.draw.rect(self.image, WHITE, (5, 5, 5, 5))
        pygame.draw.rect(self.image, WHITE, (20, 5, 5, 5))
        self.rect = self.image.get_rect(center=(x, y))
        self.direction = pygame.Vector2(0, 0)
        self.change_dir_timer = 0

    def update(self, walls, player_pos):
        target_vec = pygame.Vector2(player_pos) - pygame.Vector2(self.rect.center)
        if self.change_dir_timer <= 0:
            if abs(target_vec.x) > abs(target_vec.y):
                self.direction = pygame.Vector2(1 if target_vec.x > 0 else -1, 0)
            else:
                self.direction = pygame.Vector2(0, 1 if target_vec.y > 0 else -1)
            self.change_dir_timer = 40 
        
        self.change_dir_timer -= 1
        self.rect.x += self.direction.x * ENEMY_SPEED
        self.rect.y += self.direction.y * ENEMY_SPEED
        
        if self.rect.right < 0: self.rect.left = SCREEN_WIDTH
        elif self.rect.left > SCREEN_WIDTH: self.rect.right = 0

        hit = False
        for wall in walls:
            if self.rect.colliderect(wall.rect):
                hit = True; break
        if hit:
            self.rect.x -= self.direction.x * ENEMY_SPEED
            self.rect.y -= self.direction.y * ENEMY_SPEED
            self.direction = random.choice([pygame.Vector2(1,0), pygame.Vector2(-1,0), pygame.Vector2(0,1), pygame.Vector2(0,-1)])
            self.change_dir_timer = 20

class Food(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((8, 8), pygame.SRCALPHA)
        pygame.draw.circle(self.image, WHITE, (4, 4), 4)
        self.rect = self.image.get_rect(center=(x, y))

class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(BLUE)
        pygame.draw.rect(self.image, BLACK, (2,2,36,36), 1)
        self.rect = self.image.get_rect(topleft=(x, y))

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Pac-Player Final Ver")
    clock = pygame.time.Clock()
    font_main = pygame.font.SysFont(None, 80)
    font_score = pygame.font.SysFont(None, 40)

    # --- score.txt から初期スコアを読み込み ---
    initial_score = 100
    if os.path.exists("score.txt"):
        try:
            with open("score.txt", "r") as f:
                content = f.read().strip()
                if content:
                    initial_score = int(content)
        except ValueError:
            pass

    all_sprites, walls, foods, enemies = pygame.sprite.Group(), pygame.sprite.Group(), pygame.sprite.Group(), pygame.sprite.Group()

    for r_idx, row in enumerate(MAZE):
        for c_idx, tile in enumerate(row):
            x, y = c_idx * TILE_SIZE, r_idx * TILE_SIZE
            if tile == 1:
                w = Wall(x, y); walls.add(w); all_sprites.add(w)
            elif tile == 0:
                f = Food(x + TILE_SIZE//2, y + TILE_SIZE//2); foods.add(f); all_sprites.add(f)
            elif tile == 2:
                player = Player(x + TILE_SIZE//2, y + TILE_SIZE//2)

    # 敵を左右の端に配置
    e1 = Enemy(20, 220)
    e2 = Enemy(780, 220)
    enemies.add(e1, e2); all_sprites.add(e1, e2)

    all_sprites.add(player)
    
    score = initial_score
    start_ticks = pygame.time.get_ticks()
    last_score_tick = start_ticks
    running, game_result = True, None

    while running:
        current_tick = pygame.time.get_ticks()
        # タイムリミットの計算（クリア・オーバー後も値は保持されるが見た目用）
        time_left = max(0, LIMIT_TIME - (current_tick - start_ticks) // 1000)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            # ゲーム終了時に何かキーを押したら終了
            if event.type == pygame.KEYDOWN and game_result: running = False

        if not game_result:
            # --- ゲーム中の更新処理（終了後はここが動かないのでスコアが止まる） ---
            player.update(walls)
            enemies.update(walls, player.rect.center)
            
            # スコア減少処理
            if current_tick - last_score_tick >= 1000:
                score = max(0, score - 1)
                last_score_tick = current_tick

            # ドット獲得
            if pygame.sprite.spritecollide(player, foods, True):
                score += 1
            
            # 衝突判定
            for e in enemies:
                if player.hitbox.colliderect(e.rect):
                    game_result = "OVER"

            if len(foods) == 0: game_result = "CLEAR"
            if time_left <= 0: game_result = "TIME_UP"

        screen.fill(BLACK)
        all_sprites.draw(screen)

        s_text = font_score.render(f"SCORE: {score}  TIME: {int(time_left)}s", True, GOLD)
        screen.blit(s_text, (20, SCREEN_HEIGHT - 35))

        if game_result:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)); overlay.set_alpha(180); overlay.fill(BLACK); screen.blit(overlay, (0, 0))
            msg = "GAME CLEAR!" if game_result == "CLEAR" else "GAME OVER"
            t1 = font_main.render(msg, True, GOLD if game_result == "CLEAR" else RED)
            t2 = font_score.render(f"FINAL SCORE: {score}", True, WHITE)
            screen.blit(t1, t1.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 40)))
            screen.blit(t2, t2.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 40)))

        pygame.display.flip()
        clock.tick(FPS)

    # --- ループ終了後、スコアを score.txt に上書き保存 ---
    with open("score.txt", "w") as f:
        f.write(str(score))

    pygame.quit()

if __name__ == "__main__": main()