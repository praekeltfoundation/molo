# Inspired by http://stackoverflow.com/a/28507806
def mocked_requests_get(*args, **kwargs):
    """ This object will be used to mock requests.get() """
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    if args[0] == 'http://someurl.com/test.json':
        return MockResponse({"key1": "value1"}, 200)
    else:
        return MockResponse({"key2": "value2"}, 200)

    return MockResponse({}, 404)
