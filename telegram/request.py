import json
import urllib.error
import urllib.parse
import urllib.request

from exceptions import LiteTelegramException


def request(url: str, data: dict, method: str) -> dict:
    try:
        return _request(url, data, method)
    except (urllib.error.URLError, json.JSONDecodeError) as exc:
        raise LiteTelegramException("Failed to request url: {}.", exc)


def _request(url: str, data: dict, method: str) -> dict:
    encoded_data = urllib.parse.urlencode(data).encode("utf-8")
    request = urllib.request.Request(url, data=encoded_data, method=method)

    with urllib.request.urlopen(request) as response:
        status_code = response.getcode()
        if status_code == 200:
            response_data = response.read()
        else:
            raise LiteTelegramException("Status code is not ok: {status_code}.")

    json_data = response_data.decode("utf-8")
    return json.loads(json_data)
