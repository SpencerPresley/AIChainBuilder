# ChainBuilder

[![codecov](https://codecov.io/gh/SpencerPresley/AIChainComposer/graph/badge.svg?token=RSTTE8FH8Q)](https://codecov.io/gh/SpencerPresley/AIChainComposer)

ChainBuilder is a powerful Python library for composing and orchestrating complex LLM chains. It provides a clean, intuitive interface for building sophisticated AI pipelines while handling all the complexity of prompt management, error handling, and output parsing.

## Features

- 🔗 **Flexible Chain Composition**: Build multi-layer LLM chains with ease
- 🎯 **Smart Output Parsing**: Built-in support for JSON, Pydantic, and string parsing
- 🔄 **Fallback Handling**: Graceful degradation with configurable fallback parsers
- 🎨 **Multiple LLM Support**: Works with OpenAI, Anthropic, and Google AI models
- 🛠️ **Type Safety**: Full type hints and Pydantic model integration
- 📊 **Variable Management**: Automatic handling of chain variables and state
- 🔍 **Comprehensive Logging**: Built-in logging for debugging and monitoring

## Quick Start

```python
from dotenv import load_dotenv
import os
from chain_composer import ChainComposer
from pydantic import BaseModel

# Load API key
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Define output models
class FirstDerivative(BaseModel):
    first_derivative: str
    
class SecondDerivative(BaseModel):
    second_derivative: str

# Create prompts
first_derivative_system_message = """
You are a helpful assistant, who takes the first derivative of a function and returns the result in JSON format:
{
    "first_derivative": "<answer>"
}
"""

second_derivative_system_message = """
You are a helpful assistant, who takes a second derivative and returns the result in JSON format:

{{
    "second_derivative": "<answer>"
}}

First Derivative:
{first_derivative}
"""

human_message = """
Equation:
{equation}
"""

# Build the chain
composer = ChainComposer(
    model="gpt-4",
    api_key=api_key,
)

chain = composer.add_chain_layer(
    system_prompt=first_derivative_system_message,
    human_prompt=human_message,
    output_passthrough_key_name="first_derivative",
    parser_type="json",
    pydantic_output_model=FirstDerivative
).add_chain_layer(
    system_prompt=second_derivative_system_message,
    human_prompt=human_message,
    output_passthrough_key_name="second_derivative",
    parser_type="json",
    pydantic_output_model=SecondDerivative
)

# Run the chain
result = chain.run(
    prompt_variables_dict={
        "equation": "2x^2 + 3x + 2"
    }
)

print(result)  # Contains both first and second derivatives
```

## Building Complex Systems

ChainBuilder excels at building sophisticated AI systems. Here's an example of how it can be used to create a complex academic paper classifier:

```python
from chain_composer import ChainComposer
from pydantic import BaseModel

class MethodExtractionOutput(BaseModel):
    methods: List[str]

class AbstractSentenceAnalysis(BaseModel):
    sentence_details: List[SentenceDetails]
    overall_theme: str
    summary: str

class ClassificationOutput(BaseModel):
    classifications: List[Classification]

# Initialize chain for pre-classification analysis
pre_classification = ChainComposer(
    model="gpt-4",
    api_key=api_key,
)

# Add layers for method extraction, sentence analysis, and summarization
pre_classification.add_chain_layer(
    system_prompt=METHOD_EXTRACTION_SYSTEM_MESSAGE,
    human_prompt=HUMAN_MESSAGE_PROMPT,
    parser_type="json",
    fallback_parser_type="str",
    pydantic_output_model=MethodExtractionOutput,
    output_passthrough_key_name="method_json_output",
).add_chain_layer(
    system_prompt=ABSTRACT_SENTENCE_ANALYSIS_SYSTEM_MESSAGE,
    human_prompt=HUMAN_MESSAGE_PROMPT,
    parser_type="json",
    fallback_parser_type="str",
    pydantic_output_model=AbstractSentenceAnalysis,
    output_passthrough_key_name="sentence_analysis_output",
)

# Initialize chain for classification
classification = ChainComposer(
    model="gpt-4",
    api_key=api_key,
)

# Add classification layer
classification.add_chain_layer(
    system_prompt=CLASSIFICATION_SYSTEM_MESSAGE,
    human_prompt=HUMAN_MESSAGE_PROMPT,
    parser_type="json",
    pydantic_output_model=ClassificationOutput,
    output_passthrough_key_name="classification_output",
)

# Process an abstract
abstract = "This paper presents a novel machine learning approach..."

# Run pre-classification
pre_classification_results = pre_classification.run(
    prompt_variables_dict={"abstract": abstract}
)

# Use results for classification
classification_results = classification.run(
    prompt_variables_dict={
        **pre_classification_results,
        "categories": available_categories,
    }
)
```

## Advanced Features

### Fallback Parsing

```python
composer.add_chain_layer(
    system_prompt=prompt,
    human_prompt=human_prompt,
    parser_type="json",
    fallback_parser_type="str",  # Falls back to string if JSON parsing fails
    pydantic_output_model=OutputModel,
    output_passthrough_key_name="result"
)
```

### Variable Management

```python
# Variables are automatically passed between layers
result = composer.run(
    prompt_variables_dict={
        "input": "initial input",
        "context": "additional context"
    }
)

# Access chain variables
variables = composer.get_chain_variables()
```

### Multiple LLM Support

```python
# OpenAI
openai_chain = ChainComposer(
    model="gpt-4",
    api_key=openai_key
)

# Anthropic
claude_chain = ChainComposer(
    model="claude-2",
    api_key=anthropic_key
)

# Google
palm_chain = ChainComposer(
    model="palm2",
    api_key=google_key
)
```

## Installation

```bash
pip install chain-composer
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
