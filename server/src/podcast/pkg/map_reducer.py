import multiprocessing
from multiprocessing import Pool


class MapReducer:
    def __init__(self, map_size: int, data, map_func, reduce_func=None):
        self.map_size = map_size
        self.data = data
        self.result = []
        self.map_func = map_func
        self.reduce_func = self.default_reduce_map if reduce_func is None else reduce_func

    def default_reduce_map(self, item):
        self.result.append(item)

    def run(self, *args):
        with Pool(self.map_size) as p:
            for item in self.data:
                item_bk = item
                map_func_args = [item_bk]
                map_func_args.extend(args)
                ret = p.apply_async(self.map_func, args=map_func_args, callback=self.default_reduce_map)
            p.close()
            p.join()
        return self.result


def map_reducer_decorator():
    def wrapper(map_func):
        def inner(data, reduce_func, *args):
            map_size = multiprocessing.cpu_count()
            return MapReducer(map_size, data, map_func, reduce_func).run(*args)

        return inner

    return wrapper
