from typing import List
from pydantic import BaseModel, Field, model_validator
from .colors import Color


class HubModel(BaseModel):
    """
    Pydantic model representing a physical drone hub in the network.

    Defines and validates the topological properties of a hub, including
    its spatial coordinates, operational zone classification, optional
    visual color, and maximum concurrent drone capacity.
    """

    name: str = Field(min_length=1, description="Unique hub identifier.")
    x: int = Field(description="X-coordinate position.")
    y: int = Field(description="Y-coordinate position.")
    zone: str = Field(
        min_length=1, description="Operational zone classification."
    )
    color: str | None = Field(
        default=None, description="Optional visual color indicator."
    )
    max_drones: int = Field(
        ge=0, description="Maximum concurrent drone capacity."
    )

    @model_validator(mode="after")
    def validate_hub_model(self) -> "HubModel":
        """
        Validates the hub's operational zone classification.
        Validates the color
        Raises:
            ValueError: If the 'zone' value is not allowed.
        """

        RED = "\033[91m"
        YELLOW = "\033[93m"
        BOLD = "\033[1m"
        RESET = "\033[0m"

        valid_zones = ["normal", "blocked", "restricted", "priority"]
        color = Color()

        if self.zone not in valid_zones:
            err = (
                f"Invalid zone classification: '{self.zone}'. "
                f"Expected one of: {', '.join(valid_zones)}."
            )
            raise ValueError(
                f"\n{RED}{BOLD} • {RESET}{YELLOW}{err}" f"{RESET}"
            )
        if self.color not in color.c:
            self.color = None

        return self


class ConnectionModel(BaseModel):
    """
    Pydantic model representing a connection between two hubs.

    Defines and validates the bidirectional link between a starting
    and ending zone, including the maximum drone traffic capacity
    allowed on this specific route.
    """

    zone_1: str = Field(min_length=1, description="Name of the 1st hub")
    zone_2: str = Field(min_length=1, description="Name of the 2nd hub")
    max_link_capacity: int = Field(
        ge=0, description="Max drones link-capacity"
    )


class MapModel(BaseModel):
    """
    Pydantic model representing the global drone network map.

    Aggregates all hubs, connections, and system metadata. Validates
    the overall topological integrity by preventing overlaps, unknown
    endpoints, duplicate identifiers, and invalid routing links.
    """

    nb_drones: int = Field(ge=1, description="Number of drones")
    start_hub: HubModel = Field(description="Start hub")
    end_hub: HubModel = Field(description="End hub")
    hubs: List[HubModel] = Field(description="Hub Zones")
    connections: List[ConnectionModel] = Field(description="Connection")

    @model_validator(mode="after")
    def validate_map_model(self) -> "MapModel":
        """
        Validates the global topological integrity of the drone map.

        Cross-references hubs and connections to ensure no coordinate
        overlaps, no duplicate identifiers, and no unresolved endpoints.
        It accumulates all structural errors into a single exception.

        Returns:
            MapModel: The fully validated global map instance.

        Raises:
            ValueError: If any topological or naming conflicts occur.
        """

        RED = "\033[91m"
        YELLOW = "\033[93m"
        BOLD = "\033[1m"
        RESET = "\033[0m"

        errors = []

        coordinates = set([(h.x, h.y) for h in self.hubs])
        start_c = (self.start_hub.x, self.start_hub.y)
        end_c = (self.end_hub.x, self.end_hub.y)

        hub_names = [self.start_hub.name, self.end_hub.name] + [
            h.name for h in self.hubs
        ]

        connection_names = [z.zone_1 for z in self.connections] + [
            z.zone_2 for z in self.connections
        ]

        unknown_zones = [
            zone for zone in connection_names if zone not in hub_names
        ]

        if len(coordinates) != len(self.hubs):
            all_c = [(h.x, h.y) for h in self.hubs]
            seen = set()
            dupes = set()
            for c in all_c:
                if c in seen:
                    dupes.add(c)
                else:
                    seen.add(c)
            dupe_str = ", ".join([f"({x}, {y})" for x, y in dupes])
            errors.append(
                f"Duplicate physical coordinates among hubs: {dupe_str}."
            )

        if start_c in coordinates:
            errors.append(
                f"Start hub coordinates {start_c} conflict with an "
                "existing hub."
            )

        if end_c in coordinates:
            errors.append(
                f"End hub coordinates {end_c} conflict with an existing hub."
            )

        if start_c == end_c:
            errors.append(
                f"Start and End hubs cannot share coordinates: {start_c}."
            )

        if len(hub_names) != len(set(hub_names)):
            duplicate = list(
                set([name for name in hub_names if hub_names.count(name) != 1])
            )
            errors.append(
                "Duplicate hub identifiers detected: "
                f"{', '.join(set(duplicate))}."
            )

        if unknown_zones:
            errors.append(
                "Unresolved connection endpoints. Undefined zones: "
                f"{', '.join(set(unknown_zones))}"
            )

        seen_connections = set()
        for c in self.connections:
            connection = tuple(sorted([c.zone_1, c.zone_2]))

            if c.zone_1 == c.zone_2:
                errors.append(
                    f"Self-loop detected: Hub '{c.zone_1}' "
                    "cannot connect to itself."
                )

            elif connection in seen_connections:
                errors.append(
                    "Duplicate connection detected between hubs "
                    f"'{c.zone_1}' and '{c.zone_2}'."
                )

            else:
                seen_connections.add(connection)

        if errors:
            s = ""
            for err in errors:
                s += f"\n{RED}{BOLD} • {RESET}{YELLOW}{err}" f"{RESET}"
            raise ValueError(s)

        return self
