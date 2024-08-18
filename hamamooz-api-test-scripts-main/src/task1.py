import random
import string

import requests
import datetime
from datetime import datetime, timedelta

from config import BASE_URL
from exceptions import EndpointTestException, ConnectionException


class EndpointTestCases:
    def __init__(self):
        self.created_item = {}
        self.second_created_item = {}
        self.by_effects = []

    def run(self):
        try:
            self.test_create()
            self.test_get()
            self.test_list()
            self.test_update()
            self.test_delete()
        except Exception as e:
            if isinstance(e, requests.exceptions.ConnectionError):
                raise ConnectionException(BASE_URL)
            # self.cleanup()
            raise e
        self.cleanup()
        print("✅  All checks have passed. Hurray! 🎉")

    def test_create(self):
        url = f"{BASE_URL}/api/v1/app/"
        method = "POST"
        endpoint_name = "create"
        headers, cookies = self._get_csrf_header_and_cookies()
        correct_data = {
            "name": f"im_a_simple_app_{self._random_chars()}",
            "size": 1,
        }
        response = requests.request(
            method=method, url=url, json=correct_data, cookies=cookies, headers=headers
        )

        if response.status_code not in [200, 201]:
            raise EndpointTestException(
                endpoint=endpoint_name,
                method=method,
                reason=f"Expected status 200, 201 but got {response.status_code}",
                extra=f"\ndata: {correct_data}",
            )
        try:
            result = response.json()
        except:
            raise EndpointTestException(
                endpoint=endpoint_name,
                method=method,
                reason=f"Response is not json serialized",
            )
        keys = ("id", "name", "size", "state")
        for key in keys:
            if not result.get(key):
                raise EndpointTestException(
                    endpoint=endpoint_name,
                    method=method,
                    reason=f"Response does not include {', '.join(keys)}",
                )
            if key not in ("id", "state") and result.get(key) != correct_data.get(key):
                raise EndpointTestException(
                    endpoint=endpoint_name,
                    method=method,
                    reason=f"response data does not match the data provided in request",
                )

        self.created_item = result
        self.by_effects.append(result)
        print("✅  Passed normal creation check")

        invalid_payloads = [
            correct_data | {"name": "a" * 1000000},
            correct_data | {"name": []},
            correct_data | {"size": "some-size"},
            correct_data | {"size": "9223372036854775"},
            correct_data | {"name": None},
            correct_data | {"size": None},
        ]
        invalid_ignorable_payloads = {
            "id": [
                correct_data | {"id": "23243432232434322324343223243432"},
                correct_data | {"id": 100000000000},
            ],
            "creation_time": [
                correct_data
                | {"creation_time": str(datetime.now() - timedelta(days=10000))},
            ],
            "state": [
                correct_data | {"state": "some-state"},
            ],
        }

        for payload in invalid_payloads:
            response = requests.request(
                method=method, url=url, json=payload, cookies=cookies, headers=headers,
            )
            if response.status_code in (200, 201):
                self.by_effects.append(response.json())
            if response.status_code in (200, 201, 500):
                raise EndpointTestException(
                    endpoint=endpoint_name,
                    method=method,
                    reason=f"Expected status 4xx for invalid data but got {response.status_code}",
                )
        for key, value in invalid_ignorable_payloads.items():
            for payload in value:
                response = requests.request(
                    method=method,
                    url=url,
                    json=payload,
                    cookies=cookies,
                    headers=headers,
                )
                if response.status_code in (200, 201):
                    self.by_effects.append(response.json())
                    if payload.get("id") == response.json().get("id"):
                        raise EndpointTestException(
                            endpoint=endpoint_name,
                            method=method,
                            reason=f"{key} should not be editable by customer",
                        )
                if response.status_code in (500,):
                    raise EndpointTestException(
                        endpoint=endpoint_name,
                        method=method,
                        reason=f"Expected status 4xx for invalid data but got {response.status_code}",
                    )

        print("✅  Passed invalid data creation check")

    def test_get(self):
        url = f'{BASE_URL}/api/v1/app/{self.created_item["id"]}/'
        method = "GET"
        endpoint_name = "get"
        response = requests.request(method=method, url=url)
        if response.status_code not in [200]:
            raise EndpointTestException(
                endpoint=endpoint_name,
                method=method,
                reason=f"Expected status 200 but got {response.status_code}",
            )
        try:
            result = response.json()
        except:
            raise EndpointTestException(
                endpoint=endpoint_name,
                method=method,
                reason=f"Response is not json serialized",
            )

        keys = ("id", "name", "size", "state")
        for key in keys:
            if not result.get(key):
                raise Exception(
                    f"Testing get [method GET]  Failed. Response does not include {', '.join(keys)}"
                )
            if result.get(key) != self.created_item.get(key):
                raise Exception(
                    f"Testing get [method GET]  Failed. response data does not match the data provided in request"
                )
        non_existent_id = "9000"
        url = f"{BASE_URL}/api/v1/app/{non_existent_id}/"
        response = requests.request(method=method, url=url)
        if response.status_code != 404:
            raise Exception(
                f"Testing get [method GET]  Failed. Expected 404 status code when app does not exist"
            )
        print("✅  Passed get check")

    def test_update(self):
        url = f'{BASE_URL}/api/v1/app/{self.created_item["id"]}/'
        method = "PUT"
        endpoint_name = "update"
        headers, cookies = self._get_csrf_header_and_cookies()
        correct_data = {
            "size": 2,
        }
        response = requests.request(
            method=method, url=url, json=correct_data, cookies=cookies, headers=headers
        )

        if response.status_code not in [200, 204]:
            raise EndpointTestException(
                endpoint=endpoint_name,
                method=method,
                reason=f"Expected status 200, 201 but got {response.status_code}",
                extra=f"\ndata: {correct_data}",
            )
        try:
            result = response.json()
        except:
            raise EndpointTestException(
                endpoint=endpoint_name,
                method=method,
                reason=f"Response is not json serialized",
            )
        keys = ("id", "name", "size", "state")
        for key in keys:
            if not result.get(key):
                raise EndpointTestException(
                    endpoint=endpoint_name,
                    method=method,
                    reason=f"Response does not include {', '.join(keys)}",
                )
        if result.get('size') != correct_data.get('size'):
            raise EndpointTestException(
                endpoint=endpoint_name,
                method=method,
                reason=f"The update may not have happened, did not receive the updated value in response",
            )

        self.created_item = result
        self.by_effects.append(result)
        print("✅  Passed normal update check")

        invalid_payloads = [
            {"size": "some-size"},
            {"size": "9223372036854775"},
            {"size": None},
        ]

        cannot_be_changed_payloads = {
            "name": [
                {"name": f"im_a_moderate_app_{self._random_chars()}"},
            ],

            "id": [
                {"id": 100100},
            ],
            "creation_time": [
                {"creation_time": str(datetime.now() - timedelta(days=10000))},
            ],
            "state": [
                {"state": "some-state"},
            ],
        }
        should_only_change_specified_payload = {"size": 3, "name": f"im_a_moderate_app_{self._random_chars()}"}

        for payload in invalid_payloads:
            response = requests.request(
                method=method, url=url, json=payload, cookies=cookies, headers=headers,
            )

            if response.status_code in (200, 201, 204, 500):
                raise EndpointTestException(
                    endpoint=endpoint_name,
                    method=method,
                    reason=f"Expected status 4xx for invalid data but got {response.status_code}"
                )
        for key, value in cannot_be_changed_payloads.items():
            for payload in value:
                response = requests.request(
                    method=method, url=url, json=payload, cookies=cookies, headers=headers,
                )
                if response.status_code in (200, 201, 204):
                    result = response.json()
                    if result.get(key) == payload.get(key):
                        raise EndpointTestException(
                            endpoint=endpoint_name,
                            method=method,
                            reason=f"Expected {key} to not change but it did"
                        )

        response = requests.request(
            method=method, url=url, json=should_only_change_specified_payload, cookies=cookies, headers=headers,
        ).json()
        if response.get("name") == should_only_change_specified_payload.get("name"):
            raise EndpointTestException(
                endpoint=endpoint_name,
                method=method,
                reason=f"Expected name to not change but it did"
            )
        if response.get("size") != should_only_change_specified_payload.get("size"):
            raise EndpointTestException(
                endpoint=endpoint_name,
                method=method,
                reason=f"Expected size to be updated but it did not"
            )

        print("✅  Passed invalid data update check")

    def test_list(self):
        url = f"{BASE_URL}/api/v1/apps/"
        method = "GET"
        endpoint_name = "list"
        headers, cookies = self._get_csrf_header_and_cookies()
        self.second_created_item = requests.request(
            method="POST",
            url=f"{BASE_URL}/api/v1/app/",
            json={
                "name": f"im_a_complex_app_{self._random_chars()}",
                "size": 2,
            },
            cookies=cookies,
            headers=headers,
        ).json()
        self.by_effects.append(self.second_created_item)

        response = requests.request(method=method, url=url)
        if response.status_code not in [200, 201, 202, 204]:
            raise EndpointTestException(
                endpoint=endpoint_name,
                method=method,
                reason=f"Expected status 2xx but got {response.status_code}",
            )

        try:
            result = response.json()
        except:
            raise EndpointTestException(
                endpoint=endpoint_name,
                method=method,
                reason=f"Response is not json serialized",
            )

        result = result.get("results")
        if result == None:
            raise EndpointTestException(
                endpoint=endpoint_name,
                method=method,
                reason=f"Expected data to be in 'results' key",
            )

        if not result:
            raise EndpointTestException(
                endpoint=endpoint_name,
                method=method,
                reason=f"list is empty when it shouldn't be",
            )
        keys = ("id", "name", "size", "state")

        for item in result:
            for key in keys:
                if not item.get(key):
                    raise EndpointTestException(
                        endpoint=endpoint_name,
                        method=method,
                        reason=f"Response does not include {', '.join(keys)}",
                    )
        print("✅  Passed list check")

    def test_delete(self):
        url = f"{BASE_URL}/api/v1/app/{self.created_item.get('id')}/"
        method = "DELETE"
        endpoint_name = "delete"
        headers, cookies = self._get_csrf_header_and_cookies()
        response = requests.request(method=method, url=url, headers=headers, cookies=cookies)
        if response.status_code not in [200, 202, 204]:
            raise EndpointTestException(
                endpoint=endpoint_name,
                method=method,
                reason=f"Expected status 200,202, or 204 but got {response.status_code}",
            )
        try:
            result = response.json()
        except:
            raise EndpointTestException(
                endpoint=endpoint_name,
                method=method,
                reason=f"Response is not json serialized",
            )

        exsitence_test_check_response = requests.request(method="GET", url=url, headers=headers, cookies=cookies)
        if exsitence_test_check_response.status_code != 404:
            try:
                resp = exsitence_test_check_response.json()
            except:
                raise EndpointTestException(
                    endpoint=endpoint_name,
                    method=method,
                    reason=f"Response is not json serialized",
                )
            if resp.get("id") == self.created_item.get("id"):
                raise EndpointTestException(
                    endpoint=endpoint_name,
                    method=method,
                    reason=f"Expected data to be deleted but it doesn't seem to be",
                )

        print("✅  Passed delete check")

    def cleanup(self):
        print("Cleaning up...")
        for item in self.by_effects:
            url = f"{BASE_URL}/api/v1/app/{item.get('id')}/"
            try:
                requests.request(method="DELETE", url=url)
            except:
                pass

    def _random_chars(self, length: int = 4):
        return "".join(random.choices(string.ascii_letters + string.digits, k=length))

    def _get_csrf_header_and_cookies(self):
        response = requests.get(f"{BASE_URL}/admin/")
        token = response.cookies.get("csrftoken")
        return {"X-CSRFToken": token}, {"csrftoken": token}
