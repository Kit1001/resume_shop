class Response:

    def __init__(self, environ, code="404 Not Found", headers=None, content: bytes = b'404 Not Found'):
        if headers is None:
            headers = [('Content-type', 'text/plain; charset=utf-8')]
        self.headers = headers
        self.code = code
        self.content = content
        self.environ = environ

    def ok_200(self, content, headers=None):
        if headers is None:
            headers = []
        self.headers = [('Content-type', 'text/html; charset=utf-8')]
        self.headers.extend([*headers])
        self.content = content.encode('UTF-8')
        self.code = "200 OK"
        return self

    def redirect_303(self, url: str):
        self.code = "303 See Other"
        self.headers.extend([('Location', url)])
        return self

    def bad_request_400(self, content=b'Bad Request'):
        self.code = "400 Bad Request"
        self.content = content
        return self

    def method_not_allowed_405(self, content=b'Method Not Allowed'):
        self.code = "405 Method Not Allowed"
        self.content = content
        return self

    def set_cookie(self):
        self.code = "303 See Other"
        self.headers = [('Content-type', 'text/html; charset=utf-8'),
                        ('Set-Cookie:', 'session_id=123'),
                        ('Location', '/')
                        ]
        return self
