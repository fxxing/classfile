from base import Object
from stream import Stream


class Constant(Object):
    pass


class Utf8Info(Constant):
    def __init__(self, stream: Stream):
        # self.length = 0
        length = stream.read_u2()
        self.bytes = stream.read_bytes(length)


class FourByteType(Constant):
    def __init__(self, stream: Stream):
        self.bytes = stream.read_u4()


class IntegerInfo(FourByteType):
    pass


class FloatInfo(FourByteType):
    pass


class EightByteType(Constant):
    def __init__(self, stream: Stream):
        self.high_bytes = stream.read_u4()
        self.low_bytes = stream.read_u4()


class LongInfo(EightByteType):
    pass


class DoubleInfo(EightByteType):
    pass


class ClassInfo(Constant):
    def __init__(self, stream: Stream):
        self.name_index = stream.read_u2()


class StringInfo(Constant):
    def __init__(self, stream: Stream):
        self.string_index = stream.read_u2()


class RefInfo(Constant):
    def __init__(self, stream: Stream):
        self.class_index = stream.read_u2()
        self.name_and_type_index = stream.read_u2()


class FieldRef(RefInfo):
    pass


class MethodRef(RefInfo):
    pass


class InterfaceMethodRef(RefInfo):
    pass


class NameAndType(Constant):
    def __init__(self, stream: Stream):
        self.name_index = stream.read_u2()
        self.descriptor_index = stream.read_u2()


class MethodHandle(Constant):
    def __init__(self, stream: Stream):
        self.reference_kind = stream.read_u1()
        self.reference_index = stream.read_u2()


class MethodType(Constant):
    def __init__(self, stream: Stream):
        self.descriptor_index = stream.read_u2()


class InvokeDynamic(Constant):
    def __init__(self, stream: Stream):
        self.bootstrap_method_attr_index = stream.read_u2()
        self.name_and_type_index = stream.read_u2()


CONSTANTS = {
    7: ClassInfo,
    9: FieldRef,
    10: MethodRef,
    11: InterfaceMethodRef,
    8: StringInfo,
    3: IntegerInfo,
    4: FloatInfo,
    5: LongInfo,
    6: DoubleInfo,
    12: NameAndType,
    1: Utf8Info,
    15: MethodHandle,
    16: MethodType,
    18: InvokeDynamic,
}
