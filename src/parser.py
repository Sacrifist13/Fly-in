from typing import Dict, List, Any
from pydantic import BaseModel
from pathlib import Path
from collections import defaultdict


class Reader:
    def __init__(self, file_path: str) -> None:
        self.file_path = file_path

    def scan_file_format(self) -> False:
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
                    return False

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
                    errors.append(("UNKNOWN", unknown_lines))

                if len(nb_drone_lines) != 1:
                    errors.append(("", nb_drone_lines))

                if len(start_hub_lines) != 1:
                    errors.append(("start_hub", start_hub_lines))

                if len(end_hub_lines) != 1:
                    errors.append(("end_hub", end_hub_lines))

                if errors:
                    print("\33[31m")
                    for error_type, line in errors:
                        print(f"{error_type}")
                    print("\33[0m")

        except FileNotFoundError:
            print(f"File <{self.file_path}> not found.")
