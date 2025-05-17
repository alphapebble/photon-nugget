"""
Error handling for the API client.

This module provides error handling utilities for the API client.
"""
import requests
from typing import Dict, Type

# Error messages by exception type
ERROR_MESSAGES: Dict[Type[Exception], str] = {
    requests.ConnectionError: "Connection Error: Could not connect to the server. Please check if the server is running by executing './solar_sage.sh api start' in a terminal.",
    requests.Timeout: "Timeout Error: The server took too long to respond. Please try again later.",
    requests.RequestException: "Request Error: There was an error making the request to the server.",
}

# HTTP status code error messages
HTTP_ERROR_MESSAGES: Dict[int, str] = {
    400: "Bad Request: The server could not understand the request.",
    401: "Unauthorized: Authentication is required to access this resource.",
    403: "Forbidden: You don't have permission to access this resource.",
    404: "Not Found: The requested endpoint was not found.",
    429: "Too Many Requests: You've sent too many requests. Please wait and try again later.",
    500: "Internal Server Error: The server encountered an unexpected condition.",
    502: "Bad Gateway: The server received an invalid response from an upstream server.",
    503: "Service Unavailable: The server is temporarily unable to handle the request.",
    504: "Gateway Timeout: The upstream server failed to send a response in time."
}

def format_api_error(error: Exception) -> str:
    """
    Format API error messages in a user-friendly way.

    Args:
        error: The exception that occurred

    Returns:
        A user-friendly error message
    """
    # Check for specific exception types
    for error_type, message in ERROR_MESSAGES.items():
        if isinstance(error, error_type):
            return f"ERROR: {message}"

    # Check for HTTP errors
    if isinstance(error, requests.HTTPError) and error.response is not None:
        status_code = error.response.status_code
        if status_code in HTTP_ERROR_MESSAGES:
            return f"SERVER ERROR: {HTTP_ERROR_MESSAGES[status_code]}"
        else:
            return f"HTTP ERROR: The server returned status code {status_code}."

    # Check for JSON parsing errors
    if isinstance(error, ValueError) and "JSON" in str(error):
        return "RESPONSE ERROR: The server response was not in the expected format."

    # Generic error message
    return f"ERROR: {str(error)}"
