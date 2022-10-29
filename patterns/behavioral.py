import random
import datetime

from my_framework.database import db
from my_framework.templator import render
from patterns.creational import Model


# class based view
class Authenticate:
    def __call__(self, response):
        request = response.environ

        if request['REQUEST_METHOD'] == 'GET':
            content = render(request, 'auth.html', app_name='app')
            return response.ok_200(content=content)

        data = request.get('post-data')
        if data:
            username = data.get('username')
            password = data.get('password')
            users = Model.list(model_name='User')
            try:
                user = next(u for u in users if u.username == username and u.password == password)
                cookie = str(random.randint(10 ** 6, 10 ** 7))
                db.create('Session', {
                    "rowid": user.pk,
                    "session_id": cookie
                })
                response.code = '303 See Other'
                response.headers = [('Set-Cookie', f'session_id={cookie}; path=/'), ('Location', f'/')]
                response.content = render(request, 'auth.html', app_name='app').encode('UTF-8')
                return response
            except StopIteration:
                pass

        return response.bad_request_400()


# class based view
class Register:
    def __call__(self, response):
        request = response.environ

        if request['REQUEST_METHOD'] == 'GET':
            content = render(request, 'registration.html', app_name='app')
            return response.ok_200(content=content)

        data = request.get('post-data')
        if data:
            username = data.get('username')
            password = data.get('password')
            email = data.get('email')
            if username and password and email:
                user = Model.create(model_name='User', data={
                    "username": username,
                    "password": password,
                    "email": email
                })

                cookie = str(random.randint(10 ** 6, 10 ** 7))
                db.create('Session', {
                    "rowid": user.pk,
                    "session_id": cookie
                })
                response.code = '303 See Other'
                response.headers = [('Set-Cookie', f'session_id={cookie}; path=/'), ('Location', '/')]
                response.content = render(request, 'auth.html', app_name='app').encode('UTF-8')
                return response

        return response.bad_request_400()


# class based view
class Logout:
    def __call__(self, response):
        response.code = '303 See Other'
        response.headers = [("Access-Control-Expose-Headers", "Set-Cookie"),
            ("Set-Cookie", f'session_id=""; path=/'),
            ('Location', f'/')]
        return response
