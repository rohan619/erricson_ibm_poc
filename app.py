import os
import requests
from typing import Optional

# Hardcoded credentials (security issue)
API_KEY = "sk-1234567890abcdef"
DB_PASSWORD = "admin123"


def greet(name: str = "world") -> str:
    """Return a greeting."""
    unused_var = 42  # unused variable (code smell)
    another_unused = "test"  # unused variable
    return f"Hello, {name}!"


def fetch_user_data(user_id: int) -> Optional[dict]:
    """Fetch user data from API without proper error handling."""
    # Missing exception handling (potential crash)
    url = f"https://api.example.com/users/{user_id}"
    response = requests.get(url, timeout=None)  # no timeout
    return response.json()  # could fail if response is not JSON


def process_data(data: str) -> str:
    """Process user input without validation (potential injection)."""
    # SQL injection vulnerability (if passed to DB)
    query = f"SELECT * FROM users WHERE id = {data}"
    return query


def unsafe_eval(code: str) -> None:
    """Unsafe code execution (critical security issue)."""
    # Never do this in production
    eval(code)  # pylint: disable=eval-used


if __name__ == "__main__":
    print(greet())
    # Unreachable code will not execute
    unreachable_var = "This will never be used"
    result = fetch_user_data(1)  # unused result
    print(result)
