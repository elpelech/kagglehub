from http import HTTPStatus
from typing import Any, Dict, Optional

import aiohttp
import aiohttp.web_exceptions
import requests

from kagglehub.handle import ResourceHandle


class CredentialError(Exception):
    pass


class KaggleEnvironmentError(Exception):
    pass


class ColabEnvironmentError(Exception):
    pass


class BackendError(Exception):
    def __init__(self, message: str, error_code: Optional[int] = None) -> None:
        self.error_code = error_code
        super().__init__(message)


class NotFoundError(Exception):
    pass


class DataCorruptionError(Exception):
    pass


class KaggleApiHTTP1Error(Exception):
    def __init__(self, message: str, response: Optional[aiohttp.ClientResponse] = None) -> None:
        self.message = message
        self.response = response


class ColabHTTP1Error(Exception):
    def __init__(self, message: str, response: Optional[aiohttp.ClientResponse] = None) -> None:
        self.message = message
        self.response = response


class KaggleApiHTTPError(requests.HTTPError):
    def __init__(self, message: str, response: Optional[requests.Response] = None) -> None:
        super().__init__(message, response=response)


class ColabHTTPError(requests.HTTPError):
    def __init__(self, message: str, response: Optional[requests.Response] = None) -> None:
        super().__init__(message, response=response)


class UnauthenticatedError(Exception):
    """Exception raised for errors in the authentication process."""

    def __init__(self, message: str = "User is not authenticated") -> None:
        super().__init__(message)


def kaggle_api_raise_for_status(
    response: aiohttp.ClientResponse, resource_handle: Optional[ResourceHandle] = None
) -> None:
    """
    Wrapper around `response.raise_for_status()` that provides nicer error messages
    See: https://requests.readthedocs.io/en/latest/api/#requests.Response.raise_for_status
    """
    try:
        response.raise_for_status()
    except aiohttp.web_exceptions.HTTPUnauthorized as e:
        message = str(e)
        resource_url = resource_handle.to_url() if resource_handle else response.url
        message = (
            f"{response.status_code} Client Error."
            "\n\n"
            f"You don't have permission to access resource at URL: {resource_url}"
            "\nPlease make sure you are authenticated if you are trying to access a private resource or a resource"
            " requiring consent."
        )
        raise KaggleApiHTTP1Error(message, response=response) from e
    except aiohttp.web_exceptions.HTTPForbidden as e:
        message = str(e)
        resource_url = resource_handle.to_url() if resource_handle else response.url
        message = (
            f"{response.status_code} Client Error."
            "\n\n"
            f"You don't have permission to access resource at URL: {resource_url}"
            "\nPlease make sure you are authenticated if you are trying to access a private resource or a resource"
            " requiring consent."
        )
        raise KaggleApiHTTP1Error(message, response=response) from e
    except aiohttp.web_exceptions.HTTPNotFound as e:
        message = (
            f"{response.status_code} Client Error."
            "\n\n"
            f"Resource not found at URL: {resource_url}"
            "\nPlease make sure you specified the correct resource identifiers."
        )
        raise KaggleApiHTTP1Error(message, response=response) from e


def colab_raise_for_status(response: aiohttp.ClientResponse, resource_handle: Optional[ResourceHandle] = None) -> None:
    """
    Wrapper around `response.raise_for_status()` that provides nicer error messages
    See: https://requests.readthedocs.io/en/latest/api/#requests.Response.raise_for_status
    """
    try:
        response.raise_for_status()
    except aiohttp.web_exceptions.HTTPError as e:
        message = str(e)
        resource_url = resource_handle.to_url() if resource_handle else response.url

        if response.status in {HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN}:
            message = (
                f"{response.status} Client Error."
                "\n\n"
                f"You don't have permission to access resource at URL: {resource_url}"
                "\nPlease make sure you are authenticated if you are trying to access a private resource or a resource"
                " requiring consent."
            )
        # Default handling
        raise ColabHTTP1Error(message, response=response) from e


def process_post_response(response: Dict[str, Any]) -> None:
    """
    Postprocesses the API response to check for errors.
    """
    if not (200 <= response.get("code", 200) < 300):  # noqa: PLR2004
        error_message = response.get("message", "No error message provided")
        raise BackendError(error_message)
    elif "error" in response and response["error"] != "":
        error_code = int(response["errorCode"]) if "errorCode" in response else None
        raise BackendError(response["error"], error_code)
