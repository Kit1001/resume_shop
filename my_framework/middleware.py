"""
Функции для обработки запроса перед передачей его в page controller.
Каждая функция должна принимать и возвращать объект request.
Front controller вызывает все функции прописанные в модуле.
"""
import re
import urllib.parse

import app.notifications as notifications
import app.cart as cart
from patterns.system_architecture import dm


def session(request):
    from http import cookies
    from patterns.creational import Model

    request["USER"] = 'Anonymous'
    raw_cookie = request.get('HTTP_COOKIE', '')
    c = cookies.SimpleCookie()
    c.load(raw_cookie.replace(': ', ''))
    c_session = c.get('session_id')
    session_id = c_session.value if c_session else None
    if session_id:
        dm.cursor.execute('SELECT rowid, session_id FROM session WHERE session_id=?', (session_id,))
        try:
            user_pk = str(dm.cursor.fetchone()[0])
            request["USER"] = Model.retrieve(model_name='User', pk=user_pk)
        except TypeError:
            pass

    return request


def notifications_middleware(request):
    user = request["USER"]
    if user == 'Anonymous':
        return request

    user_pk = request["USER"].pk
    notes = notifications.retrieve_unread_number(user_pk=user_pk)[0]
    request['USER'].notifications = int(notes)
    return request


def cart_middleware(request):
    user = request["USER"]
    if user == 'Anonymous':
        return request

    user_pk = request["USER"].pk
    cart_items_num, cart_items, cart_full_cost = cart.get_detailed_cart(user_pk)
    request['USER'].cart_items_num = cart_items_num
    request['USER'].cart_items = cart_items
    request['USER'].cart_full_cost = cart_full_cost
    return request


def correct_trailing_slash(request):
    # Функция добавляет / в конец пути, если его там нет
    path: str = request['PATH_INFO']
    if not path.endswith('/'):
        request['PATH_INFO'] = f"{path}/"
    return request


def parse_query(request: dict) -> dict:
    # парсинг query string из запроса
    query_string = request.get('QUERY_STRING')
    if not query_string:
        return request

    result = {}
    r = re.compile(r'^([^=]*)=(.*)$')
    query_string = query_string.split('&')
    for string in query_string:
        key, value = r.findall(string)[0]
        result[urllib.parse.unquote_plus(key)] = urllib.parse.unquote_plus(value)
    request['query'] = result
    return request


def parse_post(request: dict) -> dict:
    # парсинг данных из post-запроса
    if request['REQUEST_METHOD'] != 'POST':
        return request

    result = {}
    content_length = int(request.get('CONTENT_LENGTH')) if request.get('CONTENT_LENGTH') != '' else 0
    data = request['wsgi.input'].read(content_length).decode('UTF-8').split('&')
    r = re.compile(r'^([^=]*)=(.*)$')
    for string in data:
        key, value = r.findall(string)[0]
        result[urllib.parse.unquote_plus(key)] = urllib.parse.unquote_plus(value)

    request['post-data'] = result
    print(result)
    return request
