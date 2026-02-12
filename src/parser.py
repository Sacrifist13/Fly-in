from typing import Dict, List, Any
from pydantic import BaseModel
from pathlib import Path
from collections import defaultdict


class Reader:
    def __init__(self, file_path: str) -> None:
        self.file_path = Path(file_path)
        self.logout_error_file = Path("logout/errors.txt")

    def scan_file_format(self) -> False:

        if not self.file_path.exists():
            print("zeubi")
        try:
            with open(self.file_path, "r") as f:
                lines = [
                    (x + 1, line.strip())
                    for x, line in enumerate(f.readlines())
                    if not line.startswith("#")
                    if line.strip() != ""
                ]

                path = Path(self.file_path)

                self.data = {}

                if not lines:
                    print(f"\33[31m{path.name} -> file is empty\33[0m")
                    return False

                errors = []

                if not lines[0][1].startswith("nb_drones:"):
                    errors.append(("first line", [lines[0]]))

                unknown_lines = [
                    line
                    for line in lines
                    if not line[1].startswith("nb_drones: ")
                    if not line[1].startswith("start_hub: ")
                    if not line[1].startswith("end_hub: ")
                    if not line[1].startswith("hub: ")
                    if not line[1].startswith("connection: ")
                ]

                nb_drone_lines = [
                    line for line in lines if line[1].startswith("nb_drones:")
                ]

                start_hub_lines = [
                    line for line in lines if line[1].startswith("start_hub:")
                ]

                end_hub_lines = [
                    line for line in lines if line[1].startswith("end_hub:")
                ]

                if unknown_lines:
                    errors.append(("unknown parameter", unknown_lines))

                if len(nb_drone_lines) != 1:
                    errors.append(("nb_drones", nb_drone_lines))

                if len(start_hub_lines) != 1:
                    errors.append(("start_hub", start_hub_lines))

                if len(end_hub_lines) != 1:
                    errors.append(("end_hub", end_hub_lines))

                if errors:
                    self.logout_error_file.parent.mkdir(
                        parents=True, exist_ok=True
                    )
                    with self.logout_error_file.open(
                        "w", encoding="utf-8"
                    ) as f:
                        s = "\33[31m"
                        s += "=== FORMAT FILE ERROR ===\n"
                        for error_type, lines_error in errors:
                            s += f"\nError {error_type} -> \n"
                            for n, line in lines_error:
                                s += f"\tline {n} -> {line}\n"
                            if error_type == "first line":
                                s += "\n[First line should be only nb_drones"
                                s += " parameter]\n"
                            elif error_type != "unknown parameter":
                                s += "\n[Should be only one line for "
                                s += "this parameter]\n"
                            else:
                                s += "\n[Should be only one of this ("
                                s += "nb_drones, start_hub, end_hub, hub, "
                                s += "connection]\n"
                            s += f"{'-' * 30}\n"
                        s += "\33[0m"
                        print(s)
                    return

        except FileNotFoundError:
            print(f"File <{self.file_path}> not found.")
