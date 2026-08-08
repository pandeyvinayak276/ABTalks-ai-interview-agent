"""Validation for deterministic interview planning using the supplied data."""

import unittest

from backend.data_loader import load_interview_data
from backend.interview_planner import InterviewPlanner


class InterviewPlannerTest(unittest.TestCase):
    def setUp(self) -> None:
        data = load_interview_data()
        self.candidate = data.get_candidate("CAND-001")
        assert self.candidate is not None
        self.planner = InterviewPlanner(self.candidate, data.curriculum)

    def test_plans_and_completes_an_interview(self) -> None:
        self.assertEqual(self.planner.state.member_id, "CAND-001")
        self.assertFalse(self.planner.done)

        questions = []
        for index in range(8):
            question = self.planner.next_question()
            self.assertIsNotNone(question)
            questions.append(question)
            done = self.planner.complete_question(question.question_number)
            if index < 7:
                self.assertFalse(done)

        self.assertEqual(len(questions), 8)
        self.assertEqual(len({question.curriculum_day for question in questions}), 8)
        self.assertEqual(len({question.objective for question in questions}), 8)
        self.assertTrue(self.planner.done)

    def test_completion_is_false_before_the_eighth_completed_question(self) -> None:
        for _ in range(7):
            question = self.planner.next_question()
            assert question is not None
            self.planner.complete_question(question.question_number)

        self.assertFalse(self.planner.done)
        self.assertEqual(len(self.planner.state.covered_curriculum_days), 7)

    def test_follow_up_is_structured_and_not_generated_text(self) -> None:
        first_question = self.planner.next_question()
        assert first_question is not None
        instruction = self.planner.add_follow_up(
            first_question.question_number,
            "Candidate described the implementation approach.",
        )
        self.planner.complete_question(first_question.question_number)
        follow_up = self.planner.next_question()

        self.assertEqual(instruction.previous_question_number, first_question.question_number)
        self.assertIsNotNone(follow_up)
        assert follow_up is not None
        self.assertTrue(follow_up.is_follow_up)
        self.assertEqual(follow_up.curriculum_day, first_question.curriculum_day)
        self.assertEqual(follow_up.follow_up_instruction, instruction)


if __name__ == "__main__":
    unittest.main()
