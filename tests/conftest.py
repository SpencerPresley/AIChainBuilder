import os
import pytest
from typing import Generator
from unittest.mock import patch
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def pytest_configure(config):
    """Configure pytest"""
    # Register custom markers
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )

@pytest.fixture(autouse=True)
def mock_env_vars():
    """Mock environment variables for testing"""
    with patch.dict(os.environ, {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", "test-api-key"),
        "ANTHROPIC_API_KEY": "test-anthropic-key",
        "GOOGLE_API_KEY": "test-google-key"
    }):
        yield

@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response"""
    return {
        "choices": [
            {
                "message": {
                    "content": '{"result": "test response"}'
                }
            }
        ]
    }

@pytest.fixture
def mock_anthropic_response():
    """Mock Anthropic API response"""
    return {
        "content": [
            {
                "text": '{"result": "test response"}'
            }
        ]
    }

@pytest.fixture
def mock_google_response():
    """Mock Google API response"""
    return {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": '{"result": "test response"}'
                        }
                    ]
                }
            }
        ]
    } 