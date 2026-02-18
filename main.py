import sys
from srcs.visualizer.game import Renderer
from srcs.parsing.parser import Parser


if __name__ == "__main__":
    argv = sys.argv
    argc = len(argv)

    if argc != 2:
        sys.exit(1)

    p = Parser(argv[1])
    map_config = p.create_map_data()
    if not map_config:
        sys.exit(1)
    game = Renderer(map_config)

    game.run()
