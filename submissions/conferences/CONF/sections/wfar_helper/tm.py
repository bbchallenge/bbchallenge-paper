from typing import Tuple, Optional, Union


class TM:
    """Turing Machine with states A-E and symbols 0,1."""

    def __init__(self, transitions: str):
        """Initialize TM from transition string format.
        Format: write0,move0,next0_write1,move1,next1 separated by '_'
        Example: "1RB---_0RC1LC_1RD1RC_1LE1LD_0RA0LE"
        where --- means undefined transition
        The current state is determined by position (first _ is A=0, second is B=1, etc.)
        """
        self.transitions = {}
        for state_idx, trans_str in enumerate(transitions.split("_")):
            if not trans_str:  # Skip empty transitions
                continue
            if len(trans_str) != 6:
                raise ValueError(f"Invalid transition format: {trans_str}")

            # Parse transition for read 0
            if trans_str[0:3] != "---":
                write = int(trans_str[0])  # 0 or 1
                move = trans_str[1]  # L or R
                next_state = ord(trans_str[2]) - ord("A")  # Convert A-E to 0-4
                self.transitions[(state_idx, 0)] = (write, move, next_state)

            # Parse transition for read 1
            if trans_str[3:] != "---":
                write = int(trans_str[3])  # 0 or 1
                move = trans_str[4]  # L or R
                next_state = ord(trans_str[5]) - ord("A")  # Convert A-E to 0-4
                self.transitions[(state_idx, 1)] = (write, move, next_state)

    def __call__(self, state: int, read: int) -> Optional[Tuple[int, str, int]]:
        """Get transition for given state and read symbol.
        Same as get_transition, but allows using TM instance as a function.
        state: 0-4 (A-E)
        read: 0 or 1
        Returns (write, move, next_state) or None if transition is undefined (---).
        next_state is 0-4 (A-E)
        """
        return self.get_transition(state, read)

    def get_transition(self, state: int, read: int) -> Optional[Tuple[int, str, int]]:
        """Get transition for given state and read symbol.
        state: 0-4 (A-E)
        read: 0 or 1
        Returns (write, move, next_state) or None if transition is undefined (---).
        next_state is 0-4 (A-E)
        """
        return self.transitions.get((state, read))

    def has_transition(self, state: int, read: int) -> bool:
        """Check if a transition exists for given state and read symbol.
        state: 0-4 (A-E)
        read: 0 or 1
        """
        return (state, read) in self.transitions
