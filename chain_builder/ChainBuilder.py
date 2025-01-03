from __future__ import annotations

import json
import logging
import os
import warnings
from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Literal,
    Optional,
    Tuple,
    TypeVar,
    Union,
    cast,
    TypeAlias,
)

from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    PromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain.schema.runnable import Runnable, RunnablePassthrough
from langchain_anthropic import ChatAnthropic
from langchain_core.output_parsers import (
    JsonOutputParser,
    PydanticOutputParser,
    StrOutputParser,
)
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, ValidationError

import tiktoken

FirstCallRequired = TypeVar("FirsCallRequired", bound=Dict[str, Any])
"""TypeVar representing a dictionary that is required on first call but optional after.

Type Structure:
    TypeVar bound to Dict[str, Any]

Usage:
    Used to enforce that a dictionary parameter must be provided on first call
    but can be optional on subsequent calls.
"""

ParserUnion: TypeAlias = Union[PydanticOutputParser, JsonOutputParser, StrOutputParser]
"""Union type representing valid parser types.

Type Structure:
    Union[PydanticOutputParser, JsonOutputParser, StrOutputParser]
"""

ParserType = TypeVar("ParserType", bound=ParserUnion)
"""TypeVar representing the main parser type.

Type Structure:
    TypeVar bound to Union[PydanticOutputParser, JsonOutputParser, StrOutputParser]

Usage:
    Used to enforce type consistency for the primary parser in chain operations.
"""

FallbackParserType = TypeVar("FallbackParserType", bound=ParserUnion)
"""TypeVar representing the fallback parser type.

Type Structure:
    TypeVar bound to Union[PydanticOutputParser, JsonOutputParser, StrOutputParser]

Usage:
    Used to enforce type consistency for the fallback parser in chain operations.
"""


class ChainBuilder:
    """A builder class for constructing and configuring LangChain chains with logging and parsing capabilities.

    This class provides functionality to construct LangChain chains with customizable prompts,
    language models, and output parsers. It includes support for logging, fallback chains,
    and various parser types.

    Attributes:
        log_file_path (Path): Path to the log file.
        logger (Logger): Logger instance for the chain builder.
        chat_prompt (ChatPromptTemplate): Template for chat prompts.
        parser (ParserType | None): Primary output parser.
        fallback_parser (ParserType | None): Fallback output parser.
        llm (Union[:class:`ChatOpenAI`, :class:`ChatAnthropic`, :class:`ChatGoogleGenerativeAI`]): Language model instance.
        chain (:class:`Runnable`): Primary chain instance.
        fallback_chain (:class:`Runnable`): Fallback chain instance.

    Methods:
        get_chain() -> :class:`Runnable`:
            Returns the primary chain instance.

        get_fallback_chain() -> :class:`Runnable`:
            Returns the fallback chain instance.

        __str__() -> str:
            Returns a string representation of the ChainBuilder.

        __repr__() -> str:
            Returns a string representation of the ChainBuilder.

        _run_pydantic_parser_logging() -> None:
            Logs Pydantic parser configuration.

        _build_chain() -> None:
            Constructs the primary chain.

        _build_fallback_chain() -> None:
            Constructs the fallback chain.
    """

    def __init__(
        self,
        *,
        chat_prompt: ChatPromptTemplate,
        llm: Union[ChatOpenAI, ChatAnthropic, ChatGoogleGenerativeAI],
        parser: ParserType | None = None,
        fallback_parser: FallbackParserType | None = None,
        logger: logging.Logger | None = None,
        log_to_console: bool | None = LOG_TO_CONSOLE,
    ) -> None:
        """Initialize a ChainBuilder instance.

        Args:
            chat_prompt (:class:`ChatPromptTemplate`): Template for structuring chat interactions.
            llm (:class:`ChatOpenAI`, :class:`ChatAnthropic`, :class:`ChatGoogleGenerativeAI`): Language model to use.
            parser (ParserType | None): Primary output parser.
                Defaults to None.
            fallback_parser (FallbackParserType | None): Fallback output parser.
                Defaults to None.
            logger (:class:`~python:logging.Logger` | None): Custom logger instance.
                Defaults to None.
            log_to_console (bool | None): Whether to log to console.
                Defaults to LOG_TO_CONSOLE.

        Returns:
            None
        """
        self.logger = logger or configure_logging(
            module_name=__name__,
            log_file_name="chain_builder",
            log_level=DEBUG,
        )

        self.chat_prompt: ChatPromptTemplate = chat_prompt
        self.parser: Optional[ParserType] = parser
        self.fallback_parser: Optional[FallbackParserType] = fallback_parser
        self.llm: Union[ChatOpenAI, ChatAnthropic, ChatGoogleGenerativeAI] = llm
        self.chain: Runnable = self._build_chain()
        self.fallback_chain: Runnable = self._build_fallback_chain()

    def __str__(self) -> str:
        """
        Returns a string representation of the ChainBuilder object.

        The string includes the class names of the chat_prompt, llm, and parser attributes.

        Returns:
            str: A string representation of the ChainBuilder object.
        """
        return f"ChainBuilder(chat_prompt={type(self.chat_prompt).__name__}, llm={self.llm.__class__.__name__}, parser={type(self.parser).__name__ if self.parser else 'None'})"

    def __repr__(self) -> str:
        """
        Returns a string representation of the object for debugging purposes.

        This method calls the __str__() method to provide a human-readable
        representation of the object.

        Returns:
            str: A string representation of the object.
        """
        return self.__str__()

    def _run_pydantic_parser_logging(self) -> None:
        """
        Logs the required fields and their default values (if any) for a Pydantic model
        if the parser is an instance of PydanticOutputParser. Additionally, logs the
        JSON schema of the Pydantic model.

        This method performs the following steps:
        1. Checks if the parser is an instance of PydanticOutputParser.
        2. Retrieves the Pydantic model from the parser.
        3. Logs each field's name and whether it is required or optional.
        4. Logs the default value of each field if it is not None.
        5. Logs the JSON schema of the Pydantic model.

        Returns:
            None
        """
        if isinstance(self.parser, PydanticOutputParser):
            pydantic_model: BaseModel = self.parser.pydantic_object
            self.logger.info("Required fields in Pydantic model:")
            for field_name, field in pydantic_model.model_fields.items():
                self.logger.info(
                    f"  {field_name}: {'required' if field.is_required else 'optional'}"
                )
                if field.default is not None:
                    self.logger.info(f"    Default: {field.default}")

            self.logger.info("\nModel Schema:")
            self.logger.info(pydantic_model.model_json_schema())

    def _build_chain(self) -> Runnable:
        """
        Builds and returns a chain of Runnable objects.

        The chain is constructed by combining a RunnablePassthrough object with
        the chat_prompt and llm attributes. If a parser is provided, it is added
        to the chain and pydantic parser logging is executed.

        Returns:
            :class:`Runnable`: The constructed chain of Runnable objects.
        """
        # Build the chain
        chain: Runnable = RunnablePassthrough() | self.chat_prompt | self.llm

        if self.parser:
            self._run_pydantic_parser_logging()
            chain: Runnable = chain | self.parser

        return chain

    def _build_fallback_chain(self) -> Runnable:
        """
        Builds the fallback chain for the Runnable.

        This method constructs a fallback chain by combining a RunnablePassthrough
        instance with the chat prompt and language model (llm). If a fallback parser
        is provided, it adds the parser to the chain and logs the parser usage.

        Returns:
            :class:`Runnable`: The constructed fallback chain.
        """
        fallback_chain: Runnable = RunnablePassthrough() | self.chat_prompt | self.llm

        if self.fallback_parser:
            self._run_pydantic_parser_logging()
            fallback_chain: Runnable = fallback_chain | self.fallback_parser

        return fallback_chain

    def get_chain(self) -> Runnable:
        """
        Retrieves the current chain.

        Returns:
            :class:`Runnable`: The current chain instance.
        """
        return self.chain

    def get_fallback_chain(self) -> Runnable:
        """Retrieve the fallback chain.

        Returns:
            :class:`Runnable`: The fallback chain instance.
        """
        return self.fallback_chain


class ChainWrapper:
    """A wrapper class for managing and executing chains with optional fallback chains.

    This class is designed to handle the execution of primary chains and, if necessary,
    fallback chains in case of errors or unexpected outputs. It supports preprocessing
    and postprocessing of input and output data, as well as logging for debugging and
    monitoring purposes.

    Attributes:
        chain (Runnable): The primary chain to be executed.
        fallback_chain (Runnable): The fallback chain to be executed if the primary chain fails.
        parser (ParserType | None): The parser to be used for processing the output of the
            primary chain.
            Defaults to None.
        fallback_parser (FallbackParserType | None): The parser to be used for processing the output
            of the fallback chain.
            Defaults to None.
        preprocessor (:class:`~python:typing.Callable` | None): A function to preprocess input data before passing
            it to the chain.
            Defaults to None.
        postprocessor (:class:`~python:typing.Callable` | None): A function to postprocess the output data from the chain.
            Defaults to None.
        logger (:class:`~logging.Logger` | None): A logger instance for logging information and debugging.
            Defaults to None.

    Methods:
        __init__(chain, fallback_chain, parser=None, fallback_parser=None,
            preprocessor=None, postprocessor=None, logger=None):
                Initializes the ChainWrapper instance with the provided parameters.

        __str__() -> str:
            Returns a string representation of the ChainWrapper object, including the chain,
            parser type, and fallback parser type.

        __repr__() -> str:
            Returns a string representation of the ChainWrapper object for debugging purposes.

        run_chain(input_data=None, is_last_chain=False) -> Any:
            Executes the primary chain with the provided input data. If an error occurs,
            attempts to execute the fallback chain. Supports preprocessing and postprocessing.

            Args:
                input_data (dict | None): The input data for the chain
                    Type: Dict[str, Any]
                is_last_chain (bool): Whether this is the last chain in sequence
                    Defaults to False

        get_parser_type() -> str | None:
            Returns the type of the parser as a string if the parser exists, otherwise None.

        get_fallback_parser_type() -> str | None:
            Returns the type of the fallback parser as a string if it exists, otherwise None.
    """

    def __init__(
        self,
        *,
        chain: Runnable,
        fallback_chain: Runnable,
        parser: ParserType | None = None,
        fallback_parser: FallbackParserType | None = None,
        preprocessor: Callable[[Dict[str, Any]], Dict[str, Any]] | None = None,
        postprocessor: Callable[[Any], Any] | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        """Initialize the ChainBuilder.

        Args:
            chain (:class:`Runnable`): The primary chain to be executed.
            fallback_chain (:class:`Runnable`): The fallback chain to be executed if the primary chain fails.
            parser (ParserType | None): The parser to be used for the primary chain.
            fallback_parser (FallbackParserType | None): The parser to be used for the fallback chain.
            preprocessor (:class:`~python:typing.Callable` | None): A function to preprocess input data before passing it to the chain.
                Defaults to None.
            postprocessor (:class:`~python:typing.Callable` | None): A function to postprocess the output data from the chain.
                Defaults to None.
            logger (:class:`~logging.Logger` | None): A logger instance for logging information.
                Defaults to None.

        """
        self.logger = logger or configure_logging(
            module_name=__name__,
            log_file_name="chain_wrapper",
            log_level=DEBUG,
        )

        self.parser: Optional[ParserType] = parser
        self.fallback_parser: Optional[FallbackParserType] = fallback_parser
        self.preprocessor: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = (
            preprocessor
        )

        self.chain: Runnable = chain
        self.fallback_chain: Runnable = fallback_chain
        self.postprocessor: Optional[Callable[[Any], Any]] = postprocessor

    def __str__(self) -> str:
        """
        Returns a string representation of the ChainWrapper object.

        The string includes the chain, the type of the parser, and the type of the fallback parser.

        Returns:
            str: A string representation of the ChainWrapper object.
        """
        return f"ChainWrapper(chain={self.chain}, parser={type(self.parser).__name__ if self.parser else 'None'}, fallback_parser={type(self.fallback_parser).__name__ if self.fallback_parser else 'None'})"

    def __repr__(self) -> str:
        """
        Returns a string representation of the object for debugging purposes.

        This method calls the __str__() method to provide a user-friendly string
        representation of the object. It is intended to be used for debugging
        and development, rather than for end-user display.

        Returns:
            str: A string representation of the object.
        """
        return self.__str__()

    def run_chain(
        self,
        *,
        input_data: Dict[str, Any] | None = None,
        is_last_chain: bool | None = False,
    ) -> Any:
        """Executes the primary chain with the provided input data.

        If an error occurs in the primary chain, and a fallback chain is provided,
        it attempts to execute the fallback chain.

        Args:
            input_data (dict | None): The input data required to run the chain.
                Type: Dict[str, Any]
                Defaults to None.
            is_last_chain (bool | None): Indicates if this is the last chain in the sequence.
                Defaults to False.

        Returns:
            :class:`~python:typing.Any`: The output from the chain execution, potentially processed by a postprocessor.

        Raises:
            ValueError: If no input data is provided.
            json.JSONDecodeError: If a JSON decode error occurs in both the main and fallback chains.
            :class:`~pydantic.ValidationError`: If a validation error occurs in both the main and fallback chains.
            TypeError: If a type error occurs in both the main and fallback chains.

        Notes:
            - If the output is a Pydantic model and this is not the last chain,
              the model is converted to a dictionary.
            - If a postprocessor is defined, it processes the output before returning.
        """
        if cast(Any, input_data) is None:
            raise ValueError(
                "No input data provided to ChainWrapper.run_chain(). Input data is required to run the chain."
            )

        if self.preprocessor:
            input_data = self.preprocessor(input_data)
        output = None

        try:
            # Attempt to invoke the primary chain
            output: Any = self.chain.invoke(input_data)
        except (
            json.JSONDecodeError,
            ValidationError,
            ValueError,
            TypeError,
        ) as main_chain_exception:
            self.logger.info(f"Error in main chain: {main_chain_exception}")
            self.logger.info("Attempting to execute fallback chain")
            if self.fallback_chain and not is_last_chain:
                self.logger.info("Fallback chain provided, executing fallback chain")
                try:
                    # Attempt to invoke the fallback chain
                    output: Any = self.fallback_chain.invoke(input_data)
                except (
                    json.JSONDecodeError,
                    ValidationError,
                    ValueError,
                    TypeError,
                ) as fallback_exception:
                    if isinstance(fallback_exception, json.JSONDecodeError):
                        self.logger.debug(
                            f"Error in fallback chain: {fallback_exception.errors()}"
                        )
                        self.logger.debug(
                            "A json decode error occurred in the main chain. Executing fallback chain. If you didn't provide a fallback chain it will not be ran, since it was a json decode error you should check how you're telling the LLM to output the json and make sure it matches your pydantic model. Additionally, LLMs will sometimes output invalid characters to json such as Latex code, leading to invalide escape sequences or characters. If this is the case you should try StrOutputParser() if it isn't your last chain layer. If it is your last chain layer, try simplifying your pydantic model and enhancing your prompt to avoid this issue. If you are using a LLM such as 'gpt-4o-mini' or 'claude-3.5-haiku' you may see better results with a larger model such as 'gpt-4o' or 'claude-3.5-sonnet'."
                        )
                        raise fallback_exception
            else:
                if isinstance(main_chain_exception, json.JSONDecodeError):
                    self.logger.debug(
                        "A json decode error occurred in the main chain. Executing fallback chain. If you didn't provide a fallback chain it will not be ran, since it was a json decode error you should check how you're telling the LLM to output the json and make sure it matches your pydantic model. Additionally, LLMs will sometimes output invalid characters to json such as Latex code, leading to invalide escape sequences or characters. If this is the case you should try StrOutputParser() if it isn't your last chain layer. If it is your last chain layer, try simplifying your pydantic model and enhancing your prompt to avoid this issue. If you are using a LLM such as 'gpt-4o-mini' or 'claude-3.5-haiku' you may see better results with a larger model such as 'gpt-4o' or 'claude-3.5-sonnet'."
                    )
                    raise main_chain_exception

        # Only need to handle intermediate chain Pydantic outputs
        # Rest are handled by JsonOutputParser or PydanticOutputParser
        if not is_last_chain and isinstance(output, BaseModel):
            return output.model_dump()

        if self.postprocessor:
            output: Any = self.postprocessor(output)

        return output

    def get_parser_type(self) -> str | None:
        """Returns the type of the parser as a string if the parser exists, otherwise returns None.

        Returns:
            str | None: The type of the parser as a string, or None if the parser
                does not exist.
        """
        return type(self.parser).__name__ if self.parser else None

    def get_fallback_parser_type(self) -> str | None:
        """Returns the type name of the fallback parser if it exists, otherwise returns None.

        Returns:
            str | None: The type name of the fallback parser as a string if it exists,
                otherwise None.
        """
        return type(self.fallback_parser).__name__ if self.fallback_parser else None


class ChainComposer:
    """Manages a sequence of chain operations.

    ChainComposer is a class that manages a sequence of chain operations, allowing for
    the addition of chains and running them in sequence with provided data.

    Methods:
        __init__(logger: Logger | None):
            Initializes the ChainComposer instance with an optional logger.
            Type: :class:`~logging.Logger` | None
            Defaults to None.

        __str__() -> str:
            Returns a string representation of the ChainComposer instance.

        __repr__() -> str:
            Returns a string representation of the ChainComposer instance.

        add_chain(chain_wrapper, output_passthrough_key_name):
            Adds a chain to the chain sequence.

            Args:
                chain_wrapper (ChainWrapper): The chain wrapper to add
                output_passthrough_key_name (str | None): Optional output key name
                    Defaults to None.

        run(data_dict, data_dict_update_function):
            Runs the chain sequence with the provided data dictionary and optional update function.

            Args:
                data_dict (dict): The input data dictionary
                    Type: Dict[str, Any]
                data_dict_update_function (callable | None): Optional update function
                    Type: Callable[[Dict[str, Any]], None]
                    Defaults to None.
            Returns:
                dict: The updated data dictionary
                    Type: Dict[str, Any]
    """

    def __init__(self, logger: logging.Logger | None = None) -> None:
        """Initializes the ChainBuilder instance.

        Args:
            logger (Logger | None): A logger instance to be used for logging.
                Type: logging.Logger | None
                If not provided, a default logger will be created.
                Defaults to None.

        Attributes:
            logger (Logger): The logger instance used for logging.
                Type: logging.Logger
            chain_sequence (list): A list to store the chain sequence.
                Type: List[Tuple[:class:`~academic_metrics.ChainBuilder.ChainBuilder.ChainWrapper`, str | None]]
        """
        self.logger = logger or configure_logging(
            module_name=__name__,
            log_file_name="chain_composer",
            log_level=DEBUG,
        )

        self.chain_sequence: List[Tuple[ChainWrapper, Optional[str]]] = []

    def __str__(self) -> str:
        """Returns a string representation of the ChainComposer object.

        The string representation includes the index and the wrapper of each
        element in the chain_sequence.

        Returns:
            str: A string representation of the ChainComposer object.
        """
        chain_info = ", ".join(
            [
                f"{idx}: {wrapper}"
                for idx, (wrapper, _) in enumerate(self.chain_sequence)
            ]
        )
        return f"ChainComposer(chains=[{chain_info}])"

    def __repr__(self) -> str:
        """Returns a string representation of the object for debugging purposes.

        This method calls the __str__() method to provide a human-readable
        representation of the object.

        Returns:
            str: A string representation of the object.
        """
        return self.__str__()

    def add_chain(
        self,
        *,
        chain_wrapper: ChainWrapper,
        output_passthrough_key_name: str | None = None,
    ) -> None:
        """Adds a chain to the chain sequence.

        Args:
            chain_wrapper (ChainWrapper): The chain wrapper to be added.
            output_passthrough_key_name (str | None): The key name for output passthrough.
                Type: str | None
                Defaults to None.

        Returns:
            None
        """
        self.chain_sequence.append((chain_wrapper, output_passthrough_key_name))

    def run(
        self,
        *,
        data_dict: Dict[str, Any],
        data_dict_update_function: Callable[[Dict[str, Any]], None] | None = None,
    ) -> Dict[str, Any]:
        """Executes a sequence of chains, updating the provided data dictionary with the results of each chain.

        Args:
            data_dict (dict): The initial data dictionary containing input variables for the chains.
                Type: Dict[str, Any]
            data_dict_update_function (callable | None): An optional function to update the data
                dictionary after each chain execution.
                Type: Callable[[Dict[str, Any]], None]
                Defaults to None.

        Returns:
            dict: The updated data dictionary after all chains have been executed.
                Type: Dict[str, Any]

        Raises:
            UserWarning: If the provided data dictionary is empty.

        Notes:
            - The method iterates over a sequence of chains (`self.chain_sequence`), executing
              each chain and updating the `data_dict` with the output.
            - If an `output_name` is provided for a chain, the output is stored in `data_dict`
              under that name; otherwise, it is stored under the key `_last_output`.
            - If `data_dict_update_function` is provided, it is called with the updated
              `data_dict` after each chain execution.
        """
        if not data_dict:
            warnings.warn(
                "No variables provided for the chain. Please ensure you have provided the necessary variables. If you have variable placeholders and do not pass them in it will result in an error."
            )

        num_chains: int = len(self.chain_sequence)
        for index, (chain_wrapper, output_name) in enumerate(self.chain_sequence):
            is_last_chain: bool = index == num_chains - 1
            output: Union[BaseModel, Dict[str, Any], str] = chain_wrapper.run_chain(
                input_data=data_dict, is_last_chain=is_last_chain
            )

            # Update data with the output
            if output_name:
                data_dict[output_name] = output
            else:
                data_dict["_last_output"] = output

            if data_dict_update_function:
                data_dict_update_function(data_dict)

        return data_dict


class ChainManager:
    """Class responsible for managing and orchestrating a sequence of chain layers,

    ChainManager is a class responsible for managing and orchestrating a sequence of chain layers,
    each of which can process input data and produce output data. It supports various types of
    language models (LLMs) and parsers, and allows for pre-processing and post-processing of data.

    Attributes:
        api_key (str): The API key for accessing the LLM service.
        llm_model (str): The name of the LLM model to use.
        llm_model_type (str): The type of the LLM model (e.g., "openai", "anthropic", "google").
            Type: Literal["openai", "anthropic", "google"]
        llm_temperature (float): The temperature setting for the LLM model.
        llm_kwargs (dict): Additional keyword arguments for the LLM model.
            Type: Dict[str, Any]
        llm (Union[:class:`ChatOpenAI`, :class:`ChatAnthropic`, :class:`ChatGoogleGenerativeAI`]): The initialized LLM instance.
        chain_composer (ChainComposer): The composer for managing the sequence of chain layers.
        chain_variables (dict): A dictionary of variables used in the chain layers.
            Type: Dict[str, Any]
        chain_variables_update_overwrite_warning_counter (int): Counter for tracking variable overwrite warnings.
        preprocessor (:class:`~python:typing.Callable`, optional): Optional preprocessor function.
        postprocessor (:class:`~python:typing.Callable`, optional): Optional postprocessor function.
        logger (:class:`~python:logging.Logger`): Logger for logging information and debugging.

    Methods:
        __str__(): Returns a string representation of the ChainManager instance.
        __repr__(): Returns a string representation of the ChainManager instance.
        _get_llm_model_type(llm_model: str) -> str:
            Determines the type of the LLM model based on its name.
        _initialize_llm(api_key: str, llm_model_type: str, llm_model: str, llm_temperature: float, llm_kwargs: Dict[str, Any]) -> Union[:class:`ChatOpenAI`, :class:`ChatAnthropic`, :class:`ChatGoogleGenerativeAI`]:
            Initializes the LLM instance based on the model type.
        _create_openai_llm(api_key: str, llm_model: str, llm_temperature: float, llm_kwargs: Dict[str, Any]) -> :class:`ChatOpenAI`:
            Creates an OpenAI LLM instance.
        _create_anthropic_llm(api_key: str, llm_model: str, llm_temperature: float, llm_kwargs: Dict[str, Any]) -> :class:`ChatAnthropic`:
            Creates an Anthropic LLM instance.
        _create_google_llm(api_key: str, llm_model: str, llm_temperature: float, llm_kwargs: Dict[str, Any]) -> :class:`ChatGoogleGenerativeAI`:
            Creates a Google Generative AI LLM instance.
        _initialize_parser(parser_type: str, pydantic_output_model: Optional[BaseModel] = None) -> ParserUnion:
            Initializes a parser based on the specified type.
        _create_pydantic_parser(pydantic_output_model: :class:`pydantic.BaseModel`) -> :class:`~langchain_core.output_parsers.PydanticOutputParser`:
            Creates a Pydantic parser.
        _create_json_parser(pydantic_output_model: Optional[BaseModel]) -> :class:`~langchain_core.output_parsers.JsonOutputParser`:
        ) -> JsonOutputParser:
            Creates a JSON parser.
        _create_str_parser() -> :class:`~langchain_core.output_parsers.StrOutputParser`:
            Creates a string parser.
        _run_chain_validation_checks(output_passthrough_key_name: str | None, ignore_output_passthrough_key_name_error: bool, parser_type: Literal["pydantic", "json", "str"] | None, pydantic_output_model: :class:`~pydantic.BaseModel` | None, fallback_parser_type: Literal["pydantic", "json", "str"] | None, fallback_pydantic_output_model: :class:`~pydantic.BaseModel` | None) -> None:
            Runs validation checks for the chain configuration.
        _format_chain_sequence(chain_sequence: List[Tuple[ChainWrapper, Optional[str]]]) -> None:
            Formats and prints the chain sequence.
        _run_validation_checks(prompt_variables_dict: Union[FirstCallRequired, None]) -> None:
            Runs validation checks for the prompt variables.
        add_chain_layer(system_prompt: str, human_prompt: str, output_passthrough_key_name: str | None = None, ignore_output_passthrough_key_name_error: bool = False, preprocessor: Callable[[Dict[str, Any]], Dict[str, Any]] | None = None, postprocessor: Callable[[Any], Any] | None = None, parser_type: Literal["pydantic", "json", "str"] | None = None, fallback_parser_type: Literal["pydantic", "json", "str"] | None = None, pydantic_output_model: :class:`~pydantic.BaseModel` | None = None, fallback_pydantic_output_model: :class:`~pydantic.BaseModel` | None = None) -> None:
            Adds a chain layer to the chain composer.
        _format_overwrite_warning(overwrites: Dict[str, Dict[str, Any]]) -> None:
            Formats a warning message for variable overwrites.
        _check_first_time_overwrites(prompt_variables_dict: Dict[str, Any]) -> None:
            Checks for first-time overwrites of global variables and issues warnings.
        _update_chain_variables(prompt_variables_dict: Dict[str, Any]) -> None:
            Updates global variables with new values, warning on first-time overwrites.
        get_chain_sequence() -> List[Tuple[ChainWrapper, Optional[str]]]:
            Returns the current chain sequence.
        print_chain_sequence() -> None:
            Prints the current chain sequence.
        get_chain_variables() -> Dict[str, Any]:
            Returns the current chain variables.
        print_chain_variables() -> None:
            Prints the current chain variables.
        run(prompt_variables_dict: Union[FirstCallRequired, None] = None) -> None:
            Runs the chain composer with the provided prompt variables.
    """

    def __init__(
        self,
        llm_model: str,
        api_key: str,
        llm_temperature: float = 0.7,
        preprocessor: Callable[[Dict[str, Any]], Dict[str, Any]] | None = None,
        postprocessor: Callable[[Any], Any] | None = None,
        log_to_console: bool = False,
        verbose: bool | None = False,
        llm_kwargs: Dict[str, Any] | None = None,
        words_to_ban: List[str] | None = None,
    ) -> None:
        """Initializes the ChainBuilder class.

        Args:
            llm_model (str): The name of the language model to be used.
            api_key (str): The API key for accessing the language model.
            llm_temperature (float, optional): The temperature setting for the language model.
                Defaults to 0.7.
            preprocessor (:class:`~python:typing.Callable` | None): A function to preprocess input data.
                Defaults to None.
            postprocessor (:class:`~python:typing.Callable` | None): A function to postprocess output data.
                Defaults to None.
            log_to_console (bool | None): Flag to enable logging to console.
                Defaults to False.
            llm_kwargs (dict | None): Additional keyword arguments for the language model.
                Type: Dict[str, Any]
            words_to_ban (list): A list of words to ban from the language model's output.
                Type: List[str]
                Defaults to None.

        """
        self.log_to_console: bool = log_to_console

        self.logger = configure_logging(
            module_name=__name__,
            log_file_name="chain_builder",
            log_level=DEBUG,
        )

        self.llm_kwargs: Dict[str, Any] = llm_kwargs if llm_kwargs is not None else {}
        self.api_key: str = api_key
        self.llm_model: str = llm_model
        self.llm_model_type: str = self._get_llm_model_type(llm_model=llm_model)
        self.words_to_ban: List[str] | None = words_to_ban
        self.logit_bias_dict: Dict[int, int] | None = None

        if self.words_to_ban is not None:
            self._validate_words_to_ban(words_to_ban=self.words_to_ban)
            self.logit_bias_dict: Dict[int, int] = self._get_logit_bias_dict(
                llm_model=self.llm_model
            )

        self.logger.info(f"Initializing LLM: {self.llm_model}")

        if verbose:
            self.llm_kwargs["verbose"] = True

        self.llm_temperature: float = llm_temperature
        self.llm: Union[ChatOpenAI, ChatAnthropic, ChatGoogleGenerativeAI] = (
            self._initialize_llm(
                api_key=self.api_key,
                llm_model_type=self.llm_model_type,
                llm_model=self.llm_model,
                llm_temperature=self.llm_temperature,
                llm_kwargs=self.llm_kwargs,
                logit_bias_dict=self.logit_bias_dict,
            )
        )
        self.logger.info(f"Initialized LLM: {self.llm}")

        self.logger.info("Initializing ChainComposer")
        self.chain_composer: ChainComposer = ChainComposer(logger=self.logger)
        self.logger.info(f"Initialized ChainComposer: {self.chain_composer}")

        self.logger.info("Initializing Chain Variables")
        self.chain_variables: Dict[str, Any] = {}
        self.logger.info(f"Initialized Chain Variables: {self.chain_variables}")

        self.chain_variables_update_overwrite_warning_counter: int = 0

        self.logger.info(f"Initializing Preprocessor {preprocessor}")
        self.preprocessor: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = (
            preprocessor
        )
        self.logger.info(f"Initialized Preprocessor: {self.preprocessor}")

        self.logger.info(f"Initializing Postprocessor {postprocessor}")
        self.postprocessor: Optional[Callable[[Any], Any]] = postprocessor
        self.logger.info(f"Initialized Postprocessor: {self.postprocessor}")

    def __str__(self) -> str:
        """
        Returns a string representation of the ChainManager object.

        The string includes the values of the :attr:`~academic_metrics.ChainBuilder.ChainManager.llm`, :attr:`~academic_metrics.ChainBuilder.ChainManager.chain_composer`, and :attr:`~academic_metrics.ChainBuilder.ChainManager.chain_variables` attributes.

        Returns:
            str: A string representation of the ChainManager object.
        """
        return (
            f"ChainManager(llm={self.llm}, chain_composer={self.chain_composer}, "
            f"global_variables={self.global_variables})"
        )

    def __repr__(self) -> str:
        """
        Returns a string representation of the object for debugging purposes.

        This method calls the __str__() method to provide a user-friendly string
        representation of the object.

        Returns:
            str: A string representation of the object.
        """
        return self.__str__()

    def _validate_words_to_ban(self, words_to_ban: List[str]) -> None:
        """
        Validate the words to ban list.

        Args:
            words_to_ban (list): The list of words to ban.
                Type: List[str]
        """
        if not isinstance(words_to_ban, list):
            raise ValueError("words_to_ban must be a list of strings")

        if not all(isinstance(word, str) for word in words_to_ban):
            raise ValueError("words_to_ban must be a list of strings")

        self.logger.info(f"Words to ban: {words_to_ban}")

        if self.llm_model_type != "openai":
            raise ValueError(
                "words_to_ban is currently only supported for OpenAI models"
            )

        if self.llm_model not in ["gpt-4o", "gpt-4o-mini"]:
            raise ValueError(
                "words_to_ban is currently only supported for gpt-4o and gpt-4o-mini"
            )

    def _get_logit_bias_dict(self, llm_model: str) -> Dict[int, int]:
        """
        Get the logit bias dictionary for the words to ban.
        """
        self.logger.info(
            f"Getting logit bias dict for words to ban: {self.words_to_ban}"
        )

        # Get the tokenizer for gpt-4o and gpt-4o-mini
        tokenizer = tiktoken.get_encoding("o200k_base")

        logit_bias: Dict[int, int] = {}

        for word in self.words_to_ban:
            token_ids: List[int] = tokenizer.encode(word)

            if len(token_ids) > 1:
                self.logger.warning(
                    f"Word to ban '{word}' has multiple tokens: {token_ids}, all tokens will be banned"
                )

            # Apply -100 bias to each token
            for token_id in token_ids:
                logit_bias[token_id] = -100

        return logit_bias

    def _get_llm_model_type(self, *, llm_model: str) -> str:
        """
        Determine the type of LLM (Large Language Model) based on the provided model name.

        Args:
            llm_model (str): The name of the LLM model.

        Returns:
            str: The type of the LLM model. Possible values are "openai", "anthropic", and "google".

        Raises:
            ValueError: If the provided LLM model name does not match any of the supported types.
        """
        if llm_model.lower().startswith("gpt"):
            return "openai"
        elif llm_model.lower().startswith("claude"):
            return "anthropic"
        elif llm_model.lower().startswith("gemini"):
            return "google"
        else:
            raise ValueError(
                f"Unsupported LLM model: {llm_model}. Supported types: gpt, claude, gemini."
            )

    def _initialize_llm(
        self,
        *,
        api_key: str | None = None,
        llm_model_type: str | None = None,
        llm_model: str | None = None,
        llm_temperature: float | None = None,
        llm_kwargs: Dict[str, Any] | None = None,
        logit_bias_dict: Dict[int, int] | None = None,
    ) -> Union[ChatOpenAI, ChatAnthropic, ChatGoogleGenerativeAI]:
        """Initializes a language model based on the specified type.

        Args:
            api_key (str | None): The API key for accessing the language model service.
                Defaults to None.
            llm_model_type (str | None): The type of the language model (e.g., "openai", "anthropic", "google").
                Defaults to None.
            llm_model (str | None): The specific model to use within the chosen type.
                Defaults to None.
            llm_temperature (float | None): The temperature setting for the language model, affecting randomness.
                Defaults to None.
            llm_kwargs (dict | None): Additional keyword arguments specific to the language model.
                Type: Dict[str, Any]
                Defaults to None.
            logit_bias_dict (dict | None): A dictionary mapping token IDs to logit bias values.
                Type: Dict[int, int]
                Defaults to None.

        Returns:
            Union[:class:`ChatOpenAI`, :class:`ChatAnthropic`, :class:`ChatGoogleGenerativeAI`]: An instance of the initialized language model.

        Raises:
            ValueError: If the specified `llm_model_type` is not supported.
        """
        if api_key is None:
            api_key = self.api_key

        if llm_model_type is None:
            llm_model_type = self.llm_model_type

        if llm_model is None:
            llm_model = self.llm_model

        if llm_temperature is None:
            llm_temperature = self.llm_temperature

        if llm_kwargs is None:
            llm_kwargs = self.llm_kwargs

        if llm_model_type == "openai":
            return self._create_openai_llm(
                api_key, llm_model, llm_temperature, llm_kwargs, logit_bias_dict
            )
        elif llm_model_type == "anthropic":
            return self._create_anthropic_llm(
                api_key, llm_model, llm_temperature, **llm_kwargs
            )
        elif llm_model_type == "google":
            return self._create_google_llm(
                api_key, llm_model, llm_temperature, **llm_kwargs
            )
        else:
            raise ValueError(
                f"Unsupported LLM model type: {llm_model_type}. Supported types: openai, anthropic, google."
            )

    def _recreate_llm(self) -> None:
        """Recreates the LLM with the current parameters."""
        self.llm = self._initialize_llm(
            api_key=self.api_key,
            llm_model_type=self.llm_model_type,
            llm_model=self.llm_model,
            llm_temperature=self.llm_temperature,
            llm_kwargs=self.llm_kwargs,
            logit_bias_dict=self.logit_bias_dict,
        )

    def _create_openai_llm(
        self,
        api_key: str,
        llm_model: str,
        llm_temperature: float,
        llm_kwargs: Dict[str, Any],
        logit_bias_dict: Dict[int, int] | None = None,
    ) -> ChatOpenAI:
        """Creates an instance of the ChatOpenAI language model.

        Args:
            api_key (str): The API key for authenticating with the OpenAI service.
            llm_model (str): The identifier of the language model to use.
            llm_temperature (float): The temperature setting for the language model,
                which controls the randomness of the output.
            llm_kwargs (dict): Additional keyword arguments to pass to the ChatOpenAI constructor.
                Type: Dict[str, Any]
            logit_bias_dict (dict | None): A dictionary mapping token IDs to logit bias values.
                Type: Dict[int, int] | None
                Defaults to None.

        Returns:
            :class:`ChatOpenAI`: An instance of the ChatOpenAI language model configured with
                the specified parameters.
        """
        request_timeout: float | None = llm_kwargs.get("request_timeout", None)
        max_retries: int = llm_kwargs.get("max_retries", 3)

        return ChatOpenAI(
            model=llm_model,
            api_key=api_key,
            temperature=llm_temperature,
            request_timeout=request_timeout,
            max_retries=max_retries,
            logit_bias=logit_bias_dict,
        )

    def _create_anthropic_llm(
        self, api_key: str, llm_model: str, llm_temperature: float, **llm_kwargs
    ) -> ChatAnthropic:
        """Creates an instance of the ChatAnthropic language model.

        Args:
            api_key (str): The API key for authenticating with the Anthropic service.
            llm_model (str): The identifier of the language model to use.
            llm_temperature (float): The temperature setting for the language model,
                controlling the randomness of the output.
            llm_kwargs (dict): Additional keyword arguments to pass to the ChatAnthropic constructor.
                Type: Dict[str, Any]

        Returns:
            :class:`ChatAnthropic`: An instance of the ChatAnthropic language model.
        """
        return ChatAnthropic(
            model=llm_model, api_key=api_key, temperature=llm_temperature, **llm_kwargs
        )

    def _create_google_llm(
        self, api_key: str, llm_model: str, llm_temperature: float, **llm_kwargs
    ) -> ChatGoogleGenerativeAI:
        """Creates an instance of ChatGoogleGenerativeAI with the specified parameters.

        Args:
            api_key (str): The API key for authenticating with the Google LLM service.
            llm_model (str): The model identifier for the Google LLM.
            llm_temperature (float): The temperature setting for the LLM,
                which controls the randomness of the output.
            llm_kwargs (dict): Additional keyword arguments to pass to the ChatGoogleGenerativeAI constructor.
                Type: Dict[str, Any]

        Returns:
            :class:`ChatGoogleGenerativeAI`: An instance of the ChatGoogleGenerativeAI class configured
                with the provided parameters.
        """
        return ChatGoogleGenerativeAI(
            model=llm_model, api_key=api_key, temperature=llm_temperature, **llm_kwargs
        )

    def _initialize_parser(
        self,
        parser_type: Literal["pydantic", "json", "str"],
        pydantic_output_model: BaseModel | None = None,
    ) -> ParserType:
        """Initializes and returns a parser based on the specified parser type.

        Args:
            parser_type (str): The type of parser to initialize.
                Must be one of "pydantic", "json", or "str".
                Type: Literal["pydantic", "json", "str"]
            pydantic_output_model (:class:`~pydantic.BaseModel` | None): The Pydantic model to use for the parser. Required if parser_type is "pydantic".
                Defaults to None.

        Returns:
            ParserUnion: An instance of the specified parser type.

        Raises:
            ValueError: If an invalid parser_type is provided.
        """
        if parser_type == "pydantic":
            parser: PydanticOutputParser = self._create_pydantic_parser(
                pydantic_output_model=pydantic_output_model
            )
            self.logger.debug(f"Created Pydantic parser: {parser}")
            return parser
        elif parser_type == "json":
            parser: JsonOutputParser = self._create_json_parser(
                pydantic_output_model=pydantic_output_model
            )
            self.logger.debug(f"Created JSON parser: {parser}")
            return parser
        elif parser_type == "str":
            parser: StrOutputParser = self._create_str_parser()
            self.logger.debug(f"Created Str parser: {parser}")
            return parser
        else:
            raise ValueError(f"Invalid parser_type: {parser_type}")

    def _create_pydantic_parser(
        self, *, pydantic_output_model: BaseModel | None
    ) -> PydanticOutputParser:
        """Creates a Pydantic output parser.

        Args:
            pydantic_output_model (:class:`~pydantic.BaseModel` | None): The Pydantic model to be used for parsing output.

        Returns:
            :class:`PydanticOutputParser`: An instance of PydanticOutputParser initialized with
                the provided Pydantic model.

        Raises:
            ValueError: If pydantic_output_model is not provided.

        Notes:
            - `pydantic_output_model` must be provided for `parser_type` 'pydantic'.
        """
        if not pydantic_output_model:
            raise ValueError(
                "pydantic_output_model must be provided for 'pydantic' parser_type."
            )
        return PydanticOutputParser(pydantic_object=pydantic_output_model)

    def _create_json_parser(
        self, *, pydantic_output_model: BaseModel | None
    ) -> JsonOutputParser:
        """Creates a JSON parser for the chain layer output.

        Args:
            pydantic_output_model (BaseModel | None): An optional Pydantic model to enforce
                typing on the JSON output.
                Type: :class:`pydantic.BaseModel` | None
                Defaults to None.

        Returns:
            :class:`JsonOutputParser`: An instance of JsonOutputParser. If pydantic_output_model is provided, the parser will enforce the model's schema on the output.

        Raises:
            UserWarning: If `pydantic_output_model` is not provided, a warning is issued
                recommending its use for proper typing of the output.
        """
        json_parser: JsonOutputParser | None = None
        if not pydantic_output_model:
            warnings.warn(
                "It is highly recommended to provide a pydantic_output_model when parser_type is 'json'. "
                "This will ensure that the output of the chain layer is properly typed and can be used in downstream chain layers."
            )
            self.logger.debug("Creating JSON parser without pydantic_output_model. ")
            json_parser = JsonOutputParser()
        else:
            self.logger.debug(
                f"Creating JSON parser with pydantic_output_model: {pydantic_output_model}"
            )
        return JsonOutputParser(pydantic_object=pydantic_output_model)

    def _create_str_parser(self) -> StrOutputParser:
        """
        Creates an instance of StrOutputParser.

        Returns:
            :class:`StrOutputParser`: An instance of the StrOutputParser class.
        """
        return StrOutputParser()

    def _run_chain_validation_checks(
        self,
        *,
        output_passthrough_key_name: str | None,
        ignore_output_passthrough_key_name_error: bool,
        parser_type: Literal["pydantic", "json", "str"] | None,
        pydantic_output_model: BaseModel | None,
        fallback_parser_type: Literal["pydantic", "json", "str"] | None,
        fallback_pydantic_output_model: BaseModel | None,
    ) -> None:
        """Validates chain configuration parameters before execution.

        Performs validation checks on chain configuration parameters to ensure proper setup
        and compatibility between different components.

        Args:
            output_passthrough_key_name (str | None): Optional key name for passing chain
                output to next layer.
                Defaults to None.
            ignore_output_passthrough_key_name_error (bool): Whether to ignore missing output key name.
                Defaults to False.
            parser_type (str | None): Type of parser to use.
                Type: Literal["pydantic", "json", "str"] | None
                Defaults to None.
            pydantic_output_model (:class:`~pydantic.BaseModel` | None): Pydantic model for output validation.
                Defaults to None.
            fallback_parser_type (str | None): Type of fallback parser.
                Type: Literal["pydantic", "json", "str"] | None
                Defaults to None.
            fallback_pydantic_output_model (:class:`~pydantic.BaseModel` | None): Pydantic model for fallback parser.
                Defaults to None.

        Raises:
            ValueError: If validation fails for:
                - Missing output key name when required
                - Invalid parser type combinations
                - Missing required models
                - Duplicate parser types
                - Same models used for main and fallback

        Warnings:
            UserWarning: For non-critical issues like:
                - Missing output key name when ignored
                - Missing recommended Pydantic models
                - Unused provided models
        """
        if (
            len(self.chain_composer.chain_sequence) > 0
            and not output_passthrough_key_name
        ):
            if not ignore_output_passthrough_key_name_error:
                raise ValueError(
                    "output_passthrough_key_name not provided and ignore_output_passthrough_key_name_error is False. output_passthrough_key_name is required to identify the output of the chain layer in order to pass the output to the next chain layer. If you do not specify output_passthrough_key_name, the output of the chain layer will not be assigned to a variable and thus will not be available to the next chain layer. If you do not need the output of the chain layer to be passed to the next chain layer, you can set ignore_output_passthrough_key_name_error to True."
                )
            else:
                warnings.warn(
                    "output_passthrough_key_name not provided when adding a chain layer after another. Output of the chain layer will not be assigned to a variable."
                )

        if parser_type is None and fallback_parser_type is not None:
            raise ValueError(
                "parser_type is None when fallback_parser_type is not None. This is not allowed."
            )

        if (parser_type is not None and pydantic_output_model is not None) and (
            fallback_parser_type is not None
            and fallback_pydantic_output_model is not None
        ):
            if pydantic_output_model == fallback_pydantic_output_model:
                raise ValueError(
                    "pydantic_output_model and fallback_pydantic_output_model are the same. This is not allowed."
                )

        if parser_type is not None:
            if parser_type not in ["pydantic", "json", "str"]:
                raise ValueError(
                    f"Unsupported parser type: {parser_type}. Supported types:\n"
                    f"\t'{PydanticOutputParser.__name__}'\n"
                    f"\t'{JsonOutputParser.__name__}'\n"
                    f"\t'{StrOutputParser.__name__}'"
                )
            if parser_type == "pydantic":
                if not pydantic_output_model:
                    raise ValueError(
                        "pydantic_output_model must be specified when parser_type is 'pydantic'."
                    )
            elif parser_type == "json":
                if not pydantic_output_model:
                    warnings.warn(
                        "It is highly recommended to provide a pydantic_output_model when parser_type is 'json'. "
                        "This will ensure that the output of the chain layer is properly typed and can be used in downstream chain layers."
                    )
        else:
            if pydantic_output_model:
                warnings.warn(
                    "pydantic_output_model is provided but parser_type is None. The pydantic_output_model will not be used."
                )

        if fallback_parser_type is not None:
            if parser_type is not None and fallback_parser_type == parser_type:
                raise ValueError(
                    "parser_type and fallback_parser_type are the same. This is not allowed."
                )

            if fallback_parser_type not in ["pydantic", "json", "str"]:
                raise ValueError(
                    f"Unsupported fallback_parser_type: {fallback_parser_type}"
                )
            if fallback_parser_type == "pydantic":
                if not fallback_pydantic_output_model:
                    raise ValueError(
                        "fallback_pydantic_output_model must be specified when fallback_parser_type is 'pydantic'."
                    )
            elif fallback_parser_type == "json":
                if not fallback_pydantic_output_model:
                    warnings.warn(
                        "It is highly recommended to provide a fallback_pydantic_output_model when fallback_parser_type is 'json'. "
                        "This will ensure that the output of the fallback chain layer is properly typed and can be used in downstream chain layers."
                    )
        else:
            if fallback_pydantic_output_model:
                warnings.warn(
                    "fallback_pydantic_output_model is provided but fallback_parser_type is None. The fallback_pydantic_output_model will not be used."
                )

    def _format_chain_sequence(
        self, chain_sequence: List[Tuple[ChainWrapper, str | None]]
    ) -> None:
        """Formats and prints the details of each chain in the given chain sequence.

        Args:
            chain_sequence (list): A list of tuples where each tuple contains a ChainWrapper
                object and an optional output name.
                Type: List[Tuple[ChainWrapper, str | None]]

        Returns:
            None
        """
        for index, (chain_wrapper, output_name) in enumerate(chain_sequence):
            print(f"Chain {index + 1}:")
            print(f"\tOutput Name: {output_name}")
            print(f"\tParser Type: {chain_wrapper.get_parser_type()}")
            print(f"\tFallback Parser Type: {chain_wrapper.get_fallback_parser_type()}")
            print(f"\tPreprocessor: {chain_wrapper.preprocessor}")
            print(f"\tPostprocessor: {chain_wrapper.postprocessor}")

    def _run_validation_checks(
        self,
        *,
        prompt_variables_dict: Union[FirstCallRequired, None],
    ) -> None:
        """Validates the input parameters for the chain execution.

        Args:
            prompt_variables_dict (dict | None): A dictionary containing the variables
                to be passed to the chain layers.
                Type: Union[FirstCallRequired, None]
                - On the first call to `run()`, this parameter must be provided.
                - On subsequent calls, it can be omitted if there are no new variables to pass.

        Raises:
            ValueError: If `prompt_variables_dict` is None on the first call to `run()`.
            TypeError: If `prompt_variables_dict` is not a dictionary when provided.

        Notes:
            - The `prompt_variables_dict` should contain keys that match the variable names
              used in the chain layers.
            - The `output_passthrough_key_name` parameter in the `add_chain_layer` method is
              used to identify the output of the chain layer and assign it to a variable.
            - If `output_passthrough_key_name` is not specified, the output of the chain layer
              will not be assigned to a variable and will not be available to the next chain layer.
            - The `ignore_output_passthrough_key_name_error` parameter can be set to True if
              the output of the chain layer is not needed for the next chain layer, such as
              when running a chain layer solely for its side effects or if it is the last
              chain layer in a multi-layer chain.
            - Ensure that the placeholder variable names in your prompt strings match the keys
              in `prompt_variables_dict` passed into the `ChainManager.run()` method.
        """
        if (
            self.chain_variables_update_overwrite_warning_counter == 0
            and prompt_variables_dict is None
        ):
            raise ValueError(
                "First call to run() must provide a prompt_variables_dict, otherwise there are no variables to pass to the chain layers. "
                "If you do not need to pass variables to the chain layers, you can set prompt_variables_dict to an empty dictionary. "
                "Subsequent calls to run() can omit prompt_variables_dict if you have no new variables to pass to the chain layers. "
                "This is because a global_variables dictionary is maintained in the ChainManager instance and is updated with each call to the class instance method _update_global_variables(), which is automatically called by run() when a new prompt_variables_dict is provided. "
            )

        if prompt_variables_dict is not None and not isinstance(
            cast(Any, prompt_variables_dict), dict
        ):
            raise TypeError(
                "prompt_variables_dict must be a dictionary. "
                "Each key should match the variable names used in your chain layers. "
                "output_passthrough_key_name parameter in add_chain_layer method is used to identify the output of the chain layer "
                "and assign it to a variable. If you do not specify output_passthrough_key_name, the output of the chain layer will not be assigned to a variable and thus will not be available to the next chain layer. "
                "If you do not need the output of the chain layer to be passed to the next chain layer, you can set ignore_output_passthrough_key_name_error to True. "
                "A time to set ignore_output_passthrough_key_name_error to True is when you are running a chain layer solely for its side effects (e.g. printing, saving to a database, etc.) without needing the output of the chain layer to be passed to the next chain layer. "
                "Another reason to set ignore_output_passthrough_key_name_error to True is if you have a multi-layer chain and this is your last chain layer. "
                "Check your prompt strings for your placeholder variables, these names should match the keys in prompt_variables_dict passed into the ChainManager.run() method."
            )

    def add_chain_layer(
        self,
        *,
        system_prompt: str,
        human_prompt: str,
        output_passthrough_key_name: str | None = None,
        ignore_output_passthrough_key_name_error: bool = False,
        preprocessor: Callable[[Dict[str, Any]], Dict[str, Any]] | None = None,
        postprocessor: Callable[[Any], Any] | None = None,
        parser_type: Literal["pydantic", "json", "str"] | None = None,
        fallback_parser_type: Literal["pydantic", "json", "str"] | None = None,
        pydantic_output_model: BaseModel | None = None,
        fallback_pydantic_output_model: BaseModel | None = None,
    ) -> None:
        """Adds a chain layer to the chain composer.

        This method configures and adds a new chain layer to the chain composer,
        allowing for the processing of input data through specified prompts and parsers.

        Args:
            system_prompt (str): The system prompt template for the chain layer.
            human_prompt (str): The human prompt template for the chain layer.
            output_passthrough_key_name (str | None): Key name for passing chain output
                to the next layer.
                Defaults to None.
            ignore_output_passthrough_key_name_error (bool): Flag to ignore missing output
                key name errors.
                Defaults to False.
            preprocessor (:class:`python:typing.Callable` | None): Function to preprocess input data.
                Defaults to None.
            postprocessor (:class:`python:typing.Callable` | None): Function to postprocess output data.
                Defaults to None.
            parser_type (str | None): Type of parser to use.
                Type: Literal["pydantic", "json", "str"] | None
                Defaults to None.
            fallback_parser_type (str | None): Type of fallback parser.
                Type: Literal["pydantic", "json", "str"] | None
                Defaults to None.
            pydantic_output_model (:class:`~pydantic.BaseModel` | None): Pydantic model for output validation.
                Defaults to None
            fallback_pydantic_output_model (:class:`~pydantic.BaseModel` | None): Pydantic model for fallback parser.
                Defaults to None.

        Returns:
            None
        """
        self.logger.info(
            f"Adding chain layer with output_passthrough_key_name: {output_passthrough_key_name}"
        )
        self.logger.info(
            f"ignore_output_passthrough_key_name_error: {ignore_output_passthrough_key_name_error}"
        )
        self.logger.info(f"parser_type: {parser_type}")
        self.logger.info(f"pydantic_output_model: {pydantic_output_model}")
        self.logger.info(f"preprocessor: {preprocessor}")
        self.logger.info(f"postprocessor: {postprocessor}")
        self.logger.info("--------------------------------")
        self.logger.info(f"system_prompt: {system_prompt}")
        self.logger.info(f"human_prompt: {human_prompt}")
        self.logger.info("--------------------------------")

        self._run_chain_validation_checks(
            output_passthrough_key_name=output_passthrough_key_name,
            ignore_output_passthrough_key_name_error=ignore_output_passthrough_key_name_error,
            parser_type=parser_type,
            pydantic_output_model=pydantic_output_model,
            fallback_parser_type=fallback_parser_type,
            fallback_pydantic_output_model=fallback_pydantic_output_model,
        )

        parser: Optional[ParserType] = None
        fallback_parser: Optional[ParserType] = None
        if parser_type:
            parser = self._initialize_parser(
                parser_type=parser_type, pydantic_output_model=pydantic_output_model
            )
        if fallback_parser_type:
            fallback_parser = self._initialize_parser(
                parser_type=fallback_parser_type,
                pydantic_output_model=fallback_pydantic_output_model,
            )
        # Create prompt templates without specifying input_variables
        system_prompt_template: PromptTemplate = PromptTemplate(template=system_prompt)
        human_prompt_template: PromptTemplate = PromptTemplate(template=human_prompt)
        system_message_prompt_template: SystemMessagePromptTemplate = (
            SystemMessagePromptTemplate.from_template(system_prompt_template.template)
        )
        human_message_prompt_template: HumanMessagePromptTemplate = (
            HumanMessagePromptTemplate.from_template(human_prompt_template.template)
        )

        chat_prompt_template: ChatPromptTemplate = ChatPromptTemplate.from_messages(
            [system_message_prompt_template, human_message_prompt_template]
        )
        # Build the chain using ChainBuilder
        chain_builder: ChainBuilder = ChainBuilder(
            chat_prompt=chat_prompt_template,
            llm=self.llm,
            parser=parser,
            fallback_parser=fallback_parser,
            logger=self.logger,
        )
        chain: Runnable = chain_builder.get_chain()
        fallback_chain: Runnable = chain_builder.get_fallback_chain()

        # Wrap the chain
        chain_wrapper: ChainWrapper = ChainWrapper(
            chain=chain,
            fallback_chain=fallback_chain,
            parser=parser,
            fallback_parser=fallback_parser,
            preprocessor=preprocessor or self.preprocessor,
            postprocessor=postprocessor or self.postprocessor,
            logger=self.logger,
        )

        # Add the chain to the composer
        self.chain_composer.add_chain(
            chain_wrapper=chain_wrapper,
            output_passthrough_key_name=output_passthrough_key_name,
        )

        # Return the ChainManager instance to allow for method chaining
        return self

    def _format_overwrite_warning(self, overwrites: Dict[str, Dict[str, Any]]) -> str:
        """Formats a warning message for overwritten values.

        Args:
            overwrites (dict): A dictionary where the key is the name of the overwritten item,
                and the value is another dictionary with 'old' and 'new' keys representing
                the old and new values respectively.
                Type: Dict[str, Dict[str, Any]]

        Returns:
            str: A formatted string that lists each overwritten item with its old and
                new values.
        """
        return "\n".join(
            f"  {key}:\n    - {details['old']}\n    + {details['new']}"
            for key, details in overwrites.items()
        )

    def _check_first_time_overwrites(
        self, prompt_variables_dict: Dict[str, Any]
    ) -> None:
        """Checks and warns if any global chain variables are being overwritten for the first time.

        This method compares the keys in the provided `prompt_variables_dict` with the existing
        `chain_variables`. If any keys match, it indicates that an overwrite is occurring. A warning
        is issued the first time this happens, detailing the old and new values of the overwritten
        variables. Subsequent overwrites will not trigger warnings.

        Args:
            prompt_variables_dict (dict): A dictionary containing the new values for the chain
                variables that may overwrite existing ones.
                Type: Dict[str, Any]

        Returns:
            None
        """
        if self.chain_variables_update_overwrite_warning_counter == 0:
            overwrites = {
                key: {
                    "old": self.chain_variables[key],
                    "new": prompt_variables_dict[key],
                }
                for key in prompt_variables_dict
                if key in self.chain_variables
            }
            if overwrites:
                warnings.warn(
                    f"Overwriting existing global variables:\n"
                    f"{self._format_overwrite_warning(overwrites)}\n"
                    "Subsequent overwrites will not trigger warnings."
                )
            self.chain_variables_update_overwrite_warning_counter += 1

    def _update_chain_variables(self, prompt_variables_dict: Dict[str, Any]) -> None:
        """Update global variables with new values, warning on first-time overwrites.

        Args:
            prompt_variables_dict (dict): A dictionary containing the new values for
                the global variables.
                Type: Dict[str, Any]

        Returns:
            None
        """
        # Update global variables with new values, warning on first-time overwrites.
        self._check_first_time_overwrites(prompt_variables_dict)
        self.chain_variables.update(prompt_variables_dict)

    def get_chain_sequence(self) -> List[Tuple[ChainWrapper, str | None]]:
        """Retrieves the chain sequence from the chain composer.

        Returns:
            list: A list of tuples where each tuple contains a ChainWrapper object and
                the output key name if output_passthrough_key_name was provided to add_chain_layer.
                Type: List[Tuple[:class:`academic_metrics.ChainBuilder.ChainBuilder.ChainWrapper`, str | None]]
        """
        return self.chain_composer.chain_sequence

    def print_chain_sequence(self) -> None:
        """Prints the chain sequence by formatting it.

        This method retrieves the chain sequence from the chain composer and
        formats it using the _format_chain_sequence method.

        Returns:
            None
        """
        chain_sequence: List[Tuple[ChainWrapper, str | None]] = (
            self.chain_composer.chain_sequence
        )
        self._format_chain_sequence(chain_sequence)

    def get_chain_variables(self) -> Dict[str, Any]:
        """Retrieve the chain variables.

        Returns:
            dict: A dictionary containing the chain variables.
                Type: Dict[str, Any]
        """
        return self.chain_variables

    def print_chain_variables(self) -> None:
        """Prints the chain variables in a formatted manner.

        This method prints the chain variables stored in the `chain_variables`
        attribute of the class. The output is formatted with a header and
        footer consisting of dashes, and each key-value pair is printed on
        a new line.

        Returns:
            None
        """
        print(f"Chain Variables:\n{'-' * 10}")
        for key, value in self.chain_variables.items():
            print(f"{key}: {value}")
        print(f"{'-' * 10}\n")

    def set_words_to_ban(self, words_to_ban: List[str]) -> None:
        """Updates the list of words to ban and recreates the OpenAI LLM with new logit bias.

        Args:
            words_to_ban (list): List of words to ban from LLM output
                Type: List[str]

        Returns:
            None
        """
        self.words_to_ban = words_to_ban
        self._validate_words_to_ban(words_to_ban)
        self.logit_bias_dict = self._get_logit_bias_dict(llm_model=self.llm_model)
        self._recreate_llm()

    def run(
        self,
        *,
        prompt_variables_dict: Union[FirstCallRequired, None] = None,
    ) -> str:
        """Executes the chain builder process.

        This method performs validation checks, updates chain variables if provided,
        and runs the chain composer with the current chain variables.

        Args:
            prompt_variables_dict (dict | None): A dictionary containing prompt variables.
                If provided, it will be used to update the chain variables.
                Type: Union[:data:`~academic_metrics.ChainBuilder.ChainBuilder.FirstCallRequired`, None]
                Defaults to None.

        Returns:
            str: The result of running the chain composer.
        """
        self._run_validation_checks(
            prompt_variables_dict=prompt_variables_dict,
        )

        if prompt_variables_dict is not None:
            self._update_chain_variables(prompt_variables_dict)

        return self.chain_composer.run(
            data_dict=self.chain_variables,
            data_dict_update_function=self._update_chain_variables,
        )
