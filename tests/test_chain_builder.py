import pytest
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import Runnable
from langchain_core.output_parsers import PydanticOutputParser, StrOutputParser
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from chain_composer._core_internal._chain_builder import _ChainBuilder
from chain_composer._logging import WARNING

class TestOutputModel(BaseModel):
    response: str

@pytest.fixture
def chat_prompt():
    return ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant."),
        ("human", "{input}")
    ])

@pytest.fixture
def llm():
    return ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

@pytest.fixture
def pydantic_parser():
    return PydanticOutputParser(pydantic_object=TestOutputModel)

@pytest.fixture
def str_parser():
    return StrOutputParser()

@pytest.fixture
def basic_builder(chat_prompt, llm):
    return _ChainBuilder(
        chat_prompt=chat_prompt,
        llm=llm,
        enable_logging=True,
        level=WARNING
    )

@pytest.fixture
def builder_with_parser(chat_prompt, llm, pydantic_parser):
    return _ChainBuilder(
        chat_prompt=chat_prompt,
        llm=llm,
        parser=pydantic_parser,
        enable_logging=True,
        level=WARNING
    )

@pytest.fixture
def builder_with_fallback(chat_prompt, llm, pydantic_parser, str_parser):
    return _ChainBuilder(
        chat_prompt=chat_prompt,
        llm=llm,
        parser=pydantic_parser,
        fallback_parser=str_parser,
        enable_logging=True,
        level=WARNING
    )

def test_chain_builder_initialization(basic_builder):
    """Test basic initialization of ChainBuilder"""
    assert basic_builder.chat_prompt is not None
    assert basic_builder.llm is not None
    assert basic_builder.parser is None
    assert basic_builder.fallback_parser is None
    assert basic_builder.debug is False
    assert isinstance(basic_builder.chain, Runnable)
    assert isinstance(basic_builder.fallback_chain, Runnable)

def test_chain_builder_with_parser(builder_with_parser):
    """Test ChainBuilder initialization with parser"""
    assert builder_with_parser.parser is not None
    assert isinstance(builder_with_parser.parser, PydanticOutputParser)
    assert builder_with_parser.fallback_parser is None

def test_chain_builder_with_fallback(builder_with_fallback):
    """Test ChainBuilder initialization with both parsers"""
    assert builder_with_fallback.parser is not None
    assert builder_with_fallback.fallback_parser is not None
    assert isinstance(builder_with_fallback.parser, PydanticOutputParser)
    assert isinstance(builder_with_fallback.fallback_parser, StrOutputParser)

def test_chain_builder_debug_warning():
    """Test debug warning when None is provided"""
    with pytest.warns(UserWarning, match="The `debug` argument takes an optional boolean value"):
        _ChainBuilder(
            chat_prompt=ChatPromptTemplate.from_messages([("system", "test")]),
            llm=ChatOpenAI(),
            debug=None
        )

def test_chain_builder_str_representation(basic_builder):
    """Test string representation of ChainBuilder"""
    str_repr = str(basic_builder)
    assert "ChainBuilder" in str_repr
    assert "ChatPromptTemplate" in str_repr
    assert "ChatOpenAI" in str_repr

def test_chain_builder_repr_representation(basic_builder):
    """Test detailed representation of ChainBuilder"""
    repr_str = repr(basic_builder)
    assert "ChainBuilder" in repr_str
    assert "chat_prompt" in repr_str
    assert "llm" in repr_str
    assert "parser" in repr_str
    assert "fallback_parser" in repr_str

def test_get_chain(basic_builder):
    """Test get_chain method returns a Runnable"""
    chain = basic_builder.get_chain()
    assert isinstance(chain, Runnable)

def test_get_fallback_chain(basic_builder):
    """Test get_fallback_chain method returns a Runnable"""
    fallback_chain = basic_builder.get_fallback_chain()
    assert isinstance(fallback_chain, Runnable) 