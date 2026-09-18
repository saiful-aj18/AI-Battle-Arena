import time

from ai.astar import a_star
from ai.minimax import get_best_action


# =========================================================
# AI BATTLE ARENA
# ALGORITHM EVALUATION
# =========================================================

ROWS = 8
COLS = 12

PLAYER_HP = 100
AI_HP = 100


# =========================================================
# TEST OBSTACLES
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

    (7, 9),
}


# =========================================================
# TEST SCENARIOS
# =========================================================

ASTAR_TESTS = [
    {
        "name": "Test 1",
        "start": (5, 9),
        "goal": (2, 3),
    },

    {
        "name": "Test 2",
        "start": (5, 9),
        "goal": (3, 6),
    },

    {
        "name": "Test 3",
        "start": (2, 2),
        "goal": (6, 8),
    },

    {
        "name": "Test 4",
        "start": (6, 8),
        "goal": (1, 2),
    },

    {
        "name": "Test 5",
        "start": (7, 8),
        "goal": (0, 10),
    },
]


MINIMAX_TESTS = [
    {
        "name": "Test 1",

        "ai_position": (5, 9),
        "player_position": (2, 2),

        "ai_hp": 100,
        "player_hp": 100,

        "ai_defending": False,
        "player_defending": False,
    },

    {
        "name": "Test 2",

        "ai_position": (3, 6),
        "player_position": (3, 5),

        "ai_hp": 80,
        "player_hp": 100,

        "ai_defending": False,
        "player_defending": False,
    },

    {
        "name": "Test 3",

        "ai_position": (4, 7),
        "player_position": (4, 5),

        "ai_hp": 100,
        "player_hp": 70,

        "ai_defending": False,
        "player_defending": False,
    },

    {
        "name": "Test 4",

        "ai_position": (5, 6),
        "player_position": (5, 5),

        "ai_hp": 50,
        "player_hp": 90,

        "ai_defending": False,
        "player_defending": False,
    },

    {
        "name": "Test 5",

        "ai_position": (2, 5),
        "player_position": (2, 4),

        "ai_hp": 100,
        "player_hp": 40,

        "ai_defending": False,
        "player_defending": False,
    },
]


# =========================================================
# RUN A* TEST
# =========================================================

def run_astar_test(test):

    start = test["start"]
    goal = test["goal"]

    start_time = time.perf_counter()

    path, nodes_explored = a_star(
        start,
        goal,
        ROWS,
        COLS,
        OBSTACLES
    )

    end_time = time.perf_counter()

    execution_time = (
        end_time - start_time
    ) * 1000

    if path:

        path_cost = len(path) - 1

    else:

        path_cost = -1

    return {
        "name": test["name"],
        "start": start,
        "goal": goal,
        "path_cost": path_cost,
        "nodes": nodes_explored,
        "time": execution_time,
        "path": path,
    }


# =========================================================
# RUN MINIMAX TEST
# =========================================================

def run_minimax_test(
    test,
    depth
):

    state = {
        "ai_position": test["ai_position"],
        "player_position": test["player_position"],

        "ai_hp": test["ai_hp"],
        "player_hp": test["player_hp"],

        "ai_defending": test["ai_defending"],
        "player_defending": test["player_defending"],

        "rows": ROWS,
        "cols": COLS,

        "obstacles": set(OBSTACLES),
    }

    start_time = time.perf_counter()

    (
        best_action,
        best_score,
        nodes,
        pruned
    ) = get_best_action(
        state,
        depth=depth
    )

    end_time = time.perf_counter()

    execution_time = (
        end_time - start_time
    ) * 1000

    return {
        "name": test["name"],
        "action": best_action,
        "score": best_score,
        "nodes": nodes,
        "pruned": pruned,
        "time": execution_time,
    }


# =========================================================
# PRINT A* RESULTS
# =========================================================

def print_astar_results(results):

    print()
    print("=" * 78)
    print("A* PATHFINDING EVALUATION")
    print("=" * 78)

    print(
        f"{'Test':<10}"
        f"{'Start':<12}"
        f"{'Goal':<12}"
        f"{'Path Cost':<12}"
        f"{'Nodes':<12}"
        f"{'Time (ms)':<12}"
    )

    print("-" * 78)

    for result in results:

        print(
            f"{result['name']:<10}"
            f"{str(result['start']):<12}"
            f"{str(result['goal']):<12}"
            f"{result['path_cost']:<12}"
            f"{result['nodes']:<12}"
            f"{result['time']:<12.4f}"
        )

    print("-" * 78)


# =========================================================
# PRINT MINIMAX RESULTS
# =========================================================

def print_minimax_results(
    results,
    depth
):

    print()
    print("=" * 78)
    print(
        f"MINIMAX + ALPHA-BETA EVALUATION "
        f"(DEPTH {depth})"
    )
    print("=" * 78)

    print(
        f"{'Test':<10}"
        f"{'Action':<20}"
        f"{'Score':<10}"
        f"{'Nodes':<12}"
        f"{'Pruned':<12}"
        f"{'Time (ms)':<12}"
    )

    print("-" * 78)

    for result in results:

        print(
            f"{result['name']:<10}"
            f"{str(result['action']):<20}"
            f"{result['score']:<10}"
            f"{result['nodes']:<12}"
            f"{result['pruned']:<12}"
            f"{result['time']:<12.4f}"
        )

    print("-" * 78)


# =========================================================
# SUMMARY
# =========================================================

def print_summary(
    astar_results,
    minimax_results
):

    # -----------------------------------------------------
    # A* averages
    # -----------------------------------------------------

    astar_times = [
        result["time"]
        for result in astar_results
    ]

    astar_nodes = [
        result["nodes"]
        for result in astar_results
    ]

    astar_costs = [
        result["path_cost"]
        for result in astar_results
        if result["path_cost"] >= 0
    ]

    avg_astar_time = (
        sum(astar_times)
        /
        len(astar_times)
    )

    avg_astar_nodes = (
        sum(astar_nodes)
        /
        len(astar_nodes)
    )

    if astar_costs:

        avg_astar_cost = (
            sum(astar_costs)
            /
            len(astar_costs)
        )

    else:

        avg_astar_cost = 0

    # -----------------------------------------------------
    # Minimax averages
    # -----------------------------------------------------

    minimax_times = [
        result["time"]
        for result in minimax_results
    ]

    minimax_nodes = [
        result["nodes"]
        for result in minimax_results
    ]

    minimax_pruned = [
        result["pruned"]
        for result in minimax_results
    ]

    avg_minimax_time = (
        sum(minimax_times)
        /
        len(minimax_times)
    )

    avg_minimax_nodes = (
        sum(minimax_nodes)
        /
        len(minimax_nodes)
    )

    avg_minimax_pruned = (
        sum(minimax_pruned)
        /
        len(minimax_pruned)
    )

    # -----------------------------------------------------
    # Print summary
    # -----------------------------------------------------

    print()
    print("=" * 78)
    print("OVERALL EVALUATION SUMMARY")
    print("=" * 78)

    print()

    print("A* Pathfinding")
    print(
        f"Average Path Cost    : "
        f"{avg_astar_cost:.2f}"
    )

    print(
        f"Average Nodes        : "
        f"{avg_astar_nodes:.2f}"
    )

    print(
        f"Average Time         : "
        f"{avg_astar_time:.4f} ms"
    )

    print()

    print("Minimax + Alpha-Beta")

    print(
        f"Average Nodes        : "
        f"{avg_minimax_nodes:.2f}"
    )

    print(
        f"Average Pruned       : "
        f"{avg_minimax_pruned:.2f}"
    )

    print(
        f"Average Time         : "
        f"{avg_minimax_time:.4f} ms"
    )

    print()

    print("=" * 78)


# =========================================================
# MAIN EVALUATION
# =========================================================

def main():

    print()
    print("AI BATTLE ARENA")
    print("Algorithm Evaluation")
    print()

    # -----------------------------------------------------
    # A* TESTS
    # -----------------------------------------------------

    astar_results = []

    for test in ASTAR_TESTS:

        result = run_astar_test(
            test
        )

        astar_results.append(
            result
        )

    print_astar_results(
        astar_results
    )

    # -----------------------------------------------------
    # MINIMAX TESTS
    # -----------------------------------------------------

    minimax_results = []

    for test in MINIMAX_TESTS:

        result = run_minimax_test(
            test,
            depth=3
        )

        minimax_results.append(
            result
        )

    print_minimax_results(
        minimax_results,
        depth=3
    )

    # -----------------------------------------------------
    # SUMMARY
    # -----------------------------------------------------

    print_summary(
        astar_results,
        minimax_results
    )


# =========================================================
# START
# =========================================================

if __name__ == "__main__":

    main()