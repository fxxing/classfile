from io import BytesIO
from typing import List

from base import Object
from const import Utf8Info
from instruction import Instruction, INSTRUCTIONS
from stream import Stream


class Attribute(Object):
    @staticmethod
    def read(class_file, stream: Stream):
        name_index = stream.read_u2()
        name: Utf8Info = class_file.constants[name_index]
        # noinspection PyTypeChecker
        s = Stream(BytesIO(stream.read_bytes(stream.read_u4())))
        return ATTRIBUTES[name.bytes](class_file, s)


class AttributeMixin(object):
    def get_attribute(self, cls):
        for attr in self.attributes:
            if isinstance(attr, cls):
                return attr


class ConstantValue(Attribute):
    def __init__(self, _, stream: Stream):
        self.constant_index = stream.read_u2()


class ExceptionTableEntry(Object):
    def __init__(self, stream: Stream):
        self.start_pc = stream.read_u2()
        self.end_pc = stream.read_u2()
        self.handler_pc = stream.read_u2()
        self.catch_type = stream.read_u2()


class Code(Attribute, AttributeMixin):
    def __init__(self, class_file, stream: Stream):
        self.max_stack = stream.read_u2()
        self.max_locals = stream.read_u2()
        code_length = stream.read_u4()
        code = stream.read_bytes(code_length)
        # noinspection PyTypeChecker
        self.instructions: List[Instruction] = self.read_bytecode(code_length, Stream(BytesIO(code)))
        self.exception_table = [ExceptionTableEntry(stream) for _ in range(stream.read_u2())]
        self.attributes = [Attribute.read(class_file, stream) for _ in range(stream.read_u2())]

    # noinspection PyMethodMayBeStatic
    def read_bytecode(self, code_length, stream: Stream) -> List[Instruction]:
        instructions = []
        addr = stream.tell()
        while addr < code_length:
            opcode = stream.read_u1()
            instructions.append(INSTRUCTIONS[opcode](addr, stream))
            addr = stream.tell()
        return instructions


class StackMapTable(Attribute):
    def __init__(self, _, stream: Stream):
        self.entries = [StackMapFrame(stream) for _ in range(stream.read_u2())]


class VerificationTypeInfoTag(Object):
    TOP = 0
    INTEGER = 1
    FLOAT = 2
    DOUBLE = 3
    LONG = 4
    NULL = 5
    UNINITIALIZED_THIS = 6
    OBJECT = 7
    UNINITIALIZED = 8


class VerificationTypeInfo(Object):
    def __init__(self, stream: Stream):
        self.tag = stream.read_u1()
        self.const_pool_index = 0
        if self.tag == VerificationTypeInfoTag.OBJECT:
            self.const_pool_index = stream.read_u2()
        self.offset = 0
        if self.tag == VerificationTypeInfoTag.UNINITIALIZED:
            self.offset = stream.read_u2()


class StackMapFrameType(Object):
    SAME = 0  # 0 - 63
    SAME_LOCALS_1_STACK_ITEM = 64  # 64 - 127
    SAME_LOCALS_1_STACK_ITEM_EXTENDED = 247
    CHOP = 248  # 248 - 250
    SAME_FRAME_EXTENDED = 251
    APPEND = 252  # 252 - 254
    FULL_FRAME = 255

    @staticmethod
    def get_type(tag):
        if 0 <= tag <= 63:
            return StackMapFrameType.SAME
        if 64 <= tag <= 127:
            return StackMapFrameType.SAME_LOCALS_1_STACK_ITEM
        if tag == 247:
            return StackMapFrameType.SAME_LOCALS_1_STACK_ITEM_EXTENDED
        if 248 <= tag <= 250:
            return StackMapFrameType.CHOP
        if tag == 251:
            return StackMapFrameType.SAME_FRAME_EXTENDED
        if 252 <= tag <= 254:
            return StackMapFrameType.APPEND
        if tag == 255:
            return StackMapFrameType.FULL_FRAME


class StackMapFrame(Object):
    def __init__(self, stream: Stream):
        self.tag = stream.read_u1()
        self.frame_type = StackMapFrameType.get_type(self.tag)
        self.offset_delta = 0
        self.locals: List[VerificationTypeInfo] = []
        self.stack: List[VerificationTypeInfo] = []
        if self.frame_type == StackMapFrameType.SAME_LOCALS_1_STACK_ITEM:
            self.stack = [VerificationTypeInfo(stream)]
        elif self.frame_type == StackMapFrameType.SAME_LOCALS_1_STACK_ITEM_EXTENDED:
            self.offset_delta = stream.read_u2()
            self.stack = [VerificationTypeInfo(stream)]
        elif self.frame_type == StackMapFrameType.CHOP:
            self.offset_delta = stream.read_u2()
        elif self.frame_type == StackMapFrameType.SAME_FRAME_EXTENDED:
            self.offset_delta = stream.read_u2()
        elif self.frame_type == StackMapFrameType.APPEND:
            self.offset_delta = stream.read_u2()
            self.locals = [VerificationTypeInfo(stream) for _ in range(self.tag - 251)]
        elif self.frame_type == StackMapFrameType.FULL_FRAME:
            self.offset_delta = stream.read_u2()
            self.locals = [VerificationTypeInfo(stream) for _ in range(stream.read_u2())]
            self.stack = [VerificationTypeInfo(stream) for _ in range(stream.read_u2())]


class Exceptions(Attribute):
    def __init__(self, _, stream: Stream):
        self.exception_index_table = [stream.read_u2() for _ in range(stream.read_u2())]


class InnerClassEntry(Object):
    def __init__(self, stream: Stream):
        self.inner_class_info_index = stream.read_u2()
        self.outer_class_info_index = stream.read_u2()
        self.inner_name_index = stream.read_u2()
        self.inner_class_access_flags = stream.read_u2()


class InnerClasses(Attribute):
    def __init__(self, _, stream: Stream):
        self.classes = [InnerClassEntry(stream) for _ in range(stream.read_u2())]


class EnclosingMethod(Attribute):
    def __init__(self, _, stream: Stream):
        self.class_index = stream.read_u2()
        self.method_index = stream.read_u2()


class Synthetic(Attribute):
    # noinspection PyUnusedLocal
    def __init__(self, _, stream: Stream):
        pass


class Signature(Attribute):
    def __init__(self, _, stream: Stream):
        self.signature_index = stream.read_u2()


class SourceFile(Attribute):
    def __init__(self, _, stream: Stream):
        self.sourcefile_index = stream.read_u2()


class SourceDebugExtension(Attribute):
    def __init__(self, _, stream: Stream):
        self.debug_extension = stream.read_bytes(stream.read_u4())


class LineNumberTableEntry(Object):
    def __init__(self, stream: Stream):
        self.start_pc = stream.read_u2()
        self.line_number = stream.read_u2()


class LineNumberTable(Attribute):
    def __init__(self, _, stream: Stream):
        self.line_number_table = [LineNumberTableEntry(stream) for _ in range(stream.read_u2())]


class LocalVariableTableEntry(Object):
    def __init__(self, stream: Stream):
        self.start_pc = stream.read_u2()
        self.length = stream.read_u2()
        self.name_index = stream.read_u2()
        self.descriptor_index = stream.read_u2()
        self.index = stream.read_u2()


class LocalVariableTable(Attribute):
    def __init__(self, _, stream: Stream):
        self.local_variable_table = [LocalVariableTableEntry(stream) for _ in range(stream.read_u2())]


class LocalVariableTypeTableEntry(Object):
    def __init__(self, stream: Stream):
        self.start_pc = stream.read_u2()
        self.length = stream.read_u2()
        self.name_index = stream.read_u2()
        self.signature_index = stream.read_u2()
        self.index = stream.read_u2()


class LocalVariableTypeTable(Attribute):
    def __init__(self, _, stream: Stream):
        self.local_variable_type_table = [LocalVariableTypeTableEntry(stream) for _ in range(stream.read_u2())]


class Deprecated(Attribute):
    # noinspection PyUnusedLocal
    def __init__(self, _, stream: Stream):
        pass


class ElementValue(Object):
    @staticmethod
    def get_value(stream: Stream):
        # type: (Stream) -> ElementValue
        tag = chr(stream.read_u1())
        if tag == 'e':
            return EnumElementValue(stream)
        if tag == 'c':
            return ClassElementValue(stream)
        if tag == '@':
            return AnnotationElementValue(stream)
        if tag == '[':
            return ArrayElementValue(stream)
        else:
            assert tag in {'B', 'C', 'D', 'F', 'I', 'J', 'S', 'Z', 's'}
            return ConstElementValue(tag, stream)


class ConstElementValue(ElementValue):
    def __init__(self, tag, stream: Stream):
        self.tag = tag
        self.const_value_index = stream.read_u2()


class EnumElementValue(ElementValue):
    def __init__(self, stream: Stream):
        self.type_name_index = stream.read_u2()
        self.const_name_index = stream.read_u2()


class ClassElementValue(ElementValue):
    def __init__(self, stream: Stream):
        self.class_info_index = stream.read_u2()


class AnnotationElementValue(ElementValue):
    def __init__(self, stream: Stream):
        self.annotation = Annotation(stream)


class ArrayElementValue(ElementValue):
    def __init__(self, stream: Stream):
        self.array_value = [ElementValue.get_value(stream) for _ in range(stream.read_u2())]


class ElementValuePair(Object):
    def __init__(self, stream: Stream):
        self.element_name_index = stream.read_u2()
        self.value = ElementValue.get_value(stream)


class Annotation(Object):
    def __init__(self, stream: Stream):
        self.type_index = stream.read_u2()
        self.element_value_pairs = [ElementValuePair(stream) for _ in range(stream.read_u2())]


class RuntimeVisibleAnnotations(Attribute):
    def __init__(self, _, stream: Stream):
        self.annotations = [Annotation(stream) for _ in range(stream.read_u2())]


class RuntimeInvisibleAnnotations(Attribute):
    def __init__(self, _, stream: Stream):
        self.element_value_pairs = [ElementValuePair(stream) for _ in range(stream.read_u2())]


class ParameterAnnotation(Object):
    def __init__(self, stream: Stream):
        self.annotations = [Annotation(stream) for _ in range(stream.read_u2())]


class RuntimeVisibleParameterAnnotations(Attribute):
    def __init__(self, _, stream: Stream):
        self.parameter_annotations = [ParameterAnnotation(stream) for _ in range(stream.read_u1())]


class RuntimeInvisibleParameterAnnotations(Attribute):
    def __init__(self, _, stream: Stream):
        self.parameter_annotations = [ParameterAnnotation(stream) for _ in range(stream.read_u1())]


class AnnotationDefault(Attribute):
    def __init__(self, _, stream: Stream):
        self.default_value = ElementValue.get_value(stream)


class BootstrapMethodEntry(Object):
    def __init__(self, stream: Stream):
        self.bootstrap_method_ref = stream.read_u2()
        self.bootstrap_arguments = [stream.read_u2() for _ in range(stream.read_u2())]


class BootstrapMethods(Attribute):
    def __init__(self, _, stream: Stream):
        self.bootstrap_methods = [BootstrapMethodEntry(stream) for _ in (stream.read_u2())]


ATTRIBUTES = {
    b'ConstantValue': ConstantValue,
    b'Code': Code,
    b'StackMapTable': StackMapTable,
    b'Exceptions': Exceptions,
    b'InnerClasses': InnerClasses,
    b'EnclosingMethod': EnclosingMethod,
    b'Synthetic': Synthetic,
    b'Signature': Signature,
    b'SourceFile': SourceFile,
    b'SourceDebugExtension': SourceDebugExtension,
    b'LineNumberTable': LineNumberTable,
    b'LocalVariableTable': LocalVariableTable,
    b'LocalVariableTypeTable': LocalVariableTypeTable,
    b'Deprecated': Deprecated,
    b'RuntimeVisibleAnnotations': RuntimeVisibleAnnotations,
    b'RuntimeInvisibleAnnotations': RuntimeInvisibleAnnotations,
    b'RuntimeVisibleParameterAnnotations': RuntimeVisibleParameterAnnotations,
    b'RuntimeInvisibleParameterAnnotations': RuntimeInvisibleParameterAnnotations,
    b'AnnotationDefault': AnnotationDefault,
    b'BootstrapMethods': BootstrapMethods,
}
