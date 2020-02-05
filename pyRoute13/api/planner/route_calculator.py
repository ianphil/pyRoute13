#!/usr/bin/env python

import pandas as pd
import networkx as nx
import math
from api.core.logger import Logger


class RouteCalculator:
    _avg_distance = 1175  # in meters
    _avg_time_to_gate = 21  # in minutes
    _terminals = ["A", "B", "C", "D", "E", "F", "T"]
    _terminal_length = 3  # eg. 'B03'

    def __init__(self, airport_json: pd.DataFrame, logger: Logger):
        self._logger = logger
        # Get the average cart speed (meters/min)
        self._avg_cart_speed = self._avg_distance / self._avg_time_to_gate

        # Initialize the NX Networks Graph
        self._G = nx.Graph()

        for row in airport_json["features"]:
            # Transform the Nodes to NetworkX schema
            if row["geometry"]["type"] == "Point":
                if row["properties"] != {}:
                    id = row["properties"]["id"]
                    if len(row["properties"]["id"]) < 2:
                        self._logger("Got Null ID Node")
                        continue
                    self._G.add_node(
                        self.convert_to_doubledigit(id),
                        lat=row["geometry"]["coordinates"][0],
                        long=row["geometry"]["coordinates"][0],
                    )
                else:
                    self._logger("got null property node: {}".format(row))

        for row in airport_json["features"]:
            # Transform the Edges to NetworkX Schema
            if row["geometry"]["type"] == "LineString":
                try:
                    startNode = self.convert_to_doubledigit(
                        row["properties"]["startNode"]
                    )
                    stopNode = self.convert_to_doubledigit(
                        row["properties"]["stopNode"]
                    )
                    if not self._G.has_node(startNode):
                        self._logger(startNode + " does not exist")
                        continue
                    if not self._G.has_node(stopNode):
                        self._logger(stopNode + " does not exist")
                        continue
                    self._G.add_edge(
                        startNode, stopNode, distance=row["properties"]["distance"],
                    )
                except KeyError as err:
                    self._logger(
                        "error raised converting edges to graph,\
                                 not found ="
                        + str(err)
                    )
                    self._logger(row)

    def get_shortest_path(self, source: str, target: str):
        return nx.shortest_path(self._G, source=source, target=target)

    def get_path_distance(self, source: str, target: str):
        return nx.shortest_path_length(
            self._G, source=source, target=target, weight="distance"
        )

    def estimate_transit_time(self, origin: str, destination: str):
        try:
            distance = self.get_path_distance(
                self.convert_to_gaterepr(origin), self.convert_to_gaterepr(destination),
            )
            est_time = distance / self._avg_cart_speed  # in minutes
            return est_time
        except nx.NetworkXNoPath:
            self._logger("Gate {} is not reachable from {}".format(destination, origin))
            return math.inf

    def get_next_step(self, origin: str, destination: str):
        try:
            path = self.get_shortest_path(
                self.convert_to_gaterepr(origin), self.convert_to_gaterepr(destination),
            )
            return path[1] if len(path) > 1 else path[0]
        except nx.NetworkXNoPath:
            self._logger("Gate {} is not reachable from {}".format(destination, origin))
            return math.inf

    def convert_to_doubledigit(self, id: str):
        if id[:4] == "gate":
            if id[-4:] == "Road":
                if len(id) == 10:
                    return id[:-5] + "0" + id[5:]
            else:
                if len(id) == 6:
                    return id[:-1] + "0" + id[5:]
        return id

    def convert_to_gaterepr(self, gate):
        if (gate[:1] in self._terminals) & (len(gate) == self._terminal_length):
            return "gate" + gate
        return gate
