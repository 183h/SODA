from os import remove


def open_file(func):
    def wrapper(*args, **kwargs):
        print ("Opening file...\n")
        file = open(kwargs["filepath"], 'r')

        func(*args, file)

        print ("\Closing temp file...")
        file.close()

    return wrapper
