import sys
import random
import pygame

# 初期化
pygame.init()
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("ダンジョン・ローグアタック")
clock = pygame.time.Clock()

# 色の定義
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (231, 76, 60)
BLUE = (52, 152, 219)
GRAY = (127, 140, 141)

# プレイヤークラス
class Player:
    def __init__(self):
        self.x = 100
        self.y = 200
        self.size = 30
        self.speed = 4
        self.hp = 100
        self.max_hp = 100

    def move(self, keys):
        if keys[pygame.K_LEFT] or keys[pygame.K_ord('a')]:
            self.x = max(0, self.x - self.speed)
        if keys[pygame.K_RIGHT] or keys[pygame.K_ord('d')]:
            self.x = min(SCREEN_WIDTH - self.size, self.x + self.speed)
        if keys[pygame.K_UP] or keys[pygame.K_ord('w')]:
            self.y = max(0, self.y - self.speed)
        if keys[pygame.K_DOWN] or keys[pygame.K_ord('s')]:
            self.y = min(SCREEN_HEIGHT - self.size, self.y + self.speed)

    def draw(self, surface):
        pygame.draw.rect(surface, BLUE, (self.x, self.y, self.size, self.size))

# 敵クラス
class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 25
        self.speed = 2
        self.hp = 30

    def chase(self, target_x, target_y):
        if self.x < target_x:
            self.x += self.speed
        elif self.x > target_x:
            self.x -= self.speed
            
        if self.y < target_y:
            self.y += self.speed
        elif self.y > target_y:
            self.y -= self.speed

    def draw(self, surface):
        pygame.draw.rect(surface, RED, (self.x, self.y, self.size, self.size))

# ゲームのメインループ
player = Player()
enemies = [Enemy(500, 100), Enemy(550, 300)]
font = pygame.font.SysFont(None, 24)

running = True
while running:
    # 1. イベント処理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = false

    # 2. キー入力と更新
    keys = pygame.key.get_pressed()
    player.move(keys)

    for enemy in enemies:
        enemy.chase(player.x, player.y)
        # 当たり判定（簡易）
        if abs(player.x - enemy.x) < 20 and abs(player.y - enemy.y) < 20:
            player.hp = max(0, player.hp - 1)

    # 3. 描画
    screen.fill(BLACK)
    
    player.draw(screen)
    for enemy in enemies:
        enemy.draw(screen)

    # UI（HP表示）
    hp_text = font.render(f"HP: {player.hp}/{player.max_hp}", True, WHITE)
    screen.blit(hp_text, (10, 10))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
