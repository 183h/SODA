from os import remove


def prepare_file(func):
    def wrapper(*args, **kwargs):

        print ("Preparing temp file...\n")

        file = open(kwargs["filepath"], 'r')
        # data = file.read()
        # file.close()
        # stripped_data = data.replace("\n", "").replace(" ", "")
        # temp_file = open(kwargs["filepath"] + ".temp", "w+")
        # temp_file.write(stripped_data)
        # temp_file.seek(0, 0)

        func(*args, file)

        # temp_file.close()
        # remove(kwargs["filepath"] + ".temp")

        print ("\nDeleting temp file...")

    return wrapper
