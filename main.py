import pygame
import sys


# =========================
# INITIALIZATION
# =========================

pygame.init()


# =========================
# SCREEN SETTINGS
# =========================

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 750

screen = pygame.display.set_mode(
    (SCREEN_WIDTH, SCREEN_HEIGHT)
)

pygame.display.set_caption("AI Battle Arena")


# =========================
# COLORS
# =========================

BACKGROUND = (12, 18, 30)
PANEL = (20, 28, 44)
PANEL_LIGHT = (28, 38, 58)

GRID_COLOR = (48, 62, 82)
GRID_HIGHLIGHT = (60, 80, 105)

TEXT = (235, 240, 248)
TEXT_MUTED = (145, 158, 180)

PLAYER_COLOR = (40, 210, 170)
AI_COLOR = (230, 80, 90)

CYAN = (45, 200, 230)
GREEN = (60, 210, 130)
RED = (230, 75, 85)
YELLOW = (240, 190, 70)

WHITE = (255, 255, 255)


# =========================
# FONT
# =========================

FONT_SMALL = pygame.font.SysFont(
    "arial",
    16
)

FONT_NORMAL = pygame.font.SysFont(
    "arial",
    20
)

FONT_MEDIUM = pygame.font.SysFont(
    "arial",
    24,
    bold=True
)

FONT_LARGE = pygame.font.SysFont(
    "arial",
    30,
    bold=True
)


# =========================
# GAME AREA
# =========================

GAME_X = 30
GAME_Y = 100

CELL_SIZE = 55

ROWS = 8
COLS = 12

GRID_WIDTH = COLS * CELL_SIZE
GRID_HEIGHT = ROWS * CELL_SIZE


# =========================
# UI PANEL POSITIONS
# =========================

TOP_BAR = pygame.Rect(
    30,
    20,
    1140,
    60
)

BATTLEFIELD_PANEL = pygame.Rect(
    30,
    90,
    760,
    570
)

AI_PANEL = pygame.Rect(
    810,
    90,
    360,
    270
)

BATTLE_LOG_PANEL = pygame.Rect(
    810,
    380,
    360,
    280
)

BOTTOM_BAR = pygame.Rect(
    30,
    680,
    1140,
    50
)


# =========================
# PLAYER / AI POSITION
# =========================

player_position = (2, 2)

ai_position = (5, 9)


# =========================
# HELPER FUNCTIONS
# =========================

def draw_text(
    text,
    font,
    color,
    x,
    y
):
    surface = font.render(
        text,
        True,
        color
    )

    screen.blit(
        surface,
        (x, y)
    )


def draw_centered_text(
    text,
    font,
    color,
    rect
):
    surface = font.render(
        text,
        True,
        color
    )

    text_rect = surface.get_rect(
        center=rect.center
    )

    screen.blit(
        surface,
        text_rect
    )


# =========================
# TOP HEADER
# =========================

def draw_header():

    pygame.draw.rect(
        screen,
        PANEL,
        TOP_BAR,
        border_radius=12
    )

    pygame.draw.rect(
        screen,
        (35, 48, 70),
        TOP_BAR,
        1,
        border_radius=12
    )

    draw_text(
        "AI BATTLE ARENA",
        FONT_LARGE,
        TEXT,
        50,
        34
    )

    draw_text(
        "TURN-BASED STRATEGIC COMBAT",
        FONT_SMALL,
        TEXT_MUTED,
        305,
        41
    )

    # Round indicator

    round_rect = pygame.Rect(
        1010,
        32,
        130,
        35
    )

    pygame.draw.rect(
        screen,
        PANEL_LIGHT,
        round_rect,
        border_radius=8
    )

    draw_centered_text(
        "ROUND 01",
        FONT_SMALL,
        CYAN,
        round_rect
    )


# =========================
# HEALTH BAR
# =========================

def draw_health_bar(
    x,
    y,
    width,
    height,
    current_hp,
    max_hp,
    color
):

    background_rect = pygame.Rect(
        x,
        y,
        width,
        height
    )

    pygame.draw.rect(
        screen,
        (45, 50, 65),
        background_rect,
        border_radius=5
    )

    hp_ratio = current_hp / max_hp

    hp_width = int(
        width * hp_ratio
    )

    hp_rect = pygame.Rect(
        x,
        y,
        hp_width,
        height
    )

    pygame.draw.rect(
        screen,
        color,
        hp_rect,
        border_radius=5
    )


# =========================
# PLAYER / AI INFO
# =========================

def draw_character_info():

    # PLAYER

    draw_text(
        "PLAYER",
        FONT_MEDIUM,
        PLAYER_COLOR,
        50,
        105
    )

    draw_text(
        "Saiful",
        FONT_SMALL,
        TEXT_MUTED,
        50,
        135
    )

    draw_health_bar(
        50,
        158,
        250,
        18,
        100,
        100,
        PLAYER_COLOR
    )

    draw_text(
        "100 / 100 HP",
        FONT_SMALL,
        TEXT,
        310,
        158
    )


    # AI

    draw_text(
        "AI OPPONENT",
        FONT_MEDIUM,
        AI_COLOR,
        430,
        105
    )

    draw_text(
        "AI Warrior",
        FONT_SMALL,
        TEXT_MUTED,
        430,
        135
    )

    draw_health_bar(
        430,
        158,
        250,
        18,
        100,
        100,
        AI_COLOR
    )

    draw_text(
        "100 / 100 HP",
        FONT_SMALL,
        TEXT,
        690,
        158
    )


# =========================
# GRID
# =========================

def draw_grid():

    grid_x = GAME_X + 20
    grid_y = GAME_Y + 110

    for row in range(ROWS):

        for col in range(COLS):

            rect = pygame.Rect(
                grid_x + col * CELL_SIZE,
                grid_y + row * CELL_SIZE,
                CELL_SIZE,
                CELL_SIZE
            )

            pygame.draw.rect(
                screen,
                (24, 33, 50),
                rect
            )

            pygame.draw.rect(
                screen,
                GRID_COLOR,
                rect,
                1
            )


# =========================
# GRID COORDINATE HELPER
# =========================

def grid_to_pixel(position):

    row, col = position

    grid_x = GAME_X + 20
    grid_y = GAME_Y + 110

    x = (
        grid_x
        + col * CELL_SIZE
        + CELL_SIZE // 2
    )

    y = (
        grid_y
        + row * CELL_SIZE
        + CELL_SIZE // 2
    )

    return x, y


# =========================
# PLAYER
# =========================

def draw_player():

    x, y = grid_to_pixel(
        player_position
    )

    # Glow

    pygame.draw.circle(
        screen,
        (25, 90, 80),
        (x, y),
        25
    )

    # Character

    pygame.draw.circle(
        screen,
        PLAYER_COLOR,
        (x, y),
        17
    )

    # Head highlight

    pygame.draw.circle(
        screen,
        WHITE,
        (x - 5, y - 5),
        4
    )


# =========================
# AI
# =========================

def draw_ai():

    x, y = grid_to_pixel(
        ai_position
    )

    # Glow

    pygame.draw.circle(
        screen,
        (100, 35, 45),
        (x, y),
        25
    )

    # Character

    pygame.draw.circle(
        screen,
        AI_COLOR,
        (x, y),
        17
    )

    # AI eyes

    pygame.draw.circle(
        screen,
        WHITE,
        (x - 6, y - 4),
        3
    )

    pygame.draw.circle(
        screen,
        WHITE,
        (x + 6, y - 4),
        3
    )


# =========================
# BATTLEFIELD
# =========================

def draw_battlefield():

    pygame.draw.rect(
        screen,
        PANEL,
        BATTLEFIELD_PANEL,
        border_radius=12
    )

    pygame.draw.rect(
        screen,
        (35, 48, 70),
        BATTLEFIELD_PANEL,
        1,
        border_radius=12
    )

    draw_character_info()

    draw_grid()

    draw_player()

    draw_ai()


# =========================
# AI BRAIN PANEL
# =========================

def draw_ai_panel():

    pygame.draw.rect(
        screen,
        PANEL,
        AI_PANEL,
        border_radius=12
    )

    pygame.draw.rect(
        screen,
        (35, 48, 70),
        AI_PANEL,
        1,
        border_radius=12
    )

    draw_text(
        "AI BRAIN",
        FONT_MEDIUM,
        CYAN,
        835,
        110
    )

    draw_text(
        "Decision System",
        FONT_SMALL,
        TEXT_MUTED,
        835,
        140
    )

    # Algorithm

    draw_text(
        "Algorithm",
        FONT_SMALL,
        TEXT_MUTED,
        835,
        180
    )

    draw_text(
        "A* + Minimax",
        FONT_NORMAL,
        TEXT,
        835,
        202
    )

    # Depth

    draw_text(
        "Search Depth",
        FONT_SMALL,
        TEXT_MUTED,
        835,
        240
    )

    draw_text(
        "3",
        FONT_NORMAL,
        TEXT,
        835,
        262
    )

    # Action

    draw_text(
        "Current Action",
        FONT_SMALL,
        TEXT_MUTED,
        980,
        180
    )

    draw_text(
        "WAITING",
        FONT_NORMAL,
        YELLOW,
        980,
        202
    )

    # Nodes

    draw_text(
        "Nodes Explored",
        FONT_SMALL,
        TEXT_MUTED,
        980,
        240
    )

    draw_text(
        "0",
        FONT_NORMAL,
        TEXT,
        980,
        262
    )

    # Status

    status_rect = pygame.Rect(
        835,
        300,
        310,
        35
    )

    pygame.draw.rect(
        screen,
        (25, 45, 55),
        status_rect,
        border_radius=7
    )

    draw_centered_text(
        "AI READY",
        FONT_SMALL,
        GREEN,
        status_rect
    )


# =========================
# BATTLE LOG
# =========================

def draw_battle_log():

    pygame.draw.rect(
        screen,
        PANEL,
        BATTLE_LOG_PANEL,
        border_radius=12
    )

    pygame.draw.rect(
        screen,
        (35, 48, 70),
        BATTLE_LOG_PANEL,
        1,
        border_radius=12
    )

    draw_text(
        "BATTLE LOG",
        FONT_MEDIUM,
        TEXT,
        835,
        400
    )

    logs = [
        "Battle initialized.",
        "Player deployed.",
        "AI opponent deployed.",
        "Waiting for player..."
    ]

    y = 445

    for log in logs:

        draw_text(
            "> " + log,
            FONT_SMALL,
            TEXT_MUTED,
            835,
            y
        )

        y += 35


# =========================
# BOTTOM CONTROLS
# =========================

def draw_bottom_bar():

    pygame.draw.rect(
        screen,
        PANEL,
        BOTTOM_BAR,
        border_radius=10
    )

    draw_text(
        "YOUR TURN",
        FONT_NORMAL,
        PLAYER_COLOR,
        50,
        695
    )

    draw_text(
        "WASD / ARROWS  Move",
        FONT_SMALL,
        TEXT_MUTED,
        240,
        699
    )

    draw_text(
        "SPACE  Attack",
        FONT_SMALL,
        TEXT_MUTED,
        480,
        699
    )

    draw_text(
        "D  Defend",
        FONT_SMALL,
        TEXT_MUTED,
        650,
        699
    )

    draw_text(
        "ESC  Quit",
        FONT_SMALL,
        TEXT_MUTED,
        800,
        699
    )


# =========================
# MAIN GAME LOOP
# =========================

clock = pygame.time.Clock()

running = True

while running:

    # =====================
    # EVENTS
    # =====================

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:

                running = False


    # =====================
    # DRAW
    # =====================

    screen.fill(
        BACKGROUND
    )

    draw_header()

    draw_battlefield()

    draw_ai_panel()

    draw_battle_log()

    draw_bottom_bar()


    # =====================
    # UPDATE SCREEN
    # =====================

    pygame.display.flip()

    clock.tick(60)


pygame.quit()

sys.exit()