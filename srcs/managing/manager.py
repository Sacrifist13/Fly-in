from typing import List, Dict, Tuple
from srcs.parsing.parser import Parser
from srcs.parsing.models import MapModel
from srcs.solver.graph_solver import Solver
from srcs.parsing.colors import Color
from srcs.visualizer.game import Renderer


class Manager:
    """Coordinates path validation, solving, and rendering.

    Handles argument validation, drone pathfinding solving, and
    orchestrates text-based and visual rendering of solutions.

    Attributes:
        argv: Command-line arguments.
        colors: Color utility for ANSI formatting.
        map_config: Map data and drone configuration.

    Methods:
        __init__: Initialize with command-line arguments.
        validate_args: Validate arguments and parse config file.
        execute: Main execution flow.
        classic_render: Render solutions in text format.
    """

    def __init__(self, argv: List[str]) -> None:
        """
        Initialize the manager with command-line arguments.

        Args:
            argv (List[str]): List of command-line arguments.
        """

        self.argv = argv
        self.colors = Color()

    def validate_args(self) -> bool:
        """
        Validates command-line arguments for the manager.

        Returns:
            bool: True if arguments are valid and map config is set, False
            otherwise.
        """

        red = self.colors.c["red"]["ansi"]
        reset = self.colors.c["reset"]

        p = Parser(self.argv[1])
        if len(self.argv) == 3:

            red = self.colors.c["red"]["ansi"]
            reset = self.colors.c["reset"]

            if self.argv[2] != "--visual":
                print(
                    f"{red}Error: Unknown argument '{self.argv[2]}'"
                    f".\nAvailable flag: --visual{reset}"
                )
                return False

            self.map_config = p.create_map_data()
            if not self.map_config:
                return False

            return True

        if len(self.argv) == 2:

            self.map_config = p.create_map_data()
            if not self.map_config:
                return False

            return True

        print(
            f"{red}Error: Invalid command format.\nUsage: uv run python3 "
            f"main.py <file_path> [--visual]{reset}"
        )
        return False

    def execute(self) -> None:
        """
        Executes the main workflow: validates arguments, generates solutions
        and timeline, renders results, and optionally launches the visualizer
        based on command-line arguments.
        """

        if not self.validate_args():
            return

        if not isinstance(self.map_config, MapModel):
            return

        solver = Solver(self.map_config)
        solutions: Dict[str, List[Tuple]] = solver.generate_solution()
        timeline: Dict[int, Dict[str, List[str]]] = solver.generate_timeline(
            solutions
        )
        if len(self.argv) == 2:
            self.classic_render(solutions, timeline)
            return

        else:
            self.classic_render(solutions, timeline)
            input(
                "\nSimulation complete. Press [ENTER] to "
                "launch the visualizer..."
            )
            render = Renderer(self.map_config)
            render.run()

    def classic_render(
        self,
        solutions: Dict[str, List[Tuple]],
        timeline: Dict[int, Dict[str, List[str]]],
    ) -> None:
        """
        Renders the drone movement timeline in a classic text format.

        Args:
            solutions (Dict[str, List[Tuple]]): Mapping of drone IDs to their
                movement steps, where each step is a tuple containing movement
                details.
            timeline (Dict[int, Dict[str, List[str]]]): Mapping of turn numbers
                to locations and the list of drone IDs present at each
                location.

        Returns:
            None: Outputs the formatted movement timeline to stdout.
        """

        all_turn = set()

        for value in solutions.values():
            for step in value:
                all_turn.add(step[1])
        nb_turn: int = max(all_turn)

        latest_loc = {}

        if not isinstance(self.map_config, MapModel):
            return

        for i in range(1, self.map_config.nb_drones + 1):
            latest_loc["D" + str(i)] = [self.map_config.start_hub.name]

        output = ""
        turn = []

        for i in range(1, nb_turn + 1):
            actual_turn = timeline[i]
            t = []

            for key, v in actual_turn.items():

                for id in v:
                    previous_loc = latest_loc[id][-1]
                    if previous_loc == key:
                        continue

                    t.append(f"{id}-{key}")

            turn.append(" ".join(t))

        output = "\n".join(turn)
        print(output)
