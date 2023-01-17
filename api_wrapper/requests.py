import requests


class RequestException(Exception):

    def __init__(self, url, message, status_code):
        self.url = url
        self.message = message
        self.status_code = status_code


class RequestBase:

    SUCCESS_CODES = (200, 201)

    def get(self, url, params=None, headers=None):
        return requests.get(url, params=params, headers=headers)

    def post(self, url, json_data, headers=None):
        return requests.post(
            url, json=json_data, headers=headers)

    def put(self, url, json_data, headers=None):
        return requests.put(url, json=json_data, headers=headers)

    def patch(self, url, json_data, headers=None):
        return requests.patch(url, json=json_data, headers=headers)

    def delete(self, url, headers=None):
        return requests.delete(url, headers=headers)

    def get_response(self, response):
        res_json = response.json()
        status_code = response.status_code
        url = response.request.url
        if status_code in self.SUCCESS_CODES:
            return res_json
        raise RequestException(url, res_json, status_code)
