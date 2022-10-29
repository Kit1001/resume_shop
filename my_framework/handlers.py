from my_framework.front_controller import front_controller
from my_framework.http import Response
from my_framework.page_controller import page_controller


def request_handler(environ, start_response):
    # Принимает environ и start_response, проставляет код ответа и возвращает подготовленный ответ в application.
    response = Response(environ=environ)
    response = front_controller(response)
    response = page_controller(response)

    start_response(response.code, response.headers)
    return [response.content]
