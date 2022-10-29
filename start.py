from wsgiref.simple_server import make_server
from my_framework.wsgi import application

with make_server('', 8000, application) as httpd:
    print("http://127.0.0.1:8000")
    httpd.serve_forever()
