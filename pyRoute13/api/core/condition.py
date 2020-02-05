#!/usr/bin/env python
from route13.core.agent import start


class Condition:
    def __init__(self):
        self.agents = []
        self.pending_wakeups = 0

    def sleep(self, agent):
        if self.pending_wakeups > 0:
            self.pending_wakeups -= 1
            start(agent)
        else:
            self.agents.append(agent)

    def wake_all(self):
        agents = self.agents
        self.agents = []
        self.pending_wakeups = 0

        for agent in agents:
            start(agent)

    def wake_one(self):
        try:
            agent = self.agents.pop()
            start(agent)
        except IndexError:
            self.pending_wakeups += 1
