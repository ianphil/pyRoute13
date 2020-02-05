#!/usr/bin/env python
from typing import List


class TrieNode:
    def __init__(self, key, children):
        self.key = key
        self.children = children


def build_trie(head: List, tail: List):
    children = []

    for key in tail:
        if key % 2 == 0 or key - 1 in head:
            new_head = head.copy()
            new_head.append(key)
            new_tail = tail.copy()
            new_tail.remove(key)
            children.append(TrieNode(key, build_trie(new_head, new_tail)))

    return children
