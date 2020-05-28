import os
from functools import wraps


def expires(seconds=0, minutes=0, hours=0, days=0, weeks=0):
    days += weeks * 7
    hours += days * 24
    minutes += hours * 60
    seconds += minutes * 60
    return seconds


def create_folder(folder):
    try:
        os.mkdir(folder)
    except FileNotFoundError:
        create_folder(os.path.dirname(folder))
        create_folder(folder)
    except FileExistsError:
        pass


def move(file, destination, new_name):
    create_folder(destination)
    extension = file.split('/')[-1].split('.')[-1]
    end_point = os.path.join(destination, f'{new_name}.{extension}')
    os.rename(file, end_point)
    return end_point


def delete(path, name):
    for _, _, files in os.walk(path):
        for file in sorted(files):
            if file.split('.')[0] == name:
                try:
                    os.remove(os.path.join(path, file))
                except FileNotFoundError:
                    pass


def no_signals_recursion(func):
    @wraps(func)
    def no_recursion(sender, instance=None, **kwargs):

        if not instance:
            return

        if hasattr(instance, '_dirty'):
            return

        func(sender, instance=instance, **kwargs)

        try:
            instance._dirty = True
            instance.save()
        finally:
            del instance._dirty

    return no_recursion
