import pygame
import sys

from ai.astar import a_star

from ai.minimax import (
    get_best_action
)


# =========================================================
# INITIALIZATION
# =========================================================

pygame.init()


# =========================================================
# SCREEN
# =========================================================

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 750

screen = pygame.display.set_mode(
    (
        SCREEN_WIDTH,
        SCREEN_HEIGHT
    )
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

FONT_HUGE = pygame.font.SysFont(
    "arial",
    48,
    bold=True
)


# =========================================================
# GRID
# =========================================================

GAME_X = 30

GAME_Y = 90

CELL_SIZE = 55

ROWS = 8

COLS = 12


# =========================================================
# PANELS
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
# POSITIONS
# =========================================================

player_position = [2, 2]

ai_position = [5, 9]


# =========================================================
# OBSTACLES
# =========================================================

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
# HP
# =========================================================

PLAYER_MAX_HP = 100

AI_MAX_HP = 100

player_hp = 100

ai_hp = 100


# =========================================================
# COMBAT
# =========================================================

PLAYER_DAMAGE = 20

AI_DAMAGE = 15

ATTACK_RANGE = 1

player_defending = False

ai_defending = False


# =========================================================
# TURN
# =========================================================

PLAYER_TURN = "PLAYER"

AI_TURN = "AI"

current_turn = PLAYER_TURN

round_number = 1


# =========================================================
# GAME STATE
# =========================================================

game_over = False

winner = None

ai_thinking = False

ai_turn_start = 0


# =========================================================
# AI INFORMATION
# =========================================================

ai_path = []

ai_nodes_explored = 0

minimax_nodes = 0

minimax_score = 0

ai_current_action = "WAITING"

SEARCH_DEPTH = 3


# =========================================================
# EFFECTS
# =========================================================

attack_effect = None

damage_effects = []


# =========================================================
# LOG
# =========================================================

battle_logs = [

    "Battle initialized.",

    "Player deployed.",

    "AI opponent deployed.",

    "Your turn."
]


# =========================================================
# TEXT
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
        (
            x,
            y
        )
    )


def centered_text(
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


# =========================================================
# LOG
# =========================================================

def add_log(message):

    battle_logs.append(
        message
    )

    if len(battle_logs) > 6:

        battle_logs.pop(0)


# =========================================================
# GRID → PIXEL
# =========================================================

def grid_to_pixel(position):

    row, col = position

    grid_x = GAME_X + 20

    grid_y = GAME_Y + 130

    return (

        grid_x
        +
        col * CELL_SIZE
        +
        CELL_SIZE // 2,

        grid_y
        +
        row * CELL_SIZE
        +
        CELL_SIZE // 2
    )


# =========================================================
# DISTANCE
# =========================================================

def get_distance(
    first,
    second
):

    return (

        abs(
            first[0]
            -
            second[0]
        )

        +

        abs(
            first[1]
            -
            second[1]
        )
    )


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

    centered_text(
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
    hp,
    max_hp,
    color
):

    background = pygame.Rect(
        x,
        y,
        width,
        height
    )

    pygame.draw.rect(
        screen,
        (45, 50, 65),
        background,
        border_radius=5
    )

    ratio = hp / max_hp

    hp_width = int(
        width * ratio
    )

    if hp_width > 0:

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
# CHARACTER INFO
# =========================================================

def draw_character_info():

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
        player_hp,
        PLAYER_MAX_HP,
        PLAYER_COLOR
    )

    draw_text(
        f"{player_hp} / {PLAYER_MAX_HP} HP",
        FONT_SMALL,
        TEXT,
        310,
        158
    )


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
        ai_hp,
        AI_MAX_HP,
        AI_COLOR
    )

    draw_text(
        f"{ai_hp} / {AI_MAX_HP} HP",
        FONT_SMALL,
        TEXT,
        690,
        158
    )


# =========================================================
# GRID
# =========================================================

def draw_grid():

    grid_x = GAME_X + 20

    grid_y = GAME_Y + 130

    for row in range(ROWS):

        for col in range(COLS):

            rect = pygame.Rect(

                grid_x
                +
                col * CELL_SIZE,

                grid_y
                +
                row * CELL_SIZE,

                CELL_SIZE,

                CELL_SIZE
            )

            pygame.draw.rect(
                screen,
                (24, 33, 50),
                rect
            )

            # =================================================
            # A* PATH
            # =================================================

            if (
                (row, col) in ai_path

                and
                (row, col)
                not in obstacles

                and
                (row, col)
                != tuple(ai_position)

                and
                (row, col)
                != tuple(player_position)
            ):

                overlay = pygame.Surface(
                    (
                        CELL_SIZE,
                        CELL_SIZE
                    ),
                    pygame.SRCALPHA
                )

                overlay.fill(
                    (45, 200, 230, 70)
                )

                screen.blit(
                    overlay,
                    rect
                )

            # =================================================
            # GRID BORDER
            # =================================================

            pygame.draw.rect(
                screen,
                GRID_COLOR,
                rect,
                1
            )

            # =================================================
            # OBSTACLE
            # =================================================

            if (
                row,
                col
            ) in obstacles:

                obstacle = rect.inflate(
                    -8,
                    -8
                )

                pygame.draw.rect(
                    screen,
                    OBSTACLE_COLOR,
                    obstacle,
                    border_radius=7
                )

                pygame.draw.rect(
                    screen,
                    OBSTACLE_BORDER,
                    obstacle,
                    2,
                    border_radius=7
                )


# =========================================================
# PLAYER
# =========================================================

def draw_player():

    x, y = grid_to_pixel(
        player_position
    )

    pygame.draw.circle(
        screen,
        (25, 90, 80),
        (x, y),
        25
    )

    if player_defending:

        pygame.draw.circle(
            screen,
            CYAN,
            (x, y),
            29,
            3
        )

        draw_text(
            "DEFEND",
            FONT_SMALL,
            CYAN,
            x - 30,
            y - 45
        )

    pygame.draw.circle(
        screen,
        PLAYER_COLOR,
        (x, y),
        17
    )

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

    pygame.draw.circle(
        screen,
        (100, 35, 45),
        (x, y),
        25
    )

    if ai_defending:

        pygame.draw.circle(
            screen,
            YELLOW,
            (x, y),
            29,
            3
        )

        draw_text(
            "DEFEND",
            FONT_SMALL,
            YELLOW,
            x - 30,
            y - 45
        )

    pygame.draw.circle(
        screen,
        AI_COLOR,
        (x, y),
        17
    )

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
# AI BRAIN
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
        "A* + Minimax",
        FONT_NORMAL,
        TEXT,
        835,
        202
    )


    # Current Action

    draw_text(
        "Current Action",
        FONT_SMALL,
        TEXT_MUTED,
        980,
        180
    )

    draw_text(
        ai_current_action,
        FONT_NORMAL,
        YELLOW,
        980,
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
        str(SEARCH_DEPTH),
        FONT_NORMAL,
        TEXT,
        835,
        262
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
        str(minimax_nodes),
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

    if game_over:

        status = "BATTLE ENDED"

        color = RED

    elif current_turn == PLAYER_TURN:

        status = "YOUR TURN"

        color = GREEN

    else:

        status = "AI THINKING"

        color = CYAN

    centered_text(
        status,
        FONT_SMALL,
        color,
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
# BOTTOM BAR
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
        "F  Defend",
        FONT_SMALL,
        TEXT_MUTED,
        650,
        699
    )

    draw_text(
        "R  Restart",
        FONT_SMALL,
        TEXT_MUTED,
        800,
        699
    )

    draw_text(
        "ESC  Quit",
        FONT_SMALL,
        TEXT_MUTED,
        900,
        699
    )


# =========================================================
# VALID POSITION
# =========================================================

def is_valid_position(position):

    row, col = position

    if row < 0 or row >= ROWS:

        return False

    if col < 0 or col >= COLS:

        return False

    if position in obstacles:

        return False

    if position == tuple(ai_position):

        return False

    return True


# =========================================================
# CALCULATE A*
# =========================================================

def calculate_ai_path():

    global ai_path
    global ai_nodes_explored

    targets = []

    player = tuple(
        player_position
    )

    directions = [

        (-1, 0),

        (1, 0),

        (0, -1),

        (0, 1)
    ]

    for dr, dc in directions:

        target = (

            player[0] + dr,

            player[1] + dc
        )

        if target[0] < 0:
            continue

        if target[0] >= ROWS:
            continue

        if target[1] < 0:
            continue

        if target[1] >= COLS:
            continue

        if target in obstacles:
            continue

        targets.append(
            target
        )

    best_path = []

    best_nodes = 0

    for target in targets:

        path, nodes = a_star(

            tuple(ai_position),

            target,

            ROWS,

            COLS,

            obstacles
        )

        if path:

            if (
                not best_path
                or
                len(path)
                <
                len(best_path)
            ):

                best_path = path

                best_nodes = nodes

    ai_path = best_path

    ai_nodes_explored = best_nodes


# =========================================================
# PLAYER MOVE
# =========================================================

def move_player(
    dr,
    dc
):

    global current_turn
    global ai_thinking
    global ai_turn_start

    if current_turn != PLAYER_TURN:
        return

    new_position = (

        player_position[0] + dr,

        player_position[1] + dc
    )

    if not is_valid_position(
        new_position
    ):

        add_log(
            "Movement blocked."
        )

        return

    player_position[0] = new_position[0]

    player_position[1] = new_position[1]

    player_defending_off()

    add_log(
        "Player moved."
    )

    calculate_ai_path()

    current_turn = AI_TURN

    ai_thinking = True

    ai_turn_start = pygame.time.get_ticks()


# =========================================================
# PLAYER DEFENDING OFF
# =========================================================

def player_defending_off():

    global player_defending

    player_defending = False


# =========================================================
# ATTACK EFFECT
# =========================================================

def create_attack_effect(
    attacker,
    target
):

    global attack_effect

    attack_effect = {

        "start":
            grid_to_pixel(attacker),

        "end":
            grid_to_pixel(target),

        "time":
            pygame.time.get_ticks()
    }


# =========================================================
# DAMAGE EFFECT
# =========================================================

def create_damage_effect(
    position,
    damage
):

    x, y = grid_to_pixel(
        position
    )

    damage_effects.append({

        "x": x,

        "y": y,

        "damage": damage,

        "time":
            pygame.time.get_ticks()
    })


# =========================================================
# DRAW ATTACK
# =========================================================

def draw_attack_effect():

    global attack_effect

    if attack_effect is None:

        return

    elapsed = (
        pygame.time.get_ticks()
        -
        attack_effect["time"]
    )

    if elapsed > 250:

        attack_effect = None

        return

    start_x, start_y = (
        attack_effect["start"]
    )

    end_x, end_y = (
        attack_effect["end"]
    )

    progress = elapsed / 250

    x = int(
        start_x
        +
        (
            end_x
            -
            start_x
        )
        *
        progress
    )

    y = int(
        start_y
        +
        (
            end_y
            -
            start_y
        )
        *
        progress
    )

    pygame.draw.line(
        screen,
        WHITE,
        (
            start_x,
            start_y
        ),
        (
            x,
            y
        ),
        6
    )

    pygame.draw.circle(
        screen,
        YELLOW,
        (
            x,
            y
        ),
        10
    )


# =========================================================
# DRAW DAMAGE
# =========================================================

def draw_damage_effects():

    now = pygame.time.get_ticks()

    remaining = []

    for effect in damage_effects:

        elapsed = (
            now
            -
            effect["time"]
        )

        if elapsed > 800:

            continue

        y = (
            effect["y"]
            -
            int(elapsed * 0.05)
        )

        font = pygame.font.SysFont(
            "arial",
            24,
            bold=True
        )

        surface = font.render(
            f"-{effect['damage']}",
            True,
            WHITE
        )

        screen.blit(
            surface,
            surface.get_rect(
                center=(
                    effect["x"],
                    y
                )
            )
        )

        remaining.append(
            effect
        )

    damage_effects.clear()

    damage_effects.extend(
        remaining
    )


# =========================================================
# PLAYER ATTACK
# =========================================================

def player_attack():

    global ai_hp
    global ai_defending
    global current_turn
    global ai_thinking
    global game_over
    global winner
    global ai_turn_start

    if current_turn != PLAYER_TURN:

        return

    distance = get_distance(
        player_position,
        ai_position
    )

    if distance > ATTACK_RANGE:

        add_log(
            "Attack failed → Out of range."
        )

        return

    create_attack_effect(
        player_position,
        ai_position
    )

    damage = PLAYER_DAMAGE

    if ai_defending:

        damage //= 2

        ai_defending = False

        add_log(
            "AI defense reduced damage."
        )

    ai_hp -= damage

    ai_hp = max(
        0,
        ai_hp
    )

    create_damage_effect(
        ai_position,
        damage
    )

    add_log(
        f"Player attacked → -{damage} HP"
    )

    if ai_hp <= 0:

        game_over = True

        winner = "PLAYER"

        add_log(
            "PLAYER WINS!"
        )

        return

    current_turn = AI_TURN

    ai_thinking = True

    ai_turn_start = pygame.time.get_ticks()


# =========================================================
# PLAYER DEFEND
# =========================================================

def player_defend():

    global player_defending
    global current_turn
    global ai_thinking
    global ai_turn_start

    if current_turn != PLAYER_TURN:

        return

    player_defending = True

    add_log(
        "Player activated defense."
    )

    current_turn = AI_TURN

    ai_thinking = True

    ai_turn_start = pygame.time.get_ticks()


# =========================================================
# AI ATTACK
# =========================================================

def ai_attack():

    global player_hp
    global player_defending
    global ai_defending
    global current_turn
    global ai_thinking
    global game_over
    global winner
    global round_number

    create_attack_effect(
        ai_position,
        player_position
    )

    damage = AI_DAMAGE

    if player_defending:

        damage //= 2

        player_defending = False

        add_log(
            "Player defense reduced damage."
        )

    player_hp -= damage

    player_hp = max(
        0,
        player_hp
    )

    create_damage_effect(
        player_position,
        damage
    )

    add_log(
        f"AI attacked → -{damage} HP"
    )

    if player_hp <= 0:

        game_over = True

        winner = "AI"

        ai_thinking = False

        add_log(
            "AI WINS!"
        )

        return

    current_turn = PLAYER_TURN

    ai_thinking = False

    round_number += 1

    add_log(
        "Your turn."
    )


# =========================================================
# AI DEFEND
# =========================================================

def ai_defend():

    global ai_defending
    global current_turn
    global ai_thinking
    global round_number

    ai_defending = True

    add_log(
        "AI activated defense."
    )

    current_turn = PLAYER_TURN

    ai_thinking = False

    round_number += 1

    add_log(
        "Your turn."
    )


# =========================================================
# AI MOVE
# =========================================================

def ai_move():

    global current_turn
    global ai_thinking
    global round_number

    calculate_ai_path()

    if len(ai_path) > 1:

        next_position = ai_path[1]

        ai_position[0] = next_position[0]

        ai_position[1] = next_position[1]

        add_log(
            "AI moved using A*."
        )

    else:

        add_log(
            "AI could not find a path."
        )

    current_turn = PLAYER_TURN

    ai_thinking = False

    round_number += 1

    add_log(
        "Your turn."
    )


# =========================================================
# MINIMAX AI DECISION
# =========================================================

def ai_make_decision():

    global minimax_nodes

    global minimax_score

    global ai_current_action

    state = {

        "ai_hp": ai_hp,

        "player_hp": player_hp,

        "ai_position":
            list(ai_position),

        "player_position":
            list(player_position),

        "ai_defending":
            ai_defending,

        "player_defending":
            player_defending
    }

    action, score, nodes = get_best_action(

        state,

        SEARCH_DEPTH
    )

    ai_current_action = action

    minimax_score = score

    minimax_nodes = nodes

    add_log(
        f"Minimax → {action}"
    )

    return action


# =========================================================
# AI TURN
# =========================================================

def run_ai_turn():

    action = ai_make_decision()

    # =====================================================
    # ATTACK
    # =====================================================

    if action == "ATTACK":

        ai_attack()

    # =====================================================
    # DEFEND
    # =====================================================

    elif action == "DEFEND":

        ai_defend()

    # =====================================================
    # MOVE
    # =====================================================

    else:

        ai_move()


# =========================================================
# PLAYER INPUT
# =========================================================

def handle_input(key):

    if game_over:

        return

    if current_turn != PLAYER_TURN:

        return

    if key in (
        pygame.K_w,
        pygame.K_UP
    ):

        move_player(
            -1,
            0
        )

    elif key in (
        pygame.K_s,
        pygame.K_DOWN
    ):

        move_player(
            1,
            0
        )

    elif key in (
        pygame.K_a,
        pygame.K_LEFT
    ):

        move_player(
            0,
            -1
        )

    elif key in (
        pygame.K_d,
        pygame.K_RIGHT
    ):

        move_player(
            0,
            1
        )

    elif key == pygame.K_SPACE:

        player_attack()

    elif key == pygame.K_f:

        player_defend()


# =========================================================
# RESTART
# =========================================================

def restart_game():

    global player_position
    global ai_position

    global player_hp
    global ai_hp

    global player_defending
    global ai_defending

    global current_turn
    global round_number

    global game_over
    global winner

    global ai_thinking

    global ai_path
    global ai_nodes_explored

    global minimax_nodes
    global minimax_score

    global ai_current_action

    global battle_logs

    player_position = [2, 2]

    ai_position = [5, 9]

    player_hp = 100

    ai_hp = 100

    player_defending = False

    ai_defending = False

    current_turn = PLAYER_TURN

    round_number = 1

    game_over = False

    winner = None

    ai_thinking = False

    ai_path = []

    ai_nodes_explored = 0

    minimax_nodes = 0

    minimax_score = 0

    ai_current_action = "WAITING"

    battle_logs = [

        "Battle initialized.",

        "Player deployed.",

        "AI opponent deployed.",

        "Your turn."
    ]

    calculate_ai_path()


# =========================================================
# GAME OVER
# =========================================================

def draw_game_over():

    if not game_over:

        return

    overlay = pygame.Surface(
        (
            SCREEN_WIDTH,
            SCREEN_HEIGHT
        ),
        pygame.SRCALPHA
    )

    overlay.fill(
        (5, 8, 15, 190)
    )

    screen.blit(
        overlay,
        (0, 0)
    )

    panel = pygame.Rect(
        300,
        235,
        600,
        280
    )

    pygame.draw.rect(
        screen,
        PANEL,
        panel,
        border_radius=18
    )

    color = (
        PLAYER_COLOR
        if winner == "PLAYER"
        else RED
    )

    pygame.draw.rect(
        screen,
        color,
        panel,
        2,
        border_radius=18
    )

    title = (
        "VICTORY!"
        if winner == "PLAYER"
        else "DEFEATED"
    )

    centered_text(
        title,
        FONT_HUGE,
        color,
        pygame.Rect(
            350,
            290,
            500,
            60
        )
    )

    message = (

        "You defeated the AI opponent."

        if winner == "PLAYER"

        else

        "The AI defeated you."
    )

    centered_text(
        message,
        FONT_NORMAL,
        TEXT,
        pygame.Rect(
            350,
            370,
            500,
            40
        )
    )

    centered_text(
        "Press R to restart",
        FONT_NORMAL,
        TEXT_MUTED,
        pygame.Rect(
            350,
            430,
            500,
            40
        )
    )


# =========================================================
# INITIAL PATH
# =========================================================

calculate_ai_path()


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

            if event.key == pygame.K_ESCAPE:

                running = False

            elif event.key == pygame.K_r:

                restart_game()

            else:

                handle_input(
                    event.key
                )


    # =====================================================
    # AI TURN
    # =====================================================

    if (
        current_turn == AI_TURN
        and ai_thinking
        and not game_over
    ):

        now = pygame.time.get_ticks()

        if now - ai_turn_start > 700:

            run_ai_turn()


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

    draw_attack_effect()

    draw_damage_effects()

    draw_game_over()

    pygame.display.flip()

    clock.tick(60)


# =========================================================
# EXIT
# =========================================================

pygame.quit()

sys.exit()