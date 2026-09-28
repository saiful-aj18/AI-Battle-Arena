# ⚔️ AI Battle Arena

### An Intelligent 2D Strategic Combat Game Powered by A* Search, Minimax & Alpha-Beta Pruning

AI Battle Arena is a turn-based 2D strategic combat game developed in **Python and Pygame** as an Artificial Intelligence course project.

The game combines **pathfinding** and **game-theoretic decision making** to create an AI opponent that can navigate obstacles, choose tactical actions, retreat when critically injured, and re-engage in combat.

Instead of using random AI behavior, the opponent uses:

- 🔎 **A* Search** for intelligent pathfinding
- 🧠 **Minimax** for strategic decision making
- ✂️ **Alpha-Beta Pruning** for optimizing Minimax search
- ⚔️ Tactical combat logic for attack, defense and retreat
- 🏆 A five-level progression system with a final boss

---

## 🎮 Game Overview

The player enters a tactical battlefield against an AI-controlled fighter.

Each turn, the player can:

- Move around the battlefield
- Attack the enemy
- Defend against incoming attacks

The AI analyzes the current game state and chooses an appropriate action.

The main AI decision process can be summarized as:

```text
                    ┌──────────────────┐
                    │   Current State  │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │   Is AI Nearby?  │
                    └────────┬─────────┘
                       Yes   │   No
                            │
              ┌─────────────┘ └─────────────┐
              ▼                             ▼
      ┌────────────────┐            ┌────────────────┐
      │ Minimax +      │            │   A* Search    │
      │ Alpha-Beta     │            │  Pathfinding   │
      └───────┬────────┘            └───────┬────────┘
              │                             │
              ▼                             ▼
       Attack / Defend /              Move toward
            Move                       the player
````

---

# ✨ Features

## 🧠 Intelligent AI

The AI is designed around multiple AI techniques rather than simple random movement.

### A* Pathfinding

A* is used to find efficient paths through the grid while avoiding obstacles.

```text
Start
  │
  ▼
┌───┬───┬───┬───┐
│   │   │ █ │   │
├───┼───┼───┼───┤
│   │ █ │ █ │   │
├───┼───┼───┼───┤
│   │   │   │   │
└───┴───┴───┴───┘
              │
              ▼
             Goal
```

The algorithm considers:

* Current movement cost `g(n)`
* Heuristic cost `h(n)`
* Total estimated cost:

```text
f(n) = g(n) + h(n)
```

The project uses **Manhattan Distance** as the heuristic.

---

## 🎯 Minimax

When the AI is close enough to interact with the player, Minimax evaluates possible actions.

Possible actions include:

* `ATTACK`
* `DEFEND`
* `MOVE`

Conceptually:

```text
                 AI Turn
                    │
          ┌─────────┼─────────┐
          ▼         ▼         ▼
       ATTACK     DEFEND     MOVE
          │         │         │
          ▼         ▼         ▼
       Evaluate   Evaluate   Evaluate
          │         │         │
          └─────────┼─────────┘
                    ▼
             Best Action
```

The AI attempts to maximize its advantage while considering the opponent's possible response.

---

## ✂️ Alpha-Beta Pruning

Alpha-Beta Pruning improves Minimax by eliminating branches that cannot affect the final decision.

```text
                  Root
               /    |    \
             A      B      C
            / \    / \    / \
           ✓   ✓  ✓  ✂  ✂  ✂
```

This allows the AI to search deeper without evaluating every possible branch.

---

# ⚔️ Combat System

The game uses a turn-based combat system.

### Player Actions

| Key             | Action  |
| --------------- | ------- |
| `W / A / S / D` | Move    |
| `Arrow Keys`    | Move    |
| `SPACE`         | Attack  |
| `F`             | Defend  |
| `R`             | Restart |
| `ESC`           | Quit    |

### Attack

The player and AI can attack when they are within attack range.

Example:

```text
PLAYER  ⚔️  AI

Player Attack
      ↓
AI HP decreases
```

### Defense

Defending activates a shield that reduces the next incoming attack.

The shield is consumed after absorbing a hit.

---

# 🏃 AI Survival & Retreat System

The AI has a tactical survival mechanism.

When the AI's HP becomes critically low, it can enter **Survival Mode**.

```text
AI HP
  │
  ▼
≤ Critical HP
  │
  ▼
SURVIVAL MODE
  │
  ├── Retreat
  │
  ├── Reposition
  │
  └── Re-engage
        │
        ▼
      Attack
```

The AI does not retreat forever.

If it remains in a weakened state for too long:

* Its HP gradually decreases
* It is forced to re-engage
* A successful attack can recover some HP

This prevents the AI from simply running away indefinitely.

---

# 🏆 Level Progression

AI Battle Arena contains **5 progressive levels**.

| Level | Fighter          |  HP | Damage | Search Depth |
| ----- | ---------------- | --: | -----: | -----------: |
| 1     | Rookie Fighter   | 100 |     15 |            3 |
| 2     | Vanguard Fighter | 120 |     16 |            3 |
| 3     | Elite Fighter    | 145 |     18 |            3 |
| 4     | Commander        | 170 |     20 |            4 |
| 5     | Final Boss       | 220 |     24 |            4 |

Each level becomes more challenging by increasing enemy strength and, at higher levels, increasing the AI search depth.

---

# 👑 Final Boss

Level 5 introduces the **Final Boss**.

The Final Boss has:

```text
HP:             220
Damage:         24
Minimax Depth:  4
```

Defeating the Final Boss completes the game.

```text
╔════════════════════════════════╗
║                                ║
║        🏆 ARENA CLEARED!       ║
║                                ║
║      FINAL BOSS DEFEATED       ║
║                                ║
║       YOU ARE THE CHAMPION     ║
║                                ║
╚════════════════════════════════╝
```

---

# 💯 Score System

The game includes a progressive scoring system.

Players earn points by dealing damage and defeating enemy fighters.

Example:

```text
Damage dealt
     ↓
+ Damage Points
     ↓
Enemy defeated
     ↓
Level Reward
     ↓
Next Level
```

The score carries across levels.

---

# 🗺️ Battlefield

The game uses an **8 × 12 grid-based battlefield**.

```text
┌───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┐
│   │   │ P │   │   │   │   │   │   │   │   │   │
├───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┤
│   │   │   │   │ █ │ █ │   │   │   │   │   │   │
├───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┤
│   │   │   │   │ █ │   │   │   │   │   │   │   │
├───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┤
│   │   │   │   │   │   │   │ █ │ █ │   │   │   │
├───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┤
│   │   │   │   │   │   │   │   │   │ AI│   │   │
└───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┘
```

Obstacles create different paths for the A* algorithm to evaluate.

---

# 📊 AI Monitoring Panel

The game interface provides information about the AI's decision process.

The AI panel displays:

* Current algorithm
* Alpha-Beta status
* Search depth
* Current action
* A* nodes explored
* A* path cost
* A* execution time
* Minimax nodes explored
* Alpha-Beta pruning count
* Minimax score

Example:

```text
AI BRAIN

Algorithms       A* + Minimax
Alpha-Beta       Enabled
Search Depth     3
Current Action   ATTACK

A* SEARCH
Nodes            16
Path Cost        5
Time             0.21 ms

MINIMAX + ALPHA-BETA
Nodes            61
Pruned           4
Score            32
```

This makes the AI's decision-making process easier to observe and demonstrate during the project presentation or viva.

---

# 🖥️ User Interface

The interface contains:

* Battlefield
* Player fighter
* AI fighter
* Obstacles
* A* path visualization
* Player HP bar
* AI HP bar
* Score
* Current level
* AI Brain panel
* Battle log
* Turn indicator
* Attack animation
* Damage indicators
* Shield animation
* Game-over / victory screen

---

# 🛠️ Technologies Used

### Programming Language

* Python 3

### Game Development

* Pygame

### Artificial Intelligence

* A* Search
* Minimax
* Alpha-Beta Pruning
* Heuristic Evaluation
* State-Space Search

### Development Tools

* Visual Studio Code
* Git
* GitHub

---

# 📁 Project Structure

```text
AI-Battle-Arena/
│
├── ai/
│   ├── __init__.py
│   ├── astar.py
│   └── minimax.py
│
├── main.py
├── evaluation.py
├── README.md
└── requirements.txt
```

### `main.py`

Contains:

* Game loop
* Pygame interface
* Battlefield
* Player controls
* AI turn handling
* Combat system
* Level progression
* Score system
* Animations

### `ai/astar.py`

Contains the A* pathfinding implementation.

### `ai/minimax.py`

Contains:

* Game state evaluation
* Possible action generation
* Minimax
* Alpha-Beta pruning
* AI action selection

### `evaluation.py`

Used to evaluate the performance of:

* A* pathfinding
* Minimax
* Alpha-Beta pruning
* Different search depths

---

# 🚀 Installation

## 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/AI-Battle-Arena.git
```

Go to the project directory:

```bash
cd AI-Battle-Arena
```

---

## 2. Create a virtual environment

### Windows

```bash
python -m venv venv
```

Activate it:

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv
```

```bash
source venv/bin/activate
```

---

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

Or install Pygame directly:

```bash
pip install pygame
```

---

# ▶️ Run the Game

```bash
python main.py
```

---

# 📊 Run AI Evaluation

The project also includes an evaluation script.

Run:

```bash
python evaluation.py
```

The evaluation can measure:

* A* path cost
* Nodes explored by A*
* A* execution time
* Minimax nodes explored
* Alpha-Beta pruning
* Minimax execution time
* Different search depths

---

# 🧪 AI Evaluation

Example A* evaluation:

```text
A* PATHFINDING EVALUATION

Test 1
Path Cost: 9
Nodes: 16

Test 2
Path Cost: 5
Nodes: 7

Test 3
Path Cost: 10
Nodes: 18
```

Example Minimax evaluation:

```text
MINIMAX + ALPHA-BETA

Depth: 3

Nodes Explored: 61
Pruned: 4
Execution Time: ...
```

The evaluation results are intended to demonstrate how the implemented AI algorithms behave under different game states.

---

# 🧠 AI Architecture

```text
                    ┌────────────────────┐
                    │   Game State       │
                    │                    │
                    │ Player Position    │
                    │ AI Position        │
                    │ HP                 │
                    │ Defense State      │
                    │ Obstacles          │
                    └─────────┬──────────┘
                              │
                 ┌────────────┴────────────┐
                 │                         │
                 ▼                         ▼
        ┌─────────────────┐       ┌──────────────────┐
        │   A* Search     │       │     Minimax      │
        │                 │       │                  │
        │ Pathfinding     │       │ Action Selection │
        └────────┬────────┘       └────────┬─────────┘
                 │                         │
                 │                 ┌───────┴────────┐
                 │                 │ Alpha-Beta      │
                 │                 │ Pruning         │
                 │                 └───────┬────────┘
                 │                         │
                 └────────────┬────────────┘
                              ▼
                    ┌──────────────────┐
                    │   AI Action      │
                    │                  │
                    │ MOVE             │
                    │ ATTACK           │
                    │ DEFEND           │
                    └──────────────────┘
```

---

# 🎯 Project Objectives

The main objectives of AI Battle Arena are:

1. Implement an intelligent pathfinding system using A*.
2. Implement strategic decision making using Minimax.
3. Optimize Minimax using Alpha-Beta pruning.
4. Create an interactive AI-based combat environment.
5. Demonstrate state-space search in a practical game.
6. Compare AI performance using measurable metrics.
7. Provide a visual representation of AI decision-making.

---

# 📚 AI Concepts Demonstrated

This project demonstrates several important Artificial Intelligence concepts:

* State Space Representation
* Search Algorithms
* Informed Search
* Heuristic Functions
* A* Search
* Game Theory
* Minimax
* Alpha-Beta Pruning
* Utility / Evaluation Functions
* Adversarial Search
* Decision Making
* Pathfinding
* Dynamic Game States

---

# 🔮 Future Improvements

Possible future improvements include:

* Multiple AI fighters
* Different fighter classes
* Ranged attacks
* Weapon types
* More complex maps
* Procedurally generated maps
* Improved AI evaluation functions
* Difficulty selection
* Sound effects and background music
* More advanced animations
* Multiplayer mode
* AI strategy visualization
* Replay system
* Leaderboard

---

# 👨‍💻 Developer

**Saiful Islam**

CSE Student
Bangladesh

### Technologies

`Python` · `Pygame` · `A*` · `Minimax` · `Alpha-Beta Pruning`

---

# 📜 License

This project was developed for academic and educational purposes.

You are free to study and modify the project for learning purposes.

---

## ⭐ If you found this project interesting

Give the repository a ⭐ on GitHub!

> **AI Battle Arena — Where Search Meets Strategy.** ⚔️🧠

