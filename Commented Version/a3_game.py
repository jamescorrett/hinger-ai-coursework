# Header: A09, My Student ID: 100523557, others student ids 100538247, 100534304, 100539397

# a3_game.py - the game loop for Hinger.
# a1_state.py knows the BOARD and the rules (legal moves, costs, hingers).
# This file knows the GAME: whose turn it is, each player's score, and who wins.

from a1_state import State

# Every player starts on 100 points, and a hinger move earns +100.
# Keeping them as named constants means there are no "magic numbers" in the code
# and they only need changing in one place.
Start_Score = 100
Hinger_Bonus = 100


def _player_names(agentA, agentB):
    """Display names; humans (None) get a label, and clashes are explained."""
    # An agent of None means a human player, so it has no .name to read.
    # Give humans a label instead.
    a = agentA.name if agentA is not None else "Human A"
    b = agentB.name if agentB is not None else "Human B"
    # If both players share a name (e.g. two default-named agents), add (A)/(B)
    # so the printed output and the returned winner are not ambiguous.
    if a == b:
        a, b = a + " (A)", b + " (B)"
    return a, b


def _get_move(agent, state, name):
    """Ask an agent or a human for a move. Returns a string (possibly junk)"""
    # This is the ONE place a move is fetched. In Part 2 (a3_advGame.py) the
    # human branch can be swapped for a hand-sign input without touching play().
    if agent is None:
        # Human: show the board, then read typed input.
        print(state)
        # .strip() removes stray spaces and .upper() lets "m" count as "M".
        return input(f"{name}, enter your move (A-Y, or Z to give up): ").strip().upper()
    # AI / scripted agent: it looks at the state and returns a letter (or None).
    move = agent.next_move(state)
    # Only upper-case it if it is a string, so None doesn't crash .upper().
    # Anything invalid is caught later in play() as an illegal move.
    return move.upper() if isinstance(move, str) else move


def play(state, agentA, agentB, verbose = True):
    """
    Play a full game, agentA moves first. An agent of None is a human
    Returns (winner_name, winner_score), or None for a draw
    """
    # Work on a COPY so the caller's board is never changed by playing the game.
    state = state.copy()
    agents = [agentA, agentB]                      # index 0 = A, index 1 = B
    names = list(_player_names(agentA, agentB))    # display names for A and B
    scores = [Start_Score, Start_Score]            # both players start on 100
    turn = 0                                       # 0 = A's go, 1 = B's go

    # The game continues while there are still counters on the board.
    while state.legal_moves():
        # "me" is the player moving now, "opp" is the other player.
        me, opp = turn, 1 - turn
        move = _get_move(agents[me], state, names[me])

        # 'Z' is the "end the game" action: the player who plays it loses
        # immediately, so the opponent is returned as the winner.
        if move == "Z":
            if verbose:
                print(f"{names[me]} gave up!")
            return names[opp], scores[opp]

        # Illegal move (empty cell, letter outside A-Y, None, junk text):
        # the player loses immediately and the opponent wins.
        if not state.is_legal(move):
            if verbose:
                print(f"{names[me]} made an illegal move: ({move!r}) and loses!")
            return names[opp], scores[opp]

        # cost and bonus are measured BEFORE the counter is removed
        # (both depend on what the board looks like at the moment of the move).
        r, c = State.letter_to_cell(move)               # letter -> (row, column)
        cost = state.cost(r, c)                         # number of active neighbours
        bonus = Hinger_Bonus if state.is_hinger(r, c) else 0   # +100 only for a hinger
        scores[me] += bonus - cost                      # net change to this player's score
        state.move(move)                                # NOW remove the counter

        if verbose:
            print (f"{names[me]} plays {move}, cost {cost} and bonus {bonus}  score: {scores[me]}")
        # Hand the turn to the other player.
        turn = opp

    # all counters removed: compare scores
    # The loop above only ends when the board is empty, so the higher score wins.
    if scores[0] == scores[1]:
        if verbose:
            print(f"Game over, draw! Both players scored {scores[0]}")
        return None                                     # None means a draw

    # w = index of the winner (0 if A has the higher score, otherwise 1).
    w = 0 if scores[0] > scores[1] else 1
    if verbose:
        print(f"Game over, {names[w]} wins with score {scores[w]} vs {scores[1-w]}")
    return names[w], scores[w]


class ScriptedAgent:
    """Test Helper: plays a fixed list of moves"""
    # A stand-in player for testing. It replays moves from a list, so each rule
    # can be tested the same way every time, without needing a real AI.
    def __init__(self, name, moves):
        self.name = name              # play() reads .name to display and return the winner
        self.moves = list(moves)      # e.g. "GM" becomes ['G', 'M']

    def next_move(self, state):
        # Hand out the next scripted move, or None if the script has run out
        # (play() treats None as an illegal move).
        return self.moves.pop(0) if self.moves else None


def tester():
    # Small helper to build a 5x5 board with a single counter on each given
    # (row, column) cell and nothing elsewhere.
    def board(*cells):
        g = [[0] * 5 for _ in range(5)]
        for r, c in cells:
            g[r][c] = 1
        return State(g)

    # win: A is next to B, so A pays cost 1(99), B pays 0(100) so B wins
    # (A is played first while B is still there, so it costs 1. By B's turn
    # A is gone, so B costs 0.)
    res = play(board((0, 0), (0 , 1)), ScriptedAgent("P1", "A"), ScriptedAgent("P2", "B"))
    assert res == ("P2", 100), res

    # draw: two isolated counters, both pay 0
    # (neither cell has an active neighbour, so both stay on 100)
    res = play(board((0, 0), (4, 4)), ScriptedAgent("P1", "A"), ScriptedAgent("P2", "Y"))
    assert res is None

    # Z loses immediately
    res = play(board((0, 0), (4, 4)), ScriptedAgent("P1", "Z"), ScriptedAgent("P2", ""))
    assert res == ("P2", 100)

    # illegal move (empty cell), then non-existent call
    # 'C' is an empty cell and '7' is not a letter A-Y, so P1 loses both times.
    res = play(board((0, 0)), ScriptedAgent("P1", "C"), ScriptedAgent("P2", ""))
    assert res == ("P2", 100)
    res = play(board((0, 0)), ScriptedAgent("P1", "7"), ScriptedAgent("P2", ""))
    assert res == ("P2", 100)

    # Hinger Bonus: 3-cell diagonal chain; middle cell is a hinger
    # P1 plays G (cost 2, bonus 100) -> 198. P2 plays A (cost 0) -> 100.
    # P1 plays M (cost 0) -> stays 198. P1 wins 198 vs 100.
    chain = board((0, 0), (1, 1), (2, 2))
    res = play(chain, ScriptedAgent("P1", "GM"), ScriptedAgent("P2", "A"))
    assert res is not None and res[0] == "P1" and res[1] == 100 + 100 - 2

    # callers state is untouched
    # play() works on a copy, so the original board still has its counter at A.
    s = board((0, 0))
    play(s, ScriptedAgent("P1", "A"), ScriptedAgent("P2", ""))
    assert s.legal_moves() == ['A']

    print("All game tests passed.")


# Run the tests only when this file is executed directly
# (python a3_game.py), not when it is imported by another module.
if __name__ == "__main__":
    tester()