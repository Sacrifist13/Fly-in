import pygame
from typing import Tuple, List
from src.parser import Parser
from src.colors import Color


class Hub:
    def __init__(
        self,
        screen: pygame.Surface,
        capacity: int,
        name: str,
        zone: str,
        x: int,
        y: int,
        color: Tuple,
        drones: int = 0,
    ) -> None:
        self.screen = screen
        self.drones = drones
        self.capacity = capacity
        self.name = name
        self.zone = zone
        self.x = x
        self.y = y
        self.color = color


class Renderer:
    def __init__(self, map_config: str):
        p = Parser(map_config)
        self.map = p.create_map_data()
        self.colors = Color()
        self.camera_x: int = 0
        self.camera_y: int = 0
        self.zoom: float = 0.5

    def init_hubs(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self.hubs: List[Hub] = []

        start_hub = self.map.start_hub
        end_hub = self.map.end_hub

        self.hubs.append(
            Hub(
                screen=screen,
                capacity=start_hub.max_drones,
                name=start_hub.name,
                zone=start_hub.name,
                x=start_hub.x,
                y=start_hub.y,
                color=(
                    self.colors.c[start_hub.color]["rgb"]
                    if start_hub.color
                    else self.colors.c_zones[start_hub.zone]
                ),
            )
        )

        self.hubs.append(
            Hub(
                screen=screen,
                capacity=end_hub.max_drones,
                name=end_hub.name,
                zone=end_hub.name,
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
                    screen=screen,
                    capacity=hub.max_drones,
                    name=hub.name,
                    zone=hub.name,
                    x=hub.x,
                    y=hub.y,
                    color=(
                        self.colors.c[hub.color]["rgb"]
                        if hub.color
                        else self.colors.c_zones[hub.zone]["rgb"]
                    ),
                )
            )

    def output_hub_info(self, hub: Hub) -> None:
        width = 160
        height = 280

        x = 10
        y = 10

        rect = (x, y, width, height)
        rect_hover = (x - 1, y - 1, width + 2, height + 2)

        pygame.draw.rect(
            self.screen,
            self.colors.c["hover"]["rgb"],
            rect_hover,
            width=2,
            border_radius=5,
        )

        pygame.draw.rect(
            self.screen,
            self.colors.c["darkdarkgray"]["rgb"],
            rect,
            border_radius=5,
        )

    def draw_hubs(self) -> None:
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
                pygame.draw.circle(
                    hub.screen,
                    self.colors.c["hover"]["rgb"],
                    (x, y),
                    radius * 1.2,
                )
                self.output_hub_info(hub)
            pygame.draw.circle(hub.screen, hub.color, (x, y), radius)

    def draw_connection(self) -> None:
        position = pygame.mouse.get_pos()
        mouse_x, mouse_y = position

        center_x = self.screen.get_width() / 2
        center_y = self.screen.get_height() / 2

        for connection in self.map.connections:
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

        self.hubs = []

        screen = pygame.display.set_mode((500, 500), pygame.RESIZABLE)

        clock = pygame.time.Clock()

        self.init_hubs(screen)

        running = True

        while running:
            clock.tick(60)
            if not self.manage_events(pygame.event.get()):
                running = False

            screen.fill(self.colors.c["darkgray"]["rgb"])
            self.draw_connection()
            self.draw_hubs()
            pygame.display.flip()

        pygame.quit()
