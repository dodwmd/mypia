import cProfile
import pstats
import io
from memory_profiler import profile as memory_profile
from functools import wraps


def cpu_profile(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        pr = cProfile.Profile()
        pr.enable()
        result = func(*args, **kwargs)
        pr.disable()
        s = io.StringIO()
        ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
        ps.print_stats()
        print(s.getvalue())
        return result
    return wrapper


def memory_profile_decorator(func):
    @wraps(func)
    @memory_profile
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper
