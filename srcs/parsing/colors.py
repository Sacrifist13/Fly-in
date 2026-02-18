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
            "black": {"ansi": "\033[30m", "rgb": (0, 0, 0), "hex": "#000000"},
            "orange": {
                "ansi": "\033[38;5;208m",
                "rgb": (255, 165, 0),
                "hex": "#FFA500",
            },
            "purple": {
                "ansi": "\033[35m",
                "rgb": (128, 0, 128),
                "hex": "#800080",
            },
            "magenta": {
                "ansi": "\033[95m",
                "rgb": (255, 0, 255),
                "hex": "#FF00FF",
            },
            "gray": {
                "ansi": "\033[90m",
                "rgb": (128, 128, 128),
                "hex": "#808080",
            },
            "brown": {
                "ansi": "\033[38;5;94m",
                "rgb": (139, 69, 19),
                "hex": "#8B4513",
            },
            "gold": {
                "ansi": "\033[38;5;220m",
                "rgb": (255, 215, 0),
                "hex": "#FFD700",
            },
            "maroon": {
                "ansi": "\033[38;5;52m",
                "rgb": (128, 0, 0),
                "hex": "#800000",
            },
            "crimson": {
                "ansi": "\033[38;5;161m",
                "rgb": (220, 20, 60),
                "hex": "#DC143C",
            },
            "lime": {
                "ansi": "\033[38;5;118m",
                "rgb": (50, 205, 50),
                "hex": "#32CD32",
            },
            "darkgray": {
                "ansi": "\033[38;5;118m",
                "rgb": (96, 96, 96),
                "hex": "#606060",
            },
            "darkdarkgray": {
                "ansi": "\033[38;5;118m",
                "rgb": (64, 64, 64),
                "hex": "#404040",
            },
            "hover": {
                "ansi": "\033[38;5;39m",
                "rgb": (0, 191, 255),
                "hex": "#00BFFF",
            },
            "reset": "\033[0m",
        }
