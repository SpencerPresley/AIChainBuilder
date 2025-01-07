import json
from typing import Dict, Any

import pytest
from langchain.schema.runnable import Runnable, RunnablePassthrough
from langchain_core.output_parsers import PydanticOutputParser, StrOutputParser
from pydantic import BaseModel, ValidationError

from chain_composer._core_internal._chain_wrapper import _ChainWrapper
from chain_composer._error_handling import _ChainExceptionFactory
from chain_composer._logging import WARNING

class TestOutputModel(BaseModel):
    response: str

class MockRunnable(Runnable):
    def __init__(self, output=None, error=None):
        self.output = output
        self.error = error

    def invoke(self, input_data: Dict[str, Any], **kwargs):
        if self.error:
            raise self.error
        return self.output

@pytest.fixture
def mock_chain():
    return MockRunnable(output={"response": "test response"})

@pytest.fixture
def mock_fallback_chain():
    return MockRunnable(output="fallback response")

@pytest.fixture
def pydantic_parser():
    return PydanticOutputParser(pydantic_object=TestOutputModel)

@pytest.fixture
def str_parser():
    return StrOutputParser()

@pytest.fixture
def basic_wrapper(mock_chain, mock_fallback_chain):
    return _ChainWrapper(
        chain=mock_chain,
        fallback_chain=mock_fallback_chain,
        enable_logging=True,
        level=WARNING
    )

@pytest.fixture
def wrapper_with_parser(mock_chain, mock_fallback_chain, pydantic_parser, str_parser):
    return _ChainWrapper(
        chain=mock_chain,
        fallback_chain=mock_fallback_chain,
        parser=pydantic_parser,
        fallback_parser=str_parser,
        enable_logging=True,
        level=WARNING
    )

def test_chain_wrapper_initialization(basic_wrapper):
    """Test basic initialization of ChainWrapper"""
    assert basic_wrapper.chain is not None
    assert basic_wrapper.fallback_chain is not None
    assert basic_wrapper.parser is None
    assert basic_wrapper.fallback_parser is None
    assert basic_wrapper.preprocessor is None
    assert basic_wrapper.postprocessor is None
    assert basic_wrapper.debug is False

def test_chain_wrapper_with_parsers(wrapper_with_parser):
    """Test ChainWrapper initialization with parsers"""
    assert wrapper_with_parser.parser is not None
    assert wrapper_with_parser.fallback_parser is not None
    assert isinstance(wrapper_with_parser.parser, PydanticOutputParser)
    assert isinstance(wrapper_with_parser.fallback_parser, StrOutputParser)

def test_chain_wrapper_debug_warning():
    """Test debug warning when None is provided"""
    with pytest.warns(UserWarning, match="The `debug` argument takes an optional boolean value"):
        _ChainWrapper(
            chain=MockRunnable(),
            fallback_chain=MockRunnable(),
            debug=None
        )

def test_chain_wrapper_str_representation(basic_wrapper):
    """Test string representation of ChainWrapper"""
    str_repr = str(basic_wrapper)
    assert "ChainWrapper" in str_repr
    assert "parser=None" in str_repr
    assert "fallback_parser=None" in str_repr

def test_chain_wrapper_repr_representation(basic_wrapper):
    """Test detailed representation of ChainWrapper"""
    repr_str = repr(basic_wrapper)
    assert "ChainWrapper" in repr_str
    assert "chain" in repr_str
    assert "parser" in repr_str
    assert "fallback_parser" in repr_str
    assert "preprocessor" in repr_str
    assert "postprocessor" in repr_str

def test_run_chain_success(basic_wrapper):
    """Test successful chain execution"""
    result = basic_wrapper.run_chain(input_data={"input": "test"})
    assert result == {"response": "test response"}

def test_run_chain_with_preprocessor():
    """Test chain execution with preprocessor"""
    def preprocessor(data: Dict[str, Any]) -> Dict[str, Any]:
        data["processed"] = True
        return data

    wrapper = _ChainWrapper(
        chain=MockRunnable(output="test"),
        fallback_chain=MockRunnable(),
        preprocessor=preprocessor
    )
    result = wrapper.run_chain(input_data={"input": "test"})
    assert result == "test"

def test_run_chain_with_postprocessor():
    """Test chain execution with postprocessor"""
    def postprocessor(data: Any) -> str:
        return f"Processed: {data}"

    wrapper = _ChainWrapper(
        chain=MockRunnable(output="test"),
        fallback_chain=MockRunnable(),
        postprocessor=postprocessor
    )
    result = wrapper.run_chain(input_data={"input": "test"})
    assert result == "Processed: test"

def test_run_chain_json_error_with_fallback(mock_fallback_chain):
    """Test chain execution with JSON error and fallback"""
    error_chain = MockRunnable(error=json.JSONDecodeError("test", "test", 0))
    wrapper = _ChainWrapper(
        chain=error_chain,
        fallback_chain=mock_fallback_chain
    )
    result = wrapper.run_chain(input_data={"input": "test"})
    assert result == "fallback response"

def test_run_chain_validation_error_with_fallback(mock_fallback_chain):
    """Test chain execution with validation error and fallback"""
    error_chain = MockRunnable(error=ValidationError.from_exception_data("test", []))
    wrapper = _ChainWrapper(
        chain=error_chain,
        fallback_chain=mock_fallback_chain
    )
    result = wrapper.run_chain(input_data={"input": "test"})
    assert result == "fallback response"

def test_run_chain_error_without_fallback():
    """Test chain execution with error and no fallback"""
    error_chain = MockRunnable(error=ValueError("test error"))
    wrapper = _ChainWrapper(
        chain=error_chain,
        fallback_chain=MockRunnable()
    )
    with pytest.raises(Exception):
        wrapper.run_chain(input_data={"input": "test"}, is_last_chain=True)

def test_get_parser_type(wrapper_with_parser):
    """Test get_parser_type method"""
    assert wrapper_with_parser.get_parser_type() == "PydanticOutputParser"

def test_get_fallback_parser_type(wrapper_with_parser):
    """Test get_fallback_parser_type method"""
    assert wrapper_with_parser.get_fallback_parser_type() == "StrOutputParser"

def test_run_chain_with_pydantic_output():
    """Test chain execution with Pydantic model output"""
    output_model = TestOutputModel(response="test")
    chain = MockRunnable(output=output_model)
    wrapper = _ChainWrapper(
        chain=chain,
        fallback_chain=MockRunnable()
    )
    result = wrapper.run_chain(input_data={"input": "test"}, is_last_chain=False)
    assert isinstance(result, dict)
    assert result["response"] == "test" 