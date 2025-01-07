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