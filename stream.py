#!/usr/bin/env python
# coding: utf-8
from typing import BinaryIO

u1 = u2 = u4 = int


class Stream(object):
    def __init__(self, file: BinaryIO):
        self.file = file

    def tell(self):
        return self.file.tell()

    def read_s4(self) ->int:
        return int.from_bytes(self.file.read(4), byteorder="big", signed=True)
    def read_u1(self) -> u1:
        return int.from_bytes(self.file.read(1), byteorder='big', signed=False)

    def read_u2(self) -> u2:
        return int.from_bytes(self.file.read(2), byteorder='big', signed=False)

    def read_u4(self) -> u4:
        return int.from_bytes(self.file.read(4), byteorder='big', signed=False)

    def read_bytes(self, n) -> bytes:
        return self.file.read(n)
