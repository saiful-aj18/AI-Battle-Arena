import pygame
import sys
import time

from ai.astar import a_star
from ai.minimax import get_best_action


# =========================================================
# INITIALIZATION
# =========================================================

pygame.init()

WIDTH = 1200
HEIGHT = 750

SCREEN = pygame.display.set_mode(
    (WIDTH, HEIGHT)
)

pygame.display.set_caption(
    "AI Battle Arena - A* + Minimax"
)

CLOCK = pygame.time.Clock()


# =========================================================
# COLORS
# =========================================================

BG_COLOR = (10, 15, 25)
PANEL_COLOR = (18, 25, 38)
PANEL_LIGHT = (25, 34, 50)

GRID_COLOR = (45, 58, 78)
GRID_ACTIVE = (55, 75, 100)

WHITE = (240, 245, 250)
GRAY = (150, 160, 175)

CYAN = (40, 220, 240)
GREEN = (70, 220, 130)
RED = (245, 80, 90)
YELLOW = (255, 205, 70)
ORANGE = (255, 145, 60)

BLUE = (70, 130, 255)
PURPLE = (170, 100, 240)

BLACK = (5, 8, 15)


# =========================================================
# FONTS
# =========================================================

FONT_SMALL = pygame.font.SysFont(
    "arial",
    14
)

FONT_NORMAL = pygame.font.SysFont(
    "arial",
    17
)

FONT_MEDIUM = pygame.font.SysFont(
    "arial",
    20,
    bold=True
)

FONT_LARGE = pygame.font.SysFont(
    "arial",
    28,
    bold=True
)

FONT_TITLE = pygame.font.SysFont(
    "arial",
    30,
    bold=True
)


# =========================================================
# GRID SETTINGS
# =========================================================

ROWS = 8
COLS = 12

CELL_SIZE = 55

GRID_X = 45
GRID_Y = 130

GRID_WIDTH = COLS * CELL_SIZE
GRID_HEIGHT = ROWS * CELL_SIZE


# =========================================================
# GAME SETTINGS
# =========================================================

MAX_HP = 100

PLAYER_DAMAGE = 20
AI_DAMAGE = 15

ATTACK_RANGE = 1

AI_DEPTH = 3

AI_THINK_DELAY = 700


# =========================================================
# OBSTACLES
# =========================================================

OBSTACLES = {
    (1, 4),
    (1, 5),

    (2, 4),

    (3, 7),
    (3, 8),

    (4, 2),
    (4, 3),

    (5, 7),

    (6, 5),
    (6, 6),
    (6, 8),

    (7, 8),
    (7, 9),
    
}


# =========================================================
# GAME STATE
# =========================================================

player_position = (2, 2)
ai_position = (5, 9)

player_hp = MAX_HP
ai_hp = MAX_HP

player_defending = False
ai_defending = False

turn = "PLAYER"

game_over = False

winner = None

ai_thinking = False

ai_action_text = "Waiting..."

battle_log = []


# =========================================================
# AI METRICS
# =========================================================

astar_path = []

astar_nodes = 0
astar_path_cost = 0
astar_time = 0.0

minimax_nodes = 0
minimax_pruned = 0
minimax_time = 0.0

minimax_score = 0

search_depth = AI_DEPTH


# =========================================================
# ANIMATION STATE
# =========================================================

attack_animation = False
attack_animation_start = 0

attack_from = None
attack_to = None

damage_number = None
damage_number_start = 0
damage_number_position = None

shield_animation = False
shield_animation_start = 0

MOVE_ANIMATION_TIME = 180


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def add_log(message):

    battle_log.append(message)

    if len(battle_log) > 8:
        battle_log.pop(0)


def reset_metrics():

    global astar_path
    global astar_nodes
    global astar_path_cost
    global astar_time

    global minimax_nodes
    global minimax_pruned
    global minimax_time
    global minimax_score

    astar_path = []

    astar_nodes = 0
    astar_path_cost = 0
    astar_time = 0.0

    minimax_nodes = 0
    minimax_pruned = 0
    minimax_time = 0.0
    minimax_score = 0


def reset_game():

    global player_position
    global ai_position

    global player_hp
    global ai_hp

    global player_defending
    global ai_defending

    global turn
    global game_over
    global winner

    global ai_thinking
    global ai_action_text

    global battle_log

    global attack_animation
    global damage_number
    global shield_animation

    player_position = (2, 2)
    ai_position = (5, 9)

    player_hp = MAX_HP
    ai_hp = MAX_HP

    player_defending = False
    ai_defending = False

    turn = "PLAYER"

    game_over = False
    winner = None

    ai_thinking = False

    ai_action_text = "Waiting..."

    battle_log = []

    attack_animation = False
    damage_number = None
    shield_animation = False

    reset_metrics()

    add_log("Battle started.")
    add_log("Your turn. Choose an action.")


# =========================================================
# GRID HELPERS
# =========================================================

def cell_rect(position):

    row, col = position

    return pygame.Rect(
        GRID_X + col * CELL_SIZE,
        GRID_Y + row * CELL_SIZE,
        CELL_SIZE,
        CELL_SIZE
    )


def cell_center(position):

    rect = cell_rect(position)

    return rect.center


def is_inside_grid(position):

    row, col = position

    return (
        0 <= row < ROWS
        and
        0 <= col < COLS
    )


def get_adjacent_positions(position):

    row, col = position

    directions = [
        (-1, 0),
        (1, 0),
        (0, -1),
        (0, 1),
    ]

    positions = []

    for dr, dc in directions:

        new_position = (
            row + dr,
            col + dc
        )

        if is_inside_grid(new_position):
            positions.append(new_position)

    return positions


# =========================================================
# DISTANCE
# =========================================================

def get_distance(a, b):

    return (
        abs(a[0] - b[0])
        +
        abs(a[1] - b[1])
    )


def can_attack(attacker, target):

    return (
        get_distance(
            attacker,
            target
        )
        <= ATTACK_RANGE
    )


# =========================================================
# DRAW TEXT
# =========================================================

def draw_text(
    text,
    position,
    font=FONT_NORMAL,
    color=WHITE
):

    surface = font.render(
        str(text),
        True,
        color
    )

    SCREEN.blit(
        surface,
        position
    )


# =========================================================
# DRAW CENTERED TEXT
# =========================================================

def draw_center_text(
    text,
    center,
    font=FONT_NORMAL,
    color=WHITE
):

    surface = font.render(
        str(text),
        True,
        color
    )

    rect = surface.get_rect(
        center=center
    )

    SCREEN.blit(
        surface,
        rect
    )


# =========================================================
# DRAW PANEL
# =========================================================

def draw_panel(
    rect,
    title=None
):

    pygame.draw.rect(
        SCREEN,
        PANEL_COLOR,
        rect,
        border_radius=12
    )

    pygame.draw.rect(
        SCREEN,
        (40, 52, 70),
        rect,
        width=1,
        border_radius=12
    )

    if title:

        draw_text(
            title,
            (
                rect.x + 16,
                rect.y + 12
            ),
            FONT_MEDIUM,
            WHITE
        )


# =========================================================
# HP BAR
# =========================================================

def draw_hp_bar(
    x,
    y,
    width,
    height,
    hp,
    max_hp,
    label,
    bar_color
):

    draw_text(
        f"{label}: {hp}/{max_hp}",
        (x, y - 24),
        FONT_NORMAL,
        WHITE
    )

    background = pygame.Rect(
        x,
        y,
        width,
        height
    )

    pygame.draw.rect(
        SCREEN,
        (45, 50, 60),
        background,
        border_radius=6
    )

    ratio = max(
        0,
        min(
            hp / max_hp,
            1
        )
    )

    foreground = pygame.Rect(
        x,
        y,
        int(width * ratio),
        height
    )

    pygame.draw.rect(
        SCREEN,
        bar_color,
        foreground,
        border_radius=6
    )

    pygame.draw.rect(
        SCREEN,
        (80, 90, 105),
        background,
        width=1,
        border_radius=6
    )


# =========================================================
# DRAW GRID
# =========================================================

def draw_grid():

    for row in range(ROWS):

        for col in range(COLS):

            position = (
                row,
                col
            )

            rect = cell_rect(
                position
            )

            if position in OBSTACLES:

                pygame.draw.rect(
                    SCREEN,
                    (35, 40, 52),
                    rect,
                    border_radius=5
                )

                pygame.draw.rect(
                    SCREEN,
                    (70, 78, 95),
                    rect,
                    width=2,
                    border_radius=5
                )

                draw_center_text(
                    "■",
                    rect.center,
                    FONT_NORMAL,
                    (90, 100, 115)
                )

            else:

                pygame.draw.rect(
                    SCREEN,
                    (20, 28, 42),
                    rect,
                    border_radius=3
                )

                pygame.draw.rect(
                    SCREEN,
                    GRID_COLOR,
                    rect,
                    width=1
                )


# =========================================================
# DRAW A* PATH
# =========================================================

def draw_astar_path():

    if not astar_path:
        return

    for index, position in enumerate(astar_path):

        if position == ai_position:
            continue

        if position == player_position:
            continue

        rect = cell_rect(position)

        overlay = pygame.Surface(
            (
                CELL_SIZE - 8,
                CELL_SIZE - 8
            ),
            pygame.SRCALPHA
        )

        overlay.fill(
            (40, 220, 240, 65)
        )

        SCREEN.blit(
            overlay,
            (
                rect.x + 4,
                rect.y + 4
            )
        )

        pygame.draw.circle(
            SCREEN,
            CYAN,
            rect.center,
            4
        )


# =========================================================
# DRAW RANGE
# =========================================================

def draw_attack_range():

    if turn != "PLAYER":
        return

    if game_over:
        return

    for position in get_adjacent_positions(
        player_position
    ):

        if position in OBSTACLES:
            continue

        rect = cell_rect(
            position
        )

        pygame.draw.rect(
            SCREEN,
            (255, 205, 70, 35),
            rect,
            width=2,
            border_radius=5
        )


# =========================================================
# DRAW PLAYER
# =========================================================

def draw_player():

    center = cell_center(
        player_position
    )

    pygame.draw.circle(
        SCREEN,
        BLUE,
        center,
        19
    )

    pygame.draw.circle(
        SCREEN,
        WHITE,
        center,
        19,
        width=2
    )

    draw_center_text(
        "P",
        center,
        FONT_MEDIUM,
        WHITE
    )


# =========================================================
# DRAW AI
# =========================================================

def draw_ai():

    center = cell_center(
        ai_position
    )

    pygame.draw.circle(
        SCREEN,
        RED,
        center,
        19
    )

    pygame.draw.circle(
        SCREEN,
        WHITE,
        center,
        19,
        width=2
    )

    draw_center_text(
        "AI",
        center,
        FONT_SMALL,
        WHITE
    )


# =========================================================
# DRAW SHIELD
# =========================================================

def draw_shield():

    global shield_animation

    if not shield_animation:
        return

    elapsed = (
        pygame.time.get_ticks()
        -
        shield_animation_start
    )

    if elapsed > 650:

        shield_animation = False

        return

    if player_defending:

        center = cell_center(
            player_position
        )

    else:

        center = cell_center(
            ai_position
        )

    radius = 28 + int(
        4 * (elapsed / 650)
    )

    pygame.draw.circle(
        SCREEN,
        CYAN,
        center,
        radius,
        width=3
    )

    pygame.draw.circle(
        SCREEN,
        (100, 220, 255),
        center,
        radius - 6,
        width=1
    )


# =========================================================
# DRAW ATTACK ANIMATION
# =========================================================

def draw_attack_animation():

    global attack_animation

    if not attack_animation:
        return

    elapsed = (
        pygame.time.get_ticks()
        -
        attack_animation_start
    )

    duration = 300

    if elapsed > duration:

        attack_animation = False

        return

    if not attack_from or not attack_to:
        return

    start = cell_center(
        attack_from
    )

    end = cell_center(
        attack_to
    )

    progress = elapsed / duration

    current_x = (
        start[0]
        +
        (end[0] - start[0])
        * progress
    )

    current_y = (
        start[1]
        +
        (end[1] - start[1])
        * progress
    )

    current = (
        int(current_x),
        int(current_y)
    )

    pygame.draw.line(
        SCREEN,
        YELLOW,
        start,
        current,
        width=5
    )

    pygame.draw.circle(
        SCREEN,
        YELLOW,
        current,
        12
    )

    pygame.draw.circle(
        SCREEN,
        WHITE,
        current,
        5
    )


# =========================================================
# DRAW DAMAGE NUMBER
# =========================================================

def draw_damage_number():

    global damage_number

    if damage_number is None:
        return

    elapsed = (
        pygame.time.get_ticks()
        -
        damage_number_start
    )

    if elapsed > 900:

        damage_number = None

        return

    x, y = damage_number_position

    y -= int(
        elapsed * 0.04
    )

    alpha = max(
        0,
        255 - int(
            elapsed * 0.28
        )
    )

    text_surface = FONT_LARGE.render(
        f"-{damage_number}",
        True,
        YELLOW
    )

    text_surface.set_alpha(
        alpha
    )

    rect = text_surface.get_rect(
        center=(x, y)
    )

    SCREEN.blit(
        text_surface,
        rect
    )


# =========================================================
# ATTACK EFFECT
# =========================================================

def start_attack_animation(
    attacker,
    target,
    damage
):

    global attack_animation
    global attack_animation_start

    global attack_from
    global attack_to

    global damage_number
    global damage_number_start
    global damage_number_position

    attack_animation = True

    attack_animation_start = (
        pygame.time.get_ticks()
    )

    attack_from = attacker
    attack_to = target

    damage_number = damage

    damage_number_start = (
        pygame.time.get_ticks()
    )

    damage_number_position = cell_center(
        target
    )


# =========================================================
# DEFEND EFFECT
# =========================================================

def start_shield_animation():

    global shield_animation
    global shield_animation_start

    shield_animation = True

    shield_animation_start = (
        pygame.time.get_ticks()
    )


# =========================================================
# PLAYER MOVE
# =========================================================

def move_player(
    dr,
    dc
):

    global player_position

    if turn != "PLAYER":
        return

    if game_over:
        return

    new_position = (
        player_position[0] + dr,
        player_position[1] + dc
    )

    if not is_inside_grid(
        new_position
    ):
        return

    if new_position in OBSTACLES:
        add_log(
            "Cannot move through obstacle."
        )

        return

    if new_position == ai_position:

        add_log(
            "Cannot move onto AI."
        )

        return

    player_position = new_position

    add_log(
        f"Player moved to {player_position}."
    )

    end_player_turn()


# =========================================================
# PLAYER ATTACK
# =========================================================

def player_attack():

    global ai_hp
    global ai_defending

    if turn != "PLAYER":
        return

    if game_over:
        return

    if not can_attack(
        player_position,
        ai_position
    ):

        add_log(
            "AI is out of attack range."
        )

        return

    damage = PLAYER_DAMAGE

    if ai_defending:

        damage = int(
            damage * 0.5
        )

        ai_defending = False

        add_log(
            "AI shield reduced damage."
        )

    ai_hp = max(
        0,
        ai_hp - damage
    )

    start_attack_animation(
        player_position,
        ai_position,
        damage
    )

    add_log(
        f"Player attacked AI for {damage} damage."
    )

    check_game_over()

    if not game_over:

        end_player_turn()


# =========================================================
# PLAYER DEFEND
# =========================================================

def player_defend():

    global player_defending

    if turn != "PLAYER":
        return

    if game_over:
        return

    player_defending = True

    start_shield_animation()

    add_log(
        "Player is defending."
    )

    end_player_turn()


# =========================================================
# END PLAYER TURN
# =========================================================

def end_player_turn():

    global turn
    global ai_thinking

    if game_over:
        return

    turn = "AI"

    ai_thinking = True


# =========================================================
# BUILD AI STATE
# =========================================================

def build_ai_state():

    return {
        "ai_position": ai_position,
        "player_position": player_position,

        "ai_hp": ai_hp,
        "player_hp": player_hp,

        "ai_defending": ai_defending,
        "player_defending": player_defending,

        "rows": ROWS,
        "cols": COLS,

        "obstacles": set(OBSTACLES),
    }


# =========================================================
# FIND A* PATH
# =========================================================

def calculate_astar():

    global astar_path
    global astar_nodes
    global astar_path_cost
    global astar_time

    # AI needs to reach a cell adjacent
    # to the player, not player's cell.

    possible_goals = []

    for position in get_adjacent_positions(
        player_position
    ):

        if position in OBSTACLES:
            continue

        if position == ai_position:
            continue

        possible_goals.append(
            position
        )

    best_path = []
    best_nodes = 0

    start_time = time.perf_counter()

    # Player cell is treated as obstacle.

    path_obstacles = set(
        OBSTACLES
    )

    path_obstacles.add(
        player_position
    )

    for goal in possible_goals:

        path, nodes = a_star(
            ai_position,
            goal,
            ROWS,
            COLS,
            path_obstacles
        )

        if path:

            if not best_path:

                best_path = path
                best_nodes = nodes

            elif len(path) < len(best_path):

                best_path = path
                best_nodes = nodes

    end_time = time.perf_counter()

    astar_path = best_path

    astar_nodes = best_nodes

    if best_path:

        astar_path_cost = (
            len(best_path) - 1
        )

    else:

        astar_path_cost = 0

    astar_time = (
        end_time - start_time
    ) * 1000


# =========================================================
# APPLY AI ACTION
# =========================================================

def execute_ai_action(
    action
):

    global ai_position
    global player_hp
    global player_defending
    global ai_defending

    global ai_action_text

    # -----------------------------------------------------
    # ATTACK
    # -----------------------------------------------------

    if action == "ATTACK":

        if not can_attack(
            ai_position,
            player_position
        ):

            add_log(
                "AI tried to attack but player is out of range."
            )

            return

        damage = AI_DAMAGE

        if player_defending:

            damage = int(
                damage * 0.5
            )

            player_defending = False

            add_log(
                "Player shield reduced AI damage."
            )

        player_hp = max(
            0,
            player_hp - damage
        )

        start_attack_animation(
            ai_position,
            player_position,
            damage
        )

        add_log(
            f"AI attacked Player for {damage} damage."
        )

    # -----------------------------------------------------
    # DEFEND
    # -----------------------------------------------------

    elif action == "DEFEND":

        ai_defending = True

        start_shield_animation()

        add_log(
            "AI is defending."
        )

    # -----------------------------------------------------
    # MOVE
    # -----------------------------------------------------

    elif (
        isinstance(action, tuple)
        and
        action[0] == "MOVE"
    ):

        new_position = action[1]

        if new_position in OBSTACLES:

            add_log(
                "AI cannot move through obstacle."
            )

            return

        if new_position == player_position:

            add_log(
                "AI cannot move onto Player."
            )

            return

        if is_inside_grid(
            new_position
        ):

            ai_position = new_position

            add_log(
                f"AI moved to {ai_position}."
            )


# =========================================================
# AI TURN
# =========================================================

def run_ai_turn():

    global turn
    global ai_thinking

    global ai_action_text

    global minimax_nodes
    global minimax_pruned
    global minimax_time
    global minimax_score

    if game_over:
        return

    # -----------------------------------------------------
    # A* SEARCH
    # -----------------------------------------------------

    calculate_astar()

    # -----------------------------------------------------
    # MINIMAX
    # -----------------------------------------------------

    state = build_ai_state()

    start_time = time.perf_counter()

    (
        best_action,
        best_score,
        nodes,
        pruned
    ) = get_best_action(
        state,
        depth=AI_DEPTH
    )

    end_time = time.perf_counter()

    minimax_time = (
        end_time - start_time
    ) * 1000

    minimax_nodes = nodes
    minimax_pruned = pruned
    minimax_score = best_score

    ai_action_text = format_ai_action(
        best_action
    )

    # -----------------------------------------------------
    # EXECUTE ACTION
    # -----------------------------------------------------

    execute_ai_action(
        best_action
    )

    check_game_over()

    if not game_over:

        turn = "PLAYER"

        ai_thinking = False

        add_log(
            "Your turn."
        )


# =========================================================
# FORMAT AI ACTION
# =========================================================

def format_ai_action(action):

    if action == "ATTACK":

        return "ATTACK"

    if action == "DEFEND":

        return "DEFEND"

    if (
        isinstance(action, tuple)
        and
        action[0] == "MOVE"
    ):

        return (
            f"MOVE → {action[1]}"
        )

    return str(action)


# =========================================================
# GAME OVER
# =========================================================

def check_game_over():

    global game_over
    global winner
    global ai_thinking

    if player_hp <= 0:

        player_hp_value = 0

        game_over = True

        winner = "AI"

        ai_thinking = False

        add_log(
            "AI wins the battle."
        )

        return

    if ai_hp <= 0:

        game_over = True

        winner = "PLAYER"

        ai_thinking = False

        add_log(
            "Player wins the battle."
        )

        return


# =========================================================
# AI BRAIN PANEL
# =========================================================

def draw_ai_brain_panel():

    rect = pygame.Rect(
        735,
        90,
        420,
        340
    )

    draw_panel(
        rect,
        "AI BRAIN"
    )

    y = rect.y + 55

    draw_text(
        "Algorithms",
        (rect.x + 18, y),
        FONT_SMALL,
        GRAY
    )

    draw_text(
        "A* + Minimax",
        (rect.x + 180, y),
        FONT_NORMAL,
        CYAN
    )

    y += 30

    draw_text(
        "Alpha-Beta",
        (rect.x + 18, y),
        FONT_SMALL,
        GRAY
    )

    draw_text(
        "Enabled",
        (rect.x + 180, y),
        FONT_NORMAL,
        GREEN
    )

    y += 30

    draw_text(
        "Search Depth",
        (rect.x + 18, y),
        FONT_SMALL,
        GRAY
    )

    draw_text(
        str(AI_DEPTH),
        (rect.x + 180, y),
        FONT_NORMAL,
        WHITE
    )

    y += 30

    draw_text(
        "Current Action",
        (rect.x + 18, y),
        FONT_SMALL,
        GRAY
    )

    draw_text(
        ai_action_text,
        (rect.x + 180, y),
        FONT_NORMAL,
        YELLOW
    )

    y += 35

    # A* section

    draw_text(
        "A* Search",
        (rect.x + 18, y),
        FONT_MEDIUM,
        CYAN
    )

    y += 28

    draw_text(
        f"Nodes: {astar_nodes}",
        (rect.x + 18, y),
        FONT_SMALL,
        WHITE
    )

    draw_text(
        f"Path Cost: {astar_path_cost}",
        (rect.x + 190, y),
        FONT_SMALL,
        WHITE
    )

    y += 25

    draw_text(
        f"Time: {astar_time:.3f} ms",
        (rect.x + 18, y),
        FONT_SMALL,
        WHITE
    )

    y += 32

    # Minimax section

    draw_text(
        "Minimax + Alpha-Beta",
        (rect.x + 18, y),
        FONT_MEDIUM,
        PURPLE
    )

    y += 28

    draw_text(
        f"Nodes: {minimax_nodes}",
        (rect.x + 18, y),
        FONT_SMALL,
        WHITE
    )

    draw_text(
        f"Pruned: {minimax_pruned}",
        (rect.x + 190, y),
        FONT_SMALL,
        GREEN
    )

    y += 25

    draw_text(
        f"Time: {minimax_time:.3f} ms",
        (rect.x + 18, y),
        FONT_SMALL,
        WHITE
    )

    draw_text(
        f"Score: {minimax_score}",
        (rect.x + 190, y),
        FONT_SMALL,
        WHITE
    )


# =========================================================
# BATTLE LOG
# =========================================================

def draw_battle_log():

    rect = pygame.Rect(
        735,
        440,
        420,
        165
    )

    draw_panel(
        rect,
        "BATTLE LOG"
    )

    y = rect.y + 48

    for message in battle_log:

        draw_text(
            "• " + message,
            (
                rect.x + 15,
                y
            ),
            FONT_SMALL,
            GRAY
        )

        y += 17

        if y > rect.bottom - 15:
            break


# =========================================================
# TOP BAR
# =========================================================

def draw_top_bar():

    draw_text(
        "AI BATTLE ARENA",
        (45, 25),
        FONT_TITLE,
        WHITE
    )

    draw_text(
        "A* Pathfinding  •  Minimax  •  Alpha-Beta",
        (48, 67),
        FONT_SMALL,
        GRAY
    )

    # Turn indicator

    if game_over:

        turn_text = (
            f"{winner} WINS"
        )

        turn_color = YELLOW

    elif ai_thinking:

        turn_text = "AI THINKING..."

        turn_color = PURPLE

    elif turn == "PLAYER":

        turn_text = "YOUR TURN"

        turn_color = CYAN

    else:

        turn_text = "AI TURN"

        turn_color = RED

    draw_center_text(
        turn_text,
        (960, 48),
        FONT_MEDIUM,
        turn_color
    )


# =========================================================
# PLAYER / AI STATUS
# =========================================================

def draw_status_panel():

    rect = pygame.Rect(
        45,
        610,
        1110,
        75
    )

    draw_panel(
        rect
    )

    draw_hp_bar(
        65,
        640,
        250,
        14,
        player_hp,
        MAX_HP,
        "PLAYER",
        BLUE
    )

    draw_hp_bar(
        360,
        640,
        250,
        14,
        ai_hp,
        MAX_HP,
        "AI",
        RED
    )

    draw_text(
        "WASD / Arrow Keys",
        (665, 615),
        FONT_SMALL,
        GRAY
    )

    draw_text(
        "Move",
        (665, 635),
        FONT_NORMAL,
        WHITE
    )

    draw_text(
        "SPACE",
        (770, 615),
        FONT_SMALL,
        GRAY
    )

    draw_text(
        "Attack",
        (770, 635),
        FONT_NORMAL,
        WHITE
    )

    draw_text(
        "F",
        (870, 615),
        FONT_SMALL,
        GRAY
    )

    draw_text(
        "Defend",
        (870, 635),
        FONT_NORMAL,
        WHITE
    )

    draw_text(
        "R",
        (970, 615),
        FONT_SMALL,
        GRAY
    )

    draw_text(
        "Restart",
        (970, 635),
        FONT_NORMAL,
        WHITE
    )


# =========================================================
# GAME OVER OVERLAY
# =========================================================

def draw_game_over():

    if not game_over:
        return

    overlay = pygame.Surface(
        (WIDTH, HEIGHT),
        pygame.SRCALPHA
    )

    overlay.fill(
        (0, 0, 0, 170)
    )

    SCREEN.blit(
        overlay,
        (0, 0)
    )

    center_x = WIDTH // 2
    center_y = HEIGHT // 2

    if winner == "PLAYER":

        title = "YOU WIN!"

        title_color = GREEN

    else:

        title = "AI WINS"

        title_color = RED

    draw_center_text(
        title,
        (
            center_x,
            center_y - 45
        ),
        FONT_TITLE,
        title_color
    )

    draw_center_text(
        "Press R to restart",
        (
            center_x,
            center_y + 15
        ),
        FONT_NORMAL,
        WHITE
    )


# =========================================================
# DRAW ALL
# =========================================================

def draw():

    SCREEN.fill(
        BG_COLOR
    )

    # Top

    draw_top_bar()

    # Main battlefield panel

    battlefield_rect = pygame.Rect(
        25,
        90,
        680,
        480
    )

    draw_panel(
        battlefield_rect,
        "BATTLEFIELD"
    )

    # Grid

    draw_grid()

    draw_attack_range()

    draw_astar_path()

    draw_player()

    draw_ai()

    draw_attack_animation()

    draw_shield()

    draw_damage_number()

    # Right panels

    draw_ai_brain_panel()

    draw_battle_log()

    # Bottom

    draw_status_panel()

    # Game over

    draw_game_over()

    pygame.display.flip()


# =========================================================
# KEYBOARD HANDLING
# =========================================================

def handle_keydown(event):

    if event.key == pygame.K_ESCAPE:

        pygame.quit()

        sys.exit()

    if event.key == pygame.K_r:

        reset_game()

        return

    if game_over:
        return

    if turn != "PLAYER":
        return

    # -----------------------------------------------------
    # MOVEMENT
    # -----------------------------------------------------

    if event.key in (
        pygame.K_w,
        pygame.K_UP
    ):

        move_player(
            -1,
            0
        )

    elif event.key in (
        pygame.K_s,
        pygame.K_DOWN
    ):

        move_player(
            1,
            0
        )

    elif event.key in (
        pygame.K_a,
        pygame.K_LEFT
    ):

        move_player(
            0,
            -1
        )

    elif event.key in (
        pygame.K_d,
        pygame.K_RIGHT
    ):

        move_player(
            0,
            1
        )

    # -----------------------------------------------------
    # ATTACK
    # -----------------------------------------------------

    elif event.key == pygame.K_SPACE:

        player_attack()

    # -----------------------------------------------------
    # DEFEND
    # -----------------------------------------------------

    elif event.key == pygame.K_f:

        player_defend()


# =========================================================
# MAIN LOOP
# =========================================================

def main():

    global ai_thinking

    reset_game()

    running = True

    while running:

        # -------------------------------------------------
        # EVENTS
        # -------------------------------------------------

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                running = False

            elif event.type == pygame.KEYDOWN:

                handle_keydown(
                    event
                )

        # -------------------------------------------------
        # AI TURN
        # -------------------------------------------------

        if (
            turn == "AI"
            and
            ai_thinking
            and
            not game_over
        ):

            pygame.time.delay(
                AI_THINK_DELAY
            )

            run_ai_turn()

        # -------------------------------------------------
        # DRAW
        # -------------------------------------------------

        draw()

        CLOCK.tick(60)

    pygame.quit()

    sys.exit()


# =========================================================
# PROGRAM START
# =========================================================

if __name__ == "__main__":

    main()