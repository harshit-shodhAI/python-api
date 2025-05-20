import os
import json
from typing import Dict, List, Any, Optional
import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

class LLMService:
    def __init__(self, model: Optional[str] = None):
        self.model = model or DEFAULT_MODEL
        self.api_key_missing = False
        
        if not openai.api_key:
            self.api_key_missing = True
            print("WARNING: OpenAI API key not found. The service will return mock responses.")
    
    def analyze_grammar(self, text: str) -> Dict[str, Any]:
        if self.api_key_missing:
            # Return a mock response if API key is missing
            return {
                "errors": [],
                "grammar_feedback": "API key missing. Please set the OPENAI_API_KEY environment variable."
            }
            
        prompt = f"""
        You are a TOEFL grammar expert. Analyze the following text for grammatical errors:

        TEXT: {text}

        Identify all grammatical errors in the text. For each error, provide:
        1. The start and end index of the error in the text
        2. The incorrect text
        3. The corrected version
        4. A brief explanation of the error

        IMPORTANT: Your response must be a valid JSON object with the following structure and nothing else:
        {{
            "errors": [
                {{
                    "start": <start_index>,
                    "end": <end_index>,
                    "wrong_version": "<incorrect_text>",
                    "correct_version": "<corrected_text>",
                    "explanation": "<brief_explanation>"
                }}
            ],
            "grammar_feedback": "<overall_feedback_on_grammar>"
        }}

        Ensure that the indices are correct by counting characters from the beginning of the text (0-indexed).
        Do not include any text outside the JSON structure. Your entire response should be parseable as JSON.
        """
        
        response = openai.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a TOEFL grammar expert that analyzes text and returns JSON. Your response MUST be valid JSON and nothing else."},
                {"role": "user", "content": prompt}
            ]
        )
        
        try:
            result = json.loads(response.choices[0].message.content)
            return result
        except json.JSONDecodeError:
            return {
                "errors": [],
                "grammar_feedback": "Unable to analyze grammar due to an error in processing the response."
            }
    
    def analyze_coherence(self, text: str, topic: str) -> Dict[str, Any]:
        if self.api_key_missing:
            # Return a mock response if API key is missing
            return {
                "coherence_feedback": "API key missing. Please set the OPENAI_API_KEY environment variable.",
                "score": 0.5
            }
            
        prompt = f"""
        You are a TOEFL coherence expert. Analyze the following text for coherence and flow:

        TOPIC: {topic}
        TEXT: {text}

        Evaluate how well the text flows, whether ideas connect logically, and if the response stays on topic.
        Consider:
        1. Logical flow between sentences and paragraphs
        2. Use of transition words and phrases
        3. Overall organization and structure
        4. Relevance to the given topic
        5. Repetition and redundancy

        IMPORTANT: Your response must be a valid JSON object with the following structure and nothing else:
        {{
            "coherence_feedback": "<detailed_feedback_on_coherence>",
            "score": <coherence_score_between_0_and_1>
        }}

        The coherence_feedback should be detailed enough to help the student improve their writing.
        Do not include any text outside the JSON structure. Your entire response should be parseable as JSON.
        """
        
        response = openai.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a TOEFL coherence expert that analyzes text and returns JSON. Your response MUST be valid JSON and nothing else."},
                {"role": "user", "content": prompt}
            ]
        )
        
        try:
            result = json.loads(response.choices[0].message.content)
            return result
        except json.JSONDecodeError:
            return {
                "coherence_feedback": "Unable to analyze coherence due to an error in processing the response.",
                "score": 0.5
            }
