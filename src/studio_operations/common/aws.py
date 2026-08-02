from __future__ import annotations

from collections.abc import Iterator
from typing import Any


def pages(client: Any, operation: str, **kwargs: Any) -> Iterator[dict[str, Any]]:
    """Yield API pages, falling back for operations without a paginator."""
    if client.can_paginate(operation):
        yield from client.get_paginator(operation).paginate(**kwargs)
    else:
        yield getattr(client, operation)(**kwargs)
