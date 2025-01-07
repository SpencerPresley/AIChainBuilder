import json
import pytest
from pydantic import ValidationError

from chain_composer._error_handling import (
    _ChainError,
    _ErrorType,
    _ChainExceptionFactory,
    _ChainComposerValidator,
    _ChainComposerErrorReference,
    _ChainWrapperErrorReference,
)

def test_error_type_enum():
    """Test ErrorType enum values"""
    assert _ErrorType.JSON_ERROR.value == "json_error"
    assert _ErrorType.VALIDATION_ERROR.value == "validation_error"
    assert _ErrorType.VALUE_ERROR.value == "value_error"
    assert _ErrorType.TYPE_ERROR.value == "type_error"
    assert _ErrorType.UNKNOWN_ERROR.value == "unknown_error"

def test_chain_composer_error_reference():
    """Test ChainComposerErrorReference enum values"""
    assert _ChainComposerErrorReference.UNSUPPORTED_LLM_MODEL.value == "unsupported_llm_model"
    assert _ChainComposerErrorReference.INVALID_PARSER_TYPE.value == "invalid_parser_type"
    assert _ChainComposerErrorReference.MISSING_PYDANTIC_MODEL.value == "missing_pydantic_model"
    assert _ChainComposerErrorReference.MISSING_OUTPUT_KEY.value == "missing_output_key"
    assert _ChainComposerErrorReference.INVALID_PARSER_COMBINATION.value == "invalid_parser_combination"
    assert _ChainComposerErrorReference.MISSING_PROMPT_VARIABLES.value == "missing_prompt_variables"
    assert _ChainComposerErrorReference.INVALID_PROMPT_VARIABLES.value == "invalid_prompt_variables"
    assert _ChainComposerErrorReference.INVALID_API_KEY.value == "invalid_api_key"

def test_chain_wrapper_error_reference():
    """Test ChainWrapperErrorReference enum values"""
    assert _ChainWrapperErrorReference.INPUT_ERROR.value == "input_error"
    assert _ChainWrapperErrorReference.MAIN_CHAIN_ERROR.value == "main_chain_error"
    assert _ChainWrapperErrorReference.FALLBACK_CHAIN_ERROR.value == "fallback_chain_error"

def test_chain_exception_factory_json_error():
    """Test ChainExceptionFactory with JSON error"""
    error = json.JSONDecodeError("test", "test", 0)
    chain_error = _ChainExceptionFactory.create_error(
        error=error,
        error_reference=_ChainWrapperErrorReference.MAIN_CHAIN_ERROR
    )
    assert isinstance(chain_error, _ChainError)

def test_chain_exception_factory_validation_error():
    """Test ChainExceptionFactory with validation error"""
    error = ValidationError.from_exception_data("test", [])
    chain_error = _ChainExceptionFactory.create_error(
        error=error,
        error_reference=_ChainWrapperErrorReference.MAIN_CHAIN_ERROR
    )
    assert isinstance(chain_error, _ChainError)

def test_chain_exception_factory_value_error():
    """Test ChainExceptionFactory with value error"""
    error = ValueError("test error")
    chain_error = _ChainExceptionFactory.create_error(
        error=error,
        error_reference=_ChainWrapperErrorReference.MAIN_CHAIN_ERROR
    )
    assert isinstance(chain_error, _ChainError)

def test_chain_exception_factory_type_error():
    """Test ChainExceptionFactory with type error"""
    error = TypeError("test error")
    chain_error = _ChainExceptionFactory.create_error(
        error=error,
        error_reference=_ChainWrapperErrorReference.MAIN_CHAIN_ERROR
    )
    assert isinstance(chain_error, _ChainError)

def test_chain_exception_factory_unknown_error():
    """Test ChainExceptionFactory with unknown error"""
    error = Exception("test error")
    chain_error = _ChainExceptionFactory.create_error(
        error=error,
        error_reference=_ChainWrapperErrorReference.MAIN_CHAIN_ERROR
    )
    assert isinstance(chain_error, _ChainError)

def test_chain_composer_validator_llm_model_type():
    """Test ChainComposerValidator LLM model type validation"""
    # Test valid models
    assert _ChainComposerValidator.validate_llm_model_type("gpt-4") == "openai"
    assert _ChainComposerValidator.validate_llm_model_type("claude-2") == "anthropic"
    assert _ChainComposerValidator.validate_llm_model_type("gemini-pro") == "google"
    
    # Test invalid model
    with pytest.raises(_ChainError):
        _ChainComposerValidator.validate_llm_model_type("invalid_model")

def test_chain_composer_validator_parser_configuration():
    """Test ChainComposerValidator parser configuration validation"""
    # Test missing output key
    with pytest.raises(_ChainError):
        _ChainComposerValidator.validate_parser_configuration(
            output_passthrough_key_name=None,
            ignore_output_passthrough_key_name_error=False,
            parser_type=None,
            pydantic_output_model=None,
            fallback_parser_type=None,
            fallback_pydantic_output_model=None
        )
    
    # Test invalid parser combination
    with pytest.raises(_ChainError):
        _ChainComposerValidator.validate_parser_configuration(
            output_passthrough_key_name="test",
            ignore_output_passthrough_key_name_error=False,
            parser_type=None,
            pydantic_output_model=None,
            fallback_parser_type="str",
            fallback_pydantic_output_model=None
        )
    
    # Test missing Pydantic model
    with pytest.raises(_ChainError):
        _ChainComposerValidator.validate_parser_configuration(
            output_passthrough_key_name="test",
            ignore_output_passthrough_key_name_error=False,
            parser_type="pydantic",
            pydantic_output_model=None,
            fallback_parser_type=None,
            fallback_pydantic_output_model=None
        )
    
    # Test invalid parser type
    with pytest.raises(_ChainError):
        _ChainComposerValidator.validate_parser_configuration(
            output_passthrough_key_name="test",
            ignore_output_passthrough_key_name_error=False,
            parser_type="invalid",
            pydantic_output_model=None,
            fallback_parser_type=None,
            fallback_pydantic_output_model=None
        )

def test_chain_composer_validator_prompt_variables():
    """Test ChainComposerValidator prompt variables validation"""
    # Test missing prompt variables
    with pytest.raises(_ChainError):
        _ChainComposerValidator.validate_prompt_variables(None, is_first_call=True)
    
    # Test invalid prompt variables type
    with pytest.raises(_ChainError):
        _ChainComposerValidator.validate_prompt_variables("not_a_dict", is_first_call=True)
    
    # Test valid prompt variables
    _ChainComposerValidator.validate_prompt_variables({"test": "value"}, is_first_call=True)
    _ChainComposerValidator.validate_prompt_variables(None, is_first_call=False) 