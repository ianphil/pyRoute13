#!/usr/bin/env python

from enum import Enum, auto
from abc import ABC


class ActionType(Enum):
    PICKUP = auto()
    DROPOFF = auto()
    SUSPEND = auto()


class ActionBase(ABC):
    def __init__(self):
        self.job = None
        self.type = None
        self.location = None


class TransferAction(ActionBase):
    def __init__(self):
        self.time = None
        self.quantity = None


class PickupAction(TransferAction):
    def __init__(self):
        self.type = ActionType.PICKUP


class DropoffAction(TransferAction):
    def __init__(self):
        self.type = ActionType.DROPOFF


class SuspendAction(ActionBase):
    def __init__(self):
        self.type = ActionType.SUSPEND
        self.suspend_time = None
        self.resume_time = None


class Route:
    def __init__(self):
        self.cart = None
        self.actions = None
        self.working_time = None
        self.score = None
