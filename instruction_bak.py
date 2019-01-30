from typing import Type

from base import Object


class Instruction(Object):
    NAME = None
    OPCODE = None
    OPERANDS = None
    DESCRIPTION = None

    def __init__(self, addr, stream):
        self.addr = addr
        if self.NAME == 'lookupswitch':
            align = stream.tell() % 4
            stream.read_bytes((4 - align) if align else 0)
            self.default = stream.read_u4()
            npairs = stream.read_u4()
            self.match_offsets = [(stream.read_u4(), stream.read_u4()) for _ in range(npairs)]
            raise Exception('verify this')
        elif self.NAME == 'tableswitch':
            align = stream.tell() % 4
            stream.read_bytes((4 - align) if align else 0)
            self.default = stream.read_u4()
            self.low = stream.read_u4()
            self.high = stream.read_u4()
            self.jump_offsets = [stream.read_u4() for _ in range(self.high - self.low + 1)]
            raise Exception('verify this')
        elif self.NAME == 'wide':
            self.opcode = stream.read_u1()
            self.index = stream.read_u2()
            # noinspection PyUnresolvedReferences
            if self.opcode == Ins.iinc.OPCODE:
                self.const = stream.read_u2()
        elif self.OPERANDS:
            for f in self.OPERANDS.split(', '):
                size, name = f.split(':')
                value = getattr(stream, 'read_u' + size)()
                if name != 'zero':
                    setattr(self, name, value)

    def __repr__(self):
        s = '{:>4}: {:15}'.format(self.addr, self.NAME)
        if self.NAME == 'lookupswitch':
            s += ' {} {}'.format(self.default, self.match_offsets)
        elif self.NAME == 'tableswitch':
            s += ' {} {}'.format(self.default, self.low, self.high, self.jump_offsets)
        elif self.NAME == 'wide':
            # noinspection PyUnresolvedReferences
            if self.opcode == Ins.iinc.OPCODE:
                s += ' iinc {} {}'.format(self.index, self.const)
            else:
                s += ' {} {}'.format(INSTRUCTIONS[self.opcode].NAME, self.index)
        elif self.OPERANDS:
            for f in self.OPERANDS.split(', '):
                name = f.split(':')[-1]
                if name != 'zero':
                    s += ' {}'.format(getattr(self, name))

        return s


INSTRUCTIONS = {}


def _def_ins(name, opcode, operands, description) -> Type:
    def __init__(self, addr, stream):
        Instruction.__init__(self, addr, stream)

    new_class = type(name, (Instruction,), {"__init__": __init__})
    new_class.NAME = name
    new_class.OPCODE = opcode
    new_class.OPERANDS = operands
    new_class.DESCRIPTION = description
    INSTRUCTIONS[opcode] = new_class
    return new_class


class Ins(object):
    aaload = _def_ins('aaload', 0x32, None, 'load onto the stack a reference from an array'),
    aastore = _def_ins('aastore', 0x53, None, 'store into a reference in an array'),
    aconst_null = _def_ins('aconst_null', 0x1, None, 'push a null reference onto the stack'),
    aload = _def_ins('aload', 0x19, '1:index', 'load a reference onto the stack from a local variable #index'),
    aload_0 = _def_ins('aload_0', 0x2a, None, 'load a reference onto the stack from local variable 0'),
    aload_1 = _def_ins('aload_1', 0x2b, None, 'load a reference onto the stack from local variable 1'),
    aload_2 = _def_ins('aload_2', 0x2c, None, 'load a reference onto the stack from local variable 2'),
    aload_3 = _def_ins('aload_3', 0x2d, None, 'load a reference onto the stack from local variable 3'),
    anewarray = _def_ins('anewarray', 0xbd, '2:index',
                         'create a new array of references of length count and component type identified by the class reference index (indexbyte1 << 8 + indexbyte2) in the constant pool'),
    areturn = _def_ins('areturn', 0xb0, None, 'return a reference from a method'),
    arraylength = _def_ins('arraylength', 0xbe, None, 'get the length of an array'),
    astore = _def_ins('astore', 0x3a, '1:index', 'store a reference into a local variable #index'),
    astore_0 = _def_ins('astore_0', 0x4b, None, 'store a reference into local variable 0'),
    astore_1 = _def_ins('astore_1', 0x4c, None, 'store a reference into local variable 1'),
    astore_2 = _def_ins('astore_2', 0x4d, None, 'store a reference into local variable 2'),
    astore_3 = _def_ins('astore_3', 0x4e, None, 'store a reference into local variable 3'),
    athrow = _def_ins('athrow', 0xbf, None, 'throws an error or exception (notice that the rest of the stack is cleared, leaving only a reference to the Throwable)'),
    baload = _def_ins('baload', 0x33, None, 'load a byte or Boolean value from an array'),
    bastore = _def_ins('bastore', 0x54, None, 'store a byte or Boolean value into an array'),
    bipush = _def_ins('bipush', 0x10, '1:value', 'push a byte onto the stack as an integer value'),
    breakpoint = _def_ins('breakpoint', 0xca, None, 'reserved for breakpoints in Java debuggers; should not appear in any class file'),
    caload = _def_ins('caload', 0x34, None, 'load a char from an array'),
    castore = _def_ins('castore', 0x55, None, 'store a char into an array'),
    checkcast = _def_ins('checkcast', 0xc0, '2:index',
                         'checks whether an objectref is of a certain type, the class reference of which is in the constant pool at index (indexbyte1 << 8 + indexbyte2)'),
    d2f = _def_ins('d2f', 0x90, None, 'convert a double to a float'),
    d2i = _def_ins('d2i', 0x8e, None, 'convert a double to an int'),
    d2l = _def_ins('d2l', 0x8f, None, 'convert a double to a long'),
    dadd = _def_ins('dadd', 0x63, None, 'add two doubles'),
    daload = _def_ins('daload', 0x31, None, 'load a double from an array'),
    dastore = _def_ins('dastore', 0x52, None, 'store a double into an array'),
    dcmpg = _def_ins('dcmpg', 0x98, None, 'compare two doubles'),
    dcmpl = _def_ins('dcmpl', 0x97, None, 'compare two doubles'),
    dconst_0 = _def_ins('dconst_0', 0x0e, None, 'push the constant 0.0 onto the stack'),
    dconst_1 = _def_ins('dconst_1', 0x0f, None, 'push the constant 1.0 onto the stack'),
    ddiv = _def_ins('ddiv', 0x6f, None, 'divide two doubles'),
    dload = _def_ins('dload', 0x18, '1:index', 'load a double value from a local variable #index'),
    dload_0 = _def_ins('dload_0', 0x26, None, 'load a double from local variable 0'),
    dload_1 = _def_ins('dload_1', 0x27, None, 'load a double from local variable 1'),
    dload_2 = _def_ins('dload_2', 0x28, None, 'load a double from local variable 2'),
    dload_3 = _def_ins('dload_3', 0x29, None, 'load a double from local variable 3'),
    dmul = _def_ins('dmul', 0x6b, None, 'multiply two doubles'),
    dneg = _def_ins('dneg', 0x77, None, 'negate a double'),
    drem = _def_ins('drem', 0x73, None, 'get the remainder from a division between two doubles'),
    dreturn = _def_ins('dreturn', 0xaf, None, 'return a double from a method'),
    dstore = _def_ins('dstore', 0x39, '1:index', 'store a double value into a local variable #index'),
    dstore_0 = _def_ins('dstore_0', 0x47, None, 'store a double into local variable 0'),
    dstore_1 = _def_ins('dstore_1', 0x48, None, 'store a double into local variable 1'),
    dstore_2 = _def_ins('dstore_2', 0x49, None, 'store a double into local variable 2'),
    dstore_3 = _def_ins('dstore_3', 0x4a, None, 'store a double into local variable 3'),
    dsub = _def_ins('dsub', 0x67, None, 'subtract a double from another'),
    dup = _def_ins('dup', 0x59, None, 'duplicate the value on top of the stack'),
    dup_x1 = _def_ins('dup_x1', 0x5a, None, 'insert a copy of the top value into the stack two values from the top. value1 and value2 must not be of the type double or long.'),
    dup_x2 = _def_ins('dup_x2', 0x5b, None,
                      'insert a copy of the top value into the stack two (if value2 is double or long it takes up the entry of value3, too) or three values'
                      '(if value2 is neither double nor long) from the top'),
    dup2 = _def_ins('dup2', 0x5c, None, 'duplicate top two stack words (two values, if value1 is not double nor long; a single value, if value1 is double or long)'),
    dup2_x1 = _def_ins('dup2_x1', 0x5d, None, 'duplicate two words and insert beneath third word (see explanation above)'),
    dup2_x2 = _def_ins('dup2_x2', 0x5e, None, 'duplicate two words and insert beneath fourth word'),
    f2d = _def_ins('f2d', 0x8d, None, 'convert a float to a double'),
    f2i = _def_ins('f2i', 0x8b, None, 'convert a float to an int'),
    f2l = _def_ins('f2l', 0x8c, None, 'convert a float to a long'),
    fadd = _def_ins('fadd', 0x62, None, 'add two floats'),
    faload = _def_ins('faload', 0x30, None, 'load a float from an array'),
    fastore = _def_ins('fastore', 0x51, None, 'store a float in an array'),
    fcmpg = _def_ins('fcmpg', 0x96, None, 'compare two floats'),
    fcmpl = _def_ins('fcmpl', 0x95, None, 'compare two floats'),
    fconst_0 = _def_ins('fconst_0', 0x0b, None, 'push 0.0f on the stack'),
    fconst_1 = _def_ins('fconst_1', 0x0c, None, 'push 1.0f on the stack'),
    fconst_2 = _def_ins('fconst_2', 0x0d, None, 'push 2.0f on the stack'),
    fdiv = _def_ins('fdiv', 0x6e, None, 'divide two floats'),
    fload = _def_ins('fload', 0x17, '1:index', 'load a float value from a local variable #index'),
    fload_0 = _def_ins('fload_0', 0x22, None, 'load a float value from local variable 0'),
    fload_1 = _def_ins('fload_1', 0x23, None, 'load a float value from local variable 1'),
    fload_2 = _def_ins('fload_2', 0x24, None, 'load a float value from local variable 2'),
    fload_3 = _def_ins('fload_3', 0x25, None, 'load a float value from local variable 3'),
    fmul = _def_ins('fmul', 0x6a, None, 'multiply two floats'),
    fneg = _def_ins('fneg', 0x76, None, 'negate a float'),
    frem = _def_ins('frem', 0x72, None, 'get the remainder from a division between two floats'),
    freturn = _def_ins('freturn', 0xae, None, 'return a float'),
    fstore = _def_ins('fstore', 0x38, '1:index', 'store a float value into a local variable #index'),
    fstore_0 = _def_ins('fstore_0', 0x43, None, 'store a float value into local variable 0'),
    fstore_1 = _def_ins('fstore_1', 0x44, None, 'store a float value into local variable 1'),
    fstore_2 = _def_ins('fstore_2', 0x45, None, 'store a float value into local variable 2'),
    fstore_3 = _def_ins('fstore_3', 0x46, None, 'store a float value into local variable 3'),
    fsub = _def_ins('fsub', 0x66, None, 'subtract two floats'),
    getfield = _def_ins('getfield', 0xb4, '2:index',
                        'get a field value of an object objectref, where the field is identified by field reference in the constant pool index (index1 << 8 + index2)'),
    getstatic = _def_ins('getstatic', 0xb2, '2:index',
                         'get a static field value of a class, where the field is identified by field reference in the constant pool index (index1 << 8 + index2)'),
    goto = _def_ins('goto', 0xa7, '2:branch', 'goes to another instruction at branchoffset (signed short constructed from unsigned bytes branchbyte1 << 8 + branchbyte2)'),
    goto_w = _def_ins('goto_w', 0xc8, '4:branch',
                      'goes to another instruction at branchoffset (signed int constructed from unsigned bytes branchbyte1 << 24 + branchbyte2 << 16 + branchbyte3 << 8 + branchbyte4)'),
    i2b = _def_ins('i2b', 0x91, None, 'convert an int into a byte'),
    i2c = _def_ins('i2c', 0x92, None, 'convert an int into a character'),
    i2d = _def_ins('i2d', 0x87, None, 'convert an int into a double'),
    i2f = _def_ins('i2f', 0x86, None, 'convert an int into a float'),
    i2l = _def_ins('i2l', 0x85, None, 'convert an int into a long'),
    i2s = _def_ins('i2s', 0x93, None, 'convert an int into a short'),
    iadd = _def_ins('iadd', 0x60, None, 'add two ints'),
    iaload = _def_ins('iaload', 0x2e, None, 'load an int from an array'),
    iand = _def_ins('iand', 0x7e, None, 'perform a bitwise and on two integers'),
    iastore = _def_ins('iastore', 0x4f, None, 'store an int into an array'),
    iconst_m1 = _def_ins('iconst_m1', 0x2, None, 'load the int value -1 onto the stack'),
    iconst_0 = _def_ins('iconst_0', 0x3, None, 'load the int value 0 onto the stack'),
    iconst_1 = _def_ins('iconst_1', 0x4, None, 'load the int value 1 onto the stack'),
    iconst_2 = _def_ins('iconst_2', 0x5, None, 'load the int value 2 onto the stack'),
    iconst_3 = _def_ins('iconst_3', 0x6, None, 'load the int value 3 onto the stack'),
    iconst_4 = _def_ins('iconst_4', 0x7, None, 'load the int value 4 onto the stack'),
    iconst_5 = _def_ins('iconst_5', 0x8, None, 'load the int value 5 onto the stack'),
    idiv = _def_ins('idiv', 0x6c, None, 'divide two integers'),
    if_acmpeq = _def_ins('if_acmpeq', 0xa5, '2:branch',
                         'if references are equal, branch to instruction at branchoffset (signed short constructed from unsigned bytes branchbyte1 << 8 + branchbyte2)'),
    if_acmpne = _def_ins('if_acmpne', 0xa6, '2:branch',
                         'if references are not equal, branch to instruction at branchoffset (signed short constructed from unsigned bytes branchbyte1 << 8 + branchbyte2)'),
    if_icmpeq = _def_ins('if_icmpeq', 0x9f, '2:branch',
                         'if ints are equal, branch to instruction at branchoffset (signed short constructed from unsigned bytes branchbyte1 << 8 + branchbyte2)'),
    if_icmpge = _def_ins('if_icmpge', 0xa2, '2:branch',
                         'if value1 is greater than or equal to value2, branch to instruction at branchoffset (signed short constructed from unsigned bytes branchbyte1 << 8 + branchbyte2)'),
    if_icmpgt = _def_ins('if_icmpgt', 0xa3, '2:branch',
                         'if value1 is greater than value2, branch to instruction at branchoffset (signed short constructed from unsigned bytes branchbyte1 << 8 + branchbyte2)'),
    if_icmple = _def_ins('if_icmple', 0xa4, '2:branch',
                         'if value1 is less than or equal to value2, branch to instruction at branchoffset (signed short constructed from unsigned bytes branchbyte1 << 8 + branchbyte2)'),
    if_icmplt = _def_ins('if_icmplt', 0xa1, '2:branch',
                         'if value1 is less than value2, branch to instruction at branchoffset (signed short constructed from unsigned bytes branchbyte1 << 8 + branchbyte2)'),
    if_icmpne = _def_ins('if_icmpne', 0xa0, '2:branch',
                         'if ints are not equal, branch to instruction at branchoffset (signed short constructed from unsigned bytes branchbyte1 << 8 + branchbyte2)'),
    ifeq = _def_ins('ifeq', 0x99, '2:branch',
                    'if value is 0, branch to instruction at branchoffset (signed short constructed from unsigned bytes branchbyte1 << 8 + branchbyte2)'),
    ifge = _def_ins('ifge', 0x9c, '2:branch',
                    'if value is greater than or equal to 0, branch to instruction at branchoffset (signed short constructed from unsigned bytes branchbyte1 << 8 + branchbyte2)'),
    ifgt = _def_ins('ifgt', 0x9d, '2:branch',
                    'if value is greater than 0, branch to instruction at branchoffset (signed short constructed from unsigned bytes branchbyte1 << 8 + branchbyte2)'),
    ifle = _def_ins('ifle', 0x9e, '2:branch',
                    'if value is less than or equal to 0, branch to instruction at branchoffset (signed short constructed from unsigned bytes branchbyte1 << 8 + branchbyte2)'),
    iflt = _def_ins('iflt', 0x9b, '2:branch',
                    'if value is less than 0, branch to instruction at branchoffset (signed short constructed from unsigned bytes branchbyte1 << 8 + branchbyte2)'),
    ifne = _def_ins('ifne', 0x9a, '2:branch',
                    'if value is not 0, branch to instruction at branchoffset (signed short constructed from unsigned bytes branchbyte1 << 8 + branchbyte2)'),
    ifnonnull = _def_ins('ifnonnull', 0xc7, '2:branch',
                         'if value is not null, branch to instruction at branchoffset (signed short constructed from unsigned bytes branchbyte1 << 8 + branchbyte2)'),
    ifnull = _def_ins('ifnull', 0xc6, '2:branch',
                      'if value is null, branch to instruction at branchoffset (signed short constructed from unsigned bytes branchbyte1 << 8 + branchbyte2)'),
    iinc = _def_ins('iinc', 0x84, '1:index, 1:const', 'increment local variable #index by signed byte const'),
    iload = _def_ins('iload', 0x15, '1:index', 'load an int value from a local variable #index'),
    iload_0 = _def_ins('iload_0', 0x1a, None, 'load an int value from local variable 0'),
    iload_1 = _def_ins('iload_1', 0x1b, None, 'load an int value from local variable 1'),
    iload_2 = _def_ins('iload_2', 0x1c, None, 'load an int value from local variable 2'),
    iload_3 = _def_ins('iload_3', 0x1d, None, 'load an int value from local variable 3'),
    impdep1 = _def_ins('impdep1', 0xfe, None, 'reserved for implementation-dependent operations within debuggers; should not appear in any class file'),
    impdep2 = _def_ins('impdep2', 0xff, None, 'reserved for implementation-dependent operations within debuggers; should not appear in any class file'),
    imul = _def_ins('imul', 0x68, None, 'multiply two integers'),
    ineg = _def_ins('ineg', 0x74, None, 'negate int'),
    instanceof = _def_ins('instanceof', 0xc1, '2:index',
                          'determines if an object objectref is of a given type, identified by class reference index in constant pool (indexbyte1 << 8 + indexbyte2)'),
    invokedynamic = _def_ins('invokedynamic', 0xba, '2:index, 2:zero',
                             'invokes a dynamic method identified by method reference index in constant pool (indexbyte1 << 8 + indexbyte2)'),
    invokeinterface = _def_ins('invokeinterface', 0xb9, '2:index, 1:count, 1:zero',
                               'invokes an interface method on object objectref, where the interface method is identified by method reference index in constant pool'
                               '(indexbyte1 << 8 + indexbyte2)'),
    invokespecial = _def_ins('invokespecial', 0xb7, '2:index',
                             'invoke instance method on object objectref, where the method is identified by method reference index in constant pool (indexbyte1 << 8 + indexbyte2)'),
    invokestatic = _def_ins('invokestatic', 0xb8, '2:index',
                            'invoke a static method, where the method is identified by method reference index in constant pool (indexbyte1 << 8 + indexbyte2)'),
    invokevirtual = _def_ins('invokevirtual', 0xb6, '2:index',
                             'invoke virtual method on object objectref, where the method is identified by method reference index in constant pool (indexbyte1 << 8 + indexbyte2)'),
    ior = _def_ins('ior', 0x80, None, 'bitwise int or'),
    irem = _def_ins('irem', 0x70, None, 'logical int remainder'),
    ireturn = _def_ins('ireturn', 0xac, None, 'return an integer from a method'),
    ishl = _def_ins('ishl', 0x78, None, 'int shift left'),
    ishr = _def_ins('ishr', 0x7a, None, 'int arithmetic shift right'),
    istore = _def_ins('istore', 0x36, '1:index', 'store int value into variable #index'),
    istore_0 = _def_ins('istore_0', 0x3b, None, 'store int value into variable 0'),
    istore_1 = _def_ins('istore_1', 0x3c, None, 'store int value into variable 1'),
    istore_2 = _def_ins('istore_2', 0x3d, None, 'store int value into variable 2'),
    istore_3 = _def_ins('istore_3', 0x3e, None, 'store int value into variable 3'),
    isub = _def_ins('isub', 0x64, None, 'int subtract'),
    iushr = _def_ins('iushr', 0x7c, None, 'int logical shift right'),
    ixor = _def_ins('ixor', 0x82, None, 'int xor'),
    jsr = _def_ins('jsr', 0xa8, '2:branch',
                   'jump to subroutine at branchoffset (signed short constructed from unsigned bytes branchbyte1 << 8 + branchbyte2) and place the return address on the stack'),
    jsr_w = _def_ins('jsr_w', 0xc9, '4:branch',
                     'jump to subroutine at branchoffset (signed int constructed from unsigned bytes branchbyte1 << 24 + branchbyte2 << 16 + branchbyte3 << 8 + branchbyte4)'
                     'and place the return address on the stack'),
    l2d = _def_ins('l2d', 0x8a, None, 'convert a long to a double'),
    l2f = _def_ins('l2f', 0x89, None, 'convert a long to a float'),
    l2i = _def_ins('l2i', 0x88, None, 'convert a long to a int'),
    ladd = _def_ins('ladd', 0x61, None, 'add two longs'),
    laload = _def_ins('laload', 0x2f, None, 'load a long from an array'),
    land = _def_ins('land', 0x7f, None, 'bitwise and of two longs'),
    lastore = _def_ins('lastore', 0x50, None, 'store a long to an array'),
    lcmp = _def_ins('lcmp', 0x94, None, 'compare two longs values'),
    lconst_0 = _def_ins('lconst_0', 0x9, None, 'push the long 0 onto the stack'),
    lconst_1 = _def_ins('lconst_1', 0x0a, None, 'push the long 1 onto the stack'),
    ldc = _def_ins('ldc', 0x12, '1:index', 'push a constant #index from a constant pool (String, int or float) onto the stack'),
    ldc_w = _def_ins('ldc_w', 0x13, '2:index',
                     'push a constant #index from a constant pool (String, int or float) onto the stack (wide index is constructed as indexbyte1 << 8 + indexbyte2)'),
    ldc2_w = _def_ins('ldc2_w', 0x14, '2:index',
                      'push a constant #index from a constant pool (double or long) onto the stack (wide index is constructed as indexbyte1 << 8 + indexbyte2)'),
    ldiv = _def_ins('ldiv', 0x6d, None, 'divide two longs'),
    lload = _def_ins('lload', 0x16, '1:index', 'load a long value from a local variable #index'),
    lload_0 = _def_ins('lload_0', 0x1e, None, 'load a long value from a local variable 0'),
    lload_1 = _def_ins('lload_1', 0x1f, None, 'load a long value from a local variable 1'),
    lload_2 = _def_ins('lload_2', 0x20, None, 'load a long value from a local variable 2'),
    lload_3 = _def_ins('lload_3', 0x21, None, 'load a long value from a local variable 3'),
    lmul = _def_ins('lmul', 0x69, None, 'multiply two longs'),
    lneg = _def_ins('lneg', 0x75, None, 'negate a long'),
    lookupswitch = _def_ins('lookupswitch', 0xab, None, 'a target address is looked up from a table using a key and execution continues from the instruction at that address'),
    lor = _def_ins('lor', 0x81, None, 'bitwise or of two longs'),
    lrem = _def_ins('lrem', 0x71, None, 'remainder of division of two longs'),
    lreturn = _def_ins('lreturn', 0xad, None, 'return a long value'),
    lshl = _def_ins('lshl', 0x79, None, 'bitwise shift left of a long value1 by value2 positions'),
    lshr = _def_ins('lshr', 0x7b, None, 'bitwise shift right of a long value1 by value2 positions'),
    lstore = _def_ins('lstore', 0x37, '1:index', 'store a long value in a local variable #index'),
    lstore_0 = _def_ins('lstore_0', 0x3f, None, 'store a long value in a local variable 0'),
    lstore_1 = _def_ins('lstore_1', 0x40, None, 'store a long value in a local variable 1'),
    lstore_2 = _def_ins('lstore_2', 0x41, None, 'store a long value in a local variable 2'),
    lstore_3 = _def_ins('lstore_3', 0x42, None, 'store a long value in a local variable 3'),
    lsub = _def_ins('lsub', 0x65, None, 'subtract two longs'),
    lushr = _def_ins('lushr', 0x7d, None, 'bitwise shift right of a long value1 by value2 positions, unsigned'),
    lxor = _def_ins('lxor', 0x83, None, 'bitwise exclusive or of two longs'),
    monitorenter = _def_ins('monitorenter', 0xc2, None, 'enter monitor for object ("grab the lock" - start of synchronized() section)'),
    monitorexit = _def_ins('monitorexit', 0xc3, None, 'exit monitor for object ("release the lock" - end of synchronized() section)'),
    multianewarray = _def_ins('multianewarray', 0xc5, '2:index, 1:dimensions',
                              'create a new array of dimensions dimensions with elements of type identified by class reference'
                              'in constant pool index (indexbyte1 << 8 + indexbyte2); the sizes of each dimension is identified by count1, [count2, etc.]'),
    new = _def_ins('new', 0xbb, '2:index', 'create new object of type identified by class reference in constant pool index (indexbyte1 << 8 + indexbyte2)'),
    newarray = _def_ins('newarray', 0xbc, '1:atype', 'create new array with count elements of primitive type identified by atype'),
    nop = _def_ins('nop', 0x0, None, 'perform no operation'),
    pop = _def_ins('pop', 0x57, None, 'discard the top value on the stack'),
    pop2 = _def_ins('pop2', 0x58, None, 'discard the top two values on the stack (or one value, if it is a double or long)'),
    putfield = _def_ins('putfield', 0xb5, '2:index',
                        'set field to value in an object objectref, where the field is identified by a field reference index in constant pool (indexbyte1 << 8 + indexbyte2)'),
    putstatic = _def_ins('putstatic', 0xb3, '2:index',
                         'set static field to value in a class, where the field is identified by a field reference index in constant pool (indexbyte1 << 8 + indexbyte2)'),
    ret = _def_ins('ret', 0xa9, '1:index', 'continue execution from address taken from a local variable #index (the asymmetry with jsr is intentional)'),
    return_ = _def_ins('return', 0xb1, None, 'return void from method'),
    saload = _def_ins('saload', 0x35, None, 'load short from array'),
    sastore = _def_ins('sastore', 0x56, None, 'store short to array'),
    sipush = _def_ins('sipush', 0x11, '2:value', 'push a short onto the stack'),
    swap = _def_ins('swap', 0x5f, None, 'swaps two top words on the stack (note that value1 and value2 must not be double or long)'),
    tableswitch = _def_ins('tableswitch', 0xaa, None, 'continue execution from an address in the table at offset index'),
    wide = _def_ins('wide', 0xc4, None,
                    'execute opcode, where opcode is either iload, fload, aload, lload, dload, istore, fstore, astore, lstore, dstore, or ret, but assume'
                    'the index is 16 bit; or execute iinc, where the index is 16 bits and the constant to increment by is a signed 16 bit short'),
