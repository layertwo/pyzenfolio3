class APIError(Exception):
    pass


class ConfigError(APIError):
    pass


class ZenfolioError(APIError):
    def __init__(self, code, message):
        super().__init__()
        self.code = code
        self.message = message

    def __str__(self):
        return '{} - {}'.format(self.code, self.message)


class HTTPError(APIError):
    def __init__(self, url, status_code, headers, content):
        super().__init__()
        self.url = url
        self.status_code = status_code
        self.headers = headers
        self.content = content

    def __str__(self):
        return '{} - {}'.format(self.url, self.status_code)
