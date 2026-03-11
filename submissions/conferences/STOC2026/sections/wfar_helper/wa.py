from typing import Dict, List, Tuple, Set
import graphviz  # type: ignore


class WA:
    """Deterministic weighted automaton."""

    def __init__(self, transitions: Dict[int, Dict[str, Tuple[int, int]]]):
        self.transitions = transitions
        self.states = set(transitions.keys())
        # Add states that are only targets
        for state_trans in transitions.values():
            for _, (target, _) in state_trans.items():
                self.states.add(target)

        if not self.is_deterministic():
            raise ValueError("Weighted automaton is not deterministic")

    def get_incoming_transitions(self, state: int) -> List[Tuple[int, str, int]]:
        """Get all transitions that lead to the given state.
        Returns a list of tuples (source_state, symbol, weight) for each incoming transition.
        """
        incoming = []
        for source, trans in self.transitions.items():
            for symbol, (target, weight) in trans.items():
                if target == state:
                    incoming.append((source, symbol, weight))
        return incoming

    def is_deterministic(self) -> bool:
        """Check if the automaton is deterministic.
        Returns True if each state has exactly one transition for each input symbol (0 and 1).
        """
        for state in self.states:
            if state not in self.transitions:
                return False  # State has no transitions
            state_trans = self.transitions[state]
            if len(state_trans) != 2:  # Must have exactly 2 transitions (0 and 1)
                return False
            if "0" not in state_trans or "1" not in state_trans:
                return False
        return True

    @classmethod
    def from_string(cls, wfa_str: str) -> "WA":
        transitions = {}
        states = wfa_str.split("_")

        for state_idx, state_str in enumerate(states):
            state_trans = {}
            zero_trans, one_trans = state_str.split(";")

            # Parse 0 transition
            target, weight = map(int, zero_trans.split(","))
            state_trans["0"] = (target, weight)

            # Parse 1 transition
            target, weight = map(int, one_trans.split(","))
            state_trans["1"] = (target, weight)

            transitions[state_idx] = state_trans

        return cls(transitions)

    def to_dot(self, show_weights: bool = False) -> graphviz.Digraph:
        dot = graphviz.Digraph("WFA")
        dot.attr(rankdir="LR")

        # Add states
        for state in self.states:
            dot.node(str(state), str(state))

        # Add transitions with colors based on weights
        for source, trans in self.transitions.items():
            for symbol, (target, weight) in trans.items():
                color = "green" if weight == 1 else "red" if weight == -1 else "black"
                if show_weights:
                    dot.edge(
                        str(source),
                        str(target),
                        label=f"{symbol}/{weight}",
                        color=color,
                    )
                else:
                    dot.edge(str(source), str(target), label=f"{symbol}", color=color)

        return dot


class WFARCert:
    def __init__(
        self,
        tm: str,
        left_wa: WA,
        right_wa: WA,
        left_special_sets: Tuple[Set[int], Set[int]],
        right_special_sets: Tuple[Set[int], Set[int]],
        accepted_tuples: List[str],
    ):
        self.tm = tm
        self.left_wa = left_wa
        self.right_wa = right_wa
        self.left_special_sets = left_special_sets  # (>=0 states, <=0 states)
        self.right_special_sets = right_special_sets  # (>=0 states, <=0 states)
        self.accepted_tuples = accepted_tuples

    @classmethod
    def from_string(cls, cert_str: str) -> "WFARCert":
        parts = cert_str.split("\n")
        if len(parts) < 5:
            raise ValueError("Invalid certificate format")

        tm = parts[0]
        left_wa = WA.from_string(parts[1])
        right_wa = WA.from_string(parts[2])

        # Parse left special sets
        left_sets = parts[3].split("_")
        left_ge0 = set(map(int, left_sets[0].split(","))) if left_sets[0] else set()
        left_le0 = (
            set(map(int, left_sets[1].split(",")))
            if len(left_sets) > 1 and left_sets[1]
            else set()
        )

        # Parse right special sets
        right_sets = parts[4].split("_")
        right_ge0 = set(map(int, right_sets[0].split(","))) if right_sets[0] else set()
        right_le0 = (
            set(map(int, right_sets[1].split(",")))
            if len(right_sets) > 1 and right_sets[1]
            else set()
        )

        # Parse accepted tuples (if present)
        accepted_tuples = parts[5].split("_") if len(parts) > 5 else []

        return cls(
            tm,
            left_wa,
            right_wa,
            (left_ge0, left_le0),
            (right_ge0, right_le0),
            accepted_tuples,
        )

    def visualize(self, output_prefix: str = "wfa_cert"):
        """Generate visualization for both WAs"""
        # Visualize left WA
        left_dot = self.left_wa.to_dot()
        left_dot.render(f"{output_prefix}_left", format="png", cleanup=True)

        # Visualize right WA
        right_dot = self.right_wa.to_dot()
        right_dot.render(f"{output_prefix}_right", format="png", cleanup=True)

        print(
            f"Visualizations generated as {output_prefix}_left.png and {output_prefix}_right.png"
        )
