import sys
from pathlib import Path

# Ensure the repository root is on sys.path so tests can import app.py
sys.path.append(str(Path(__file__).resolve().parents[1]))

from app import greet


def test_greet_default():
    assert greet() == "Hello, world!"


def test_greet_name():
    assert greet("Rohan") == "Hello, Rohan!"
