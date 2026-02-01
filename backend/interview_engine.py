"""
Interview Engine Module
Manages the interview flow with adaptive difficulty and early termination
RULE-BASED (No external AI API required)
"""

from typing import Dict, List, Tuple
import random


class InterviewEngine:
    """Interview engine with adaptive difficulty (offline-safe)"""

    def __init__(self):
        self.difficulty_levels = ['easy', 'medium', 'hard']
        self.current_difficulty = 'easy'
        self.question_count = 0
        self.max_questions = 10
        self.question_types = ['technical', 'conceptual', 'behavioral', 'scenario-based']

    # ------------------------------------------------------------------
    # QUESTION BANK (Skill-aware, difficulty-aware)
    # ------------------------------------------------------------------
    QUESTION_BANK = {
        "easy": {
            "technical": [
                "What is {skill} and where have you used it?",
                "Explain basic features of {skill}."
            ],
            "conceptual": [
                "What problem does {skill} solve?",
                "Explain core concepts of {skill}."
            ],
            "behavioral": [
                "Tell me about a project you enjoyed working on.",
                "How do you approach learning a new technology?"
            ],
            "scenario-based": [
                "How would you debug a simple error in your application?",
                "What steps do you take when your code doesn’t work?"
            ]
        },
        "medium": {
            "technical": [
                "How would you optimize performance in a {skill} project?",
                "Explain common challenges you faced while using {skill}."
            ],
            "conceptual": [
                "Compare {skill} with an alternative technology.",
                "Explain trade-offs involved when using {skill}."
            ],
            "behavioral": [
                "Describe a challenging project and how you handled it.",
                "Tell me about a time you worked under pressure."
            ],
            "scenario-based": [
                "How would you design a scalable web application?",
                "How would you handle a production bug reported by users?"
            ]
        },
        "hard": {
            "technical": [
                "Design a scalable system using {skill} for millions of users.",
                "How would you improve fault tolerance in a {skill} system?"
            ],
            "conceptual": [
                "Explain internal architecture or algorithms behind {skill}.",
                "Discuss limitations of {skill} in large-scale systems."
            ],
            "behavioral": [
                "Tell me about a critical technical decision you made.",
                "How do you balance speed vs quality in deadlines?"
            ],
            "scenario-based": [
                "A production system goes down suddenly. Walk me through your response.",
                "How would you redesign a legacy system for scalability?"
            ]
        }
    }

    # ------------------------------------------------------------------
    # QUESTION GENERATION
    # ------------------------------------------------------------------
    def generate_question(
        self,
        resume_data: Dict,
        jd_data: Dict,
        difficulty: str,
        question_type: str,
        previous_qa: List[Dict] = None
    ) -> Tuple[str, List[str]]:
        """
        Generate interview question without external AI
        """

        resume_skills_dict = resume_data.get("skills", {})
        jd_skills_dict = jd_data.get("required_skills", {})
        resume_skills = []
        for v in resume_skills_dict.values():
            resume_skills.extend(v)

        jd_skills = []
        for v in jd_skills_dict.values():
            jd_skills.extend(v)

        # Pick relevant skill
        combined_skills = list(set(resume_skills + jd_skills))
        skill = random.choice(combined_skills) if combined_skills else "programming"

        # Select question
        templates = self.QUESTION_BANK[difficulty][question_type]
        question_template = random.choice(templates)
        question = question_template.format(skill=skill)

        expected_topics = [skill, question_type, difficulty]

        return question, expected_topics

    # ------------------------------------------------------------------
    # ADAPTIVE DIFFICULTY
    # ------------------------------------------------------------------
    def adjust_difficulty(self, recent_scores: List[float]) -> str:
        if not recent_scores:
            return self.current_difficulty

        avg_score = sum(recent_scores) / len(recent_scores)

        if avg_score > 75:
            if self.current_difficulty == "easy":
                self.current_difficulty = "medium"
            elif self.current_difficulty == "medium":
                self.current_difficulty = "hard"

        elif avg_score < 40:
            if self.current_difficulty == "hard":
                self.current_difficulty = "medium"
            elif self.current_difficulty == "medium":
                self.current_difficulty = "easy"

        return self.current_difficulty

    # ------------------------------------------------------------------
    # EARLY TERMINATION
    # ------------------------------------------------------------------
    def should_terminate_early(self, recent_scores: List[float]) -> bool:
        if len(recent_scores) < 3:
            return False

        last_three = recent_scores[-3:]
        avg_last_three = sum(last_three) / 3

        return avg_last_three < 30

    # ------------------------------------------------------------------
    # QUESTION TYPE ROTATION
    # ------------------------------------------------------------------
    def get_next_question_type(self) -> str:
        return self.question_types[self.question_count % len(self.question_types)]

    # ------------------------------------------------------------------
    # MAIN INTERVIEW STEP
    # ------------------------------------------------------------------
    def conduct_interview(self, resume_data: Dict, jd_data: Dict) -> Dict:
        question_type = self.get_next_question_type()

        question, expected_topics = self.generate_question(
            resume_data,
            jd_data,
            self.current_difficulty,
            question_type
        )

        self.question_count += 1

        return {
            "question_number": self.question_count,
            "question": question,
            "expected_topics": expected_topics,
            "difficulty": self.current_difficulty,
            "question_type": question_type,
            "max_questions": self.max_questions,
            "time_limit": 60
        }

    def reset(self):
        self.current_difficulty = "easy"
        self.question_count = 0
