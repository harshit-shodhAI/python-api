# TOEFL Teaching App - Report Generation Tool

This backend service analyzes student speaking transcripts and generates detailed reports with:

1. Highlighted errors in the transcript (with start and end indices)
2. Grammar feedback
3. Coherence analysis

## Features

- Identifies grammatical errors in student transcripts
- Provides specific corrections for each error
- Analyzes the overall coherence and flow of the response
- Returns structured JSON output for easy integration with frontend

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Set up environment variables in .env file
    ```
    OPENAI_API_KEY=your_api_key_here
    ```

3. Run the application:
   ```
   uvicorn app.main:app --reload
   ```

## API Usage

POST `http://127.0.0.1:8000/analyze` endpoint accepts JSON input with student transcripts and returns detailed analysis.

Example request:
```json
{
  "transcripts": [
    {
      "topic": "The Impact of Smartphones on Daily Life",
      "paragraph": "Smartphones have significantly transformed daily life..."
    }
  ]
}
```

Example response:
```json
{
  "results": [
    {
      "topic": "The Impact of Smartphones on Daily Life",
      "errors": [
        {
          "start": 10,
          "end": 15,
          "wrong_version": "have",
          "correct_version": "has"
        }
      ],
      "grammar_feedback": "Overall good grammar with minor subject-verb agreement issues.",
      "coherence_feedback": "The response is well-structured and maintains focus on the topic."
    }
  ]
}
```

OR 

Run for command line testing:
```python analyze_transcripts.py --input sample_input.json --pretty```