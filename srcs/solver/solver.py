from typing import Any, Dict, List, Tuple
from srcs.parsing.models import MapModel, HubModel
import heapq as hp


class Solver:

    def __init__(self, map_config: MapModel):
        self.map = map_config
        self.reservation: Dict[Tuple, List[str]] = {}

    def init_registry(self) -> None:
        self.records: Dict[str, List[Any]] = {}
        self.index_hubs: Dict[str, HubModel] = {}

        cost = {"normal": 1, "restricted": 2, "priority": 1}

        hubs = [self.map.start_hub, self.map.end_hub] + self.map.hubs
        for hub in hubs:
            self.records[hub.name] = []
            self.index_hubs[hub.name] = hub

        for connection in self.map.connections:
            zone_1 = connection.zone_1
            zone_2 = connection.zone_2
            max_link_capacity = connection.max_link_capacity
            zone_type_1 = self.index_hubs[zone_1].zone
            zone_type_2 = self.index_hubs[zone_2].zone

            if zone_type_1 == "blocked" or zone_type_2 == "blocked":
                continue

            package_1 = {}
            package_2 = {}

            package_1 = {
                "zone": zone_2,
                "type": zone_type_2,
                "cost": cost[zone_type_2],
                "capacity": self.index_hubs[zone_2].max_drones,
                "link_capacity": max_link_capacity,
            }

            package_2 = {
                "zone": zone_1,
                "type": zone_type_1,
                "cost": cost[zone_type_1],
                "capacity": self.index_hubs[zone_1].max_drones,
                "link_capacity": max_link_capacity,
            }

            self.records[zone_1].append(package_1)
            self.records[zone_2].append(package_2)

    def _is_available(
        self, location: str, turn: int, capacity: int, is_endpoint: bool
    ) -> bool:
        if is_endpoint:
            return True

        if not (location, turn) in self.reservation:
            return True

        if len(self.reservation[(location, turn)]) < capacity:
            return True
        return False

    def _book_reservation(self, id: str, location: str, turn: int) -> None:
        if (location, turn) in self.reservation:
            self.reservation[(location, turn)].append(id)
            return
        self.reservation[(location, turn)] = [id]

    def _find_path(self, start_hub: str, end_hub: str) -> List[Tuple]:
        visited = set()
        heap = []
        path = []
        turn = 0

        hp.heappush(heap, (turn, 0, start_hub, path))
        while heap:
            move = hp.heappop(heap)

            if (move[2], move[0]) in visited:
                continue

            visited.add((move[2], move[0]))

            if move[2] == end_hub:
                return move[3]

            for d in self.records[move[2]]:
                turn_to_go = d["cost"]
                end_point = (
                    True
                    if d["zone"] == start_hub or d["zone"] == end_hub
                    else False
                )
                if self._is_available(
                    d["zone"], move[0] + turn_to_go, d["capacity"], end_point
                ):
                    link = sorted([move[2], d["zone"]])
                    link_str = link[0] + "-" + link[1]
                    if self._is_available(
                        link_str, move[0], d["link_capacity"], False
                    ):
                        priority = move[1]

                        if d["type"] == "priority":
                            priority -= 1

                        hp.heappush(
                            heap,
                            (
                                move[0] + turn_to_go,
                                priority,
                                d["zone"],
                                move[3] + [(d["zone"], move[0] + turn_to_go)],
                            ),
                        )
            end_point = (
                True if move[2] == start_hub or move[2] == end_hub else False
            )
            if self._is_available(
                move[2],
                move[0] + 1,
                self.index_hubs[move[2]].max_drones,
                end_point,
            ):
                hp.heappush(
                    heap,
                    (
                        move[0] + 1,
                        move[1],
                        move[2],
                        move[3] + [(move[2], move[0] + 1)],
                    ),
                )

    def _generate_solution(self) -> Dict[str, List[Tuple]]:
        self.init_registry()

        solution: Dict[str, List[Tuple]] = {}

        for i in range(1, self.map.nb_drones + 1):
            id = "D" + str(i)
            solution[id] = self._find_path(
                self.map.start_hub.name, self.map.end_hub.name
            )
            if isinstance(solution[id], List):
                for i in range(len(solution[id])):
                    if i + 1 < len(solution[id]):
                        if solution[id][i][0] != solution[id][i + 1][0]:
                            link = sorted(
                                [solution[id][i][0], solution[id][i + 1][0]]
                            )
                            link_str = link[0] + "-" + link[1]
                            self._book_reservation(
                                id, link_str, solution[id][i][1]
                            )
                    self._book_reservation(
                        id, solution[id][i][0], solution[id][i][1]
                    )
        return solution

    def _generate_timeline(
        self, solutions: Dict[str, List[Tuple]]
    ) -> Dict[int, Dict[str, List[str]]]:

        if not self.map:
            return

        timeline: Dict[int, Dict[str, List[str]]] = {}

        nb_turn = set()

        for value in solutions.values():
            for step in value:
                nb_turn.add(step[1])

        max_turn = max(nb_turn)

        for i in range(0, max_turn + 1):
            timeline[i] = {}

        for key, value in solutions.items():
            for i in range(len(value)):
                if value[i][0] in timeline[value[i][1]]:
                    timeline[value[i][1]][value[i][0]] += [key]
                else:
                    timeline[value[i][1]][value[i][0]] = [key]
                if i + 1 < len(value):
                    if value[i][0] == value[i + 1][0]:
                        continue
                    diff = value[i + 1][1] - value[i][1]
                    if diff > 1:
                        link_sorted = sorted([value[i][0], value[i + 1][0]])
                        link = link_sorted[0] + "-" + link_sorted[1]
                        for j in range(1, diff):
                            if link in timeline[value[i][1] + j]:
                                timeline[value[i][1] + j][link] += [key]
                            else:
                                timeline[value[i][1] + j][link] = [key]
        timeline[0][self.map.start_hub.name] = [
            key for key in solutions.keys()
        ]
        return timeline
