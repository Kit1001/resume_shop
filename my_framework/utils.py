import os
import re
from urllib.parse import unquote

from patterns.creational import Model, Prototype


def parse_query(request: dict) -> dict | None:
    query_string = request.get('QUERY_STRING')
    if not query_string:
        return None
    result = {}
    r = re.compile(r'^([^=]*)=(.*)$')
    query_string = query_string.split('&')
    for string in query_string:
        key, value = r.findall(string)[0]
        result[unquote(key)] = unquote(value)
    return result


def parse_post(request: dict) -> dict | None:
    result = {}
    content_length = int(request.get('CONTENT_LENGTH')) if request.get('CONTENT_LENGTH') != '' else 0
    data = request['wsgi.input'].read(content_length).decode('UTF-8').split('&')
    r = re.compile(r'^([^=]*)=(.*)$')
    for string in data:
        key, value = r.findall(string)[0]
        result[unquote(key)] = unquote(value)
    return result


def get_views():
    def condition(directory):
        condition_1 = not directory.startswith(('.', '_'))
        condition_2 = os.path.isdir(directory)
        return all((condition_1, condition_2))

    dirs = [d for d in os.listdir() if condition(d) and 'views.py' in os.listdir(d)]
    return dirs
