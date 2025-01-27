[![SVG Banners](https://svg-banners.vercel.app/api?type=glitch&text1=Chain%20Composer&width=200&height=705)](https://github.com/Akshay090/svg-banners)

# ChainComposer

[![codecov](https://codecov.io/gh/SpencerPresley/AIChainComposer/graph/badge.svg?token=RSTTE8FH8Q)](https://codecov.io/gh/SpencerPresley/AIChainComposer) [![PyPi](https://img.shields.io/pypi/v/ChainComposer)](https://pypi.org/project/ChainComposer/) [![Documentation](https://img.shields.io/badge/docs-latest-blue)](https://chaincomposer.readthedocs.io/en/latest/)

[![GitHub issues](https://img.shields.io/github/issues/SpencerPresley/AIChainComposer)](https://github.com/SpencerPresley/AIChainComposer/issues) [![GitHub forks](https://img.shields.io/github/forks/SpencerPresley/AIChainComposer)](https://github.com/SpencerPresley/AIChainComposer/network) [![GitHub stars](https://img.shields.io/github/stars/SpencerPresley/AIChainComposer)](https://github.com/SpencerPresley/AIChainComposer/stargazers) [![GitHub license](https://img.shields.io/github/license/SpencerPresley/AIChainComposer)](https://github.com/SpencerPresley/AIChainComposer/blob/main/LICENSE) [![GitHub star chart](https://img.shields.io/github/stars/SpencerPresley/AIChainComposer?style=social)](https://star-history.com/#SpencerPresley/AIChainComposer) [![Downloads](https://static.pepy.tech/badge/chaincomposer/month)](https://pepy.tech/project/chaincomposer)

[![Share on Reddit](https://img.shields.io/badge/-Share%20on%20Reddit-orange)](https://www.reddit.com/submit?url=https%3A%2F%2Fgithub.com%2FSpencerPresley%2FAIChainComposer&title=ChainComposer%20-%20Powerful%20Python%20library%20for%20LLM%20chains) [![Share on X/Twitter](https://img.shields.io/badge/-Share%20on%20Twitter-blue)](https://twitter.com/intent/tweet?text=Check%20out%20ChainComposer%20-%20Powerful%20Python%20library%20for%20LLM%20chains%20%23AI%20%23Python%0A%0Ahttps%3A%2F%2Fgithub.com%2FSpencerPresley%2FAIChainComposer) [![Share on LinkedIn](https://img.shields.io/badge/-Share%20on%20LinkedIn-blue)](https://www.linkedin.com/shareArticle?mini=true&url=https%3A%2F%2Fgithub.com%2FSpencerPresley%2FAIChainComposer&title=ChainComposer%20-%20Powerful%20Python%20library%20for%20LLM%20chains) [![Share on Hacker News](https://img.shields.io/badge/-Share%20on%20Hacker%20News-orange)](https://news.ycombinator.com/submitlink?u=https%3A%2F%2Fgithub.com%2FSpencerPresley%2FAIChainComposer&t=ChainComposer%20-%20Powerful%20Python%20library%20for%20LLM%20chains) [![Share on Pinterest](https://img.shields.io/badge/-Share%20on%20Pinterest-red)](https://pinterest.com/pin/create/button/?url=https%3A%2F%2Fgithub.com%2FSpencerPresley%2FAIChainComposer&description=ChainComposer%20-%20Powerful%20Python%20library%20for%20LLM%20chains) [![Share on Facebook](https://img.shields.io/badge/-Share%20on%20Facebook-blue)](https://www.facebook.com/sharer/sharer.php?u=https%3A%2F%2Fgithub.com%2FSpencerPresley%2FAIChainComposer) [![Share on Telegram](https://img.shields.io/badge/-Share%20on%20Telegram-blue)](https://telegram.me/share/url?url=https%3A%2F%2Fgithub.com%2FSpencerPresley%2FAIChainComposer&text=ChainComposer%20-%20Powerful%20Python%20library%20for%20LLM%20chains)

ChainComposer is a powerful Python library for composing and orchestrating complex LLM chains. It provides a clean, intuitive interface for building sophisticated AI pipelines while handling all the complexity of prompt management, error handling, and output parsing.

## Table of Contents

- [ChainComposer](#chaincomposer)
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

| Category | Features | Benefits |
|----------|----------|-----------|
| 🔗 Chain Building | • Multi-layer Chain Support<br>• Flexible Composition<br>• Dynamic Variable Flow<br>• Chain State Management | • Complex AI workflows<br>• Modular design<br>• Data persistence<br>• State tracking |
| 🎯 Output Handling | • JSON Parsing<br>• Pydantic Integration<br>• String Processing<br>• Fallback Parsing | • Structured outputs<br>• Type safety<br>• Format flexibility<br>• Error resilience |
| 🤖 LLM Integration | • OpenAI Support<br>• Anthropic Support<br>• Google AI Support<br>• Multi-Model Chains | • Model flexibility<br>• Provider choice<br>• Mixed model chains<br>• Optimal performance |
| 🛠️ Development Tools | • Type Hints<br>• Comprehensive Logging<br>• Error Handling<br>• Debug Support | • Code reliability<br>• Easy debugging<br>• Error recovery<br>• Development speed |
| 📊 Variable Management | • Automatic Flow<br>• State Tracking<br>• Context Preservation<br>• Chain Variables | • Data consistency<br>• Context awareness<br>• Clean interfaces<br>• Easy debugging |
| 🔄 Process Control | • Async Support<br>• Rate Limiting<br>• Retry Logic<br>• Error Recovery | • High performance<br>• API compliance<br>• Reliability<br>• Fault tolerance |
| 📝 Prompt Management | • Template Support<br>• Dynamic Insertion<br>• Context Management<br>• Format Control | • Clean prompts<br>• Easy updates<br>• Context control<br>• Format consistency |
| 🔍 Monitoring | • Chain Tracking<br>• Variable Inspection<br>• Error Logging<br>• Performance Metrics | • Easy debugging<br>• State visibility<br>• Issue tracking<br>• Optimization |

## Installation

```bash
pip install ChainComposer
```

> [!TIP]
> While the install command is `pip install ChainComposer`,
> to import modules you should do so like this: `from chain_composer import ChainComposer`.

## Quick Start

This is a simple example of how to use ChainComposer. Here I build 2 layer chain where the AI from the first layer takes the first derivative of a function and the second layer AI takes the second derivative of that function.

Using ChainComposer can be broken down into 4 steps:

1. Define the output models (the structure you want the LLM to output)
2. Create the prompts (the system and human messages as strings)
3. Create the chain layers (the layers of the chain)
4. Run the chain

```python
from dotenv import load_dotenv
import os
import json
from pydantic import BaseModel
from chain_composer import ChainComposer

# Load the API key
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Step 1: Define the output models
class FirstDerivative(BaseModel):
    first_derivative: str

# Here we are telling the LLM for the first layer we want output in the following format:
# {
#     "first_derivative": "<answer>"
# }
    
# Step 2: Define the second layer output model
class SecondDerivative(BaseModel):
    second_derivative: str

# Here we are telling the LLM for the second layer we want output in the following format:
# {
#     "second_derivative": "<answer>"
# }

# Step 3: Create the prompts
# Define the first layer system message
first_derivative_system_message = """
You are a helpful assistant, who takes the first derivative of a function and returns the result in the following format:

{{
    "first_derivative": "<answer>"
}}

Note: You should always return json. Do not include the markdown json format, just return the json.
"""

# Define the second layer system message
second_derivative_system_message = """
You are a helpful assistant, who takes a second derivative and returns the result in the following format:

{{
    "second_derivative": "<answer>"
}}

Note: You should always return json. Do not include the markdown json format, just return the json.
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

# Step 4: Create the chain
# Define the chain with the json parser
# Here we'll be using the json parser, but you can also use pydantic and string parsers
cp = ChainComposer(
    model="gpt-4o-mini",
    api_key=api_key,
)

cp.add_chain_layer( # Add the first layer
    system_prompt=first_derivative_system_message, # The system message for the layer
    human_prompt=human_message, # The human message for the layer
    parser_type="json", # The parser type for the layer
    pydantic_output_model=FirstDerivative, # The output model for the layer
    output_passthrough_key_name="first_derivative_output", # The key name for the output passthrough
).add_chain_layer( # Add the second layer
    system_prompt=second_derivative_system_message, # The system message for the layer
    human_prompt=human_message_2, # The human message for the layer
    parser_type="json", # The parser type for the layer
    pydantic_output_model=SecondDerivative, # The output model for the layer
    output_passthrough_key_name="second_derivative_output", # The key name for the output passthrough
)

# Run the chain by calling the `run()` method and passing in a dictionary of variables.
# Here we start running it by providing the `equation` variable. This will be used in the first and second layers' human prompts.
# The `output_passthrough_key_name` argument we passed in to the `add_chain_layer()` method will be used to 
# insert new variables into this dictionary, thus allowing the flow of outputs into placeholder variables in the prompts.
result = cp.run(
    {
        "equation": "2x^2 + 3x + 2"
    }
)

print(result)

# for a prettier output, you can import `json` and use `json.dumps()`
# print(json.dumps(result, indent=4))
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
