from typing import Dict, List, Tuple, Set
from wa import WA
from tm import TM


class WFARConfig:
    def __init__(
        self,
        tm_state: int = 0,
        tm_read: int = 0,
        left_wa_state: int = 0,
        right_wa_state: int = 0,
        lower_bound: int | None = 0,
        upper_bound: int | None = 0,
    ):
        self.tm_state = tm_state
        self.tm_read = tm_read
        self.left_wa_state = left_wa_state
        self.right_wa_state = right_wa_state
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, WFARConfig):
            return False
        return (
            self.tm_state == other.tm_state
            and self.tm_read == other.tm_read
            and self.left_wa_state == other.left_wa_state
            and self.right_wa_state == other.right_wa_state
            and self.lower_bound == other.lower_bound
            and self.upper_bound == other.upper_bound
        )

    def __hash__(self) -> int:
        return hash(
            (
                self.tm_state,
                self.tm_read,
                self.left_wa_state,
                self.right_wa_state,
                self.lower_bound,
                self.upper_bound,
            )
        )

    def matches(self, other: "WFARConfig") -> bool:
        """Check if this config matches another, considering that None bounds are more general.
        Returns True if this config is more general than or equal to other."""
        if (
            self.tm_state != other.tm_state
            or self.tm_read != other.tm_read
            or self.left_wa_state != other.left_wa_state
            or self.right_wa_state != other.right_wa_state
        ):
            return False

        if self.lower_bound is not None and other.lower_bound is not None:
            if self.lower_bound > other.lower_bound:
                return False

        if self.upper_bound is not None and other.upper_bound is not None:
            if self.upper_bound < other.upper_bound:
                return False

        # Accepted config [0] A0 [0] ≥3 ≤7 does not match [0] A0 [0] - ≤7
        # However, since "other" should come from closure algorithm, we should
        # never be in the case where one of its bound is -, hence this case check
        # is not super relevant.
        if other.lower_bound is None and self.lower_bound is not None:
            return False

        # Same as above.
        if other.upper_bound is None and self.upper_bound is not None:
            return False

        # Accepted config [0] A0 [0] - ≤7 matches [0] A0 [0] ≥3 ≤0
        return True

    def format(self) -> str:
        """Format config as [left_wa] TMstateTMread [right_wa] ≥lower ≤upper"""
        tm_state_char = chr(ord("A") + self.tm_state)
        lower_str = f"≥{self.lower_bound}" if self.lower_bound is not None else "-"
        upper_str = f"≤{self.upper_bound}" if self.upper_bound is not None else "-"
        return f"[{self.left_wa_state}] {tm_state_char}{self.tm_read} [{self.right_wa_state}] {lower_str} {upper_str}"

    @classmethod
    def from_string(cls, config_str: str) -> "WFARConfig":
        parts = config_str.split(",")
        if len(parts) != 6:
            raise ValueError("Invalid WFARConfig format")

        # Convert TM state letter to number (A=0, B=1, ..., E=4)
        tm_state = ord(parts[0]) - ord("A")
        tm_read = int(parts[1])
        left_wa_state = int(parts[2])
        right_wa_state = int(parts[3])
        lower_bound = int(parts[4]) if parts[4] != "-" else None
        upper_bound = int(parts[5]) if parts[5] != "-" else None

        return cls(
            tm_state, tm_read, left_wa_state, right_wa_state, lower_bound, upper_bound
        )


class WFARCert:
    def __init__(
        self,
        tm: str,
        left_wa: WA,
        right_wa: WA,
        left_special_sets: Tuple[Set[int], Set[int]],
        right_special_sets: Tuple[Set[int], Set[int]],
        accepted_configs: Set[WFARConfig],
    ):
        self.tm = TM(tm)
        self.left_wa = left_wa
        self.right_wa = right_wa
        self.left_special_sets = left_special_sets  # (>=0 states, <=0 states)
        self.right_special_sets = right_special_sets  # (>=0 states, <=0 states)
        self.accepted_configs = accepted_configs

    def get_next_configs(self, config: WFARConfig) -> Set[WFARConfig]:
        """Get all possible next configurations from the given configuration.
        Returns a set of WFARConfig objects representing possible next states."""
        next_configs: Set[WFARConfig] = set()

        # Get TM transition
        tm_trans = self.tm(config.tm_state, config.tm_read)
        if tm_trans is None:
            return next_configs  # No transition defined

        write, move, next_tm_state = tm_trans

        if move == "R":
            # Get left WA transition for the written symbol
            left_trans = self.left_wa.transitions[config.left_wa_state][str(write)]
            next_left_state, left_weight = left_trans

            # Find all right WA transitions that can reach the target state
            incoming_right = self.right_wa.get_incoming_transitions(
                config.right_wa_state
            )

            for source_right, symbol, right_weight in incoming_right:
                # Compute weight change
                weight_change = left_weight - right_weight

                # Compute new bounds
                new_lower = (
                    config.lower_bound + weight_change
                    if config.lower_bound is not None
                    else None
                )
                new_upper = (
                    config.upper_bound + weight_change
                    if config.upper_bound is not None
                    else None
                )

                # Create new config
                next_config = WFARConfig(
                    next_tm_state,
                    int(symbol),  # symbol is "0" or "1"
                    next_left_state,
                    source_right,
                    new_lower,
                    new_upper,
                )
                next_configs.add(next_config)
        else:  # move == "L"
            # Get right WA transition for the written symbol
            right_trans = self.right_wa.transitions[config.right_wa_state][str(write)]
            next_right_state, right_weight = right_trans

            # Find all left WA transitions that can reach the target state
            incoming_left = self.left_wa.get_incoming_transitions(config.left_wa_state)

            for source_left, symbol, left_weight in incoming_left:
                # Compute weight change
                weight_change = right_weight - left_weight

                # Compute new bounds
                new_lower = (
                    config.lower_bound + weight_change
                    if config.lower_bound is not None
                    else None
                )
                new_upper = (
                    config.upper_bound + weight_change
                    if config.upper_bound is not None
                    else None
                )

                # Create new config
                next_config = WFARConfig(
                    next_tm_state,
                    int(symbol),  # symbol is "0" or "1"
                    source_left,
                    next_right_state,
                    new_lower,
                    new_upper,
                )
                next_configs.add(next_config)

        return next_configs

    def find_matching_config(self, config: WFARConfig) -> WFARConfig | None:
        """Find a configuration in the accepted set that matches the given config.
        Returns the matching config if found, None otherwise."""
        for accepted in self.accepted_configs:
            if accepted.matches(config):
                return accepted
        return None

    def is_accepted(self, config: WFARConfig) -> bool:
        """Check if a configuration is accepted, considering that None bounds are more general."""
        return self.find_matching_config(config) is not None

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

        # Parse accepted configurations (if present)
        accepted_configs = set()
        if len(parts) > 5:
            for config_str in parts[5].split("_"):
                if config_str:
                    accepted_configs.add(WFARConfig.from_string(config_str))

        return cls(
            tm,
            left_wa,
            right_wa,
            (left_ge0, left_le0),
            (right_ge0, right_le0),
            accepted_configs,
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
