import pygame
from typing import Tuple, List
from src.parser import Parser
from src.colors import Color


class Hub:
    def __init__(
        self,
        capacity: int,
        name: str,
        zone: str,
        x: int,
        y: int,
        color: Tuple,
        drones: int = 0,
    ) -> None:
        self.drones = drones
        self.capacity = capacity
        self.name = name
        self.zone = zone
        self.x = x
        self.y = y
        self.color = color


class Connection:
    def __init__(
        self, zone_1: str, zone_2: str, capacity: int, drones: int = 0
    ) -> None:
        self.zone_1 = zone_1
        self.zone_2 = zone_2
        self.drones = drones
        self.capacity = capacity


class Renderer:
    def __init__(self, map_config: str):
        p = Parser(map_config)
        self.map = p.create_map_data()
        self.colors = Color()
        self.camera_x: int = 0
        self.camera_y: int = 0
        self.zoom: float = 0.5

    def init_datas(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self.font = pygame.font.SysFont("arial", 16)
        self.hubs: List[Hub] = []
        self.connections: List[Connection] = []

        start_hub = self.map.start_hub
        end_hub = self.map.end_hub

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
                    else self.colors.c_zones[start_hub.zone]
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
                    else self.colors.c_zones[end_hub.zone]["rgb"]
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
                        else self.colors.c_zones[hub.zone]["rgb"]
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

    def output_info(self, obj: Hub | Connection | None) -> None:
        if not obj:
            return

        def get_min_width(obj: Hub | Connection):
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

        x = 10
        y = 10

        padding_x = 10
        padding_y = 10
        line_height = 25
        value_column_x = 90

        if isinstance(obj, Hub):
            width = 240
            height = 140
            title = "- HUB -"
            output_text = [
                ("Name", str(obj.name)),
                ("Drones", f"{obj.drones}/{obj.capacity}"),
                ("Zone", str(obj.zone)),
                ("Coord", f"({obj.x}, {obj.y})"),
            ]

        else:
            width = 240
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

    def is_mouse_over_hubs(self) -> Hub | None:
        position = pygame.mouse.get_pos()
        mouse_x, mouse_y = position

        center_x = self.screen.get_width() / 2
        center_y = self.screen.get_height() / 2

        for hub in self.hubs:
            x = int((hub.x * 100 - self.camera_x) * self.zoom + center_x)
            y = int((hub.y * 100 - self.camera_y) * self.zoom + center_y)
            radius = 10 * self.zoom

            gap_x = mouse_x - x
            gap_y = mouse_y - y

            square_gap = pow(gap_x, 2) + pow(gap_y, 2)

            if square_gap <= pow(radius, 2):
                return hub
        return None

    def is_mouse_over_connections(self, hover_hubs: bool) -> Connection | None:
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

    def draw_hubs(self, hover: Hub | None) -> None:

        center_x = self.screen.get_width() / 2
        center_y = self.screen.get_height() / 2

        for hub in self.hubs:
            x = int((hub.x * 100 - self.camera_x) * self.zoom + center_x)
            y = int((hub.y * 100 - self.camera_y) * self.zoom + center_y)
            radius = 10 * self.zoom

            if hover and hover == hub:
                pygame.draw.circle(
                    self.screen,
                    self.colors.c["hover"]["rgb"],
                    (x, y),
                    radius * 1.2,
                )
            pygame.draw.circle(self.screen, hub.color, (x, y), radius)

    def draw_connection(self, hover: Connection | None) -> None:

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
                    (0, 0, 0),
                    (x1, y1),
                    (x2, y2),
                    3 if self.zoom > 1 else 2,
                )

    def draw(self) -> None:
        hover_hub = self.is_mouse_over_hubs()
        hover_connection = self.is_mouse_over_connections(
            True if hover_hub else False
        )

        self.draw_connection(hover_connection)

        self.draw_hubs(hover_hub)

        self.output_info(hover_hub if hover_hub else hover_connection)

    def manage_events(self, events: List) -> bool:
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
        return True

    def run(self) -> None:
        if not self.map:
            return

        pygame.init()

        clock = pygame.time.Clock()

        screen = pygame.display.set_mode((500, 500), pygame.RESIZABLE)

        clock = pygame.time.Clock()

        self.init_datas(screen)

        running = True

        while running:
            clock.tick(60)
            if not self.manage_events(pygame.event.get()):
                running = False

            screen.fill(self.colors.c["darkgray"]["rgb"])
            self.draw()
            pygame.display.flip()

        pygame.quit()
