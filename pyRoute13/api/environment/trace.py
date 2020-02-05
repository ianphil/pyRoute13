#!/usr/bin/env python

import time
import calendar
from abc import ABC, abstractmethod
from termcolor import colored
from colorama import init
from websocket_server import WebsocketServer
from threading import Thread
import json

# This fixes termcolor for Windows
init()

# TODO: Create lib singleton
gmt_sec = calendar.timegm(time.gmtime())


class Trace(ABC):
    @abstractmethod
    def cart_plan_is(self, cart, unfiltered, filtered):
        pass

    @abstractmethod
    def cart_arrives(self, cart):
        pass

    @abstractmethod
    def cart_passes(self, cart):
        pass

    @abstractmethod
    def cart_departs(self, cart, destination):
        pass

    @abstractmethod
    def cart_waits(self, cart, time):
        pass

    @abstractmethod
    def cart_begins_loading(self, cart, quantity):
        pass

    @abstractmethod
    def cart_finishes_loading(self, cart):
        pass

    @abstractmethod
    def cart_begins_unloading(self, cart, quantity):
        pass

    @abstractmethod
    def cart_finishes_unloading(self, cart):
        pass

    @abstractmethod
    def cart_suspends_service(self, cart):
        pass

    @abstractmethod
    def cart_resumes_service(self, cart):
        pass

    @abstractmethod
    def job_introducted(self, job):
        pass

    @abstractmethod
    def job_assigned(self, job):
        pass

    @abstractmethod
    def job_succeeded(self, job):
        pass

    @abstractmethod
    def job_failed(self, job):
        pass

    @abstractmethod
    def planner_started(self):
        pass

    @abstractmethod
    def planner_finished(self):
        pass


class TextTrace(Trace):
    def __init__(self, timeline, time_formatter, output):
        self.timeline = timeline
        self.format_time = time_formatter
        self.output = output
        self._colors = [
            "grey",
            "red",
            "green",
            "yellow",
            "blue",
            "magenta",
            "cyan",
            "white",
        ]
        self.complete_jobs = []
        self.failed_jobs = []

    # TODO: Create user defined Formatter() for TextTrace or refactor to use
    # __format__?
    def _format(self, cart, text):
        time = self.format_time(self.timeline.time)
        line = "{} {}".format(time, text)
        if cart:
            line = self._format_text_color(cart, line)
        self.output(line)

    def _format_text_color(self, cart, text):
        c = self._colors[cart.id % len(self._colors)]
        return colored(text, c)

    def cart_plan_is(self, cart, unfiltered, filtered):
        u = ", ".join(str(x.id) for x in unfiltered)
        f = ", ".join(str(x.id) for x in filtered)
        self._format(cart, "Cart {} plan {} merges to {}".format(cart.id, u, f))

    def cart_arrives(self, cart):
        self._format(
            cart,
            "Cart {} arrives at location {}".format(cart.id, cart.last_known_location),
        )

    def cart_passes(self, cart):
        self._format(
            cart,
            "Cart {} passes location {}".format(cart.id, cart.last_known_location),
        )

    def cart_departs(self, cart, destination):
        self._format(
            cart,
            "Cart {} departs location {} for location {}".format(
                cart.id, cart.last_known_location, destination
            ),
        )

    def cart_waits(self, cart, time):
        self._format(
            cart, "Cart {} waits until {}".format(cart.id, self.format_time(time)),
        )

    def cart_begins_loading(self, cart, quantity):
        self._format(
            cart,
            "Cart {} begins loading {} items (payload={})".format(
                cart.id, quantity, cart.payload
            ),
        )

    def cart_finishes_loading(self, cart):
        self._format(
            cart, "Cart {} finishes loading (payload={})".format(cart.id, cart.payload),
        )

    def cart_begins_unloading(self, cart, quantity):
        self._format(
            cart,
            "Cart {} begins unloading {} items (payload={})".format(
                cart.id, quantity, cart.payload
            ),
        )

    def cart_finishes_unloading(self, cart):
        self._format(
            cart, "Cart {} finish unloading (payload={})".format(cart.id, cart.payload),
        )

    def cart_suspends_service(self, cart):
        self._format(
            cart,
            "Cart {} suspends service at location {}".format(
                cart.id, cart.last_known_location
            ),
        )

    def cart_resumes_service(self, cart):
        self._format(
            cart,
            "Cart {} resumes service at location {}".format(
                cart.id, cart.last_known_location
            ),
        )

    def job_introducted(self, job):
        self._format(None, "Job {} introduced".format(job.id))

    def job_assigned(self, job):
        self._format(
            job.assigned_to,
            "Cart {} commits to job {}".format(job.assigned_to.id, job.id),
        )

    def job_succeeded(self, job):
        self.complete_jobs.append(job)
        self._format(job.assigned_to, "Job {} succeeded".format(job.id))

    def job_failed(self, job):
        self.failed_jobs.append(job)
        self._format(job.assigned_to, "Job {} failed".format(job.id))

    def planner_started(self):
        self._format(None, "Planning cycle Started")

    def planner_finished(self):
        self._format(None, "Planning Cycle finished. New plan finished")


class WSTrace(Trace):
    def __init__(self, timeline, time_formatter, port):
        self.timeline = timeline
        self.format_time = time_formatter
        self._colors = [
            "grey",
            "red",
            "green",
            "yellow",
            "blue",
            "magenta",
            "cyan",
            "white",
        ]

        # Set up WebSocket Server
        self.ws = WebsocketServer(port)
        server_thread = Thread(target=self.ws.run_forever)
        server_thread.daemon = True
        server_thread.start()

    def _send(self, message):
        event = {**message, "time": self.format_time(self.timeline.time)}
        json_event = json.dumps(event)
        line = json_event
        if message.get("cartId"):
            line = self._format_text_color(message.get("cartId"), json_event)
        print(line)
        self.ws.send_message_to_all(json_event)

    def _format_text_color(self, cart_id, text):
        c = self._colors[cart_id % len(self._colors)]
        return colored(text, c)

    def cart_plan_is(self, cart, unfiltered, filtered):
        self._send(
            {
                "type": "CART.PLAN_IS",
                "plan": [job.__dict__ for job in unfiltered],
                "merges": [job.__dict__ for job in filtered],
                "cartId": cart.id,
            }
        )
        # self._send('Cart {} plan {} merges to {}'.format(cart.id, u, f))

    def cart_arrives(self, cart):
        self._send(
            {
                "type": "CART.ARRIVES",
                "cartId": cart.id,
                "lastKnownLocation": cart.last_known_location,
            }
        )

    def cart_passes(self, cart):
        self._send(
            {
                "type": "CART.PASSES",
                "cartId": cart.id,
                "lastKnownLocation": cart.last_known_location,
            }
        )

    def cart_departs(self, cart, destination):
        self._send(
            {
                "type": "CART.DEPARTS",
                "cartId": cart.id,
                "lastKnownLocation": cart.last_known_location,
                "destination": destination,
            }
        )

    def cart_waits(self, cart, time):
        self._send({"type": "CART.WAITS", "cartId": cart.id, "resumeTime": time})

    def cart_begins_loading(self, cart, quantity):
        self._send(
            {
                "type": "CART.BEGINS_LOADING",
                "cartId": cart.id,
                "quantity": quantity,
                "payload": cart.payload,
            }
        )

    def cart_finishes_loading(self, cart):
        self._send(
            {
                "type": "CART.FINISHES_LOADING",
                "cartId": cart.id,
                "payload": cart.payload,
            }
        )

    def cart_begins_unloading(self, cart, quantity):
        self._send(
            {
                "type": "CART.BEGINS_UNLOADING",
                "cartId": cart.id,
                "quantity": quantity,
                "payload": cart.payload,
            }
        )

    def cart_finishes_unloading(self, cart):
        self._send(
            {
                "type": "CART.FINISHES_UNLOADING",
                "cartId": cart.id,
                "payload": cart.payload,
            }
        )

    def cart_suspends_service(self, cart):
        self._send(
            {
                "type": "CART.SUSPENDS_SERVICE",
                "cartId": cart.id,
                "lastKnownLocation": cart.last_known_location,
            }
        )

    def cart_resumes_service(self, cart):
        self._send(
            {
                "type": "CART.RESUMES_SERVICE",
                "cartId": cart.id,
                "lastKnownLocation": cart.last_known_location,
            }
        )

    def job_introducted(self, job):
        self._send({"type": "JOB.INTRODUCED", "jobId": job.id})

    def job_assigned(self, job):
        self._send(
            {"type": "JOB.ASSIGNED", "jobId": job.id, "assignedTo": job.assigned_to.id,}
        )

    def job_succeeded(self, job):
        self._send({"type": "JOB.SUCCEEDED", "jobId": job.id})

    def job_failed(self, job):
        self._send({"type": "JOB.FAILED", "jobId": job.id})

    def planner_started(self):
        self._send({"type": "PLANNER.STARTED"})

    def planner_finished(self):
        self._send({"type": "PLANNER.FINISHED"})


def format_time_HM(sim_time: int):
    time1 = time.gmtime(sim_time)
    return time.strftime("%H:%M", time1)


def format_time_HMS(sim_time: int):
    time1 = time.gmtime(sim_time)
    return time.strftime("%H:%M:%S", time1)
