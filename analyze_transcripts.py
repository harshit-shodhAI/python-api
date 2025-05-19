import json
import sys
import argparse
from typing import Dict, List, Any
import os

app_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app')
if app_dir not in sys.path:
    sys.path.append(app_dir)

from app.grammar_checker import GrammarChecker
from app.coherence_analyzer import CoherenceAnalyzer
from app.llm_service import LLMService

if not os.getenv("OPENAI_API_KEY"):
    print("Warning: OPENAI_API_KEY environment variable is not set.")
    print("Please set it using: export OPENAI_API_KEY=your_api_key_here")
    print("Or create a .env file in the project root with OPENAI_API_KEY=your_api_key_here")

def analyze_transcript(topic: str, paragraph: str) -> Dict[str, Any]:
    grammar_checker = GrammarChecker()
    coherence_analyzer = CoherenceAnalyzer()
    
    errors, grammar_feedback = grammar_checker.check_grammar(paragraph)
    
    coherence_analysis = coherence_analyzer.analyze_coherence(paragraph, topic)
    
    return {
        "topic": topic,
        "errors": errors,
        "grammar_feedback": grammar_feedback,
        "coherence_feedback": coherence_analysis.get("feedback", "No coherence feedback available.")
    }

def main():
    parser = argparse.ArgumentParser(description="Analyze TOEFL speaking transcripts")
    parser.add_argument("--input", "-i", type=str, help="Input JSON file with transcripts")
    parser.add_argument("--output", "-o", type=str, help="Output JSON file for results")
    parser.add_argument("--pretty", "-p", action="store_true", help="Pretty print JSON output")
    
    args = parser.parse_args()
    
    if args.input:
        with open(args.input, 'r') as f:
            transcripts = json.load(f)
    else:
        print("Reading from stdin... (Ctrl+D to end)")
        transcripts = json.load(sys.stdin)
    
    results = []
    for transcript in transcripts:
        result = analyze_transcript(transcript["topic"], transcript["paragraph"])
        results.append(result)
    
    output = {"results": results}
    indent = 2 if args.pretty else None
    output_json = json.dumps(output, indent=indent)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output_json)
        print(f"Results written to {args.output}")
    else:
        print(output_json)

if __name__ == "__main__":
    main()
