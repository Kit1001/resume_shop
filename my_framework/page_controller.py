import importlib

from my_framework.utils import get_views
from my_framework.http import Response
from my_framework.routes import routes as routes
from patterns.structural import routes as dec_routes


def page_controller(response: Response) -> Response:
    # Принимает объект request, вызывает соответствующее пути представление,
    # передавая в него объект request, затем возвращает подготовленный html контент.
    request = response.environ
    path = request['PATH_INFO']
    routes.update(dec_routes)
    view = routes.get(path)
    if view:
        return view(response)
    else:
        return response


for view_file in get_views():
    importlib.import_module(f'{view_file}.views')
