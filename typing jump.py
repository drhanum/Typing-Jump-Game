import pygame
import random

pygame.init()
# Display
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Word Jump - IMAGE ONLY - NO ROAD")
clock = pygame.time.Clock()

# Warna
WHITE = (255, 255, 255)
GREEN = (0, 200, 80)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Font
def load_comic_font(size):
    return pygame.font.SysFont("Comic Sans MS", size)

def render_text_outline(font_obj, text, inner_color, outline_color=BLACK, thickness=2):
    base = font_obj.render(text, True, inner_color)
    outline = font_obj.render(text, True, outline_color)
    w = base.get_width() + thickness*2
    h = base.get_height() + thickness*2
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    offs = [(0, -thickness),(0, thickness),(-thickness,0),(thickness,0)]
    for dx, dy in offs:
        surf.blit(outline, (dx + thickness, dy + thickness))
    surf.blit(base, (thickness, thickness))
    return surf

font = load_comic_font(36)
small_font = load_comic_font(20)

scroll_speed = 2
jumping = False
vx, vy = 0, 0
jump_target = None

# Platform
PLATFORM_W, PLATFORM_H = 250, 80
platform_img = pygame.image.load("project UAS/platform.png").convert_alpha()
platform_img = pygame.transform.scale(platform_img, (PLATFORM_W, PLATFORM_H))

def generate_platforms(n=6, start_y=HEIGHT-150):
    plats = []
    side = "left"
    for i in range(n):
        y = start_y - i*150
        word = random.choice(word_list)
        x = 100 if side == "left" else WIDTH - PLATFORM_W - 100
        side = "right" if side == "left" else "left"
        plats.append({
            "rect": pygame.Rect(x, y, PLATFORM_W, PLATFORM_H),
            "word": word,
            "colors": [WHITE]*len(word)
        })
    return plats

# Ground
GROUND_HEIGHT = 80
background_img = pygame.image.load("project UAS/background.jpg").convert_alpha()
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))

# Player
PLAYER_W, PLAYER_H = 80, 80
player_img = pygame.image.load("project UAS/hamster.png").convert_alpha()
player_img = pygame.transform.scale(player_img, (PLAYER_W, PLAYER_H))
player = pygame.Rect(WIDTH//2, HEIGHT - 100, 50, 50)
gravity = 0.6

# Game state
score = 0
lives = 3
game_over = False
typed_word = ""
saved_score_this_run = False

# Leaderboard
LEADERBOARD_FILE = "leaderboard.txt"
leaderboard = []

def load_leaderboard():
    global leaderboard
    try:
        with open(LEADERBOARD_FILE, "r") as f:
            lines = f.readlines()
        leaderboard = [int(x.strip()) for x in lines if x.strip().isdigit()]
        leaderboard.sort(reverse=True)
        leaderboard = leaderboard[:10]
    except:
        leaderboard = []

def save_leaderboard():
    with open(LEADERBOARD_FILE, "w") as f:
        for s in leaderboard:
            f.write(str(s) + "\n")

def add_score(sc):
    leaderboard.append(sc)
    leaderboard.sort(reverse=True)
    del leaderboard[10:]
    save_leaderboard()

# Word List
word_list = [
    'mawar','bulan','kursi','naga','kuda','matana','merak','tronton','kucing','singkong',
    'apel','nanas','melati','ular','burung','meja','botol','gelas','ikan','jangkrik',
    'kodok','teratai','rubik','hiu','nemo','tulip','peony','anggrek','lily','anggur',
    'jeruk','melon','pisang','pink','ungu','pelangi','dompet','tripod','pizza','kopi',
    'vanilla','sepatu','sandal','natal','emas','silver','kuning','rambut','awan','langit',
    'harimau','serigala','permen','kabel','laptop','cooler','tembok','gelang','pohon','sushi',
    'kacamata','hidup','jatuh','kaca','hujan','matahari','mata','hari','hati','jendela',
    'kemeja','kaos','kipas','angin','lantai','tanda','bendera','tiang','lapangan','rumput',
    'batu','makan','pintu','lift','tangga','roda','mesin','piala','payung','teduh',
    'duri','jaket','riang','siang','angsa','sapi','pinjam','jam','jambu','buah','renaldi'
]

platforms = generate_platforms()
current_index = 0
load_leaderboard()

def reset_game():
    global player, score, lives, game_over, typed_word, platforms
    global current_index, jumping, vx, vy, jump_target, saved_score_this_run

    player.x = WIDTH//4
    player.y = HEIGHT - 100 - PLAYER_H
    score = 0
    lives = 3
    game_over = False
    typed_word = ""
    jumping = False
    vx = vy = 0
    jump_target = None
    platforms[:] = generate_platforms()
    current_index = 0
    saved_score_this_run = False

running = True
while running:
    screen.blit(background_img, (0, 0))

    pygame.draw.rect(screen, (65,170,70), (0, HEIGHT - GROUND_HEIGHT, WIDTH, GROUND_HEIGHT))
    pygame.draw.rect(screen, (55,150,60), (0, HEIGHT - GROUND_HEIGHT, WIDTH, 12))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:

            if game_over:
                if event.key == pygame.K_r:
                    reset_game()
                elif event.key == pygame.K_q:
                    running = False
                continue

            if event.key == pygame.K_BACKSPACE:
                typed_word = typed_word[:-1]

            elif event.key == pygame.K_RETURN:
                typed_clean = typed_word.strip().lower()
                target = platforms[current_index]["word"].lower()

                if typed_clean == target:
                    trg = platforms[current_index]["rect"]
                    jump_target = trg
                    dx = trg.centerx - player.centerx
                    steps = 30
                    vx = dx / steps
                    vy = -12
                    jumping = True

                    score += 10
                    current_index += 1
                    if current_index >= len(platforms):
                        more = generate_platforms(4, platforms[-1]["rect"].y - 120)
                        platforms.extend(more)

                else:
                    lives -= 1
                    if lives <= 0:
                        game_over = True
                        if not saved_score_this_run:
                            add_score(score)
                            saved_score_this_run = True

                typed_word = ""

            else:
                typed_word += event.unicode
                active = platforms[current_index]
                for i, ch in enumerate(active["word"]):
                    if i < len(typed_word):
                        active["colors"][i] = GREEN if typed_word[i].lower() == ch.lower() else RED
                    else:
                        active["colors"][i] = WHITE

    if not game_over:
        if jumping and jump_target:
            player.centerx += vx
            player.bottom += vy
            vy += gravity

            if player.bottom >= jump_target.top and abs(player.centerx - jump_target.centerx) < 24:
                player.bottom = jump_target.top
                jumping = False
                vy = 0
                jump_target = None

        if player.top < HEIGHT//2:
            for plat in platforms:
                plat["rect"].y += scroll_speed
            player.y += scroll_speed

        for plat in platforms:
            screen.blit(platform_img, plat["rect"].topleft)
            x = plat["rect"].x + 30
            y = plat["rect"].y - 45
            for i, ch in enumerate(plat["word"]):
                txt = render_text_outline(font, ch, plat["colors"][i])
                screen.blit(txt, (x + i*22, y))

        screen.blit(player_img, (player.centerx - PLAYER_W//2, player.bottom - PLAYER_H))
        screen.blit(render_text_outline(small_font, f"Score: {score}", WHITE), (20, 20))
        screen.blit(render_text_outline(small_font, f"Lives: {lives}", WHITE), (20, 50))
        screen.blit(render_text_outline(small_font, f"Typed: {typed_word}", WHITE), (20, 80))

    else:
        over = render_text_outline(font, "Game Over", WHITE)
        scr = render_text_outline(small_font, f"Final Score: {score}", WHITE)
        screen.blit(over, (WIDTH//2 - over.get_width()//2, HEIGHT//2 - 150))
        screen.blit(scr, (WIDTH//2 - scr.get_width()//2, HEIGHT//2 - 100))

        lbl = render_text_outline(small_font, "Leaderboard (Top 10)", WHITE)
        screen.blit(lbl, (WIDTH//2 - lbl.get_width()//2, HEIGHT//2 - 50))

        y = HEIGHT//2
        for i, s in enumerate(leaderboard):
            t = render_text_outline(small_font, f"{i+1}. {s}", WHITE)
            screen.blit(t, (WIDTH//2 - 40, y + i*28))

        inst = render_text_outline(small_font, "Press R to Restart or Q to Quit", WHITE)
        screen.blit(inst, (WIDTH//2 - inst.get_width()//2, HEIGHT - 60))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()