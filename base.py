
class Object(object):
    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self.__dict__)