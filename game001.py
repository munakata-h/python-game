import pygame
import sys
import os

# --- 1. 画像ファイルの自動生成 (変更なし) ---
def create_dummy_assets():
    pygame.init()
    def draw_base_player(surface):
        pygame.draw.ellipse(surface, (255, 200, 0), (5, 5, 20, 20)) 
        pygame.draw.circle(surface, (0, 0, 0), (10, 12), 2)
        pygame.draw.circle(surface, (0, 0, 0), (20, 12), 2)
        pygame.draw.rect(surface, (0, 100, 255), (5, 20, 20, 15))
    s1 = pygame.Surface((30, 40), pygame.SRCALPHA); draw_base_player(s1)
    pygame.draw.rect(s1, (0, 0, 0), (8, 35, 6, 5)); pygame.draw.rect(s1, (0, 0, 0), (16, 35, 6, 5))
    pygame.image.save(s1, "player_stand.png")
    s2 = pygame.Surface((30, 40), pygame.SRCALPHA); draw_base_player(s2)
    pygame.draw.rect(s2, (0, 0, 0), (12, 35, 6, 5)); pygame.image.save(s2, "player_walk1.png")
    s3 = pygame.Surface((30, 40), pygame.SRCALPHA); draw_base_player(s3)
    pygame.draw.rect(s3, (5, 35, 6, 5), (5, 35, 6, 5)); pygame.image.save(s3, "player_walk2.png")

create_dummy_assets()

# --- 2. 設定 ---
SCREEN_WIDTH, SCREEN_HEIGHT = 1024, 768
FPS = 60
LIMIT_TIME = 60 
SKY_BLUE, BROWN, GOLD, WHITE, RED, NAVY, BLACK = (135, 206, 235), (139, 69, 19), (255, 215, 0), (255, 255, 255), (255, 50, 50), (0, 0, 128), (0, 0, 0)
GRAVITY, PLAYER_SPEED, JUMP_POWER = 0.8, 6, -14

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        def load_p(name): return pygame.transform.scale(pygame.image.load(name).convert_alpha(), (45, 60))
        self.stand_r = load_p("player_stand.png")
        self.stand_l = pygame.transform.flip(self.stand_r, True, False)
        self.walk_r = [load_p("player_walk1.png"), load_p("player_walk2.png")]
        self.walk_l = [pygame.transform.flip(f, True, False) for f in self.walk_r]
        self.image = self.stand_r
        self.rect = self.image.get_rect(topleft=(50, 620))
        self.vel_y = 0
        self.on_ground = False
        self.facing_right = True
        self.anime_count = 0
        self.last_platform_y = 680 # 直前の足場の高さ

    def update(self, platforms):
        keys = pygame.key.get_pressed()
        moving = False
        if keys[pygame.K_LEFT]: self.rect.x -= PLAYER_SPEED; self.facing_right = False; moving = True
        if keys[pygame.K_RIGHT]: self.rect.x += PLAYER_SPEED; self.facing_right = True; moving = True
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP]) and self.on_ground:
            self.vel_y = JUMP_POWER; self.on_ground = False
        
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y
        self.on_ground = False
        
        # 点数計算用の判定
        hits = pygame.sprite.spritecollide(self, platforms, False)
        score_change = 0
        for p in hits:
            if self.vel_y > 0:
                self.rect.bottom = p.rect.top
                # 着地した足場の高さが変わっていたら点数増減
                if p.rect.top < self.last_platform_y: score_change = 10
                elif p.rect.top > self.last_platform_y: score_change = -30
                self.last_platform_y = p.rect.top
                self.vel_y = 0; self.on_ground = True
            elif self.vel_y < 0:
                self.rect.top = p.rect.bottom; self.vel_y = 0

        self.anime_count += 1
        if not self.on_ground: self.image = self.walk_r[0] if self.facing_right else self.walk_l[0]
        elif moving:
            idx = (self.anime_count // 8) % 2
            self.image = self.walk_r[idx] if self.facing_right else self.walk_l[idx]
        else: self.image = self.stand_r if self.facing_right else self.stand_l
        
        return score_change

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h):
        super().__init__()
        self.image = pygame.Surface((w, h)); self.image.fill(BROWN)
        self.rect = self.image.get_rect(topleft=(x, y))

class Goal(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((60, 80)); self.image.fill(GOLD)
        self.rect = self.image.get_rect(topleft=(x, y))

def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Score Attack Adventure")
    clock = pygame.time.Clock()
    
    # フォント設定
    sys_fonts = pygame.font.get_fonts()
    jp_font = next((f for f in ["msuigothic", "msgothic", "notosanscjkjp"] if f in sys_fonts), None)
    font_main = pygame.font.SysFont(jp_font, 80)
    font_info = pygame.font.SysFont(jp_font, 32)
    font_score = pygame.font.SysFont(None, 60)

    all_sprites, platforms, goals = pygame.sprite.Group(), pygame.sprite.Group(), pygame.sprite.Group()
    level_data = [(0, 680, 500, 40), (800, 650, 300, 150), (450, 580, 200, 10), (750, 480, 150, 20), (550, 380, 120, 10), (350, 280, 100, 20), (850, 280, 100, 20), (250, 180, 80, 10), (700, 180, 80, 10), (50, 100, 150, 30), (850, 100, 150, 30)]
    for d in level_data:
        p = Platform(*d); platforms.add(p); all_sprites.add(p)
    g1, g2 = Goal(70, 20), Goal(860, 20)
    goals.add(g1, g2); all_sprites.add(g1, g2)
    player = Player(); all_sprites.add(player)

    score = 100
    start_ticks = pygame.time.get_ticks()
    running, game_result = True, None

    while running:
        time_left = max(0, LIMIT_TIME - (pygame.time.get_ticks() - start_ticks) / 1000)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.KEYDOWN and game_result: running = False

        if not game_result:
            score_diff = player.update(platforms)
            score = max(0, score + score_diff)
            if pygame.sprite.collide_rect(player, g1) or pygame.sprite.collide_rect(player, g2):
                game_result = "CLEAR"
            if time_left <= 0: game_result = "TIME_UP"

        screen.fill(SKY_BLUE)
        all_sprites.draw(screen)

        # スコア表示
        s_text = font_score.render(f"SCORE: {score}", True, BLACK)
        # screen.blit(s_text, (20, 20))
        s_rect = s_text.get_rect(center=(SCREEN_WIDTH // 2, 40)) 
        screen.blit(s_text, s_rect)

        # 操作方法とタイムバー
        pygame.draw.rect(screen, (30, 30, 30), (0, 728, SCREEN_WIDTH, 40))
        c_text = font_info.render("操作：矢印キーで移動 ＆ スペースでジャンプ", True, WHITE)
        screen.blit(c_text, c_text.get_rect(center=(SCREEN_WIDTH//2, 748)))
        pygame.draw.rect(screen, WHITE, (312, 60, 400, 20), 2)
        pygame.draw.rect(screen, RED if time_left < 10 else NAVY, (312, 60, (time_left/LIMIT_TIME)*400, 20))

        if game_result:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)); overlay.set_alpha(180); overlay.fill(BLACK); screen.blit(overlay, (0, 0))
            msg = f"スコア: {score}"
            t1 = font_main.render("GOAL!!" if game_result == "CLEAR" else "TIME UP", True, GOLD)
            t2 = font_main.render(msg, True, WHITE)
            screen.blit(t1, t1.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50)))
            screen.blit(t2, t2.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50)))

        if player.rect.y > 720: # 落下
            player.rect.topleft = (50, 620); player.vel_y = 0; score = max(0, score - 20)

        pygame.display.flip(); clock.tick(FPS)

    # 点数を保存
    with open("score.txt", "w") as f: f.write(str(score))
    pygame.quit()

if __name__ == "__main__": main()