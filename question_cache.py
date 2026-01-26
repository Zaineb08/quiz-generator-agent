"""
Question Cache Manager
Prevents repetition of questions within a quiz session and across sessions
"""

import json
import os
import hashlib
import random
from typing import List, Optional
from models import Question


class QuestionCache:
    """Manages a cache of generated questions to prevent repetition"""

    def save_user_choice(self, question: Question, user_choice: str):
        """Ajoute le choix de l'utilisateur à la question correspondante dans le cache"""
        question_hash = self.get_question_hash(question)
        for q in self.cache["questions"]:
            if q.get("hash") == question_hash:
                q["user_choice"] = user_choice
                self.save()
                return
        # Si la question n'est pas encore dans le cache, on l'ajoute avec le choix
        question_data = {
            "hash": question_hash,
            "id": question.id,
            "topic": question.topic,
            "level": question.level,
            "question": question.question,
            "options": question.options,
            "correct_answer": question.correct_answer,
            "type": question.type,
            "user_choice": user_choice
        }
        self.cache["questions"].append(question_data)
        self.save()

    FILE = "questions_cache.json"
    
    def __init__(self):
        self.cache = self.load()
        self.session_hashes = set()  # Track this session in memory
    
    def load(self):
        """Load question cache from file"""
        if os.path.exists(self.FILE):
            with open(self.FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"questions": [], "session_asked": []}
    
    def save(self):
        """Save question cache to file"""
        with open(self.FILE, "w", encoding="utf-8") as f:
            json.dump(self.cache, f, indent=2, ensure_ascii=False)
    
    def get_question_hash(self, question: Question) -> str:
        """Generate a hash for a question to detect duplicates"""
        # Use just the question text for hashing to catch similar variations
        question_text = question.question.strip().lower()
        return hashlib.md5(question_text.encode()).hexdigest()
    
    def question_exists_globally(self, question: Question) -> bool:
        """Check if question already exists in global cache"""
        question_hash = self.get_question_hash(question)
        for cached_q in self.cache["questions"]:
            if cached_q.get("hash") == question_hash:
                return True
        return False
    
    def get_cached_question(self, topic: str, level: str) -> Optional[Question]:
        """Get a random cached question for topic/level that hasn't been asked this session"""
        # Filter questions matching topic and level
        matching_questions = [
            q for q in self.cache["questions"]
            if q.get("topic") == topic and q.get("level") == level
        ]
        
        if not matching_questions:
            return None
        
        # Shuffle to get random questions
        random.shuffle(matching_questions)
        
        # Return first one that hasn't been asked this session
        for q_data in matching_questions:
            q = Question(**{k: q_data[k] for k in ["id", "topic", "level", "question", "options", "correct_answer", "type"]})
            if not self.was_asked_in_session(q):
                return q
        
        # All matching cached questions have been asked this session
        return None
    
    def was_asked_in_session(self, question: Question) -> bool:
        """Check if question was asked in current session (fast in-memory check)"""
        question_hash = self.get_question_hash(question)
        return question_hash in self.session_hashes
    
    def add_question(self, question: Question):
        """Add a new question to the global cache"""
        if not self.question_exists_globally(question):
            question_data = {
                "hash": self.get_question_hash(question),
                "id": question.id,
                "topic": question.topic,
                "level": question.level,
                "question": question.question,
                "options": question.options,
                "correct_answer": question.correct_answer,
                "type": question.type
            }
            self.cache["questions"].append(question_data)
            self.save()
    
    def start_session(self):
        """Reset session tracking for new quiz"""
        self.session_hashes = set()  # Clear in-memory set
    
    def mark_as_asked(self, question: Question):
        """Mark a question as asked in this session"""
        question_hash = self.get_question_hash(question)
        self.session_hashes.add(question_hash)  # Add to in-memory set
    
    def get_stats(self) -> dict:
        """Get cache statistics"""
        return {
            "total_cached": len(self.cache["questions"]),
            "asked_this_session": len(self.session_hashes),
            "unique_topics": len(set(q.get("topic") for q in self.cache["questions"]))
        }
    
    def clear_cache(self):
        """Clear all cached questions (use with caution)"""
        self.cache = {"questions": [], "session_asked": []}
        self.session_hashes = set()
        self.save()
        print("Question cache cleared!")


if __name__ == "__main__":
    # Test the cache
    cache = QuestionCache()
    
    # Display stats
    stats = cache.get_stats()
    print("Question Cache Stats:")
    print(f"  Total cached questions: {stats['total_cached']}")
    print(f"  Asked this session: {stats['asked_this_session']}")
    print(f"  Unique topics: {stats['unique_topics']}")
