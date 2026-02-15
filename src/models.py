from pydantic import BaseModel, Field, model_validator


class HubModel(BaseModel):
    """
    Pydantic model representing a physical drone hub in the network.

    Defines and validates the topological properties of a hub, including
    its spatial coordinates, operational zone classification, optional
    visual color, and maximum concurrent drone capacity.
    """

    name: str = Field(min_length=1, description="Unique hub identifier.")
    x: int = Field(ge=0, description="X-coordinate position.")
    y: int = Field(ge=0, description="Y-coordinate position.")
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
        Raises:
            ValueError: If the 'zone' value is not allowed.
        """

        valid_zones = ["normal", "blocked", "restricted", "priority"]

        if self.zone not in valid_zones:
            raise ValueError(
                f"Invalid zone classification: '{self.zone}'. "
                f"Expected one of: {', '.join(valid_zones)}."
            )
        return self


class ConnectionModel(BaseModel):
    zone_1: str = Field(min_length=1, description="Name of the 1st hub")
    zone_2: str = Field(min_length=1, description="Name of the 2nd hub")
    max_link_capacity: int = Field(
        ge=0, description="Max drones link-capacity"
    )
