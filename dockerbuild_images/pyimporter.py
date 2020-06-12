import importlib


_cache = {}


class PyImporterError(ImportError):
    pass


def import_no_cache(path):
    if '.' in path:
        path_to_item, last_item = path.rsplit('.', 1)
    else:
        path_to_item, last_item = path, None

    try:
        item = importlib.import_module(path_to_item)
    except ImportError as e:
        raise PyImporterError('pyimporter: import error "%s" | %s' % (
            path_to_item,
            str(e),
        ))
    except TypeError as e:
        raise TypeError('pyimporter: problem with importing "%s" | %s' % (
            path_to_item,
            str(e),
        ))

    if last_item is None:
        return item

    # In case of trying to get some submodule, like
    # "example_module.something" (where "something" is a
    # module) we will get AttributeError, because a submodule
    # is not an attribute of a given parent module (unless
    # it's imported in __init__).
    try:
        return getattr(item, last_item)
    except AttributeError:
        try:
            return importlib.import_module(path)
        except ImportError:
            raise PyImporterError('%s.>>%s<< part could not be found' % (path_to_item, last_item))


def import_(path):
    global _cache
    if path not in _cache:
        _cache[path] = import_no_cache(path)
    return _cache[path]


def invalidate_cache():
    global _cache
    _cache.clear()
