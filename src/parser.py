import re
import sys
import json
from typing import List, Tuple, Any, Dict
from pathlib import Path


class Parser:

    RED = "\033[91m"
    YELLOW = "\033[93m"
    BOLD = "\033[1m"
    RESET = "\033[0m"

    def __init__(self, file_path: str) -> None:
        self.file_path = Path(file_path)
        self.map: Dict[str, Any] = {}

    def scan_file_format(self) -> List[Tuple[str | Any, ...]] | None:
        """
        Scans and validates the map file structural format using regex.

        Reads the file line by line, ignoring comments and empty lines.
        It validates the syntax against the required patterns for drones,
        hubs, and connections. It ensures exactly one 'nb_drones',
        'start_hub', and 'end_hub' exists. Errors print to stderr.

        Returns:
            List[Tuple[str | Any, ...]] | None: Extracted regex groups for
            each valid line. Returns None if the file is unreadable or if
            any parsing errors are detected.
        """

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
            return None

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
                    return None

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
                return None

            return valid_reg_groups

        except PermissionError:
            print(f"File <{self.file_path}> permission error.")
            return None

        except Exception as e:
            print(
                f"{self.RED}Unexpected error reading file -> "
                f"{type(e).__name__}: {e}{self.RESET}"
            )
            return None

    def _parse_hub_metadata(
        self, metadata: str, invalid_metadata: bool
    ) -> List[str | None] | None:

        parse_metadata: List[str | None] = ["normal", None, "1"]
        valid_param = ["zone", "color", "max_drones"]
        param_find = []
        errors = []

        if not metadata:
            return parse_metadata

        try:
            params = metadata.split()
            for parameter in params:
                param_value = parameter.split("=")

                if not len(param_value) == 2:
                    errors.append(
                        "Invalid hub metadata format: expected 'key=value', "
                        f"got '{parameter}'"
                    )

                else:
                    param, value = param_value

                    if param not in valid_param:
                        errors.append(
                            f"Unknown hub metadata key: '{param}' in "
                            f"'{parameter}'. Allowed keys: "
                            f"{', '.join(valid_param)}"
                        )
                        continue
                    if param in param_find:
                        errors.append(
                            f"Duplicate metadata argument: '{param}'"
                            " is defined multiple times."
                        )
                        continue

                    param_find.append(param)
                    if param == "zone":
                        parse_metadata[0] = value
                    elif param == "color":
                        parse_metadata[1] = value
                    else:
                        parse_metadata[2] = value

            if errors:
                if not invalid_metadata:
                    print(
                        f"\n{self.RED}{self.BOLD}=== ❌ PARSING ERRORS IN "
                        f"'{self.file_path.name}' ==={self.RESET}\n",
                        file=sys.stderr,
                    )
                print(
                    f"{self.YELLOW}Raw metadata block: "
                    f"[{metadata}]{self.RESET}\n",
                    file=sys.stderr,
                )
                for err in errors:
                    print(
                        f"{self.RED} • {self.RESET}{self.YELLOW}"
                        f"{err}{self.RESET}",
                        file=sys.stderr,
                    )

                return None

            return parse_metadata

        except Exception as e:
            print(
                f"{self.RED}Unexpected error parsing file -> "
                f"{type(e).__name__}: {e}{self.RESET}"
            )
            return None

    def _parse_connection_metadata(
        self, metadata: str, invalid_metadata: bool
    ) -> str | None:
        parse_metadata = "1"
        errors = []

        if not metadata:
            return parse_metadata
        try:
            params = metadata.split()
            if len(params) != 1:
                errors.append(
                    f"Too many arguments in connection metadata: expected 1, "
                    f"got {len(params)}."
                )
            else:
                param_value = params[0].split("=")

                if not len(param_value) == 2:
                    errors.append(
                        "Invalid connection metadata format: expected "
                        f"'key=value', got '{param_value}'"
                    )
                else:
                    param, value = param_value

                    if param != "max_link_capacity":
                        errors.append(
                            f"Unknown connection metadata key: '{param}' in "
                            f"'{param_value}'. Allowed key: max_link_capacity"
                        )
                    else:
                        return value

            if errors:
                if not invalid_metadata:
                    print(
                        f"\n{self.RED}{self.BOLD}=== ❌ PARSING ERRORS IN "
                        f"'{self.file_path.name}' ==={self.RESET}\n",
                        file=sys.stderr,
                    )
                print(
                    f"{self.YELLOW}Raw metadata block: "
                    f"[{metadata}]{self.RESET}\n",
                    file=sys.stderr,
                )
                for err in errors:
                    print(
                        f"{self.RED} • {self.RESET}{self.YELLOW}"
                        f"{err}{self.RESET}",
                        file=sys.stderr,
                    )
            return None

        except Exception as e:
            print(
                f"{self.RED}Unexpected error parsing file -> "
                f"{type(e).__name__}: {e}{self.RESET}"
            )
            return None

    def format_data_for_pydantic(self) -> bool:
        """
        Formats validated regex groups into a structured dictionary.

        Calls the file scanner to retrieve regex groups and iterates
        through them, parsing specific metadata for hubs and connections.
        If all data is valid, it populates the 'map' attribute. Errors
        are aggregated to avoid partial parsing and provide feedback.

        Returns:
            bool: True if the dictionary is successfully built and
            formatted, False if any metadata parsing errors occur.
        """

        valid_reg_groups = self.scan_file_format()

        invalid_metadata = False

        if not valid_reg_groups:
            return False

        self.map["hub"] = []
        self.map["connection"] = []

        try:
            for group in valid_reg_groups:

                if group[0] == "nb_drones":
                    self.map[group[0]] = group[1]

                elif "hub" in group[0]:

                    metadata = self._parse_hub_metadata(
                        group[4], invalid_metadata
                    )

                    if not metadata:
                        invalid_metadata = True
                        print(f"{self.YELLOW}{'-' * 20}{self.RESET}")
                        continue

                    if group[0] == "start_hub" or group[0] == "end_hub":
                        self.map[group[0]] = {
                            "name": group[1],
                            "x": group[2],
                            "y": group[3],
                            "zone": metadata[0],
                            "color": metadata[1],
                            "max_drones": metadata[2],
                        }
                    else:
                        self.map["hub"].append(
                            {
                                "name": group[1],
                                "x": group[2],
                                "y": group[3],
                                "zone": metadata[0],
                                "color": metadata[1],
                                "max_drones": metadata[2],
                            }
                        )
                else:
                    metadata = self._parse_connection_metadata(
                        group[3], invalid_metadata
                    )

                    if not metadata:
                        invalid_metadata = True
                        print(f"{self.YELLOW}{'-' * 20}{self.RESET}")
                        continue

                    self.map["connection"].append(
                        {
                            "zone_1": group[1],
                            "zone_2": group[2],
                            "max_link_capacity": metadata,
                        }
                    )
        except Exception as e:
            print(
                f"{self.RED}Unexpected error parsing file -> "
                f"{type(e).__name__}: {e}{self.RESET}"
            )
            return False

        if invalid_metadata:
            return False

        return True
