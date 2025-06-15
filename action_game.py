import pygame
import sys
import random

# Pygameの初期化
pygame.init()

# 画面設定
screen_width = 1100
screen_height = 800
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("シンプルアクションゲーム")

# 色の定義
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

MAX_ROCKS = 11
ROCK_SPAWN_CHANCE = 90



# 星の数
STAR_COUNT = 60

# 星リストを作成（座標と大きさ）
stars = []
for _ in range(STAR_COUNT):
    x = random.randint(0, screen_width-1)
    y = random.randint(0, screen_height-1)
    r = random.randint(1, 2)  # 星の半径（大きさ）
    stars.append((x, y, r))


# スプライトグループの作成
all_sprites = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
boss_group = pygame.sprite.Group()
rock_group = pygame.sprite.Group()

# 画像の事前読み込み
rock_image = pygame.image.load("rock.png").convert_alpha()
rock_image = pygame.transform.scale(rock_image, (60, 60))

# プレイヤークラス
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("player_plane.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (40, 50))
        self.rect = self.image.get_rect()
        self.rect.centerx = screen_width // 2
        self.rect.bottom = screen_height - 10
        self.speed = 4

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < screen_width:
            self.rect.x += self.speed
        if keys[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] and self.rect.bottom < screen_height:
            self.rect.y += self.speed

# 弾の設定
bullet_width = 5
bullet_height = 15
bullet_speed = 8
bullets = []

# ---ここに追加---
boss_bullets = []
boss_bullet_width = 6
boss_bullet_height = 40
boss_bullet_speed = 5
last_boss_shot_time = 0


# 敵キャラクタークラス
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("enemy_character.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (40, 40))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.health = 3

    def update(self):
        self.rect.y += 3
        if self.rect.top > screen_height:
            self.kill()

# Rockクラス
class Rock(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = rock_image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self):
        self.rect.y += 3
        if self.rect.top > screen_height:
            self.kill()


# ボスキャラクタークラス
class Boss(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("boss_character.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (130, 90))
        self.rect = self.image.get_rect()
        self.rect.centerx = screen_width // 2
        self.rect.y = -100
        self.health = 30
        self.direction_x = 1
        self.direction_y = 1
        self.speed_x = 2
        self.speed_y = 1.5

    def update(self):
        if self.rect.top < 50:
            self.rect.y += 1
        else:
            self.rect.x += self.speed_x * self.direction_x
        if self.rect.right > screen_width or self.rect.left < 0:
            self.direction_x *= -1
            # 画面外にはみ出した場合は補正
            if self.rect.right > screen_width:
                self.rect.right = screen_width
            if self.rect.left < 0:
                self.rect.left = 0

        self.rect.y += self.speed_y * self.direction_y
        # 画面内で反転し、はみ出した場合は補正
        if self.rect.top < 50:
            self.direction_y *= -1
            self.rect.top = 50
        if self.rect.bottom > screen_height - 100:
            self.direction_y *= -1
            self.rect.bottom = screen_height - 100





# プレイヤーインスタンスの作成
player = Player()
all_sprites.add(player)

# スコア
score = 0
font = pygame.font.Font(None, 36)
game_over_font = pygame.font.Font(None, 140)

# ---ここに追加---
boss_respawn_delay = 10000  # ボス再出現までの待ち時間（ミリ秒、例：5秒）
last_boss_kill_time = None  # 最初はNone



# ゲームオーバーフラグ
game_over = False

# ゲームループ
clock = pygame.time.Clock()
running = True
boss_spawned = False

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not game_over:
                # 弾の発射処理（インデント修正）
                bullets.append(pygame.Rect(
                    player.rect.centerx - bullet_width//2,
                    player.rect.top,
                    bullet_width,
                    bullet_height
                ))

    if not game_over:
        # プレイヤー移動処理
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.rect.left > 0:
            player.rect.x -= player.speed
        if keys[pygame.K_RIGHT] and player.rect.right < screen_width:
            player.rect.x += player.speed
        if keys[pygame.K_UP] and player.rect.top > 0:
            player.rect.y -= player.speed
        if keys[pygame.K_DOWN] and player.rect.bottom < screen_height:
            player.rect.y += player.speed

        # 岩の生成
        if len(rock_group) < MAX_ROCKS and random.randint(1, ROCK_SPAWN_CHANCE) == 1:
            x = random.randint(0, screen_width - 40)
            rock = Rock(x, 0)
            rock_group.add(rock)
            all_sprites.add(rock)

        # スプライト更新（インデント修正）
        all_sprites.update()

        # 弾の移動
        bullets_to_remove = []
        for bullet in bullets:
            bullet.y -= bullet_speed
            if bullet.y < 0:
                bullets_to_remove.append(bullet)
        
        for bullet in bullets_to_remove:
            if bullet in bullets:
                bullets.remove(bullet)

        # 敵の生成
        if random.randint(1, 15) == 1 and len(enemy_group) < 5:
            x = random.randint(0, screen_width - 50)
            enemy = Enemy(x, 0)
            enemy_group.add(enemy)
            all_sprites.add(enemy)

        # ボスの生成
        # ボスの生成
        current_time = pygame.time.get_ticks()  # すでに使っていれば再利用OK
        if (
            score >= 50
            and not boss_spawned
            and (last_boss_kill_time is None or current_time - last_boss_kill_time > boss_respawn_delay)):
            boss = Boss()
            boss_group.add(boss)
            all_sprites.add(boss)
            boss_spawned = True



        # ---ここから追加---
        # ボスが弾を撃つ
        if boss_group:
            current_time = pygame.time.get_ticks()
            if current_time - last_boss_shot_time > 700:
                for boss in boss_group:
                    boss_bullets.append(pygame.Rect(
                        boss.rect.centerx - boss_bullet_width//2,
                        boss.rect.bottom,
                        boss_bullet_width,
                        boss_bullet_height
                    ))
                last_boss_shot_time = current_time

        # ボス弾の移動
        boss_bullets_to_remove = []
        for bullet in boss_bullets:
            bullet.y += boss_bullet_speed
            if bullet.y > screen_height:
                boss_bullets_to_remove.append(bullet)     
        for bullet in boss_bullets_to_remove:
            boss_bullets.remove(bullet)

        # ボス弾とプレイヤーの衝突判定
        for bullet in boss_bullets:
            if player.rect.colliderect(bullet):
                game_over = True
        # ---ここまで追加


        # 衝突判定
        if pygame.sprite.spritecollideany(player, 
            pygame.sprite.Group(enemy_group, boss_group, rock_group)):
            game_over = True


        for rock in rock_group:
            if player.rect.colliderect(rock.rect.inflate(-10, -10)):
                game_over = True

        # 弾と敵の衝突判定
        for bullet in bullets[:]:
            for enemy in enemy_group:
                if bullet.colliderect(enemy.rect):
                    bullets.remove(bullet)
                    enemy.health -= 1
                    if enemy.health <= 0:
                        enemy.kill()
                        score += 1

            for boss in boss_group:
                if bullet.colliderect(boss.rect):
                    bullets.remove(bullet)
                    boss.health -= 1
                    if boss.health <= 0:
                        boss.kill()
                        score += 10
                        boss_spawned = False
                        last_boss_kill_time = pygame.time.get_ticks()

    # 描画処理
    screen.fill(BLACK)
    
    for x, y, r in stars:
        pygame.draw.circle(screen, WHITE, (x, y), r)

    all_sprites.draw(screen)

    for bullet in boss_bullets:
        pygame.draw.rect(screen, (255, 128, 0), bullet)  # オレンジ色の火

    # 弾の描画
    for bullet in bullets:
        pygame.draw.rect(screen, WHITE, bullet)

    # スコア表示
    score_text = font.render(f"スコア: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

    # ゲームオーバー表示
    if game_over:
        game_over_text = game_over_font.render("GAME OVER", True, RED)
        screen.blit(game_over_text, (screen_width//2 - game_over_text.get_width()//2, screen_height//2 - game_over_text.get_height()//2))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
