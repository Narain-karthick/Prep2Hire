"""
Scoring Engine Module
Evaluates interview answers using rule-based, explainable scoring
(No external AI API required)
"""

import re
from typing import Dict, List


class ScoringEngine:
    """Scores candidate answers on multiple metrics"""

    def __init__(self):
        # Weight distribution for final score
        self.weights = {
            'accuracy': 0.30,
            'clarity': 0.20,
            'depth': 0.25,
            'relevance': 0.15,
            'time_efficiency': 0.10
        }

    # ------------------------------------------------------------------
    # MAIN SCORING FUNCTION
    # ------------------------------------------------------------------
    def score_answer(
        self,
        question: str,
        answer: str,
        expected_topics: List[str],
        time_taken: int,
        max_time: int = 60
    ) -> Dict:
        """
        Score an interview answer on multiple metrics
        """

        if not answer or len(answer.strip()) < 10:
            return {
                'accuracy': 0,
                'clarity': 0,
                'depth': 0,
                'relevance': 0,
                'time_efficiency': 0,
                'overall': 0,
                'feedback': "Answer is too short or empty."
            }

        answer_lower = answer.lower()
        word_count = len(answer.split())

        # ---------------- Accuracy ----------------
        topics_covered = sum(
            1 for topic in expected_topics if topic.lower() in answer_lower
        )
        accuracy = min(
            100,
            (topics_covered / max(len(expected_topics), 1)) * 100
        )

        # ---------------- Clarity ----------------
        structure_markers = [
            'first', 'second', 'then', 'because', 'therefore',
            'however', 'for example', 'in conclusion'
        ]
        has_structure = any(m in answer_lower for m in structure_markers)
        clarity = min(
            100,
            (word_count / 50) * 50 + (50 if has_structure else 0)
        )

        # ---------------- Depth ----------------
        technical_terms = len(
            re.findall(r'\b[A-Z]{2,}\b|\b\w+\(\)', answer)
        )
        depth = min(
            100,
            (word_count / 100) * 70 + technical_terms * 5
        )

        # ---------------- Relevance ----------------
        question_words = set(re.findall(r'\b\w{4,}\b', question.lower()))
        answer_words = set(re.findall(r'\b\w{4,}\b', answer_lower))
        overlap = len(question_words.intersection(answer_words))
        relevance = min(
            100,
            (overlap / max(len(question_words), 1)) * 100
        )

        # ---------------- Time Efficiency ----------------
        time_efficiency = self._calculate_time_score(time_taken, max_time)

        # ---------------- Overall Score ----------------
        overall = (
            accuracy * self.weights['accuracy'] +
            clarity * self.weights['clarity'] +
            depth * self.weights['depth'] +
            relevance * self.weights['relevance'] +
            time_efficiency * self.weights['time_efficiency']
        )

        feedback = f"Covered {topics_covered}/{len(expected_topics)} expected topics with a {'clear' if has_structure else 'basic'} explanation."

        return {
            'accuracy': round(accuracy, 2),
            'clarity': round(clarity, 2),
            'depth': round(depth, 2),
            'relevance': round(relevance, 2),
            'time_efficiency': round(time_efficiency, 2),
            'overall': round(overall, 2),
            'feedback': feedback
        }

    # ------------------------------------------------------------------
    # TIME EFFICIENCY LOGIC
    # ------------------------------------------------------------------
    def _calculate_time_score(self, time_taken: int, max_time: int) -> int:
        if time_taken <= 0:
            return 0

        optimal_min = max_time * 0.6
        optimal_max = max_time * 0.8

        if optimal_min <= time_taken <= optimal_max:
            return 100
        elif time_taken < optimal_min:
            return int((time_taken / optimal_min) * 100)
        elif time_taken <= max_time:
            penalty = (time_taken - optimal_max) / (max_time - optimal_max)
            return int(100 - (penalty * 20))
        else:
            return max(0, 50 - int((time_taken - max_time) / 10))

    # ------------------------------------------------------------------
    # FINAL INTERVIEW SCORE
    # ------------------------------------------------------------------
    def calculate_final_score(self, all_scores: List[Dict]) -> Dict:
        if not all_scores:
            return {
                'final_score': 0,
                'skill_breakdown': {},
                'strengths': [],
                'weaknesses': [],
                'recommendation': 'Unable to assess - no answers provided',
                'hiring_readiness': 'NOT RECOMMENDED'
            }

        avg_scores = {metric: 0 for metric in self.weights}
        avg_scores['overall'] = 0

        for metric in avg_scores:
            values = [s[metric] for s in all_scores if metric in s]
            avg_scores[metric] = sum(values) / len(values) if values else 0

        strengths = [
            metric.replace('_', ' ').title()
            for metric, score in avg_scores.items()
            if metric != 'overall' and score >= 75
        ]

        weaknesses = [
            metric.replace('_', ' ').title()
            for metric, score in avg_scores.items()
            if metric != 'overall' and score < 50
        ]

        final_score = avg_scores['overall']

        if final_score >= 80:
            recommendation = "Excellent - Ready for interviews"
            hiring_readiness = "HIGHLY RECOMMENDED"
        elif final_score >= 65:
            recommendation = "Good - Minor improvements needed"
            hiring_readiness = "RECOMMENDED"
        elif final_score >= 50:
            recommendation = "Fair - Needs practice"
            hiring_readiness = "CONDITIONAL"
        else:
            recommendation = "Needs significant improvement"
            hiring_readiness = "NOT RECOMMENDED"

        return {
            'final_score': round(final_score, 2),
            'skill_breakdown': {k: round(v, 2) for k, v in avg_scores.items()},
            'strengths': strengths or ['None identified'],
            'weaknesses': weaknesses or ['None identified'],
            'recommendation': recommendation,
            'hiring_readiness': hiring_readiness,
            'total_questions': len(all_scores)
        }
