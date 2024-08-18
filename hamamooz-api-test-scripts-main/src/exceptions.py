from typing import Optional


class EndpointTestException(Exception):
    def __init__(
        self, endpoint: str, method: str, reason: str, extra: Optional[str] = None
    ):
        msg = f"Testing {endpoint} [method {method}]  Failed. {reason}. {extra or ''}"
        super().__init__(msg)


class ConnectionException(Exception):
    def __init__(self, base_url):
        super().__init__(
            f"Failed to connect to {base_url}. Are you sure your project is up and running?"
        )
