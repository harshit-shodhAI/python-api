from typing import Dict, List, Any, Tuple
import re
from app.utils import merge_overlapping_errors
from app.llm_service import LLMService

class GrammarChecker:
    def __init__(self):
        self.llm_service = LLMService()
    
    def check_grammar(self, text: str) -> Tuple[List[Dict[str, Any]], str]:
        try:
            result = self.llm_service.analyze_grammar(text)
            
            errors = result.get("errors", [])
            grammar_feedback = result.get("grammar_feedback", "No grammar feedback available.")
            
            for error in errors:
                if "start" not in error or "end" not in error or \
                   "wrong_version" not in error or "correct_version" not in error:
                    continue
                
                try:
                    error["start"] = int(error["start"])
                    error["end"] = int(error["end"])
                except (ValueError, TypeError):
                    continue
            
            merged_errors = merge_overlapping_errors(errors)
            
            return merged_errors, grammar_feedback
            
        except Exception as e:
            print(f"Error in grammar analysis: {str(e)}")
            return [], "Unable to analyze grammar due to an error."
    
################# EXTRA FUNCTIONS #################
    def _check_plural_singular_agreement(self, text: str) -> List[Dict[str, Any]]:
        errors = []
        
        patterns = [
            (r'\b(a|an|the|this|that|each|every|one)\s+([a-z]+)\s+(are|were|have)\b', 
             lambda m: m.group(1) + " " + m.group(2) + " " + 
                      ("is" if m.group(3) == "are" else "was" if m.group(3) == "were" else "has")),
            
            # plural subject with singular verb
            (r'\b(these|those|many|several|few|two|three|four|five)\s+([a-z]+s)\s+(is|was|has)\b',
             lambda m: m.group(1) + " " + m.group(2) + " " + 
                      ("are" if m.group(3) == "is" else "were" if m.group(3) == "was" else "have")),
            
            # incorrect plural forms
            (r'\b(one|a|an|each|every)\s+([a-z]+s)\b',
             lambda m: m.group(1) + " " + m.group(2)[:-1]),
            
            # incorrect singular forms for countable nouns
            (r'\b(many|several|few|two|three|four|five)\s+([a-z]+)\b',
             lambda m: m.group(1) + " " + m.group(2) + "s" if not m.group(2).endswith("s") else m.group(0))
        ]
        
        for pattern, replacement in patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                start, end = match.span()
                if callable(replacement):
                    correction = replacement(match)
                else:
                    correction = replacement
                
                errors.append({
                    "start": start,
                    "end": end,
                    "wrong_version": text[start:end],
                    "correct_version": correction
                })
        
        return errors
    
    def _check_article_usage(self, text: str) -> List[Dict[str, Any]]:
        errors = []
        patterns = [
            (r'\b(go to|at|in)\s+([a-z]+)(\s+|\.|,|;|:)',
             lambda m: m.group(1) + " the " + m.group(2) + m.group(3) 
             if m.group(2) in ["university", "hospital", "school", "airport", "mall", "office", "bank", "store"] 
             else m.group(0)),
            
            # Incorrect article usage with vowel sounds
            (r'\ba\s+([aeiou][a-z]*)\b', lambda m: "an " + m.group(1)),
            
            # Incorrect article usage with consonant sounds
            (r'\ban\s+([bcdfghjklmnpqrstvwxyz][a-z]*)\b', lambda m: "a " + m.group(1)),
            
            # Unnecessary articles with uncountable nouns
            (r'\b(a|an)\s+(information|advice|knowledge|furniture|news|equipment|traffic|weather|homework|luggage|money)\b',
             lambda m: m.group(2))
        ]
        
        for pattern, replacement in patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                start, end = match.span()
                if callable(replacement):
                    correction = replacement(match)
                else:
                    correction = replacement
                
                # Only add error if there's an actual change
                if correction.lower() != text[start:end].lower():
                    errors.append({
                        "start": start,
                        "end": end,
                        "wrong_version": text[start:end],
                        "correct_version": correction
                    })
        
        return errors
    
    def _check_preposition_errors(self, text: str) -> List[Dict[str, Any]]:
        errors = []
        
        # Common preposition error patterns
        preposition_rules = {
            r'\barrived\s+to\b': "arrived at",
            r'\bdifferent\s+than\b': "different from",
            r'\bin\s+([0-9]+|a|the)\s+(morning|afternoon|evening|night)\b': 
                lambda m: "in the " + m.group(2) if m.group(1) in ["a", "the"] else "in the " + m.group(1) + " " + m.group(2),
            r'\bmarried\s+with\b': "married to",
            r'\bcomposed\s+of\s+by\b': "composed of",
            r'\bconsist\s+in\b': "consist of",
            r'\bdepend\s+of\b': "depend on",
            r'\binterested\s+about\b': "interested in",
            r'\blistening\s+music\b': "listening to music",
            r'\bpay\s+attention\s+in\b': "pay attention to",
            r'\bsimilar\s+like\b': "similar to",
            r'\bwait\s+you\b': "wait for you",
            r'\bon\s+weekend\b': "on the weekend",
            r'\bin\s+television\b': "on television",
            r'\bon\s+last\s+(month|year|week)\b': lambda m: "last " + m.group(1),
            r'\bin\s+next\s+(month|year|week)\b': lambda m: "next " + m.group(1)
        }
        
        for pattern, replacement in preposition_rules.items():
            for match in re.finditer(pattern, text, re.IGNORECASE):
                start, end = match.span()
                if callable(replacement):
                    correction = replacement(match)
                else:
                    correction = replacement
                
                errors.append({
                    "start": start,
                    "end": end,
                    "wrong_version": text[start:end],
                    "correct_version": correction
                })
        
        return errors
        
    def _generate_grammar_feedback(self, text: str, errors: List[Dict[str, Any]]) -> str:
        if not errors:
            return "The grammar in this response is excellent. No significant errors were found."
        
        # Categorize errors
        error_categories = {
            "subject-verb agreement": 0,
            "article usage": 0,
            "verb tense": 0,
            "prepositions": 0,
            "word choice": 0,
            "punctuation": 0,
            "sentence structure": 0,
            "other": 0
        }
        
        for error in errors:
            wrong = error["wrong_version"].lower()
            correct = error["correct_version"].lower()
            
            # Categorize based on error patterns
            if any(word in wrong for word in ["is", "are", "am", "was", "were"]):
                error_categories["subject-verb agreement"] += 1
            elif any(word in wrong for word in ["a", "an", "the"]):
                error_categories["article usage"] += 1
            elif any(suffix in wrong for suffix in ["ed", "ing", "s", "es"]):
                error_categories["verb tense"] += 1
            elif any(word in wrong for word in ["in", "on", "at", "to", "for", "with", "by"]):
                error_categories["prepositions"] += 1
            elif "," in wrong or "." in wrong or ";" in wrong:
                error_categories["punctuation"] += 1
            else:
                error_categories["word choice"] += 1
        
        # Generate feedback based on error categories
        feedback_parts = []
        
        # Overall assessment
        error_count = len(errors)
        if error_count <= 2:
            feedback_parts.append("The grammar in this response is generally good with only a few minor errors.")
        elif error_count <= 5:
            feedback_parts.append("The grammar in this response is acceptable but has several errors that could be improved.")
        else:
            feedback_parts.append("The grammar in this response needs significant improvement as there are multiple errors.")
        
        # Add specific feedback for the most common error categories
        sorted_categories = sorted(error_categories.items(), key=lambda x: x[1], reverse=True)
        major_issues = [cat for cat, count in sorted_categories if count > 0][:3]
        
        if major_issues:
            feedback_parts.append("The main areas for improvement are:")
            
            for issue in major_issues:
                if issue == "subject-verb agreement":
                    feedback_parts.append("- Subject-verb agreement: Make sure the verb form matches the subject (singular/plural).")
                elif issue == "article usage":
                    feedback_parts.append("- Article usage: Pay attention to when to use 'a', 'an', or 'the'.")
                elif issue == "verb tense":
                    feedback_parts.append("- Verb tense: Maintain consistent verb tenses throughout your response.")
                elif issue == "prepositions":
                    feedback_parts.append("- Preposition usage: Review the correct prepositions to use with specific words.")
                elif issue == "word choice":
                    feedback_parts.append("- Word choice: Some words are used incorrectly or inappropriately in context.")
                elif issue == "punctuation":
                    feedback_parts.append("- Punctuation: Pay attention to proper punctuation usage.")
                elif issue == "sentence structure":
                    feedback_parts.append("- Sentence structure: Some sentences are structured incorrectly.")
        
        return "\n".join(feedback_parts)
