import os

BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000")

# for addr in ("127.0.0.1", "localhost"):
#     if addr in BASE_URL:
#         BASE_URL = BASE_URL.replace(addr, "host.docker.internal")
