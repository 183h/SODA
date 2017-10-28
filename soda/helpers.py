from os import remove
from functools import wraps


def prepare_file(func):
    @wraps(func)
    def wrapper(*args, **kwargs):

        print("Preparing temp file...")

        file = open(kwargs["filepath"], 'r')
        data = file.read()
        file.close()
        stripped_data = data.replace(" ", "").replace("\n", " ")
        newfile = open(kwargs["filepath"] + ".temp", "w+")
        newfile.write(stripped_data)
        newfile.seek(0, 0)

        func(*args, newfile)

        newfile.close()
        remove(kwargs["filepath"] + ".temp")

        print("Deleting temp file...")

    return wrapper
