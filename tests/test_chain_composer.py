import os
import pytest
from pydantic import BaseModel
from typing import Dict, Any
from unittest.mock import patch

from chain_composer import ChainComposer
from chain_composer._error_handling import _ChainError

# Test Models
class TestOutputModel(BaseModel):
    result: str

class TestInputModel(BaseModel):
    input: str

# Fixtures
@pytest.fixture
def api_key() -> str:
    """Get API key from environment"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY not found in environment")
    return api_key

@pytest.fixture
def basic_composer(api_key: str) -> ChainComposer:
    """Create a basic ChainComposer instance"""
    return ChainComposer(
        model="gpt-4",
        api_key=api_key,
    )

@pytest.fixture
def system_prompt() -> str:
    return """You are a helpful assistant that formats responses as JSON:
    {{
        "result": "<your response>"
    }}
    """

@pytest.fixture
def second_layer_system_prompt() -> str:
    return """You are a helpful assistant that takes the previous result and formats it:
    {{
        "result": "<processed previous result>"
    }}
    
    Previous result: {first_result}
    """

@pytest.fixture
def human_prompt() -> str:
    return "Process this input: {input_text}"

# Basic Initialization Tests
def test_chain_composer_initialization(api_key: str):
    """Test basic initialization of ChainComposer"""
    composer = ChainComposer(
        model="gpt-4",
        api_key=api_key,
    )
    assert composer is not None
    assert composer.api_key == api_key
    assert composer.llm_model == "gpt-4"
    assert composer.llm_model_type == "openai"

def test_chain_composer_invalid_model():
    """Test initialization with invalid model"""
    with pytest.raises(_ChainError):
        ChainComposer(
            model="invalid-model",
            api_key="dummy-key",
        )

# Chain Layer Tests
def test_add_single_chain_layer(basic_composer: ChainComposer, system_prompt: str, human_prompt: str):
    """Test adding a single chain layer"""
    composer = basic_composer.add_chain_layer(
        system_prompt=system_prompt,
        human_prompt=human_prompt,
        output_passthrough_key_name="result",
        parser_type="json",
        pydantic_output_model=TestOutputModel
    )
    
    assert len(composer.get_chain_sequence()) == 1

def test_add_multiple_chain_layers(basic_composer: ChainComposer, system_prompt: str, human_prompt: str):
    """Test adding multiple chain layers"""
    composer = basic_composer.add_chain_layer(
        system_prompt=system_prompt,
        human_prompt=human_prompt,
        output_passthrough_key_name="first_result",
        parser_type="json",
        pydantic_output_model=TestOutputModel
    ).add_chain_layer(
        system_prompt=system_prompt,
        human_prompt=human_prompt,
        output_passthrough_key_name="second_result",
        parser_type="pydantic",
        pydantic_output_model=TestOutputModel
    )
    
    assert len(composer.get_chain_sequence()) == 2

# Execution Tests
@patch('langchain_openai.ChatOpenAI')
def test_simple_chain_execution(mock_openai, basic_composer: ChainComposer, system_prompt: str, human_prompt: str, mock_openai_response):
    """Test executing a simple chain"""
    # Configure mock
    mock_instance = mock_openai.return_value
    mock_instance.invoke.return_value = mock_openai_response
    
    composer = basic_composer.add_chain_layer(
        system_prompt=system_prompt,
        human_prompt=human_prompt,
        output_passthrough_key_name="result",
        parser_type="json",
        pydantic_output_model=TestOutputModel
    )
    
    result = composer.run(
        prompt_variables_dict={
            "input_text": "Hello, world!"
        }
    )
    
    assert "result" in result
    assert isinstance(result["result"], dict)
    assert "result" in result["result"]

@patch('langchain_openai.ChatOpenAI')
def test_multi_layer_chain_execution(mock_openai, basic_composer: ChainComposer, system_prompt: str, human_prompt: str, second_layer_system_prompt: str, mock_openai_response):
    """Test executing a multi-layer chain"""
    # Configure mock
    mock_instance = mock_openai.return_value
    mock_instance.invoke.return_value = mock_openai_response
    
    composer = basic_composer.add_chain_layer(
        system_prompt=system_prompt,
        human_prompt=human_prompt,
        output_passthrough_key_name="first_result",
        parser_type="json",
        pydantic_output_model=TestOutputModel
    ).add_chain_layer(
        system_prompt=second_layer_system_prompt,
        human_prompt=human_prompt,
        output_passthrough_key_name="final_result",
        parser_type="pydantic",
        pydantic_output_model=TestOutputModel
    )
    
    result = composer.run(
        prompt_variables_dict={
            "input_text": "Test input"
        }
    )
    
    assert "first_result" in result
    assert "final_result" in result
    assert isinstance(result["first_result"], dict)
    assert isinstance(result["final_result"], TestOutputModel)

# Error Handling Tests
def test_missing_api_key():
    """Test initialization without API key"""
    with pytest.raises(_ChainError):
        ChainComposer(
            model="gpt-4",
            api_key="",
        )

def test_invalid_parser_type(basic_composer: ChainComposer, system_prompt: str, human_prompt: str):
    """Test adding chain layer with invalid parser type"""
    with pytest.raises(_ChainError):
        basic_composer.add_chain_layer(
            system_prompt=system_prompt,
            human_prompt=human_prompt,
            output_passthrough_key_name="result",
            parser_type="invalid",  # type: ignore
            pydantic_output_model=TestOutputModel
        )

def test_missing_pydantic_model(basic_composer: ChainComposer, system_prompt: str, human_prompt: str):
    """Test adding chain layer with pydantic parser but no model"""
    with pytest.raises(_ChainError):
        basic_composer.add_chain_layer(
            system_prompt=system_prompt,
            human_prompt=human_prompt,
            output_passthrough_key_name="result",
            parser_type="pydantic",
        )

# Chain Variables Tests
def test_chain_variables_update(basic_composer: ChainComposer):
    """Test updating chain variables"""
    variables = {"test_key": "test_value"}
    basic_composer._update_chain_variables(variables)
    assert basic_composer.get_chain_variables() == variables 