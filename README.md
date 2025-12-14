# Graph Algorithms Visualizer

A high-performance graph visualization tool featuring a C++ backend for computational efficiency and a Python/Tkinter GUI for interactive graph manipulation.

## Features

- **Interactive Graph Editor**: Create and modify graphs with point-and-click interface
- **Multiple Algorithms**:
  - Dijkstra's Shortest Path
  - Minimum Spanning Tree (Kruskal's Algorithm)
  - Maximum Spanning Tree
  - Chinese Postman Problem (Eulerian Circuit)
  - Traveling Salesman Problem (Held-Karp DP / Nearest Neighbor Heuristic)
- **Cross-Platform**: Runs on Linux, macOS, and Windows
- **Real-time Visualization**: See algorithm results highlighted on the graph

## Requirements

### Linux / macOS

- Python 3.8 or higher
- Tkinter (usually included with Python)
- GCC/G++ with C++17 support

```bash
# Ubuntu/Debian
sudo apt install python3 python3-tk g++

# Fedora
sudo dnf install python3 python3-tkinter gcc-c++

# macOS (with Homebrew)
brew install python3 gcc
```

### Windows

- Python 3.8+ from [python.org](https://www.python.org/downloads/)
- MinGW-w64 or Visual Studio Build Tools with C++17 support

## Installation

1. Clone or download the repository:

```bash
git clone https://github.com/Azreyo/Graph-Visualizer
cd Graph-Visualizer
```

2. Compile the C++ backend (optional - the application auto-compiles on first run):

```bash
# Linux/macOS
g++ -O3 -std=c++17 -o graph_algorithms graph_algorithms.cpp

# Windows (MinGW)
g++ -O3 -std=c++17 -o graph_algorithms.exe graph_algorithms.cpp
```

## Usage

### Running the Application

```bash
python3 graph_app.py
```

On Windows:
```cmd
python graph_app.py
```

### Interface Overview

The application window is divided into two main sections:

**Left Panel** - Controls and Information
- Edit Mode: Switch between adding nodes, edges, and selecting start/end points
- Algorithms: Execute graph algorithms
- Actions: Load example graph, clear graph, clear highlights
- Graph Info: Current node/edge count and selected start/end nodes
- Result: Algorithm output and path details

**Right Panel** - Canvas
- Interactive drawing area for the graph

### Basic Operations

| Action | Method |
|--------|--------|
| Add Node | Select "Add Node" mode, click on canvas |
| Add Edge | Select "Add Edge" mode, click two nodes sequentially |
| Delete Node | Right-click on a node |
| Set Start Node | Select "Set Start" mode, click a node |
| Set End Node | Select "Set End" mode, click a node |

### Algorithm Descriptions

**Dijkstra's Shortest Path**
- Finds the shortest path between the start (green) and end (red) nodes
- Requires both start and end nodes to be set
- Time Complexity: O((V + E) log V)

**Minimum Spanning Tree**
- Finds the subset of edges connecting all nodes with minimum total weight
- Uses Kruskal's algorithm with Union-Find
- Time Complexity: O(E log E)

**Maximum Spanning Tree**
- Similar to MST but maximizes total edge weight
- Useful for finding the "strongest" connections

**Chinese Postman Problem**
- Finds the shortest route that traverses every edge at least once
- Returns to the starting vertex (Eulerian circuit)
- Uses minimum weight matching for odd-degree vertices

**Traveling Salesman Problem**
- Finds the shortest route visiting every node exactly once
- Uses Held-Karp dynamic programming for graphs up to 20 nodes
- Falls back to nearest neighbor heuristic for larger graphs
- Time Complexity: O(n^2 * 2^n) for exact solution

## Building for Distribution

### Linux

```bash
# Install PyInstaller
pip install pyinstaller

# Create standalone executable
pyinstaller --onefile --windowed graph_app.py

# Copy the C++ executable to dist folder
cp graph_algorithms dist/
```

### Windows (Cross-compile from Linux)

```bash
# Install MinGW-w64
sudo apt install mingw-w64

# Cross-compile C++ backend
x86_64-w64-mingw32-g++ -O3 -std=c++17 -static -o graph_algorithms.exe graph_algorithms.cpp
```

## Troubleshooting

**"graph_algorithms.cpp not found"**
- Ensure `graph_algorithms.cpp` is in the same directory as `graph_app.py`

**Compilation errors**
- Verify g++ supports C++17: `g++ --version` (requires GCC 7+)
- On older systems, try: `g++ -O3 -std=c++14 -o graph_algorithms graph_algorithms.cpp`

**Tkinter not found**
- Install the python3-tk package for your distribution
- On Windows, reinstall Python and ensure "tcl/tk" is selected

**Algorithm timeout**
- TSP with more than 15 nodes may take significant time
- Consider using smaller graphs or waiting for the nearest neighbor fallback

## Technical Details

### C++ Backend

The C++ component handles all graph algorithms for maximum performance:

- Priority queue-based Dijkstra implementation
- Union-Find with path compression and rank optimization
- Floyd-Warshall for all-pairs shortest paths
- Hierholzer's algorithm for Eulerian circuits
- Bitmask DP for exact TSP solution

### Communication Protocol

The Python GUI communicates with the C++ backend via stdin/stdout:

```
Input format:
<algorithm_name>
<n> <m>
<u1> <v1> <w1>
<u2> <v2> <w2>
...
[algorithm-specific parameters]

Output format:
[algorithm-specific results]
```

## License

This project is provided as-is for educational purposes.

## Contributing

Contributions are welcome. Please ensure any changes maintain cross-platform compatibility and include appropriate error handling.
