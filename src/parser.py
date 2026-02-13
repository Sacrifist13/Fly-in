import re
import sys
import typing as tp
from pydantic import BaseModel
from pathlib import Path
from collections import defaultdict


class Reader:

    RED = "\033[91m"
    YELLOW = "\033[93m"
    BOLD = "\033[1m"
    RESET = "\033[0m"

    def __init__(self, file_path: str) -> None:
        self.file_path = Path(file_path)

    def scan_file_format(self) -> False:

        errors = []

        REG_NB = "^(nb_drones)\\s*:\\s*(\\d+)\\s*$"
        REG_HUB = (
            "^(start_hub|end_hub|hub):\\s*([^\\s-]+)\\s+(\\d+)\\s+"
            "(\\d+)\\s*(?:\\s+\\[\\s*(.*?)\\s*\\])?\\s*$"
        )
        REG_CONNECTION = (
            "^(connection)\\s*:\\s*([^\\s-]+)\\s*-\\s*([^\\s-]+)\\"
            "s*(?:\\s+\\[(.*?)\\])?\\s*$"
        )

        REGEX = [REG_NB, REG_HUB, REG_CONNECTION]

        valid_reg_groups = []

        if not self.file_path.exists():
            print(
                f"\n{self.RED}{self.BOLD}❌ [ERROR] File not found: "
                f"{self.file_path.name}{self.RESET}\n",
                file=sys.stderr,
            )
            return False

        try:
            with open(self.file_path, "r") as f:
                lines = [
                    (x + 1, line.strip())
                    for x, line in enumerate(f.readlines())
                    if not line.startswith("#")
                    if line.strip() != ""
                ]

                if not lines:
                    print(
                        f"\n{self.RED}{self.BOLD}❌ [ERROR] File is empty: "
                        f"{self.file_path.name}{self.RESET}\n",
                        file=sys.stderr,
                    )
                    return False

                if not lines[0][1].startswith("nb_drones"):
                    errors.append(
                        f"Line {lines[0][0]} | First line must define the "
                        "'nb_drones' parameter."
                    )

                for line in lines:
                    valid = False
                    for reg in REGEX:
                        g = re.match(reg, line[1])
                        if g:
                            valid_reg_groups.append(g.groups())
                            valid = True
                            break
                        else:
                            continue
                    if not valid:
                        errors.append(
                            f"{f'Line {line[0]}':<10} | "
                            f"Invalid syntax -> {line[1]}"
                        )

                nb_drones_lines = 0
                start_hub_lines = 0
                end_hub_lines = 0

            for group in valid_reg_groups:
                if group[0] == "nb_drones":
                    nb_drones_lines += 1
                elif group[0] == "start_hub":
                    start_hub_lines += 1
                elif group[0] == "end_hub":
                    end_hub_lines += 1

            if nb_drones_lines != 1:
                errors.append(
                    f"{'Parameter':<10} | 'nb_drones' must appear exactly "
                    f"once (found {nb_drones_lines})."
                )
            if start_hub_lines != 1:
                errors.append(
                    f"{'Parameter':<10} | 'start_hub' must appear exactly "
                    f"once (found {start_hub_lines})."
                )
            if end_hub_lines != 1:
                errors.append(
                    f"{'Parameter':<10} | 'end_hub' must appear exactly "
                    f"once (found {end_hub_lines})."
                )

            if errors:
                print(
                    f"\n{self.RED}{self.BOLD}=== ❌ PARSING ERRORS IN "
                    f"'{self.file_path.name}' ==={self.RESET}\n",
                    file=sys.stderr,
                )

                for err in errors:
                    print(
                        f"{self.RED} • {self.RESET}{self.YELLOW}"
                        f"{err}{self.RESET}",
                        file=sys.stderr,
                    )
                return False

            self.valid_reg_groups = valid_reg_groups

            return True

        except PermissionError:
            print(f"File <{self.file_path}> permission error.")
            return False

        except Exception as e:
            print(
                f"\33[31mUnexpected error reading file -> "
                f"{type(e).__name__}: {e}"
            )
            return False
