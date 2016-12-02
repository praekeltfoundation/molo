from .constants import AVAILABLE_ARTICLES
from .constants import RELATED_IMAGE


# Inspired by http://stackoverflow.com/a/28507806
def mocked_requests_get(url, *args, **kwargs):
    """ This object will be used to mock requests.get() """
    class MockResponse:
        def __init__(self, content, status_code):
            self.content = content
            self.status_code = status_code

        def content(self):
            return self.content

    if url == "http://localhost:8000/api/v2/pages/":
        return MockResponse(AVAILABLE_ARTICLES, 200)
    elif url == "http://localhost:8000/api/v2/images/1":
        return MockResponse(RELATED_IMAGE, 200)

    return MockResponse({}, 404)
