import sys
from srcs.visualizer.game import Renderer
from srcs.parsing.parser import Parser
from srcs.solver.solver import Solver


if __name__ == "__main__":
    argv = sys.argv
    argc = len(argv)

    if argc != 2:
        sys.exit(0)

    p = Parser(argv[1])
    map_config = p.create_map_data()

    if not map_config:
        sys.exit(0)

    game = Renderer(map_config)

    game.run()

    # solv = Solver(map_config)
    # solv._generate_solution()
