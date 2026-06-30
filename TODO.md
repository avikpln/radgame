# TODO

## General

- [ ] Add unit testing, test automation, and logging throughout
- [ ] Add documentation throughout the entire codebase
- [ ] Set up version control properly (tags, releases for built `.exe`)
- [ ] Add a version number / package metadata
- [ ] Gather all scattered TODOs into this single file (ongoing)

---

## GUI (`radgamegui.py`)

- [ ] Re-attempt a full UML diagram for the GUI (previous attempt in Gaphor became unusable — try a different tool)
- [ ] Replace `RuntimeError` usage with custom exceptions
- [ ] Add checkboxes for timer and Randy toggle in the UI
- [ ] Add a list box for selecting Randy count
- [ ] Merge button command callbacks (`__play_btn`, `__reset_btn`, etc.) into a single method
- [ ] Decide whether to keep the `__exit` wrapper method or remove it
- [ ] Clarify the purpose of `__randy_refresh_callback`
- [ ] Decide whether GUI should be responsible for creating/placing Randys in the maze
- [ ] Add a key binding to pause the game (e.g. spacebar)
- [ ] Revisit whether `__display_walker_collision` (currently commented out) should be implemented for 2-walker collisions, distinct from the crowd case (3+)
- [ ] Investigate `__timer` null-check necessity in `__timer_callback`

---

## Core Engine (`radgame.py`)

- [ ] Validate that `location` is in range across all relevant methods (`add_door`, `enter`, etc.)
- [ ] Fix `add_door`: input `location` argument is currently ignored (a random location is always chosen instead)
- [ ] Move `Walker`-specific argument parsing into `Walker.__init__`
- [ ] Rename `State` to `Position` in `Player`
- [ ] Fix `Player.exit`: should use `get_prev_location` after calling `super().exit()`, and rename `prev_location` to `last_exit_location`
- [ ] Fix `Randy.__walk`: clarify why `location[0]`/`location[1]` indexing is used instead of `location.x`/`location.y`
- [ ] Move `Game` constructor keyword-argument parsing into `__init__` directly

---

## Graph Module (`graph.py`)

- [ ] Validate inputs (`n`, `p`, graph, vertex) across `get_random_graph`, `DFS`, `BFS`, and related functions
- [ ] Investigate whether DFS-based distance calculation is worth adding alongside BFS
- [ ] Stop edge iteration early in `get_random_tree` once the full tree is found (currently iterates all edges)
- [ ] Investigate the ~1% performance difference from swapping endpoint order in `find_graph_diameter_endpoints`

---

## Build & Packaging

- [ ] Confirm `Build.bat` works end-to-end on a clean machine (no prior PyInstaller install)
- [ ] Consider publishing built `.exe` via GitHub Releases instead of (or in addition to) local builds
- [ ] Investigate cross-platform packaging options (currently Windows-only via PyInstaller `.exe`)

---

## Acknowledgements (from original source comments)

- Thanks to David Naori for ideas: door coloring, timer feature
