# -*- coding: utf-8 -*-
from functools import wraps

def singleton(class_):
    """
    Decorator to ensure a class has only one instance.
    :param class_: Class to decorate.
    :return: Instance of the class.
    """
    __instances = {}

    @wraps(class_)
    def get_instance(*args, **kwargs):
        if class_ not in __instances:
            __instances[class_] = class_(*args, **kwargs)
        return __instances[class_]

    return get_instance
