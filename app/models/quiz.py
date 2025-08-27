# backend/app/models/quiz.py

from pydantic import BaseModel
from typing import List, Dict

# --- Schemas para OBTENER un quiz ---
class OptionSchema(BaseModel):
    id: int
    option_text: str
    class Config:
        from_attributes = True

class QuestionSchema(BaseModel):
    id: int
    question_text: str
    options: List[OptionSchema] = []
    class Config:
        from_attributes = True

class QuizSchema(BaseModel):
    module_id: int
    questions: List[QuestionSchema] = []

# --- Schemas para ENVIAR y RECIBIR resultados ---
class QuizSubmission(BaseModel):
    answers: Dict[int, int] # { question_id: option_id }

class AnswerResult(BaseModel):
    question_id: int
    user_option_id: int
    correct_option_id: int
    is_correct: bool

class QuizResultDetailed(BaseModel): # <-- El modelo que faltaba
    score: float
    passed: bool
    total_questions: int
    correct_count: int
    incorrect_count: int
    detailed_results: List[AnswerResult]

class QuizStatus(BaseModel):
    can_attempt: bool
    attempts_made: int
    max_attempts: int = 3