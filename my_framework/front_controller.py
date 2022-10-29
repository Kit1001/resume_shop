from inspect import isfunction

from my_framework import middleware
from my_framework.http import Response


def front_controller(response: Response):
    # Принимает объект request, выполняет все функции из модуля middleware,
    # передавая в них объект request, затем возвращает его.
    middleware_vars = vars(middleware)
    middleware_funcs = [middleware_vars.get(func) for func in middleware_vars if
                        isfunction(middleware_vars[func])
                        and not getattr(middleware_vars[func], '__name__').startswith('_')]
    request = response.environ
    for func in middleware_funcs:
        request = func(request)

    response.environ = request
    return response
