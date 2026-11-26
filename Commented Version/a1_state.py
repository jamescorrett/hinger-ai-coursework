# Header: A09, My Student ID: 100523557, others student ids 100538247, 100534304, 100539397

# a1_state.py - the rules engine for Hinger.
# The State class knows the BOARD only: which moves are legal, what a move costs,
# how many regions there are and which cells are hingers.
# It knows nothing about players or scores; that is handled in a3_game.py.

class State:
    # Board size as a class constant, so there are no hardcoded 5s in the logic.
    SIZE = 5

    def __init__(self, grid: list[list[int]]):
        # Copying rows is enough because the cells are ints, which are immutable.
        self.grid: list[list[int]] = [row[:] for row in grid]

    def __str__(self):
        return "\n".join(
            " ".join(str(cell) for cell in row)
            for row in self.grid
    )

    def  copy(self):
        return State(self.grid)

    @staticmethod
    def letter_to_cell(letter: str):
        """'A'..'Y' -> (r,c), or None if not a board move."""
        # Must be a single-character string; this stops None or "a1" crashing.
        if not isinstance(letter, str) or len(letter) !=1:
            return None
        # 'A' -> 0, 'B' -> 1, ... 'Y' -> 24. 'Z' gives 25, so it is rejected as a
        # board move (it is the special "end the game" action).
        idx = ord(letter.upper()) - ord('A')
        if 0 <= idx < 25:
            # divmod splits the index into (row, column). E.g. 'M' = 12 -> (2, 2).
            return divmod(idx, State.SIZE)
        return None

    def is_active(self, r: int, c: int) -> bool:
        # A cell is active if it still holds at least one counter.
        return self.grid[r][c] > 0

    def neighbours(self, r: int, c: int):
        """In-bounds cells adjacent to (r, c), including diagonals."""
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dc == 0 and dr == 0:
                    continue
                nr, nc = r + dr, c + dc
                if 0 <= nr < State.SIZE and 0 <= nc < State.SIZE:
                    yield nr, nc

    def cost(self, r: int, c: int):
        # Cost of a move on (r, c) = number of ACTIVE cells next to it.
        # Must be measured before the move is made.
        return sum(1 for nr, nc in self.neighbours(r, c) if self.is_active(nr, nc))

    def legal_moves(self):
        return [chr(ord('A') + r * self.SIZE + c) for r in range(self.SIZE) for c in range(self.SIZE) if self.is_active(r, c)]

    def is_legal(self, letter: str):
        cell = self.letter_to_cell(letter)
        return cell is not None and self.is_active(*cell)

    def move(self, letter: str):
        # Removes ONE counter from the chosen cell, changing this state in place.
        # Returns True if it worked and False if the move was illegal, so the
        # game loop can tell whether a move was valid.
        cell = self.letter_to_cell(letter)
        if cell is None or not self.is_active(*cell):
            return False
        r, c = cell
        self.grid[r][c] -= 1
        return True

    def numRegions(self):
        """Count connected groups of active cells (8-neighbour adjacency)."""
        visited = set()   # cells already assigned to a region
        count = 0         # number of regions found so far
        for r in range(self.SIZE):
            for c in range(self.SIZE):
                # An active cell we haven't seen yet must belong to a NEW region.
                if self.is_active(r, c) and (r, c) not in visited:
                    count += 1
                    # Flood fill (depth-first search with a stack): visit every
                    # active cell reachable from here and mark it as visited, so
                    # the whole region is counted once.
                    stack = [(r, c)]
                    visited.add((r, c))
                    while stack:
                        cr, cc = stack.pop()
                        for nr, nc in self.neighbours(cr, cc):
                            if self.is_active(nr, nc) and (nr, nc) not in visited:
                                visited.add((nr, nc))
                                stack.append((nr, nc))

        return count

    def is_hinger(self, r, c):
        """One counter, and removing it increases the region count"""
        if self.grid[r][c] != 1:
            return False
        after = self.copy()
        after.grid[r][c] = 0
        return after.numRegions() > self.numRegions()

    def numHingers(self):
        # Count the cells for which is_hinger is True.
        return sum(1 for r in range(self.SIZE) for c in range(self.SIZE) 
                   if self.is_hinger(r, c))

    def successors(self):
        """Yield every state reachable by removing one counter"""
        for letter in self.legal_moves():
            nxt = self.copy()
            nxt.move(letter)
            yield nxt

def tester():
    # State s1 from Figure 1.1: eleven active cells in two regions
    # (the lone cell at (0,4), and everything else).
    s1 = [[1,1,0,0,1],
          [1,1,0,0,0],
          [0,0,1,1,1],
          [0,0,0,1,1],
          [0,0,0,0,1]]
    sa = State(s1)
    print(sa)

    assert sa.numRegions() == 2          # (0,4) is alone, the rest is joined
    assert sa.cost(4, 4) == 2            # Alice's move 'Y': neighbours (3,3), (3,4)
    assert not sa.is_hinger(4, 4)        # a corner of the block, so no split -> no bonus

    assert sa.move('Y')                  # s1 -> s2
    assert sa.is_hinger(2, 2)            # centre is the only link between the two blocks
    assert sa.cost(2, 2) == 3            # Bob's move 'M': neighbours (1,1), (2,3), (3,3)
    assert sa.move('M')                  # s2 -> s3
    assert sa.numRegions() == 3          # removing the hinger split the board in three

    # edge cases
    assert State([[0]*5 for _ in range(5)]).numRegions() == 0   # empty board, no regions
    assert not sa.move('M')              # centre is already empty, so illegal
    assert not sa.move('Z')              # 'Z' is not a board cell
    assert not sa.move('a1')             # more than one character is rejected
    # one successor per active cell
    assert len(list(State(s1).successors())) == len(State(s1).legal_moves())

    # diagonal chain: middle two are hingers, ends and the lone cells are not
    # chain = (0,1)-(1,2)-(2,3)-(3,4), plus a separate lone cell at (4,0)
    chain = State([[0,1,0,0,0],
                   [0,0,1,0,0],
                   [0,0,0,1,0],
                   [0,0,0,0,1],
                   [1,0,0,0,0]])
    assert chain.numHingers() == 2       # (1,2) and (2,3) are bridges
    assert chain.numRegions() == 2       # the chain, and the lone cell
    print("All tests passed.")

# Run the tests only when this file is executed directly (python a1_state.py),
# not when it is imported by another module such as a3_game.py.
if __name__ == "__main__":
    tester()
