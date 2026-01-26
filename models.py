from pydantic import BaseModel
from typing import List

class Question(BaseModel):
    id: str
    topic: str
    level: str
    question: str
    options: List[str]
    correct_answer: str
    type: str = "MCQ"
