import pygame
from typing import Tuple, List, Dict
from srcs.parsing.models import MapModel
from srcs.parsing.colors import Color
from rich.console import Console
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table, box
from rich.columns import Columns
from rich.align import Align
from srcs.solver.solver import Solver
import json


class Hub:
    """
    Represents a physical node within the drone infrastructure network.

    This class serves as a data container and state tracker for a hub,
    managing its spatial positioning, operational capacity, and visual
    representation for both graphical (Pygame) and terminal (Rich) rendering.

    Attributes:
        drones (int): The current number of drones stationed at the hub.
        capacity (int): The maximum hosting capacity of the hub.
        name (str): Unique identifier for the hub.
        zone (str): Geographical or operational zone classification.
        x (int): Spatial X-coordinate on the global map.
        y (int): Spatial Y-coordinate on the global map.
        color (Tuple[int, int, int]): RGB color tuple used for Pygame
        color_panel (str): Hexadecimal or named color string used for
        rendering. Rich Terminal UI borders.
    """

    def __init__(
        self,
        capacity: int,
        name: str,
        zone: str,
        x: int,
        y: int,
        color: Tuple,
        color_panel: str,
        drones: int = 0,
    ) -> None:
        self.drones = drones
        self.capacity = capacity
        self.name = name
        self.zone = zone
        self.x = x
        self.y = y
        self.color = color
        self.color_panel = color_panel


class Connection:
    """
    Represents a transit route linking two hubs within the network.

    This class defines the infrastructure for drone movement between specific
    zones, enforcing traffic constraints through capacity limits and tracking
    real-time drone occupancy during the simulation.

    Attributes:
        zone_1 (str): Identifier of the origin or first connected hub.
        zone_2 (str): Identifier of the destination or second connected hub.
        drones (int): Current number of drones performing a transit
            on this route.
        capacity (int): Maximum drone traffic allowed concurrently
            on this connection.
    """

    def __init__(
        self, zone_1: str, zone_2: str, capacity: int, drones: int = 0
    ) -> None:
        self.zone_1 = zone_1
        self.zone_2 = zone_2
        self.drones = drones
        self.capacity = capacity


class Renderer:
    """
    The central visualization engine responsible for multi-interface
    synchronization.

    This engine orchestrates a dual-display environment: a dynamic spatial map
    rendered via Pygame and a real-time diagnostic dashboard rendered via Rich
    Terminal. It manages camera transformations (zoom/pan), event handling,
    and data projection from the MapModel into visual components.

    Attributes:
        map (MapModel): The validated topological data source.
        colors (Color): Palette provider for consistent UI styling.
        camera_x (int): Horizontal offset for the spatial map view.
        camera_y (int): Vertical offset for the spatial map view.
        zoom (float): Current magnification level of the map.
        turn (int): Simulation step counter.
        hub_offset (int): Vertical scroll position for the Hub Terminal UI.
        connection_offset (int): Vertical scroll position for the Connection
        Terminal UI.
        icon_drone (pygame.Surface | None): Optimized graphical asset for
        drone display. screen (pygame.Surface): The main Pygame display
        surface. hubs (List[Hub]): Initialized graphical hub instances.
        connections (List[Connection]): Initialized graphical connection
        instances.
    """

    def __init__(self, map_config: MapModel):
        """
        Initializes the renderer with map data and default view settings.

        Args:
            map_config: An instance of MapModel containing the validated
            network.
        """

        self.map = map_config
        self.colors = Color()
        self.camera_x: int = 0
        self.camera_y: int = 0
        self.zoom: float = 0.5
        self.turn = 0
        self.hub_offset = 0
        self.connection_offset = 0
        self.icon_drone: pygame.Surface | None = None

    def _init_datas(self, screen: pygame.Surface) -> None:
        """
        Initialize the graphical components and simulation data structures.

        This method maps raw map data into Hub and Connection objects for
        rendering. It configures fonts, determines color schemes for
        nodes based on their attributes, and optimizes the drone icon
        surface for alpha transparency.

        Args:
            screen (pygame.Surface): The main Pygame surface used for
                displaying the simulation.
        """

        self.screen = screen
        self.font = pygame.font.SysFont("arial", 16)
        self.hubs: List[Hub] = []
        self.connections: List[Connection] = []

        start_hub = self.map.start_hub
        end_hub = self.map.end_hub

        solver = Solver(self.map)

        self.solutions: Dict[str, List[Tuple]] = solver._generate_solution()

        nb_turn = set()

        for value in self.solutions.values():
            for step in value:
                nb_turn.add(step[1])

        self.max_turn = max(nb_turn)

        self.timeline: Dict[int, Dict[str, List[str]]] = (
            solver._generate_timeline(self.solutions)
        )

        self.hubs.append(
            Hub(
                capacity=start_hub.max_drones,
                name=start_hub.name,
                zone=start_hub.zone,
                x=start_hub.x,
                y=start_hub.y,
                color=(
                    self.colors.c[start_hub.color]["rgb"]
                    if start_hub.color
                    else self.colors.c["darkdarkgray"]["rgb"]
                ),
                color_panel=(
                    self.colors.c[start_hub.color]["hex"]
                    if start_hub.color
                    else self.colors.c["darkdarkgray"]["hex"]
                ),
                drones=self.map.nb_drones,
            )
        )

        self.hubs.append(
            Hub(
                capacity=end_hub.max_drones,
                name=end_hub.name,
                zone=end_hub.zone,
                x=end_hub.x,
                y=end_hub.y,
                color=(
                    self.colors.c[end_hub.color]["rgb"]
                    if end_hub.color
                    else self.colors.c["darkdarkgray"]["rgb"]
                ),
                color_panel=(
                    self.colors.c[end_hub.color]["hex"]
                    if end_hub.color
                    else self.colors.c["darkdarkgray"]["hex"]
                ),
            )
        )

        for hub in self.map.hubs:
            self.hubs.append(
                Hub(
                    capacity=hub.max_drones,
                    name=hub.name,
                    zone=hub.zone,
                    x=hub.x,
                    y=hub.y,
                    color=(
                        self.colors.c[hub.color]["rgb"]
                        if hub.color
                        else self.colors.c["darkdarkgray"]["rgb"]
                    ),
                    color_panel=(
                        self.colors.c[hub.color]["hex"]
                        if hub.color and hub.color != "black"
                        else self.colors.c["darkdarkgray"]["hex"]
                    ),
                )
            )

        for c in self.map.connections:
            self.connections.append(
                Connection(
                    zone_1=c.zone_1,
                    zone_2=c.zone_2,
                    capacity=c.max_link_capacity,
                )
            )

        if self.icon_drone is not None:
            self.icon_drone = self.icon_drone.convert_alpha()

    def _calculate_hub_card(self) -> int:
        """
        Calculate the maximum number of hub cards that fit on the screen.

        Determines the total capacity based on the current terminal size.
        It evaluates the available height and a fixed column width (50%
        of the terminal) to return the optimal grid count for display.

        Returns:
            int: Total number of cards that can be rendered simultaneously.
        """

        console = Console()

        width, height = console.size

        CARD_HEIGHT = 8
        CARD_WIDTH = 30

        available_height = height - 8

        rows = max(1, available_height // CARD_HEIGHT)

        left_panel_width = int(width * 0.5)
        cols = max(1, left_panel_width // CARD_WIDTH)

        return rows * cols

    def _calculate_connection_card(self) -> int:
        """
        Determine the maximum number of connection cards for the UI grid.

        This method calculates the grid capacity by assessing the current
        terminal dimensions. It accounts for a fixed card height and a
        dedicated width (50% of the terminal) to compute the total
        renderable count of connection cards.

        Returns:
            int: The total count of connection cards that can be displayed.
        """

        console = Console()

        width, height = console.size

        CARD_HEIGHT = 6
        CARD_WIDTH = 30

        available_height = height - 8

        rows = max(1, available_height // CARD_HEIGHT)

        left_panel_width = int(width * 0.5)
        cols = max(1, left_panel_width // CARD_WIDTH)

        return rows * cols

    def _generate_hub_grid(self, hub_offset: int) -> Columns:
        """
        Generate a grid of Rich panels representing hub information.

        This method creates a subset of hub cards based on the calculated
        capacity and a given offset. Each card displays the hub's zone,
        coordinates, and real-time drone occupancy with dynamic color
        coding (green for available space, red for full capacity).

        Args:
            hub_offset (int): The starting index for the slice of hubs
                to be displayed in the current view.

        Returns:
            Columns: A Rich Columns object containing the formatted
                hub panels for the UI layout.
        """

        hub_panels = []
        max_panels = self._calculate_hub_card()

        hub_cards = self.hubs[hub_offset : max_panels + hub_offset]

        for hub in hub_cards:
            tab = Table(box=box.ROUNDED, show_header=False, expand=True)
            tab.add_column("Key", style="dim")
            tab.add_column("Value", justify="right")
            tab.add_row("Zone", hub.zone)
            tab.add_row("Coord", f"({hub.x}, {hub.y})")
            status_color = "green" if hub.drones < hub.capacity else "red"
            tab.add_row(
                "Drones",
                f"[bold {status_color}]{hub.drones}/{hub.capacity}[/]",
            )
            panel = Panel(
                tab,
                title=f"[bold]{hub.name}[/]",
                border_style=hub.color_panel,
                expand=False,
            )
            hub_panels.append(panel)

        return Columns(
            hub_panels, expand=True, equal=True, align="center", padding=2
        )

    def _generate_connection_grid(self, connection_offset: int) -> Columns:
        """
        Generate a grid of Rich panels representing connections.

        This method creates a subset of connection cards based on UI
        capacity and an offset. Each card displays drone traffic via
        dynamic color-coded tables. It maps hub colors to the panel's
        title and subtitle to visually link connections to their
        respective endpoints.

        Args:
            connection_offset (int): The starting index for the slice
                of connections to be displayed in the current view.

        Returns:
            Columns: A Rich Columns object containing the formatted
                connection panels for the UI layout.
        """

        connection_panels = []
        max_panels = self._calculate_connection_card()

        connection_cards = self.connections[
            connection_offset : max_panels + connection_offset
        ]

        for connection in connection_cards:
            tab = Table(box=box.ROUNDED, show_header=False, expand=True)
            status_color = (
                "green" if connection.drones < connection.capacity else "red"
            )
            tab.add_row(
                "Drones",
                f"[bold {status_color}]{connection.drones}/"
                f"{connection.capacity}[/]",
            )

            zone_1_color = next(
                hub.color_panel
                for hub in self.hubs
                if hub.name == connection.zone_1
            )
            zone_2_color = next(
                hub.color_panel
                for hub in self.hubs
                if hub.name == connection.zone_2
            )

            border_color = (
                self.colors.c["darkdarkgray"]["hex"]
                if connection.drones < connection.capacity
                else self.colors.c["hover"]["hex"]
            )

            panel = Panel(
                tab,
                title=(f"[bold {zone_1_color}]{connection.zone_1}[/]"),
                subtitle=f"[bold {zone_2_color}]{connection.zone_2}[/]",
                border_style=border_color,
                expand=False,
            )
            connection_panels.append(panel)

        return Columns(
            connection_panels,
            expand=True,
            equal=True,
            align="center",
            padding=2,
        )

    def _create_layout(self) -> Layout:
        """
        Construct and organize the terminal's main dashboard layout.

        This method defines the hierarchical structure of the UI using
        Rich Layouts. It creates a top header for simulation turns and
        splits the bottom section into two panels for real-time hub
        status and connection status monitoring.

        Returns:
            Layout: A Rich Layout object representing the complete
                dashboard architecture with nested panels.
        """

        layout = Layout()
        layout.split_column(
            Layout(name="top", ratio=1), Layout(name="bottom", ratio=9)
        )

        turn = Align(f"[bold]{self.turn}", align="center", vertical="middle")
        layout["top"].update(
            Panel(
                turn,
                title="FLY-IN",
                border_style=self.colors.c["hover"]["hex"],
            )
        )

        layout["bottom"].split_row(Layout(name="left"), Layout(name="right"))

        layout["left"].update(
            Panel(
                self._generate_hub_grid(self.hub_offset),
                title="HUB STATUS",
                border_style=self.colors.c["hover"]["hex"],
            )
        )

        layout["right"].update(
            Panel(
                self._generate_connection_grid(self.connection_offset),
                title="CONNECTION_STATUS",
                border_style=self.colors.c["hover"]["hex"],
            )
        )

        return layout

    def _output_info(self, obj: Hub | Connection | None) -> None:
        """
        Render an overlay information panel for a selected object.

        This method generates a dynamic Pygame surface containing detailed
        metrics for a Hub or Connection. It calculates the panel's size
        based on text width, draws a themed container, and blits
        attribute-value pairs onto the screen at a fixed position.

        Args:
            obj (Hub | Connection | None): The simulation object to
                inspect. If None, the method returns without rendering.
        """

        if not obj:
            return

        def get_min_width(obj: Hub | Connection) -> int:
            """
            Calculate the required panel width based on text metrics.

            This helper measures the pixel width of the longest descriptive
            string (Name for Hubs, or the longest Zone name for
            Connections) using the current font settings to ensure the
            UI container fits the content.

            Args:
                obj (Hub | Connection): The object whose attributes
                    will be rendered.

            Returns:
                int: The width in pixels of the longest text line.
            """

            if isinstance(obj, Hub):
                return self.font.render(
                    f"• Name: {obj.name}", True, self.colors.c["hover"]["rgb"]
                ).get_width()
            else:
                size_1 = self.font.render(
                    f"• Zone 1: {obj.zone_1}",
                    True,
                    self.colors.c["hover"]["rgb"],
                ).get_width()
                size_2 = self.font.render(
                    f"• Zone 2: {obj.zone_2}",
                    True,
                    self.colors.c["hover"]["rgb"],
                ).get_width()
                return size_1 if size_1 > size_2 else size_2

        padding_x = 10
        padding_y = 10
        line_height = 25
        value_column_x = 90

        if isinstance(obj, Hub):
            width = get_min_width(obj) + 80
            height = 140
            title = "- HUB -"
            output_text = [
                ("Name", str(obj.name)),
                ("Drones", f"{obj.drones}/{obj.capacity}"),
                ("Zone", str(obj.zone)),
                ("Coord", f"({obj.x}, {obj.y})"),
            ]

        else:
            width = get_min_width(obj) + 80
            height = 120
            title = "- CONNECTION -"
            output_text = [
                ("Zone 1", str(obj.zone_1)),
                ("Zone 2", str(obj.zone_2)),
                ("Drones", f"{obj.drones}/{obj.capacity}"),
            ]

        rect = (1, 1, width - 2, height - 2)
        rect_hover = (0, 0, width, height)

        container = pygame.Surface((width, height), pygame.SRCALPHA)

        pygame.draw.rect(
            container,
            self.colors.c["hover"]["rgb"],
            rect_hover,
            width=2,
            border_radius=5,
        )
        pygame.draw.rect(
            container,
            self.colors.c["darkdarkgray"]["rgb"],
            rect,
            border_radius=5,
        )

        t = self.font.render(title, True, self.colors.c["hover"]["rgb"])
        container.blit(t, (padding_x, padding_y))
        padding_y += 30

        for label, value in output_text:
            label_surf = self.font.render(
                f"• {label}:", True, self.colors.c["white"]["rgb"]
            )
            container.blit(label_surf, (padding_x, padding_y))

            value_surf = self.font.render(
                value, True, self.colors.c["hover"]["rgb"]
            )
            container.blit(value_surf, (padding_x + value_column_x, padding_y))

            padding_y += line_height

        self.screen.blit(container, (20, 20))

    def output_commands(self) -> None:
        """
        Render the on-screen command guide for user navigation.

        This method draws a persistent UI overlay in the bottom-right
        corner of the screen. It lists available keyboard and mouse
        controls, including scrolling for hubs and connections, turn
        progression, and camera manipulation, within a styled semi-
        transparent container.
        """

        width = 280
        height = 130
        padding_x = 10
        padding_y = 10

        container = pygame.Surface((width, height), pygame.SRCALPHA)

        rect = (1, 1, width - 2, height - 2)
        rect_hover = (0, 0, width, height)

        pygame.draw.rect(
            container,
            self.colors.c["hover"]["rgb"],
            rect_hover,
            width=2,
            border_radius=5,
        )
        pygame.draw.rect(
            container,
            self.colors.c["darkdarkgray"]["rgb"],
            rect,
            border_radius=5,
        )

        title = self.font.render(
            "COMMANDS", True, self.colors.c["hover"]["rgb"]
        )
        output_text = [
            ("Scroll Hubs", "UP / DOWN"),
            ("Scroll Connections", "LEFT / RIGHT"),
            ("Next Turn", "SPACE"),
            ("Zoom & Pan", "MOUSE"),
        ]

        container.blit(title, ((width - title.get_width()) / 2, padding_y))
        padding_y += 30

        for label, value in output_text:
            label_surf = self.font.render(
                f"• {label}:", True, self.colors.c["white"]["rgb"]
            )
            container.blit(label_surf, (padding_x, padding_y))

            value_surf = self.font.render(
                value, True, self.colors.c["hover"]["rgb"]
            )
            container.blit(value_surf, (padding_x + 160, padding_y))

            padding_y += 20

        self.screen.blit(
            container,
            (
                self.screen.get_width() - width - 10,
                self.screen.get_height() - height - 10,
            ),
        )

    def _is_mouse_over_hubs(self) -> Hub | None:
        """
        Check if the mouse cursor is currently hovering over any hub.

        This method converts the cursor's screen coordinates into the
        simulation's world space by accounting for zoom and camera
        offsets. It uses the Pythagorean theorem to perform circular
        collision detection for each hub based on its projected radius.

        Returns:
            Hub | None: The hub object being hovered over, or None if
                the mouse is not touching any hub.
        """

        position = pygame.mouse.get_pos()
        mouse_x, mouse_y = position

        center_x = self.screen.get_width() / 2
        center_y = self.screen.get_height() / 2

        for hub in self.hubs:
            x = int((hub.x * 100 - self.camera_x) * self.zoom + center_x)
            y = int((hub.y * 100 - self.camera_y) * self.zoom + center_y)
            radius = 20 * self.zoom

            gap_x = mouse_x - x
            gap_y = mouse_y - y

            square_gap = pow(gap_x, 2) + pow(gap_y, 2)

            if square_gap <= pow(radius, 2):
                return hub
        return None

    def _is_mouse_over_connections(
        self, hover_hubs: bool
    ) -> Connection | None:
        """
        Detect connection hovering using vector projection onto segments.

        This method calculates the shortest distance from the mouse cursor
        to a line segment. It projects the mouse vector onto the
        connection vector to find the nearest point 'C' on the segment.
        By clamping the scalar projection 't' between 0 and 1, it ensures
        the collision check is confined to the finite segment limits.

        Args:
            hover_hubs (bool): If True, skips detection to prioritize
                hub selection over overlapping connections.

        Returns:
            Connection | None: The hovered connection if the squared
                distance to the segment is within the threshold (20px).
        """

        if hover_hubs:
            return None

        position = pygame.mouse.get_pos()
        mouse_x, mouse_y = position

        center_x = self.screen.get_width() / 2
        center_y = self.screen.get_height() / 2

        for connection in self.connections:
            zone_1 = next(
                (hub for hub in self.hubs if hub.name == connection.zone_1),
                None,
            )
            zone_2 = next(
                (hub for hub in self.hubs if hub.name == connection.zone_2),
                None,
            )

            if zone_1 and zone_2:
                x1 = int(
                    (zone_1.x * 100 - self.camera_x) * self.zoom + center_x
                )
                y1 = int(
                    (zone_1.y * 100 - self.camera_y) * self.zoom + center_y
                )
                x2 = int(
                    (zone_2.x * 100 - self.camera_x) * self.zoom + center_x
                )
                y2 = int(
                    (zone_2.y * 100 - self.camera_y) * self.zoom + center_y
                )

                segment = pow((x2 - x1), 2) + pow((y2 - y1), 2)
                t = (
                    ((mouse_x - x1) * (x2 - x1)) + ((mouse_y - y1) * (y2 - y1))
                ) / segment

                if t > 1:
                    t = 1
                elif t < 0:
                    t = 0

                cx = x1 + t * (x2 - x1)
                cy = y1 + t * (y2 - y1)

                gap = pow((mouse_x - cx), 2) + pow((mouse_y - cy), 2)

                if gap <= 20:
                    return connection
        return None

    def _draw_hubs(self, hover: Hub | None) -> None:
        """
        Render all hubs on the screen using perspective transformations.

        This method projects world coordinates to pixel space and applies
        scaling to both radius and icons based on the current zoom level.
        It features a highlight effect for hovered hubs (1.2x scale) and
        conditionally renders drone icons when zoom levels are sufficient
        to maintain visual clarity.

        Args:
            hover (Hub | None): The currently hovered hub instance to be
                drawn with a selection highlight.
        """

        center_x = self.screen.get_width() / 2
        center_y = self.screen.get_height() / 2

        for hub in self.hubs:
            x = int((hub.x * 100 - self.camera_x) * self.zoom + center_x)
            y = int((hub.y * 100 - self.camera_y) * self.zoom + center_y)
            radius = 20 * self.zoom

            if hover and hover == hub:
                pygame.draw.circle(
                    self.screen,
                    self.colors.c["hover"]["rgb"],
                    (x, y),
                    radius * 1.2,
                )
            pygame.draw.circle(self.screen, hub.color, (x, y), radius)

            if self.icon_drone and hub.drones > 0 and self.zoom > 0.6:
                width = 30 * self.zoom
                height = 30 * self.zoom

                drone_img = pygame.transform.scale(
                    self.icon_drone, (width, height)
                )
                self.screen.blit(
                    drone_img, (x - (15 * self.zoom), y - (15 * self.zoom))
                )

    def _draw_connection(self, hover: Connection | None) -> None:
        """
        Draw network edges using linear interpolation and dynamic styling.

        This method projects the start and end points of a connection from
        world coordinates to screen pixels. It applies a multi-pass
        rendering technique: a background highlight for hovered states
        and a foreground stroke with variable thickness and color-coding
        to reflect drone traffic and current zoom levels.

        Args:
            hover (Connection | None): The connection currently under
                selection to be rendered with an emphasized stroke.
        """

        center_x = self.screen.get_width() / 2
        center_y = self.screen.get_height() / 2

        for connection in self.connections:
            zone_1 = next(
                (hub for hub in self.hubs if hub.name == connection.zone_1),
                None,
            )
            zone_2 = next(
                (hub for hub in self.hubs if hub.name == connection.zone_2),
                None,
            )

            if zone_1 and zone_2:
                x1 = int(
                    (zone_1.x * 100 - self.camera_x) * self.zoom + center_x
                )
                y1 = int(
                    (zone_1.y * 100 - self.camera_y) * self.zoom + center_y
                )
                x2 = int(
                    (zone_2.x * 100 - self.camera_x) * self.zoom + center_x
                )
                y2 = int(
                    (zone_2.y * 100 - self.camera_y) * self.zoom + center_y
                )
                if hover and hover == connection:
                    pygame.draw.line(
                        self.screen,
                        self.colors.c["hover"]["rgb"],
                        (x1, y1),
                        (x2, y2),
                        5,
                    )
                pygame.draw.line(
                    self.screen,
                    (
                        self.colors.c["darkdarkgray"]["rgb"]
                        if connection.drones <= 0
                        else (0, 0, 0)
                    ),
                    (x1, y1),
                    (x2, y2),
                    3 if self.zoom > 1 else 2,
                )

    def _draw(self) -> None:
        """
        Execute the master rendering pipeline for the simulation.

        This method orchestrates the drawing sequence by first performing
        collision detection to determine the hover state. It then
        sequentially renders connections, hubs, and UI overlays. The
        order ensures correct Z-layering, where interactive info panels
        and command guides are drawn last to remain on top.
        """

        hover_hub = self._is_mouse_over_hubs()
        hover_connection = self._is_mouse_over_connections(
            True if hover_hub else False
        )

        self._draw_connection(hover_connection)

        self._draw_hubs(hover_hub)

        self._output_info(hover_hub if hover_hub else hover_connection)

        self.output_commands()

    def _update_advencement(self, backspace: bool) -> None:
        turn = self.timeline[self.turn]

        for hub in self.hubs:
            if hub.name != self.map.end_hub.name:
                hub.drones = 0

        for connection in self.connections:
            connection.drones = 0

        for key, value in turn.items():
            link = key.split("-")
            if len(link) == 1:
                hub = next(hub for hub in self.hubs if hub.name == key)
                if hub.name != self.map.end_hub.name:
                    hub.drones = len(value)
                else:
                    if backspace:
                        hub.drones -= len(value)
                    else:
                        hub.drones += len(value)
            else:
                zone_a = link[0]
                zone_b = link[1]
                connection = next(
                    c
                    for c in self.connections
                    if (c.zone_1 == zone_a and c.zone_2 == zone_b)
                    or (c.zone_1 == zone_b and c.zone_2 == zone_a)
                )
                connection.drones = len(value)

    def _manage_events(self, events: List, live: Live) -> bool:
        """
        Handle user input for camera control and UI navigation.

        This dispatcher processes mouse and keyboard events to update the
        simulation state. It manages zoom levels, adjusts camera offsets
        via relative mouse movement, and implements pagination for hub
        and connection displays. It also triggers UI refreshes through
        the Rich Live context upon data changes.

        Args:
            events (List): A list of Pygame events to process.
            live (Live): The Rich Live display instance for UI updates.

        Returns:
            bool: False if a QUIT event is detected, True otherwise.
        """

        for event in events:
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEWHEEL:
                if event.y > 0:
                    self.zoom += 0.1 if self.zoom < 2 else 0
                else:
                    self.zoom -= 0.1 if self.zoom > 0.3 else 0
            if event.type == pygame.MOUSEMOTION:
                if event.buttons[0]:
                    self.camera_x -= event.rel[0] / self.zoom
                    self.camera_y -= event.rel[1] / self.zoom
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    items_per_page = self._calculate_hub_card()
                    if self.hub_offset + items_per_page < len(self.hubs):
                        self.hub_offset += items_per_page
                    else:
                        self.hub_offset = len(self.hubs) - 1
                    live.update(self._create_layout())

                if event.key == pygame.K_UP:
                    items_per_page = self._calculate_hub_card()
                    if self.hub_offset - items_per_page >= 0:
                        self.hub_offset -= items_per_page
                    else:
                        self.hub_offset = 0
                    live.update(self._create_layout())

                if event.key == pygame.K_RIGHT:
                    items_per_page = self._calculate_connection_card()
                    if self.connection_offset + items_per_page < len(
                        self.connections
                    ):
                        self.connection_offset += items_per_page
                    else:
                        self.connection_offset = len(self.connections) - 1
                    live.update(self._create_layout())

                if event.key == pygame.K_LEFT:
                    items_per_page = self._calculate_connection_card()
                    if self.connection_offset - items_per_page >= 0:
                        self.connection_offset -= items_per_page
                    else:
                        self.connection_offset = 0
                    live.update(self._create_layout())

                if event.key == pygame.K_SPACE:
                    if self.turn < self.max_turn:
                        self.turn += 1
                        self._update_advencement(False)
                        live.update(self._create_layout())

                if event.key == pygame.K_BACKSPACE:
                    if self.turn > 0:
                        self.turn -= 1
                        self._update_advencement(True)
                        live.update(self._create_layout())

        return True

    def run(self) -> None:
        """
        Execute the main application loop and resource management.

        This method initializes the Pygame environment, loads graphical
        assets with fallback error handling, and orchestrates the
        dual-rendering system. It synchronizes a 60 FPS Pygame display
        for the map visualization with a Rich Live terminal interface
        for telemetry data, maintaining state until the user exits.
        """

        pygame.init()

        try:
            self.icon: pygame.Surface = pygame.image.load(
                "srcs/visualizer/img/logo.png"
            )
            self.icon_drone = pygame.image.load(
                "srcs/visualizer/img/drone.png"
            )
            pygame.display.set_icon(self.icon)

        except Exception:
            print(
                f"{self.colors.c['red']['ansi']}[WARNING] Visualizer assets "
                "not found,"
                f" proceeding with default icons.{self.colors.c['reset']}"
            )

        clock = pygame.time.Clock()

        screen = pygame.display.set_mode((800, 600), pygame.RESIZABLE)

        clock = pygame.time.Clock()

        self._init_datas(screen)

        running = True

        with Live(
            self._create_layout(),
            refresh_per_second=4,
            screen=True,
        ) as live:
            while running:
                clock.tick(60)
                events = pygame.event.get()
                if not self._manage_events(events, live):
                    running = False
                screen.fill(self.colors.c["darkgray"]["rgb"])
                self._draw()
                pygame.display.flip()

        pygame.quit()
