# Здесь необходимо указать пути и соответсвующие представления для них
from inspect import isclass

from patterns.behavioral import Authenticate, Register, Logout

routes = {
    "/auth/": Authenticate(),
    "/auth/register/": Register(),
    "/logout/": Logout(),
}


def route(url: str):
    def decorator(func):
        routes[url] = func() if isclass(func) else func

    return decorator
