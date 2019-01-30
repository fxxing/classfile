from attribute import Code
from classfile import ClassFile
from const import Utf8Info
from stream import Stream

if __name__ == "__main__":
    with open('/Users/fxxing/Desktop/rt/java/lang/Byte.class', 'rb') as f:
        stream = Stream(f)
        cf = ClassFile(stream)
        # print(cf)
        for method in cf.methods:
            name: Utf8Info = cf.constants[method.name_index]
            print(name.bytes)
            code = method.get_attribute(Code)
            for ins in code.instructions:
                print('\t', ins)
