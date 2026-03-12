import os
import sys
import json
from typing import List, Dict

# Unused import (code smell)
import hashlib

# Hardcoded secret (security issue)
SECRET_KEY = "supersecretkey123"

def insecure_function(password: str) -> str:
    """Function with security vulnerabilities."""
    # Weak hashing (security issue)
    hashed = hashlib.md5(password.encode()).hexdigest()
    return hashed

def process_list(items: List[str]) -> Dict[str, int]:
    """Process list with potential issues."""
    result = {}
    for item in items:
        # Missing input validation (could cause errors)
        result[item] = len(item)
    return result

def unused_function():
    """This function is never called (dead code)."""
    return "This is dead code"

# Global variable that might not be used
GLOBAL_VAR = 42

if __name__ == "__main__":
    # Potential division by zero (runtime error)
    divisor = 0
    result = 10 / divisor
    print(result)