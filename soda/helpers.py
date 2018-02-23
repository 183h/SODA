def open_file(func):
    def wrapper(*args, **kwargs):
        file = open(kwargs["filepath"], 'r')
        func(*args, file)
        file.close()

    return wrapper
