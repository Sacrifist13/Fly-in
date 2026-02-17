import sys
import threading
from visualizer.renderer_game import Renderer
from visualizer.renderer_term import MyApp
from src.parser import Parser


def run_game(app: Renderer) -> None:
    app.run()

if __name__ == "__main__":
    argv = sys.argv
    argc = len(argv)

    if argc != 2:
        sys.exit(1)

    p = Parser(argv[1])
    map_config = p.create_map_data()
    if not map_config:
        sys.exit(1)
    app = MyApp(map_config)
    game = Renderer(map_config)

    #thread_1 = threading.Thread(target=run_game, args=[game])

    #thread_1.start()
    app.run()

    #thread_1.join()
