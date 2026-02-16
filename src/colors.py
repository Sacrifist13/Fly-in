class Color:
    def __init__(self) -> None:
        """
        Centralized color management for multi-interface rendering.

        Stores a predefined dictionary mapping color names to their
        respective ANSI escape codes (terminal), RGB tuples (Pygame),
        and Hexadecimal strings (Textual).
        """

        self.c = {
            "red": {"ansi": "\033[91m", "rgb": (255, 0, 0), "hex": "#FF0000"},
            "green": {
                "ansi": "\033[92m",
                "rgb": (0, 255, 0),
                "hex": "#00FF00",
            },
            "blue": {"ansi": "\033[94m", "rgb": (0, 0, 255), "hex": "#0000FF"},
            "yellow": {
                "ansi": "\033[93m",
                "rgb": (255, 255, 0),
                "hex": "#FFFF00",
            },
            "cyan": {
                "ansi": "\033[96m",
                "rgb": (0, 255, 255),
                "hex": "#00FFFF",
            },
            "white": {
                "ansi": "\033[97m",
                "rgb": (255, 255, 255),
                "hex": "#FFFFFF",
            },
            "reset": {"ansi": "\033[0m", "rgb": (0, 0, 0), "hex": "#000000"},
        }
