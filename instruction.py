from typing import Type

from base import Object
from util import to_signed_byte, to_signed_short, to_signed_int


class ArrayType(object):
    BOOLEAN = 4
    CHAR = 5
    FLOAT = 6
    DOUBLE = 7
    BYTE = 8
    SHORT = 9
    INT = 10
    LONG = 11


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
            self.low = stream.read_s4()
            self.high = stream.read_s4()
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
                size, field = f.split(':')
                value = getattr(stream, 'read_u' + size)()
                if self.NAME == 'iinc' and field == 'const':
                    value = to_signed_byte(value)
                elif self.NAME == 'bipush' and field == 'value':
                    value = to_signed_byte(value)
                elif self.NAME == 'sipush' and field == 'value':
                    value = to_signed_short(value)
                elif f == '2:branch':
                    value = addr + to_signed_short(value)
                elif f == '4:branch':
                    value = addr + to_signed_int(value)
                if field != 'zero':
                    setattr(self, field, value)

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


def _def_ins(name, opcode, operands=None) -> Type:
    def __init__(self, addr, stream):
        Instruction.__init__(self, addr, stream)

    new_class = type(name, (Instruction,), {"__init__": __init__})
    new_class.NAME = name
    new_class.OPCODE = opcode
    new_class.OPERANDS = operands
    INSTRUCTIONS[opcode] = new_class
    return new_class


class Ins(object):
    aaload = _def_ins('aaload', 0x32),
    aastore = _def_ins('aastore', 0x53),
    aconst_null = _def_ins('aconst_null', 0x01),
    aload = _def_ins('aload', 0x19, '1:index'),
    aload_0 = _def_ins('aload_0', 0x2a),
    aload_1 = _def_ins('aload_1', 0x2b),
    aload_2 = _def_ins('aload_2', 0x2c),
    aload_3 = _def_ins('aload_3', 0x2d),
    anewarray = _def_ins('anewarray', 0xbd, '2:index'),
    areturn = _def_ins('areturn', 0xb0),
    arraylength = _def_ins('arraylength', 0xbe),
    astore = _def_ins('astore', 0x3a, '1:index'),
    astore_0 = _def_ins('astore_0', 0x4b),
    astore_1 = _def_ins('astore_1', 0x4c),
    astore_2 = _def_ins('astore_2', 0x4d),
    astore_3 = _def_ins('astore_3', 0x4e),
    athrow = _def_ins('athrow', 0xbf),
    baload = _def_ins('baload', 0x33),
    bastore = _def_ins('bastore', 0x54),
    bipush = _def_ins('bipush', 0x10, '1:value'),
    breakpoint = _def_ins('breakpoint', 0xca),
    caload = _def_ins('caload', 0x34),
    castore = _def_ins('castore', 0x55),
    checkcast = _def_ins('checkcast', 0xc0, '2:index'),
    d2f = _def_ins('d2f', 0x90),
    d2i = _def_ins('d2i', 0x8e),
    d2l = _def_ins('d2l', 0x8f),
    dadd = _def_ins('dadd', 0x63),
    daload = _def_ins('daload', 0x31),
    dastore = _def_ins('dastore', 0x52),
    dcmpg = _def_ins('dcmpg', 0x98),
    dcmpl = _def_ins('dcmpl', 0x97),
    dconst_0 = _def_ins('dconst_0', 0x0e),
    dconst_1 = _def_ins('dconst_1', 0x0f),
    ddiv = _def_ins('ddiv', 0x6f),
    dload = _def_ins('dload', 0x18, '1:index'),
    dload_0 = _def_ins('dload_0', 0x26),
    dload_1 = _def_ins('dload_1', 0x27),
    dload_2 = _def_ins('dload_2', 0x28),
    dload_3 = _def_ins('dload_3', 0x29),
    dmul = _def_ins('dmul', 0x6b),
    dneg = _def_ins('dneg', 0x77),
    drem = _def_ins('drem', 0x73),
    dreturn = _def_ins('dreturn', 0xaf),
    dstore = _def_ins('dstore', 0x39, '1:index'),
    dstore_0 = _def_ins('dstore_0', 0x47),
    dstore_1 = _def_ins('dstore_1', 0x48),
    dstore_2 = _def_ins('dstore_2', 0x49),
    dstore_3 = _def_ins('dstore_3', 0x4a),
    dsub = _def_ins('dsub', 0x67),
    dup = _def_ins('dup', 0x59),
    dup_x1 = _def_ins('dup_x1', 0x5a),
    dup_x2 = _def_ins('dup_x2', 0x5b),
    dup2 = _def_ins('dup2', 0x5c),
    dup2_x1 = _def_ins('dup2_x1', 0x5d),
    dup2_x2 = _def_ins('dup2_x2', 0x5e),
    f2d = _def_ins('f2d', 0x8d),
    f2i = _def_ins('f2i', 0x8b),
    f2l = _def_ins('f2l', 0x8c),
    fadd = _def_ins('fadd', 0x62),
    faload = _def_ins('faload', 0x30),
    fastore = _def_ins('fastore', 0x51),
    fcmpg = _def_ins('fcmpg', 0x96),
    fcmpl = _def_ins('fcmpl', 0x95),
    fconst_0 = _def_ins('fconst_0', 0x0b),
    fconst_1 = _def_ins('fconst_1', 0x0c),
    fconst_2 = _def_ins('fconst_2', 0x0d),
    fdiv = _def_ins('fdiv', 0x6e),
    fload = _def_ins('fload', 0x17, '1:index'),
    fload_0 = _def_ins('fload_0', 0x22),
    fload_1 = _def_ins('fload_1', 0x23),
    fload_2 = _def_ins('fload_2', 0x24),
    fload_3 = _def_ins('fload_3', 0x25),
    fmul = _def_ins('fmul', 0x6a),
    fneg = _def_ins('fneg', 0x76),
    frem = _def_ins('frem', 0x72),
    freturn = _def_ins('freturn', 0xae),
    fstore = _def_ins('fstore', 0x38, '1:index'),
    fstore_0 = _def_ins('fstore_0', 0x43),
    fstore_1 = _def_ins('fstore_1', 0x44),
    fstore_2 = _def_ins('fstore_2', 0x45),
    fstore_3 = _def_ins('fstore_3', 0x46),
    fsub = _def_ins('fsub', 0x66),
    getfield = _def_ins('getfield', 0xb4, '2:index'),
    getstatic = _def_ins('getstatic', 0xb2, '2:index'),
    goto = _def_ins('goto', 0xa7, '2:branch'),
    goto_w = _def_ins('goto_w', 0xc8, '4:branch'),
    i2b = _def_ins('i2b', 0x91),
    i2c = _def_ins('i2c', 0x92),
    i2d = _def_ins('i2d', 0x87),
    i2f = _def_ins('i2f', 0x86),
    i2l = _def_ins('i2l', 0x85),
    i2s = _def_ins('i2s', 0x93),
    iadd = _def_ins('iadd', 0x60),
    iaload = _def_ins('iaload', 0x2e),
    iand = _def_ins('iand', 0x7e),
    iastore = _def_ins('iastore', 0x4f),
    iconst_m1 = _def_ins('iconst_m1', 0x02),
    iconst_0 = _def_ins('iconst_0', 0x03),
    iconst_1 = _def_ins('iconst_1', 0x04),
    iconst_2 = _def_ins('iconst_2', 0x05),
    iconst_3 = _def_ins('iconst_3', 0x06),
    iconst_4 = _def_ins('iconst_4', 0x07),
    iconst_5 = _def_ins('iconst_5', 0x08),
    idiv = _def_ins('idiv', 0x6c),
    if_acmpeq = _def_ins('if_acmpeq', 0xa5, '2:branch'),
    if_acmpne = _def_ins('if_acmpne', 0xa6, '2:branch'),
    if_icmpeq = _def_ins('if_icmpeq', 0x9f, '2:branch'),
    if_icmpge = _def_ins('if_icmpge', 0xa2, '2:branch'),
    if_icmpgt = _def_ins('if_icmpgt', 0xa3, '2:branch'),
    if_icmple = _def_ins('if_icmple', 0xa4, '2:branch'),
    if_icmplt = _def_ins('if_icmplt', 0xa1, '2:branch'),
    if_icmpne = _def_ins('if_icmpne', 0xa0, '2:branch'),
    ifeq = _def_ins('ifeq', 0x99, '2:branch'),
    ifge = _def_ins('ifge', 0x9c, '2:branch'),
    ifgt = _def_ins('ifgt', 0x9d, '2:branch'),
    ifle = _def_ins('ifle', 0x9e, '2:branch'),
    iflt = _def_ins('iflt', 0x9b, '2:branch'),
    ifne = _def_ins('ifne', 0x9a, '2:branch'),
    ifnonnull = _def_ins('ifnonnull', 0xc7, '2:branch'),
    ifnull = _def_ins('ifnull', 0xc6, '2:branch'),
    iinc = _def_ins('iinc', 0x84, '1:index, 1:const'),
    iload = _def_ins('iload', 0x15, '1:index'),
    iload_0 = _def_ins('iload_0', 0x1a),
    iload_1 = _def_ins('iload_1', 0x1b),
    iload_2 = _def_ins('iload_2', 0x1c),
    iload_3 = _def_ins('iload_3', 0x1d),
    impdep1 = _def_ins('impdep1', 0xfe),
    impdep2 = _def_ins('impdep2', 0xff),
    imul = _def_ins('imul', 0x68),
    ineg = _def_ins('ineg', 0x74),
    instanceof = _def_ins('instanceof', 0xc1, '2:index'),
    invokedynamic = _def_ins('invokedynamic', 0xba, '2:index, 2:zero'),
    invokeinterface = _def_ins('invokeinterface', 0xb9, '2:index, 1:count, 1:zero'),
    invokespecial = _def_ins('invokespecial', 0xb7, '2:index'),
    invokestatic = _def_ins('invokestatic', 0xb8, '2:index'),
    invokevirtual = _def_ins('invokevirtual', 0xb6, '2:index'),
    ior = _def_ins('ior', 0x80),
    irem = _def_ins('irem', 0x70),
    ireturn = _def_ins('ireturn', 0xac),
    ishl = _def_ins('ishl', 0x78),
    ishr = _def_ins('ishr', 0x7a),
    istore = _def_ins('istore', 0x36, '1:index'),
    istore_0 = _def_ins('istore_0', 0x3b),
    istore_1 = _def_ins('istore_1', 0x3c),
    istore_2 = _def_ins('istore_2', 0x3d),
    istore_3 = _def_ins('istore_3', 0x3e),
    isub = _def_ins('isub', 0x64),
    iushr = _def_ins('iushr', 0x7c),
    ixor = _def_ins('ixor', 0x82),
    jsr = _def_ins('jsr', 0xa8, '2:branch'),
    jsr_w = _def_ins('jsr_w', 0xc9, '4:branch'),
    l2d = _def_ins('l2d', 0x8a),
    l2f = _def_ins('l2f', 0x89),
    l2i = _def_ins('l2i', 0x88),
    ladd = _def_ins('ladd', 0x61),
    laload = _def_ins('laload', 0x2f),
    land = _def_ins('land', 0x7f),
    lastore = _def_ins('lastore', 0x50),
    lcmp = _def_ins('lcmp', 0x94),
    lconst_0 = _def_ins('lconst_0', 0x09),
    lconst_1 = _def_ins('lconst_1', 0x0a),
    ldc = _def_ins('ldc', 0x12, '1:index'),
    ldc_w = _def_ins('ldc_w', 0x13, '2:index'),
    ldc2_w = _def_ins('ldc2_w', 0x14, '2:index'),
    ldiv = _def_ins('ldiv', 0x6d),
    lload = _def_ins('lload', 0x16, '1:index'),
    lload_0 = _def_ins('lload_0', 0x1e),
    lload_1 = _def_ins('lload_1', 0x1f),
    lload_2 = _def_ins('lload_2', 0x20),
    lload_3 = _def_ins('lload_3', 0x21),
    lmul = _def_ins('lmul', 0x69),
    lneg = _def_ins('lneg', 0x75),
    lookupswitch = _def_ins('lookupswitch', 0xab),
    lor = _def_ins('lor', 0x81),
    lrem = _def_ins('lrem', 0x71),
    lreturn = _def_ins('lreturn', 0xad),
    lshl = _def_ins('lshl', 0x79),
    lshr = _def_ins('lshr', 0x7b),
    lstore = _def_ins('lstore', 0x37, '1:index'),
    lstore_0 = _def_ins('lstore_0', 0x3f),
    lstore_1 = _def_ins('lstore_1', 0x40),
    lstore_2 = _def_ins('lstore_2', 0x41),
    lstore_3 = _def_ins('lstore_3', 0x42),
    lsub = _def_ins('lsub', 0x65),
    lushr = _def_ins('lushr', 0x7d),
    lxor = _def_ins('lxor', 0x83),
    monitorenter = _def_ins('monitorenter', 0xc2),
    monitorexit = _def_ins('monitorexit', 0xc3),
    multianewarray = _def_ins('multianewarray', 0xc5, '2:index, 1:dimensions'),
    new = _def_ins('new', 0xbb, '2:index'),
    newarray = _def_ins('newarray', 0xbc, '1:atype'),
    nop = _def_ins('nop', 0x00),
    pop = _def_ins('pop', 0x57),
    pop2 = _def_ins('pop2', 0x58),
    putfield = _def_ins('putfield', 0xb5, '2:index'),
    putstatic = _def_ins('putstatic', 0xb3, '2:index'),
    ret = _def_ins('ret', 0xa9, '1:index'),
    return_ = _def_ins('return', 0xb1),
    saload = _def_ins('saload', 0x35),
    sastore = _def_ins('sastore', 0x56),
    sipush = _def_ins('sipush', 0x11, '2:value'),
    swap = _def_ins('swap', 0x5f),
    tableswitch = _def_ins('tableswitch', 0xaa),
    wide = _def_ins('wide', 0xc4),
