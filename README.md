# ChainBuilder

[![codecov](https://codecov.io/gh/SpencerPresley/AIChainComposer/graph/badge.svg?token=RSTTE8FH8Q)](https://codecov.io/gh/SpencerPresley/AIChainComposer)

ChainBuilder is a powerful Python library for composing and orchestrating complex LLM chains. It provides a clean, intuitive interface for building sophisticated AI pipelines while handling all the complexity of prompt management, error handling, and output parsing.

## Table of Contents

- [ChainBuilder](#chainbuilder)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Installation](#installation)
  - [Quick Start](#quick-start)
  - [Advanced Features](#advanced-features)
    - [Fallback Parsing](#fallback-parsing)
    - [Variable Management](#variable-management)
    - [Multiple LLM Support](#multiple-llm-support)
  - [Building Complex Systems](#building-complex-systems)
    - [Step 0: Load the API Key](#step-0-load-the-api-key)
    - [Step 1: Define the Output Models](#step-1-define-the-output-models)
    - [Step 2: Define our Classification Categories](#step-2-define-our-classification-categories)
    - [Step 3: Create the Prompts](#step-3-create-the-prompts)
    - [Step 4: Create the Chain Layers](#step-4-create-the-chain-layers)
    - [Step 5: Run the Chain](#step-5-run-the-chain)
  - [Contributing](#contributing)
  - [License](#license)

## Features

- 🔗 **Flexible Chain Composition**: Build multi-layer LLM chains with ease
- 🎯 **Smart Output Parsing**: Built-in support for JSON, Pydantic, and string parsing
- 🔄 **Fallback Handling**: Graceful degradation with configurable fallback parsers
- 🎨 **Multiple LLM Support**: Works with OpenAI, Anthropic, and Google AI models
- 🛠️ **Type Safety**: Full type hints and Pydantic model integration
- 📊 **Variable Management**: Automatic handling of chain variables and state
- 🔍 **Comprehensive Logging**: Built-in logging for debugging and monitoring

## Installation

```bash
pip install chain-composer
```

## Quick Start

This is a simple example of how to use ChainComposer. Here I build 2 layer chain where the AI from the first layer takes the first derivative of a function and the second layer AI takes the second derivative of that function.

```python
from dotenv import load_dotenv
import os
import json
from pydantic import BaseModel
from chain_composer import ChainComposer

# Load the API key
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Define the output models
class FirstDerivative(BaseModel):
    first_derivative: str
    
class SecondDerivative(BaseModel):
    second_derivative: str

# Define the first layer system message
first_derivative_system_message = """
You are a helpful assistant, who takes the first derivative of a function and returns the result in the following format:

{{
    "first_derivative": "<answer>"
}}

IMPORTANT: You should always return json. Do not include the markdown json format, just return the json.
"""

# Define the second layer system message
second_derivative_system_message = """
You are a helpful assistant, who takes a second derivative and returns the result in the following format:

{{
    "second_derivative": "<answer>"
}}

IMPORTANT: You should always return json. Do not include the markdown json format, just return the json.
"""

# Define the human message for the first layer
human_message = """
Equation:

{equation}
"""

# Define the human message for the second layer
human_message_2 = """
Original Equation:

{equation}

First Derivative:

{first_derivative}
"""

# Define the chain with the json parser
def with_json_parser():
    # Initialize the chain composer
    cp = ChainComposer(
        model="gpt-4o-mini",
        api_key=api_key,
    )
    
    # Add the layers with parser_type="json"
    return cp.add_chain_layer(
        system_prompt=first_derivative_system_message,
        human_prompt=human_message,
        output_passthrough_key_name="first_derivative",
        parser_type="json",
        pydantic_output_model=FirstDerivative
    ).add_chain_layer(
        system_prompt=second_derivative_system_message,
        human_prompt=human_message_2,
        output_passthrough_key_name="second_derivative",
        parser_type="json",
        pydantic_output_model=SecondDerivative
    )

# Define the chain with the pydantic parser
def with_pydantic_parser():
    # Initialize the chain composer
    cp = ChainComposer(
        model="gpt-4o-mini",
        api_key=api_key,
    )
    
    # Add the layers with parser_type="pydantic"
    return cp.add_chain_layer(
        system_prompt=first_derivative_system_message,
        human_prompt=human_message,
        output_passthrough_key_name="first_derivative",
        parser_type="pydantic",
        pydantic_output_model=FirstDerivative
    ).add_chain_layer(
        system_prompt=second_derivative_system_message,
        human_prompt=human_message,
        output_passthrough_key_name="second_derivative",
        parser_type="pydantic",
        pydantic_output_model=SecondDerivative
    )

# Run the chain with the json parser, providing the equation as a variable in a dictionary
json_result = with_json_parser().run(
    {
        "equation": "2x^2 + 3x + 2"
    }
)

# Run the chain with the pydantic parser, providing the equation as a variable in a dictionary
pydantic_result = with_pydantic_parser().run(
    {
        "equation": "2x^2 + 3x + 2"
    }
)

# Prints the json results
def print_json_result(result: dict):
    print(f"With json parser type on the final layer prior to running, the output is a dictionary:\n\nType: {type(result)}\n{json.dumps(result, indent=4)}\n")
    
# Prints the pydantic results
def print_in_depth_pydantic_result(result: dict):
    print(f"\n\nFor the pydantic parser type for the final layer, the output dictionary will contain the pydantic model passed in as the value of the key passed in as the output_passthrough_key_name in the last layer.\n")
    print(f"Original Input:\n{result['equation']}\n")
    print(f"Output from first layer is sent to next as json, thus is json in output:\n\nType: {type(result['first_derivative'])}\n\n{result['first_derivative']}\n")
    print(f"Output from second layer is sent to next as json, but if the parser_type is \"pydantic\", it will be converted back to a pydantic model before being added back to the return dict:\n\nType: {type(result['second_derivative'])}\n\n{result['second_derivative']}")

print_json_result(json_result)
print_in_depth_pydantic_result(pydantic_result)
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
    {
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
    model="gpt-4o-mini",
    api_key=openai_key
)

# Anthropic
claude_chain = ChainComposer(
    model="claude-3.5-sonnet-20240620",
    api_key=anthropic_key
)

# Google
palm_chain = ChainComposer(
    model="gemini-1.5-flash-002",
    api_key=google_key
)
```

## Building Complex Systems

ChainBuilder excels at building sophisticated AI systems. Here's an example of how it can be used to create a complex academic paper classifier:

For this example, we will go through a step by step setup of building out the prompts and complex multi-layer chain.

If you would like to see the full code for this you can find it [here](examples/complex_example/complex_example.py).

If you'd like to try running the script yourself, just clone the repo, install the dependencies, and run the script:

```bash
git clone https://github.com/SpencerPresley/AIChainComposer.git
cd AIChainComposer
pip install -r requirements.txt
python examples/complex_example/complex_example.py
```

### Step 0: Load the API Key

First, we need to load the API key for the LLM we want to use.

```python
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
```

### Step 1: Define the Output Models

The output models are pydantic models that will enforce the LLM to conform to a specific output format.

This example will consist of 2 layers and 3 outputs.

We will:

1. Create a pre-classification layer to identify methdologies used in the paper and construct a sentence analysis layer to analyze the abstract and identify the overall theme and summary.
2. Create a classification layer to classify the paper into one of the available categories.

The reason for the pre-classification layer is to be able to break down the problem into smaller, more manageable parts.

For classifying research papers, we need to be careful that the classifications outputted are not based on the methods used, but rather the overall theme of the research being conducted.

Additionally, we want to get full context of the paper. Since LLMs tend to skim content, we will force the LLM to read each sentence in the provided abstract, having them provide sentence details and reasoning for each sentence.

The classification will be the second layer, it will receive the outputs from the pre-classification layer to use them to better classify the paper.

This takes a lot of responsibility off of the classification layer, allowing it to focus on the task of classification, and thus resulting in a more accurate classification.

To give us some more information about how the LLM went about the problem it was given, we will also require it to provide us a reasoning and confidence score for each output.

**Pydantic Output Models**:

```python
from pydantic import BaseModel
from typing import List

class MethodExtractionOutput(BaseModel):
    methods: List[str]
    confidence: float

class SentenceDetails(BaseModel):
    sentence: str
    meaning: str
    reasoning: str

class SentenceAnalysisOutput(BaseModel):
    sentence_details: List[SentenceDetails]
    overall_theme: str
    confidence: float

class Classification(BaseModel):
    classification: str

class ClassificationOutput(BaseModel):
    classifications: List[Classification]
    confidence: float
```

### Step 2: Define our Classification Categories

To define the categories, we will use a taxonomy released by the National Science Foundation. It can be found [here](https://ncses.nsf.gov/pubs/ncses23200).

This is a 3 level taxonomy, but for this example we will only be classifying into the top categories. If you want to explore the full code which implements a classification system across all levels, check out [Academic Metrics](https://pypi.org/project/academic-metrics/) - a Python package I built that automates the collection of institutional research data and uses AI to classify publications into the full taxonomy, while also providing comprehensive analytics in various output formats. You can find the Academic Metrics source code [here](https://github.com/SpencerPresley/COSC425-DATA), and you can find the code for the classification system which uses AIChainComposer [here](https://github.com/SpencerPresley/COSC425-DATA/blob/main/src/academic_metrics/AI/abstract_classifier.py).

To see this taxonomy in-memory as a string, see [taxonomy.py](examples/complex_example/taxonomy.py).

Once we have the taxonomy in-memory as a string, we can load it into a dictionary, and since we're only using the top categories, we can easily convert it to a list of strings.

```python
import json

taxonomy = json.loads(TAXONOMY_AS_STRING)
categories = list(taxonomy.keys())
```

### Step 3: Create the Prompts

For the prompts we need:

- A system message for each layer
- A human message which contains the abstract of the paper we want to classify

Due to the power of the composer, we can just define these as strings with placeholders, we don't have to worry about making langchain components.

To see the prompts used for this example, see [prompts.py](examples/complex_example/prompts.py).

### Step 4: Create the Chain Layers

Now that we have our output models, categories, and prompts, we can create the chain layers.

```python
from chain_composer import ChainComposer

# Initialize chain for pre-classification composer
cp = ChainComposer(
    model="gpt-4o-mini",
    api_key=api_key,
)

# Add layers for method extraction and sentence analysis
# You can chain as many layers as you want, and you can use the same composer for each layer

# Add our method extraction layer
cp.add_chain_layer(
    system_prompt=method_extraction_system_message, # The system message for the layer
    human_prompt=human_message_prompt, # The human message for the layer
    parser_type="json", # The parser type for the layer
    pydantic_output_model=MethodExtractionOutput, # The output model for the layer
    output_passthrough_key_name="method_json_output", # The key name for the output passthrough
)

# Add our sentence analysis layer
cp.add_chain_layer(
    system_prompt=sentence_analysis_system_message, # The system message for the layer
    human_prompt=human_message_prompt, # The human message for the layer
    parser_type="json", # The parser type for the layer
    pydantic_output_model=SentenceAnalysisOutput, # The output model for the layer
    output_passthrough_key_name="sentence_analysis_output", # The key name for the output passthrough
)

# Add classification layer
cp.add_chain_layer(
    system_prompt=classification_system_message, # The system message for the layer
    human_prompt=human_message_prompt, # The human message for the layer
    parser_type="json", # The parser type for the layer
    pydantic_output_model=ClassificationOutput, # The output model for the layer
    output_passthrough_key_name="classification_output", # The key name for the output passthrough
)
```

### Step 5: Run the Chain

Now that we have our chain layers, we can run the chain.

The `run()` method takes in a dictionary of variables whose keys should match placeholder variables in the prompts.

The `run()` method returns a dictionary which:

- Contains the original input variable
- Outputs with keys matching the `output_passthrough_key_name` for each layer

To see the abstract we are using, see [abstract.py](examples/complex_example/abstract.py).

```python
# Process an abstract
from abstract import abstract

# Notice our keys match the placeholders in the prompts
result = cp.run(
    {
        "abstract": abstract,
        "categories": categories,
        "method_json_format": method_json_format,
        "sentence_analysis_json_format": sentence_analysis_json_format,
        "classification_json_format": classification_json_format,
    }
)
```

Once this is finished, we can print out the results from each layer.

For brevity, let's just print out the outputs from each layer.

```python
print(f"Method Extraction Output:\n{json.dumps(result['method_json_output'], indent=4)}\n")
print(f"Sentence Analysis Output:\n{json.dumps(result['sentence_analysis_output'], indent=4)}\n")
print(f"Classification Output:\n{json.dumps(result['classification_output'], indent=4)}\n")
```

The results from this will be:

```bash
Method Extraction Output:
{
    "methods": [
        "discussion/seminar format",
        "videotaped interview",
        "support group attendance",
        "senior center activity",
        "center visit",
        "culminating research paper"
    ],
    "confidence": 0.85
}

Sentence Analysis Output:
{
    "sentence_details": [
        {
            "sentence": "With the aging of Baby Boomers, 2030 will mark the first time in U.S. history that those aged 65 and older will outnumber children.",
            "meaning": "In 2030, there will be more individuals aged 65 and older in the U.S. than there are children.",
            "reasoning": "This indicates a demographic shift due to the aging Baby Boomer generation, which is a significant change in the population structure.",
            "confidence": 0.95
        },
        {
            "sentence": "This population shift is expected to place unprecedented demands on the healthcare system in terms of both volume and complexity of care.",
            "meaning": "The increasing number of older adults will create new challenges for the healthcare system, both in the number of patients and the complexity of their health needs.",
            "reasoning": "An aging population typically requires more healthcare services, which can be more complicated due to multiple health issues.",
            "confidence": 0.9
        },
        {
            "sentence": "Given these population shifts and emphasis on an interdisciplinary approach to care, a 4-credit Honors aging course was developed for Honors students in nursing and other health-related majors.",
            "meaning": "In response to demographic changes, a specialized course on aging was created for high-achieving nursing and health students.",
            "reasoning": "The course aims to prepare students for the unique challenges posed by an aging population, highlighting the need for interdisciplinary collaboration in healthcare.",
            "confidence": 0.92
        },
        {
            "sentence": "Aging Reexamined, Reimagined is offered in a discussion/seminar format with limited enrollment to allow for deep reflective discourse about pertinent issues affecting older adults.",
            "meaning": "The course is structured as a seminar with small class sizes to facilitate in-depth discussions about important topics related to aging.",
            "reasoning": "A smaller class size enhances student engagement and allows for more meaningful interactions regarding complex issues faced by older adults.",
            "confidence": 0.88
        },
        {
            "sentence": "Topics include physical/cognitive changes, ageism, Alzheimer's disease, sexuality, aging in place, polypharmacy, addiction, depression, caregiving, elder justice, and end-of-life care.",
            "meaning": "The course covers a wide range of important subjects related to aging and the challenges faced by older adults.",
            "reasoning": "These topics are relevant to understanding the multifaceted nature of aging and the healthcare needs of older individuals.",
            "confidence": 0.95
        },
        {
            "sentence": "Guest speakers share their expertise on selected issues, otherwise students alternate leading discussions on remaining topics.",
            "meaning": "The course includes guest lectures and student-led discussions to enhance learning and engagement.",
            "reasoning": "Inviting experts and allowing students to lead discussions fosters a richer educational environment and practical insights into aging issues.",
            "confidence": 0.9
        },
        {
            "sentence": "There are three focused reflections on assigned experiences which include conducting a videotaped interview with a retired community-based older adult, attending a support group or senior center activity, and visiting a center to view various physical/technological adaptive aids that maintain mobility and independence in the home.",
            "meaning": "Students participate in hands-on experiences that involve interacting with older adults and observing aids that support their independence.",
            "reasoning": "These experiential learning activities are designed to enhance students' understanding of the practical aspects of aging and care.",
            "confidence": 0.91
        },
        {
            "sentence": "There is also a culminating research paper on an issue of their choice.",
            "meaning": "At the end of the course, students must write a research paper on a topic related to aging that interests them.",
            "reasoning": "This assignment encourages independent research and allows students to explore a specific issue in depth, reinforcing their learning.",
            "confidence": 0.87
        },
        {
            "sentence": "Student evaluations are overwhelmingly positive; comments include gaining in-depth knowledge about the unique needs of this population and the importance of healthy aging with an emphasis on a positive, inter-professional approach to care.",
            "meaning": "Students have given high ratings to the course, noting that they have learned a lot about older adults' needs and the benefits of collaborative care.",
            "reasoning": "Positive evaluations suggest that the course effectively meets its educational objectives and resonates with students' experiences and learning.",
            "confidence": 0.94
        },
        {
            "sentence": "It is incumbent upon educators to better prepare students to recognize ageist attitudes, as well as address the significant impact of this longevity revolution.",
            "meaning": "Educators have a responsibility to teach students about ageism and the implications of an increasing older population.",
            "reasoning": "Recognizing and combating ageism is essential for healthcare professionals who will work with older adults, especially as their numbers grow.",
            "confidence": 0.93
        }
    ],
    "overall_theme": "The necessity of preparing healthcare students for the challenges of an aging population through specialized education and interdisciplinary approaches.",
    "confidence": 0.92
}

Classification Output:
{
    "classifications": [
        {
            "categories": [
                "Health sciences",
                "Education",
                "Social sciences"
            ],
            "confidence": 0.92
        }
    ]
}
```

And this is just the tip of the iceberg.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
