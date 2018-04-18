def open_file(func):
    def wrapper(*args, **kwargs):
        file = open(kwargs["filepath"], 'r')
        func(*args, file)
        file.close()

    return wrapper


def support_arguments(func):
    def wrapper(args):
        if args is None:
            func()
        else:
            func(*args)

    return wrapper


def flatten(container):
    for i in container:
        if isinstance(i, (list, tuple)):
            for j in flatten(i):
                yield j
        else:
            yield i

def str_to_int_or_float(s):
    f = float(s)
    i = int(f)
    return i if i == f else f