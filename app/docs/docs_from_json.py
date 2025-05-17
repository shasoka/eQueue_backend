from pathlib import Path
from typing import Any

import orjson


class ResponseDocs:
    def __init__(self, path: str):
        self._data: dict[str, Any] = orjson.loads(Path(path).read_bytes())

    def get(self, module: str, endpoint: str) -> dict:
        try:
            return {
                "responses": self._data[module][endpoint]["responses"],
                "description": self._data[module][endpoint]["description"],
            }
        except KeyError:
            raise ValueError(
                f"Response docs not found for {module}.{endpoint}"
            )


_responses = ResponseDocs("docs/swagger_docs.json")

login_user_docs = _responses.get(
    module="users",
    endpoint="login_user",
)
