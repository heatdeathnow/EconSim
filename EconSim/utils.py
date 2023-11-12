from __future__ import annotations
from variables import logger, working_directory
from typing import Callable, Any, Self
from time import perf_counter
from sys import exc_info
from linecache import getline
from abc import ABCMeta

class MethodLogger(ABCMeta):
    def __new__(cls: type[Self], name: str, bases: tuple[type, ...], namespace: dict[str, Any]) -> type:
        for key, val in namespace.items():
            if not key.startswith('__') and callable(val):
                namespace[key] = log(val)

        return type(name, bases, namespace)

# class MethodLogger(ABCMeta):
#     def __new__(cls: type[Self], name: str, bases: tuple[type, ...], namespace: dict[str, Any]) -> Self:
#         for key, val in namespace.items():
#             if not key.startswith('__') and callable(val):
#                 namespace[key] = log(val)

#         return super().__new__(cls, name, bases, namespace)    

def log(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Logs the time taken for the decorated function or method to complete. It also logs the exceptions that might occour.
    """

    def wrapper(*args, **kwargs) -> Any:
        result = None

        try:
            start_time = perf_counter()
            result = func(*args, **kwargs)
            end_time = perf_counter()

            logger.info(f"""Time taken for callable `{func.__name__}` to complete: {end_time - start_time:.2f} seconds.""")
        
        except Exception:
            exc_type, _, exc_traceback = exc_info()
            exc_traceback = exc_traceback.tb_next  # type: ignore

            exception_type = exc_type.__name__  # type: ignore
            exception_func = exc_traceback.tb_frame.f_code.co_name  # type: ignore
            exception_line = exc_traceback.tb_lineno  # type: ignore
            exception_file = '.' + exc_traceback.tb_frame.f_code.co_filename[len(working_directory):]  # type: ignore
            exception_code = getline(exception_file, exception_line).strip()
            
            if exc_traceback is None:
                logger.info(f"""A `{exception_type}` Exception has been handled within the `{exception_func}` callable.""")

            else:
                message = f"""A `{exception_type}` Exception within the `{exception_func}` callable has cause a crash.
The exception occured within the "{exception_file}" module, at the {exception_line}º line. It was caused by the following line of code: `{exception_code}`.
"""

                logger.critical(message)
                return

        return result

    return wrapper
