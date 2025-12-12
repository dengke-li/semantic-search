from tenacity import (
    retry,
    retry_if_exception,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)
import httpx


def is_retriable_http_status(exc: BaseException) -> bool:
    """
    Retry ONLY on:
    - 429 Too Many Requests
    - transient 503 Service Unavailable
    """
    return (
        isinstance(exc, httpx.HTTPStatusError)
        and exc.response is not None
        and exc.response.status_code in {429, 503}
    )

# Retry policy for **NETWORK ERRORS** and rate limit errors and **429 / 503**
retry_policy = retry(
    retry=(
        retry_if_exception_type(httpx.RequestError) |     # connection drop, DNS, timeout
        retry_if_exception(is_retriable_http_status)
    ),
    stop=stop_after_attempt(4),
    wait=wait_exponential(multiplier=0.5, min=0.5, max=6),
    reraise=True,
)