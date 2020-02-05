#!/usr/bin/env python


class LocationId(int):
    def __new__(cls, value=0):
        i = int.__new__(cls, value)
        return i
