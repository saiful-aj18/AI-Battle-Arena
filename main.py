import pygame
import sys

from ai.astar import a_star


# =========================================================
# INITIALIZATION
# =========================================================

pygame.init()


# =========================================================
# SCREEN SETTINGS
# =========================================================

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 750

screen = pygame.display.set_mode(
    (SCREEN_WIDTH, SCREEN_HEIGHT)
)

pygame.display.set_caption(
    "AI Battle Arena"
)


# =========================================================
# COLORS
# =========================================================

BACKGROUND = (12, 18, 30)

PANEL = (20, 28, 44)
PANEL_LIGHT = (28, 38, 58)

GRID_COLOR = (48, 62, 82)

OBSTACLE_COLOR = (55, 65, 82)
OBSTACLE_BORDER = (85, 100, 120)

TEXT = (235, 240, 248)
TEXT_MUTED = (145, 158, 180)

PLAYER_COLOR = (40, 210, 170)
AI_COLOR = (230, 80, 90)

CYAN = (45, 200, 230)
GREEN = (60, 210, 130)
RED = (230, 75, 85)
YELLOW = (240, 190, 70)

WHITE = (255, 255, 255)


# =========================================================
# FONTS
# =========================================================

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


# =========================================================
# GAME / GRID SETTINGS
# =========================================================

GAME_X = 30
GAME_Y = 90

CELL_SIZE = 55

ROWS = 8
COLS = 12


# =========================================================
# UI PANELS
# =========================================================

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


# =========================================================
# PLAYER / AI POSITION
# =========================================================

player_position = [2, 2]

ai_position = [5, 9]

# =========================================================
# A* PATH DATA
# =========================================================

ai_path = []

ai_nodes_explored = 0

ai_path_index = 0


# =========================================================
# OBSTACLES
# =========================================================
#
# Format:
# (row, column)
#
# These cells cannot be entered.
#

obstacles = {
    (1, 4),
    (1, 5),
    (1, 6),

    (2, 6),

    (3, 3),
    (3, 4),

    (4, 7),
    (4, 8),

    (5, 4),

    (6, 6),
    (6, 7),
}


# =========================================================
# GAME STATE
# =========================================================

PLAYER_TURN = "PLAYER"
AI_TURN = "AI"

current_turn = PLAYER_TURN

round_number = 1

ai_thinking = False

ai_turn_start_time = 0


# =========================================================
# BATTLE LOG
# =========================================================

battle_logs = [
    "Battle initialized.",
    "Player deployed.",
    "AI opponent deployed.",
    "Your turn."
]


# =========================================================
# HELPER FUNCTIONS
# =========================================================

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


def add_log(message):

    battle_logs.append(message)

    # Keep only last 6 messages

    if len(battle_logs) > 6:
        battle_logs.pop(0)


# =========================================================
# HEADER
# =========================================================

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
        f"ROUND {round_number:02}",
        FONT_SMALL,
        CYAN,
        round_rect
    )


# =========================================================
# HEALTH BAR
# =========================================================

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


# =========================================================
# CHARACTER INFORMATION
# =========================================================

def draw_character_info():

    # -------------------------
    # PLAYER
    # -------------------------

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


    # -------------------------
    # AI
    # -------------------------

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


# =========================================================
# GRID POSITION → SCREEN POSITION
# =========================================================

def grid_to_pixel(position):

    row, col = position

    grid_x = GAME_X + 20
    grid_y = GAME_Y + 130

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


# =========================================================
# GRID
# =========================================================

def draw_grid():

    grid_x = GAME_X + 20
    grid_y = GAME_Y + 130

    for row in range(ROWS):

        for col in range(COLS):

            rect = pygame.Rect(
                grid_x + col * CELL_SIZE,
                grid_y + row * CELL_SIZE,
                CELL_SIZE,
                CELL_SIZE
            )

            # Normal cell

            pygame.draw.rect(
                screen,
                (24, 33, 50),
                rect
            )

            # Grid border

            pygame.draw.rect(
                screen,
                GRID_COLOR,
                rect,
                1
            )
            
            # =====================================================
            # A* PATH VISUALIZATION
            # =====================================================
            if (
                (row, col) in ai_path
                and (row, col) != tuple(ai_position)
                and (row, col) != tuple(player_position)
                ):
                
                path_surface = pygame.Surface(
                    (CELL_SIZE, CELL_SIZE),
                    pygame.SRCALPHA
                    )
                path_surface.fill(
                    (45, 200, 230, 70)
                    )
                screen.blit(
                    path_surface,
                    rect
                    )

            # -------------------------
            # OBSTACLE
            # -------------------------

            if (row, col) in obstacles:

                obstacle_rect = rect.inflate(
                    -8,
                    -8
                )

                pygame.draw.rect(
                    screen,
                    OBSTACLE_COLOR,
                    obstacle_rect,
                    border_radius=7
                )

                pygame.draw.rect(
                    screen,
                    OBSTACLE_BORDER,
                    obstacle_rect,
                    2,
                    border_radius=7
                )

                # X pattern

                pygame.draw.line(
                    screen,
                    (95, 105, 120),
                    obstacle_rect.topleft,
                    obstacle_rect.bottomright,
                    2
                )

                pygame.draw.line(
                    screen,
                    (95, 105, 120),
                    obstacle_rect.topright,
                    obstacle_rect.bottomleft,
                    2
                )


# =========================================================
# PLAYER
# =========================================================

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

    # Body

    pygame.draw.circle(
        screen,
        PLAYER_COLOR,
        (x, y),
        17
    )

    # Highlight

    pygame.draw.circle(
        screen,
        WHITE,
        (x - 5, y - 5),
        4
    )


# =========================================================
# AI
# =========================================================

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

    # Body

    pygame.draw.circle(
        screen,
        AI_COLOR,
        (x, y),
        17
    )

    # Eyes

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


# =========================================================
# BATTLEFIELD
# =========================================================

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


# =========================================================
# AI BRAIN PANEL
# =========================================================

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
        "A* Search",
        FONT_NORMAL,
        TEXT,
        835,
        202
    )

    # Search Depth

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

    # Current Action

    draw_text(
        "Current Action",
        FONT_SMALL,
        TEXT_MUTED,
        980,
        180
    )

    if current_turn == PLAYER_TURN:

        action_text = "WAITING"
        action_color = YELLOW

    else:

        action_text = "THINKING"
        action_color = CYAN

    draw_text(
        action_text,
        FONT_NORMAL,
        action_color,
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
        str(ai_nodes_explored),
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

    if current_turn == PLAYER_TURN:

        draw_centered_text(
            "YOUR TURN",
            FONT_SMALL,
            GREEN,
            status_rect
        )

    else:

        draw_centered_text(
            "AI TURN",
            FONT_SMALL,
            CYAN,
            status_rect
        )


# =========================================================
# BATTLE LOG
# =========================================================

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

    y = 445

    for log in battle_logs:

        draw_text(
            "> " + log,
            FONT_SMALL,
            TEXT_MUTED,
            835,
            y
        )

        y += 35


# =========================================================
# BOTTOM CONTROLS
# =========================================================

def draw_bottom_bar():

    pygame.draw.rect(
        screen,
        PANEL,
        BOTTOM_BAR,
        border_radius=10
    )

    if current_turn == PLAYER_TURN:

        draw_text(
            "YOUR TURN",
            FONT_NORMAL,
            PLAYER_COLOR,
            50,
            695
        )

    else:

        draw_text(
            "AI TURN",
            FONT_NORMAL,
            AI_COLOR,
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


# =========================================================
# VALID POSITION CHECK
# =========================================================

def is_valid_position(
    position
):

    row, col = position

    # Outside grid

    if row < 0 or row >= ROWS:
        return False

    if col < 0 or col >= COLS:
        return False

    # Obstacle

    if (row, col) in obstacles:
        return False

    # Player cannot move into AI

    if position == tuple(ai_position):
        return False

    # AI cannot move into Player

    if position == tuple(player_position):
        return False

    return True


# =========================================================
# PLAYER MOVEMENT
# =========================================================

def move_player(
    row_change,
    col_change
):

    global current_turn
    global ai_thinking
    global ai_turn_start_time

    new_row = (
        player_position[0]
        + row_change
    )

    new_col = (
        player_position[1]
        + col_change
    )

    new_position = (
        new_row,
        new_col
    )

    # Check movement

    if not is_valid_position(
        new_position
    ):

        add_log(
            "Movement blocked."
        )

        return

    # Update position

    player_position[0] = new_row
    player_position[1] = new_col

    add_log(
        f"Player moved → ({new_row}, {new_col})"
    )
    
    calculate_ai_path()

    # Player turn finished

    current_turn = AI_TURN

    ai_thinking = True

    ai_turn_start_time = pygame.time.get_ticks()

    add_log(
        "AI is thinking..."
    )


# =========================================================
# TEMPORARY AI MOVEMENT
# =========================================================
#
# IMPORTANT:
# This is NOT A*.
#
# We are using a simple one-step movement only to
# demonstrate the turn system.
#
# Step 3 will replace this with REAL A*.
#


# =========================================================
# CALCULATE AI PATH USING A*
# =========================================================

def calculate_ai_path():
    
    global ai_path
    global ai_nodes_explored
    global ai_path_index

    start = tuple(ai_position)

    player = tuple(player_position)

    # Possible cells around player

    target_cells = []

    directions = [
        (-1, 0),
        (1, 0),
        (0, -1),
        (0, 1)
    ]

    for row_change, col_change in directions:

        target = (
            player[0] + row_change,
            player[1] + col_change
        )

        # Inside grid

        if target[0] < 0 or target[0] >= ROWS:
            continue

        if target[1] < 0 or target[1] >= COLS:
            continue

        # Not obstacle

        if target in obstacles:
            continue

        target_cells.append(target)

    # Find shortest valid path

    best_path = []
    best_nodes = 0

    for target in target_cells:

        path, nodes = a_star(
            start,
            target,
            ROWS,
            COLS,
            obstacles
        )

        if path:

            if (
                not best_path
                or len(path) < len(best_path)
            ):

                best_path = path
                best_nodes = nodes

    ai_path = best_path

    ai_nodes_explored = best_nodes

    ai_path_index = 0

    if ai_path:

        add_log(
            f"A* path found → {len(ai_path) - 1} moves"
        )

        add_log(
            f"Nodes explored → {ai_nodes_explored}"
        )

    else:

        add_log(
            "A* could not find a path."
        )

# =========================================================
# MOVE AI ALONG A* PATH
# =========================================================

def ai_move():

    global current_turn
    global round_number
    global ai_thinking
    global ai_path_index

    # No path

    if not ai_path:

        calculate_ai_path()

    # If path exists

    if len(ai_path) > 1:

        # First cell is current AI position
        #
        # So move to next cell

        next_position = ai_path[1]

        ai_position[0] = next_position[0]

        ai_position[1] = next_position[1]

        # Remove first cell from path

        ai_path_index += 1

        add_log(
            f"AI follows A* → ({next_position[0]}, {next_position[1]})"
        )

    else:

        add_log(
            "AI is already near target."
        )

    # AI turn finished

    current_turn = PLAYER_TURN

    ai_thinking = False

    round_number += 1

    add_log(
        "Your turn."
    )

# =========================================================
# HANDLE PLAYER KEYBOARD
# =========================================================

def handle_player_input(
    key
):

    if current_turn != PLAYER_TURN:

        return

    # UP

    if key in (
        pygame.K_w,
        pygame.K_UP
    ):

        move_player(
            -1,
            0
        )

    # DOWN

    elif key in (
        pygame.K_s,
        pygame.K_DOWN
    ):

        move_player(
            1,
            0
        )

    # LEFT

    elif key in (
        pygame.K_a,
        pygame.K_LEFT
    ):

        move_player(
            0,
            -1
        )

    # RIGHT

    elif key in (
        pygame.K_d,
        pygame.K_RIGHT
    ):

        move_player(
            0,
            1
        )


# =========================================================
# MAIN LOOP
# =========================================================

clock = pygame.time.Clock()

running = True


while running:

    # =====================================================
    # EVENTS
    # =====================================================

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False

        if event.type == pygame.KEYDOWN:

            # Quit

            if event.key == pygame.K_ESCAPE:

                running = False

            # Player controls

            if current_turn == PLAYER_TURN:

                handle_player_input(
                    event.key
                )


    # =====================================================
    # AI TURN
    # =====================================================

    if (
        current_turn == AI_TURN
        and ai_thinking
    ):

        current_time = pygame.time.get_ticks()

        # Wait 700 milliseconds

        if (
            current_time
            - ai_turn_start_time
            > 700
        ):

            ai_move()


    # =====================================================
    # DRAW
    # =====================================================

    screen.fill(
        BACKGROUND
    )

    draw_header()

    draw_battlefield()

    draw_ai_panel()

    draw_battle_log()

    draw_bottom_bar()


    # =====================================================
    # UPDATE
    # =====================================================

    pygame.display.flip()

    clock.tick(60)


# =========================================================
# EXIT
# =========================================================

pygame.quit()

sys.exit()