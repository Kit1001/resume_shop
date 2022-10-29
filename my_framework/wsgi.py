import time

from my_framework.handlers import request_handler


# def timeit(func):
#     def wrapper(*args, **kwargs):
#         start = time.perf_counter()
#         result = func(*args, **kwargs)
#         print(time.perf_counter() - start)
#         return result
#
#     return wrapper


def application(environ, start_response):
    response = request_handler(environ, start_response)
    return response
