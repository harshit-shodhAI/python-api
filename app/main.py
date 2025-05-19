from typing import Dict, List, Any, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import json
import sys
import os

if os.path.basename(os.getcwd()) == 'app':
    sys.path.append(os.path.dirname(os.getcwd()))
    from grammar_checker import GrammarChecker
    from coherence_analyzer import CoherenceAnalyzer
else:
    from app.grammar_checker import GrammarChecker
    from app.coherence_analyzer import CoherenceAnalyzer

app = FastAPI(
    title="TOEFL Speaking Transcript Analyzer",
    description="API for analyzing TOEFL speaking transcripts and providing feedback",
    version="1.0.0"
)

grammar_checker = GrammarChecker()
coherence_analyzer = CoherenceAnalyzer()

class TranscriptItem(BaseModel):
    topic: str
    paragraph: str

class TranscriptRequest(BaseModel):
    transcripts: List[TranscriptItem]

class ErrorItem(BaseModel):
    start: int
    end: int
    wrong_version: str
    correct_version: str

class AnalysisResult(BaseModel):
    topic: str
    errors: List[ErrorItem]
    grammar_feedback: str
    coherence_feedback: str

class AnalysisResponse(BaseModel):
    results: List[AnalysisResult]

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_transcripts(request: TranscriptRequest) -> Dict[str, Any]:
    results = []
    
    for transcript in request.transcripts:
        errors, grammar_feedback = grammar_checker.check_grammar(transcript.paragraph)
        
        coherence_analysis = coherence_analyzer.analyze_coherence(
            transcript.paragraph, transcript.topic
        )
        
        results.append({
            "topic": transcript.topic,
            "errors": errors,
            "grammar_feedback": grammar_feedback,
            "coherence_feedback": coherence_analysis.get("feedback", "No coherence feedback available.")
        })
    
    return {"results": results}

@app.get("/")
async def root():
    return {
        "name": "TOEFL Speaking Transcript Analyzer",
        "version": "1.0.0",
        "endpoints": {
            "/analyze": "POST - Analyze TOEFL speaking transcripts"
        }
    }

def analyze_transcript_text(topic: str, paragraph: str) -> Dict[str, Any]:
    errors, grammar_feedback = grammar_checker.check_grammar(paragraph)
    coherence_analysis = coherence_analyzer.analyze_coherence(paragraph, topic)
    
    return {
        "topic": topic,
        "errors": errors,
        "grammar_feedback": grammar_feedback,
        "coherence_feedback": coherence_analysis["feedback"]
    }

if __name__ == "__main__":
    import uvicorn
    import argparse
    
    parser = argparse.ArgumentParser(description="TOEFL Speaking Transcript Analyzer")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host to run the server on")
    parser.add_argument("--port", type=int, default=8000, help="Port to run the server on")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    
    args = parser.parse_args()
    
    uvicorn.run("app.main:app", host=args.host, port=args.port, reload=args.reload)
