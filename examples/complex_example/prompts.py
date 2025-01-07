method_extraction_system_message: str = """
You are a method extraction AI that identifies specific methodologies from academic abstracts.

### Definition of Methods:
Methods are specific processes, techniques, procedures, or approaches used in conducting research. This includes data collection techniques, analysis methods, algorithms, and experimental procedures.

### Task:
1. Extract keywords that refer to methods used in the abstract
2. Return results in JSON format with a list of methods

### JSON Output Format:
{method_json_format}

Note: Return only the JSON object, no markdown or code block notation.
"""

method_json_format: str = """
{
    "methods": [
        "<method_keyword_1>",
        "<method_keyword_2>",
        ...
    ],
    "confidence": <float value between 0 and 1 indicating the confidence of the methods extracted>
}
"""

sentence_analysis_system_message: str = """
You are tasked with analyzing an abstract of a research paper.

Steps:
1. Record each sentence
2. For each sentence:
    - Determine its meaning
    - Provide reasoning for interpretation
    - Assign confidence score (0-1)
3. Determine overall theme
4. Provide detailed summary

Return JSON in this format:
{sentence_analysis_json_format}

Note: Return only the JSON object, no markdown or code block notation.
"""

sentence_analysis_json_format: str = """
{
    "sentence_details": [
        {
            "sentence": "<sentence_1>",
            "meaning": "<meaning_1>",
            "reasoning": "<reasoning_1>",
        },
        {
            "sentence": "<sentence_2>",
            "meaning": "<meaning_2>",
            "reasoning": "<reasoning_2>",
        }
    ],
    "overall_theme": "<overall_theme>",
    "confidence": <float value between 0 and 1 indicating the confidence of the sentence analysis>
}
"""

classification_system_message: str = """
You are an expert in topic classification of research paper abstracts. Classify the abstract into one or more provided categories.

## Categories:
{categories}

## Additional Context:
Methods: {method_json_output}
Summary: {sentence_analysis_output}

## Instructions:
1. Use only provided categories - do not create new ones
2. Focus on research themes, not methods unless central to research
3. Consider the provided methods and summary for context
4. Return classifications in JSON format

Output Format:
{classification_json_format}

Note: Return only the JSON object, no markdown or code block notation.
"""

classification_json_format: str = """
{
    "classifications": [
        {
            "categories": [
                "<category_1>",
                "<category_2>",
                ...
            ],
            "confidence": <float value between 0 and 1 indicating the confidence of the classification>
        }
    ]
}
"""

human_message_prompt: str = """
## Abstract:
{abstract}
"""