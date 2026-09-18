import time

from ai.astar import a_star
from ai.minimax import get_best_action


# =========================================================
# GAME CONFIGURATION
# =========================================================

ROWS = 8
COLS = 12

PLAYER_HP = 100
AI_HP = 100


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
    (7, 9),
}


# =========================================================
# A* TEST CASES
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


# =========================================================
# MINIMAX TEST CASES
# =========================================================

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
# RUN A* EVALUATION
# =========================================================

def run_astar_evaluation():

    print()
    print("=" * 78)
    print("A* PATHFINDING EVALUATION")
    print("=" * 78)

    print(
        f"{'Test':<10}"
        f"{'Start':<12}"
        f"{'Goal':<12}"
        f"{'Path Cost':<15}"
        f"{'Nodes':<12}"
        f"{'Time (ms)':<15}"
    )

    print("-" * 78)

    total_path_cost = 0
    total_nodes = 0
    total_time = 0

    successful_tests = 0

    for test in ASTAR_TESTS:

        start = test["start"]
        goal = test["goal"]

        # -------------------------------------------------
        # Run A*
        # -------------------------------------------------

        start_time = time.perf_counter()

        path, nodes_explored = a_star(
            start,
            goal,
            ROWS,
            COLS,
            set(OBSTACLES)
        )

        end_time = time.perf_counter()

        # -------------------------------------------------
        # Execution time
        # -------------------------------------------------

        execution_time = (
            end_time - start_time
        ) * 1000

        # -------------------------------------------------
        # Path cost
        # -------------------------------------------------

        if path:

            path_cost = len(path) - 1

            successful_tests += 1

        else:

            path_cost = -1

        # -------------------------------------------------
        # Add totals
        # -------------------------------------------------

        if path_cost >= 0:

            total_path_cost += path_cost

        total_nodes += nodes_explored
        total_time += execution_time

        # -------------------------------------------------
        # Print result
        # -------------------------------------------------

        print(
            f"{test['name']:<10}"
            f"{str(start):<12}"
            f"{str(goal):<12}"
            f"{path_cost:<15}"
            f"{nodes_explored:<12}"
            f"{execution_time:<15.4f}"
        )

    print("-" * 78)

    # -----------------------------------------------------
    # Average
    # -----------------------------------------------------

    test_count = len(ASTAR_TESTS)

    if successful_tests > 0:

        average_path_cost = (
            total_path_cost
            / successful_tests
        )

    else:

        average_path_cost = 0

    average_nodes = (
        total_nodes
        / test_count
    )

    average_time = (
        total_time
        / test_count
    )

    return {
        "average_path_cost": average_path_cost,
        "average_nodes": average_nodes,
        "average_time": average_time,
        "successful_tests": successful_tests,
        "total_tests": test_count,
    }


# =========================================================
# CREATE MINIMAX STATE
# =========================================================

def create_minimax_state(test):

    return {

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


# =========================================================
# RUN MINIMAX EVALUATION
# =========================================================

def run_minimax_evaluation(depth=3):

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
        f"{'Score':<12}"
        f"{'Nodes':<12}"
        f"{'Pruned':<12}"
        f"{'Time (ms)':<15}"
    )

    print("-" * 78)

    total_nodes = 0
    total_pruned = 0
    total_time = 0

    results = []

    for test in MINIMAX_TESTS:

        state = create_minimax_state(
            test
        )

        # -------------------------------------------------
        # Run Minimax + Alpha-Beta
        # -------------------------------------------------

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

        # -------------------------------------------------
        # Execution time
        # -------------------------------------------------

        execution_time = (
            end_time - start_time
        ) * 1000

        # -------------------------------------------------
        # Format action
        # -------------------------------------------------

        if isinstance(
            best_action,
            tuple
        ):

            action_text = (
                f"MOVE {best_action[1]}"
            )

        else:

            action_text = best_action

        # -------------------------------------------------
        # Add totals
        # -------------------------------------------------

        total_nodes += nodes

        total_pruned += pruned

        total_time += execution_time

        # -------------------------------------------------
        # Save result
        # -------------------------------------------------

        results.append({

            "test": test["name"],

            "action": action_text,

            "score": best_score,

            "nodes": nodes,

            "pruned": pruned,

            "time": execution_time,

        })

        # -------------------------------------------------
        # Print result
        # -------------------------------------------------

        print(
            f"{test['name']:<10}"
            f"{action_text:<20}"
            f"{best_score:<12}"
            f"{nodes:<12}"
            f"{pruned:<12}"
            f"{execution_time:<15.4f}"
        )

    print("-" * 78)

    # -----------------------------------------------------
    # Average values
    # -----------------------------------------------------

    test_count = len(MINIMAX_TESTS)

    average_nodes = (
        total_nodes
        / test_count
    )

    average_pruned = (
        total_pruned
        / test_count
    )

    average_time = (
        total_time
        / test_count
    )

    return {

        "average_nodes": average_nodes,

        "average_pruned": average_pruned,

        "average_time": average_time,

        "results": results,

    }


# =========================================================
# MINIMAX DEPTH EXPERIMENT
# =========================================================

def run_depth_experiment():

    depths = [
        1,
        2,
        3,
        4,
    ]

    print()
    print("=" * 78)
    print("MINIMAX DEPTH EXPERIMENT")
    print("=" * 78)

    print(
        f"{'Depth':<10}"
        f"{'Nodes':<15}"
        f"{'Pruned':<15}"
        f"{'Time (ms)':<15}"
    )

    print("-" * 78)

    depth_results = []

    for depth in depths:

        total_nodes = 0
        total_pruned = 0
        total_time = 0

        # -------------------------------------------------
        # Run all test cases for current depth
        # -------------------------------------------------

        for test in MINIMAX_TESTS:

            state = create_minimax_state(
                test
            )

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

            total_nodes += nodes

            total_pruned += pruned

            total_time += execution_time

        # -------------------------------------------------
        # Calculate averages
        # -------------------------------------------------

        test_count = len(
            MINIMAX_TESTS
        )

        average_nodes = (
            total_nodes
            / test_count
        )

        average_pruned = (
            total_pruned
            / test_count
        )

        average_time = (
            total_time
            / test_count
        )

        # -------------------------------------------------
        # Save result
        # -------------------------------------------------

        depth_results.append({

            "depth": depth,

            "nodes": average_nodes,

            "pruned": average_pruned,

            "time": average_time,

        })

        # -------------------------------------------------
        # Print result
        # -------------------------------------------------

        print(
            f"{depth:<10}"
            f"{average_nodes:<15.2f}"
            f"{average_pruned:<15.2f}"
            f"{average_time:<15.4f}"
        )

    print("-" * 78)

    return depth_results


# =========================================================
# PRINT OVERALL SUMMARY
# =========================================================

def print_summary(
    astar_results,
    minimax_results
):

    print()
    print("=" * 78)
    print("OVERALL EVALUATION SUMMARY")
    print("=" * 78)

    print()

    # -----------------------------------------------------
    # A*
    # -----------------------------------------------------

    print("A* Pathfinding")

    print(
        f"Successful Tests      : "
        f"{astar_results['successful_tests']}/"
        f"{astar_results['total_tests']}"
    )

    print(
        f"Average Path Cost     : "
        f"{astar_results['average_path_cost']:.2f}"
    )

    print(
        f"Average Nodes         : "
        f"{astar_results['average_nodes']:.2f}"
    )

    print(
        f"Average Time          : "
        f"{astar_results['average_time']:.4f} ms"
    )

    print()

    # -----------------------------------------------------
    # Minimax
    # -----------------------------------------------------

    print("Minimax + Alpha-Beta")

    print(
        f"Average Nodes         : "
        f"{minimax_results['average_nodes']:.2f}"
    )

    print(
        f"Average Pruned        : "
        f"{minimax_results['average_pruned']:.2f}"
    )

    print(
        f"Average Time          : "
        f"{minimax_results['average_time']:.4f} ms"
    )

    print()

    print("=" * 78)


# =========================================================
# MAIN
# =========================================================

def main():

    print()
    print("=" * 78)
    print("AI BATTLE ARENA")
    print("Algorithm Evaluation")
    print("=" * 78)

    # -----------------------------------------------------
    # A* Evaluation
    # -----------------------------------------------------

    astar_results = run_astar_evaluation()

    # -----------------------------------------------------
    # Minimax Evaluation
    # -----------------------------------------------------

    minimax_results = run_minimax_evaluation(
        depth=3
    )

    # -----------------------------------------------------
    # Overall Summary
    # -----------------------------------------------------

    print_summary(
        astar_results,
        minimax_results
    )

    # -----------------------------------------------------
    # Depth Experiment
    # -----------------------------------------------------

    run_depth_experiment()

    print()

    print("=" * 78)
    print("EVALUATION COMPLETED")
    print("=" * 78)


# =========================================================
# PROGRAM ENTRY
# =========================================================

if __name__ == "__main__":
    main()