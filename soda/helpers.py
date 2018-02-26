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
