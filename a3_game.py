# Header: A09, My Student ID: 100523557, others student ids 100538247, 100534304, 100539397 

from a1_state import State

Start_Score = 100
Hinger_Bonus = 100

def _player_names(agentA, agentB):
    """Display names; humans (None) get a label, and clashes are explained."""
    a = agentA.name if agentA is not None else "Human A"
    b = agentB.name if agentB is not None else "Human B"
    if a == b:
        a, b = a + " (A)", b + " (B)"
    return a, b
    
def _get_move(agent, state, name):
    """Ask an agent or a human for a move. Returns a string (possibly junk)"""
    if agent is None:
        print(state)
        return input(f"{name}, enter your move (A-Y, or Z to give up): ").strip().upper()
    move = agent.next_move(state)
    return move.upper() if isinstance(move, str) else move

def play(state, agentA, agentB, verbose = True):
    """
    Play a full game, agentA moves first. An agent of None is a human
    Returns (winner_name, winner_score), or None for a draw
    """
    state = state.copy()
    agents = [agentA, agentB]
    names = list(_player_names(agentA, agentB))
    scores = [Start_Score, Start_Score]
    turn = 0
    
    while state.legal_moves():
        me, opp = turn, 1 - turn
        move = _get_move(agents[me], state, names[me])
        
        if move == "Z":
            if verbose:
                print(f"{names[me]} gave up!")
            return names[opp], scores[opp]
        
        if not state.is_legal(move):
            if verbose:
                print(f"{names[me]} made an illegal move: ({move!r}) and loses!")
            return names[opp], scores[opp]
        
        # cost and bonus are measured BEFORE the counter is removed
        r, c = State.letter_to_cell(move)
        cost = state.cost(r, c)
        bonus = Hinger_Bonus if state.is_hinger(r, c) else 0
        scores[me] += bonus - cost
        state.move(move)
        
        if verbose:
            print (f"{names[me]} plays {move}, cost {cost} and bonus {bonus}  score: {scores[me]}")
        turn = opp
        
    # all counters removed: compare scores
    if scores[0] == scores[1]:
        if verbose:
            print(f"Game over, draw! Both players scored {scores[0]}")
        return None

    w = 0 if scores[0] > scores[1] else 1
    if verbose:
        print(f"Game over, {names[w]} wins with score {scores[w]} vs {scores[1-w]}")
    return names[w], scores[w]
    
class ScriptedAgent:
    """Test Helper: plays a fixed list of moves"""
    def __init__(self, name, moves):
        self.name = name
        self.moves = list(moves)
    
    def next_move(self, state):
        return self.moves.pop(0) if self.moves else None
    
def tester():
    def board(*cells):
        g = [[0] * 5 for _ in range(5)]
        for r, c in cells:
            g[r][c] = 1
        return State(g)
    
    # win: A is next to B, so A pays cost 1(99), B pays 0(100) so B wins
    res = play(board((0, 0), (0 , 1)), ScriptedAgent("P1", "A"), ScriptedAgent("P2", "B"))
    assert res == ("P2", 100), res
    
    # draw: two isolated counters, both pay 0
    res = play(board((0, 0), (4, 4)), ScriptedAgent("P1", "A"), ScriptedAgent("P2", "Y"))
    assert res is None
    
    # Z loses immediately
    res = play(board((0, 0), (4, 4)), ScriptedAgent("P1", "Z"), ScriptedAgent("P2", ""))
    assert res == ("P2", 100)
    
    # illegal move (empty cell), then non-existent call
    res = play(board((0, 0)), ScriptedAgent("P1", "C"), ScriptedAgent("P2", ""))
    assert res == ("P2", 100)
    res = play(board((0, 0)), ScriptedAgent("P1", "7"), ScriptedAgent("P2", ""))
    assert res == ("P2", 100)
    
    # Hinger Bonus: 3-cell diagonal chain; middle cell is a hinger
    chain = board((0, 0), (1, 1), (2, 2))
    res = play(chain, ScriptedAgent("P1", "GM"), ScriptedAgent("P2", "A"))
    assert res is not None and res[0] == "P1" and res[1] == 100 + 100 - 2
    
    # callers state is untouched
    s = board((0, 0))
    play(s, ScriptedAgent("P1", "A"), ScriptedAgent("P2", ""))
    assert s.legal_moves() == ['A']
    
    print("All game tests passed.")
    
if __name__ == "__main__":
    tester()