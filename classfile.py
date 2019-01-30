from typing import List

from attribute import Attribute, AttributeMixin
from base import Object
from const import Constant, CONSTANTS, DoubleInfo, LongInfo
from stream import Stream


class ClassFile(Object, AttributeMixin):
    def __init__(self, stream: Stream):
        magic = stream.read_u4()
        if magic != 0xCAFEBABE:
            raise Exception('Wrong magic')
        self.minor_version = stream.read_u2()
        self.major_version = stream.read_u2()
        self.constants: List[Constant] = self.read_constants(stream)
        self.access_flags = stream.read_u2()
        self.this_class = stream.read_u2()
        self.super_class = stream.read_u2()
        self.interfaces = [stream.read_u2() for _ in range(stream.read_u2())]
        self.fields: List[FieldMethodInfo] = [FieldMethodInfo(self, stream) for _ in range(stream.read_u2())]
        self.methods: List[FieldMethodInfo] = [FieldMethodInfo(self, stream) for _ in range(stream.read_u2())]
        self.attributes: List[Attribute] = [Attribute.read(self, stream) for _ in range(stream.read_u2())]
        print(self.attributes)

    # noinspection PyMethodMayBeStatic
    def read_constants(self, stream: Stream) -> List[Constant]:
        values = [None]
        count = stream.read_u2()
        i = 0
        while i < count - 1:
            tag = stream.read_u1()
            const = CONSTANTS[tag](stream)
            values.append(const)
            if isinstance(const, (LongInfo, DoubleInfo)):
                i += 1
                values.append(None)
            i += 1
        return values


class FieldMethodInfo(Object, AttributeMixin):
    def __init__(self, class_file: ClassFile, stream: Stream):
        self.access_flags = stream.read_u2()
        self.name_index = stream.read_u2()
        self.descriptor_index = stream.read_u2()
        self.attributes: List[Attribute] = [Attribute.read(class_file, stream) for _ in range(stream.read_u2())]
        print(class_file.constants[self.name_index], self.attributes)


class AccessFlag(object):
    ACC_PUBLIC = 0x0001
    ACC_FINAL = 0x0010
    ACC_SUPER = 0x0020
    ACC_INTERFACE = 0x0200
    ACC_ABSTRACT = 0x0400
    ACC_SYNTHETIC = 0x1000
    ACC_ANNOTATION = 0x2000
    ACC_ENUM = 0x4000
