#!/usr/bin/env python

from route13.environment.cart import Cart


class Cart_Factory:
    def __init__(self):
        self._next_id = 0

    def cart(self, capacity, last_known_location, payload=0):
        c = Cart()
        c.id = self._next_id = self._next_id + 1
        c.capacity = capacity
        c.last_known_location = last_known_location
        c.payload = payload

        return c
