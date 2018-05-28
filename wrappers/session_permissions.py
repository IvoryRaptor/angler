import inspect


def session_permissions_func(func):
    def wrapper(*args, **kw):
        handle = args[0]
        p = handle.resource + '/' + handle.action
        permissions = handle.get_session('permissions', [])
        if p in permissions:
            return func(*args, **kw)
    return wrapper

def undo_func(obj):
    pass

def session_permissions_class(cls):
    # Get the original implementation
    orig_getattribute = cls.__getattribute__

    # Make a new definition
    def new_getattribute(self, name):
        result = orig_getattribute(self, name)
        if hasattr(result, '__call__') and inspect.signature(result).parameters.__len__() == 1:
            p = orig_getattribute(self, 'resource') + '/' + orig_getattribute(self, 'action')
            permissions = orig_getattribute(self, 'get_session')('permissions', [])
            if p not in permissions:
                return undo_func
        return result

    # Attach to the class and return
    cls.__getattribute__ = new_getattribute
    return cls