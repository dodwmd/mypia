import cProfile
import pstats
import io
from memory_profiler import profile as memory_profile
from functools import wraps

def cpu_profile(output_file=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            pr = cProfile.Profile()
            pr.enable()
            result = func(*args, **kwargs)
            pr.disable()
            
            if output_file:
                with open(output_file, 'w') as f:
                    ps = pstats.Stats(pr, stream=f).sort_stats('cumulative')
                    ps.print_stats()
            else:
                s = io.StringIO()
                ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
                ps.print_stats()
                print(s.getvalue())
            
            return result
        return wrapper
    return decorator

def memory_profile_decorator(output_file=None):
    def decorator(func):
        @wraps(func)
        @memory_profile(stream=open(output_file, 'w') if output_file else None)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorator
