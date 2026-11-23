# Header: A09, My Student ID: 100523557, others student ids 100538247, 100534304, 100539397 

class State:
    SIZE = 5

    def __init__(self, grid: list[list[int]]):
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
        if not isinstance(letter, str) or len(letter) !=1:
            return None
        idx = ord(letter.upper()) - ord('A')
        if 0 <= idx < 25:
            return divmod(idx, State.SIZE)
        return None

    def is_active(self, r: int, c: int) -> bool:
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
        return sum(1 for nr, nc in self.neighbours(r, c) if self.is_active(nr, nc))

    def legal_moves(self):
        return [chr(ord('A') + r * self.SIZE + c) for r in range(self.SIZE) for c in range(self.SIZE) if self.is_active(r, c)]

    def is_legal(self, letter: str):
        cell = self.letter_to_cell(letter)
        return cell is not None and self.is_active(*cell)

    def move(self, letter: str):
        cell = self.letter_to_cell(letter)
        if cell is None or not self.is_active(*cell):
            return False
        r, c = cell
        self.grid[r][c] -= 1
        return True

    def numRegions(self):
        """Count connected groups of active cells (8-neighbour adjacency)."""
        visited = set()
        count = 0
        for r in range(self.SIZE):
            for c in range(self.SIZE):
                if self.is_active(r, c) and (r, c) not in visited:
                    count += 1
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
        return sum(1 for r in range(self.SIZE) for c in range(self.SIZE) 
                   if self.is_hinger(r, c))

    def successors(self):
        """Yield every state reachable by removing one counter"""
        for letter in self.legal_moves():
            nxt = self.copy()
            nxt.move(letter)
            yield nxt

def tester():
    s1 = [[1,1,0,0,1],
          [1,1,0,0,0],
          [0,0,1,1,1],
          [0,0,0,1,1],
          [0,0,0,0,1]]
    sa = State(s1)
    print(sa)

    assert sa.numRegions() == 2
    assert sa.cost(4, 4) == 2
    assert not sa.is_hinger(4, 4)

    assert sa.move('Y')
    assert sa.is_hinger(2, 2)
    assert sa.cost(2, 2) == 3
    assert sa.move('M')
    assert sa.numRegions() == 3

    # edge cases
    assert State([[0]*5 for _ in range(5)]).numRegions() == 0
    assert not sa.move('M')
    assert not sa.move('Z')
    assert not sa.move('a1')
    assert len(list(State(s1).successors())) == len(State(s1).legal_moves())

    # diagonal chain: middle two are hingers, ends and the lone cells are not
    chain = State([[0,1,0,0,0],
                   [0,0,1,0,0],
                   [0,0,0,1,0],
                   [0,0,0,0,1],
                   [1,0,0,0,0]])
    assert chain.numHingers() == 2
    assert chain.numRegions() == 2
    print("All tests passed.")

if __name__ == "__main__":
    tester()