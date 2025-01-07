import os
import json
from dotenv import load_dotenv
from chain_composer import ChainComposer

from models import (
    MethodExtractionOutput,
    SentenceAnalysisOutput,
    ClassificationOutput,
)
from prompts import (
    method_extraction_system_message,
    sentence_analysis_system_message,
    classification_system_message,
    human_message_prompt,
    method_json_format,
    sentence_analysis_json_format,
    classification_json_format,
)
from abstract import abstract
from taxonomy import TAXONOMY_AS_STRING

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

taxonomy = json.loads(TAXONOMY_AS_STRING)
categories = list(taxonomy.keys())

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

result =cp.run(
    {
        "abstract": abstract,
        "categories": categories,
        "method_json_format": method_json_format,
        "sentence_analysis_json_format": sentence_analysis_json_format,
        "classification_json_format": classification_json_format,
    }
)

print(f"Method Extraction Output:\n{json.dumps(result['method_json_output'], indent=4)}\n")
print(f"Sentence Analysis Output:\n{json.dumps(result['sentence_analysis_output'], indent=4)}\n")
print(f"Classification Output:\n{json.dumps(result['classification_output'], indent=4)}\n")