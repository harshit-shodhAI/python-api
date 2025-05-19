import re
from typing import Dict, List, Any
from app.llm_service import LLMService

class CoherenceAnalyzer:
    def __init__(self):
        self.llm_service = LLMService()
    
    def analyze_coherence(self, text: str, topic: str) -> Dict[str, Any]:
        try:
            result = self.llm_service.analyze_coherence(text, topic)
            
            coherence_feedback = result.get("coherence_feedback", "No coherence feedback available.")
            coherence_score = result.get("score", 0.5)
            
            try:
                coherence_score = float(coherence_score)
                coherence_score = max(0.0, min(1.0, coherence_score))
            except (ValueError, TypeError):
                coherence_score = 0.5
            
            return {
                "feedback": coherence_feedback,
                "score": coherence_score
            }
            
        except Exception as e:
            print(f"Error in coherence analysis: {str(e)}")
            return {
                "feedback": "Unable to analyze coherence due to an error.",
                "score": 0.5
            }
    
################# EXTRA FUNCTIONS #################
    def _count_transition_words(self, text: str) -> int:
        count = 0
        text_lower = text.lower()
        
        for word in self.transition_words:
            count += text_lower.count(word)
        
        return count
    
    def _count_filler_phrases(self, text: str) -> int:
        count = 0
        text_lower = text.lower()
        
        for phrase in self.filler_phrases:
            if len(phrase.split()) == 1:
                pattern = r'\b' + re.escape(phrase) + r'\b'
                count += len(re.findall(pattern, text_lower))
            else:
                count += text_lower.count(phrase)
        
        return count
    
    def _calculate_topic_relevance(self, text: str, topic: str) -> float:
        stop_words = set(['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'with', 'by', 'about', 'as', 'of', 'is', 'are', 'was', 'were'])
        
        topic_words = set(word.lower() for word in re.findall(r'\b[a-zA-Z]{3,}\b', topic) if word.lower() not in stop_words)
        text_words = set(word.lower() for word in re.findall(r'\b[a-zA-Z]{3,}\b', text) if word.lower() not in stop_words)
        
        if not topic_words:
            return 0.5
        
        overlap = len(topic_words.intersection(text_words))
        relevance = min(1.0, overlap / max(1, len(topic_words)))
        
        # boost score if key topic words appear multiple times in text
        topic_key_words = [word for word in topic_words if len(word) > 3]
        if topic_key_words:
            repetition_boost = 0
            text_lower = text.lower()
            for word in topic_key_words:
                count = len(re.findall(r'\b' + re.escape(word) + r'\b', text_lower))
                if count > 1:
                    repetition_boost += min(0.2, 0.05 * count)  # cap the boost
            
            relevance = min(1.0, relevance + repetition_boost)
        
        return relevance
    
    def _analyze_sentence_flow(self, sentences: List[str]) -> float:
        if len(sentences) <= 1:
            return 1.0
        
        lengths = [len(s.split()) for s in sentences]
        length_diffs = [abs(lengths[i] - lengths[i-1]) for i in range(1, len(lengths))]
        avg_length_diff = sum(length_diffs) / len(length_diffs)
        normalized_length_diff = max(0, 1 - (avg_length_diff / 10))  # normalize to 0-1
        
        overlap_scores = []
        for i in range(1, len(sentences)):
            prev_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', sentences[i-1].lower()))
            curr_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', sentences[i].lower()))
            
            if not prev_words or not curr_words:
                overlap_scores.append(0.5)  # default middle value
                continue
                
            overlap = len(prev_words.intersection(curr_words))
            overlap_scores.append(min(1.0, overlap / min(len(prev_words), len(curr_words))))
        
        avg_overlap = sum(overlap_scores) / max(1, len(overlap_scores))
        
        # check for transition words at the beginning of sentences
        transition_scores = []
        for s in sentences[1:]:
            s_lower = s.lower().strip()
            has_transition = any(s_lower.startswith(word) for word in self.transition_words)
            transition_scores.append(1.0 if has_transition else 0.0)
        
        avg_transition = sum(transition_scores) / max(1, len(transition_scores))
        
        # combine metrics (weighted)
        flow_score = (normalized_length_diff * 0.3) + (avg_overlap * 0.5) + (avg_transition * 0.2)
        
        return max(0.0, min(1.0, flow_score))
    
    def _analyze_repetition(self, text: str) -> float:
        # tokenize and clean words
        words = re.findall(r'\b[a-z]{3,}\b', text.lower())
        
        if not words:
            return 1.0
        
        # count word frequencies
        word_counts = {}
        for word in words:
            if word not in ["the", "and", "that", "this", "with", "from"]:  # skip common words
                word_counts[word] = word_counts.get(word, 0) + 1
        
        # calculate repetition score
        if not word_counts:
            return 1.0
        
        max_count = max(word_counts.values())
        unique_ratio = len(word_counts) / len(words)
        
        # penalize for high repetition
        repetition_score = (unique_ratio * 0.7) + (1 - (max_count / len(words)) * 0.3)
        
        return max(0.0, min(1.0, repetition_score))
    
    def _calculate_coherence_score(self, metrics: Dict[str, Any]) -> float:
        # weights for different metrics
        weights = {
            "transition_word_count": 0.2,
            "filler_phrase_count": -0.15,  # negative weight
            "topic_relevance": 0.25,
            "sentence_flow": 0.25,
            "repetition": 0.15
        }
        
        # normalize transition word count
        sentence_count = metrics["sentence_count"]
        normalized_transition = min(1.0, metrics["transition_word_count"] / max(1, sentence_count - 1))
        
        # normalize filler phrase count (inverse relationship)
        normalized_filler = max(0.0, 1.0 - (metrics["filler_phrase_count"] / max(1, sentence_count * 2)))
        
        # calculate weighted score
        score = (
            normalized_transition * weights["transition_word_count"] +
            normalized_filler * weights["filler_phrase_count"] +
            metrics["topic_relevance"] * weights["topic_relevance"] +
            metrics["sentence_flow"] * weights["sentence_flow"] +
            metrics["repetition"] * weights["repetition"]
        )
        
        # ensure score is between 0 and 1
        return max(0.0, min(1.0, score))
    
    def _generate_coherence_feedback(self, metrics: Dict[str, Any], score: float) -> str:
        feedback_parts = []
        
        # overall assessment
        if score >= 0.8:
            feedback_parts.append("The response demonstrates excellent coherence and flow. Ideas are well-connected and logically organized.")
        elif score >= 0.6:
            feedback_parts.append("The response shows good coherence overall. The ideas generally flow well, though there are some areas for improvement.")
        elif score >= 0.4:
            feedback_parts.append("The response has moderate coherence. While some ideas connect logically, there are noticeable issues with flow and organization.")
        else:
            feedback_parts.append("The response lacks coherence. Ideas appear disconnected, and the overall organization needs significant improvement.")
        
        # specific feedback based on metrics
        if metrics["transition_word_count"] / max(1, metrics["sentence_count"]) < 0.3:
            feedback_parts.append("Consider using more transition words/phrases (like 'however', 'therefore', 'in addition') to improve the flow between ideas.")
        
        if metrics["filler_phrase_count"] / max(1, metrics["sentence_count"]) > 0.5:
            feedback_parts.append("Reduce the use of filler words and phrases (like 'um', 'uh', 'like', 'you know') to make your response more concise and clear.")
        
        if metrics["topic_relevance"] < 0.5:
            feedback_parts.append("Try to stay more focused on the main topic. Some parts of your response seem to drift away from the central theme.")
        
        if metrics["sentence_flow"] < 0.5:
            feedback_parts.append("Work on creating smoother transitions between sentences. Some sentences seem disconnected from those before or after them.")
        
        if metrics["repetition"] < 0.6:
            feedback_parts.append("Avoid repeating the same words or phrases too frequently. Using synonyms and varied expressions will make your response more engaging.")
        
        if metrics["avg_sentence_length"] > 25:
            feedback_parts.append("Consider breaking up some longer sentences to improve clarity and readability.")
        elif metrics["avg_sentence_length"] < 8:
            feedback_parts.append("Try combining some short sentences to create more complex and sophisticated sentence structures.")
        
        return "\n".join(feedback_parts)
