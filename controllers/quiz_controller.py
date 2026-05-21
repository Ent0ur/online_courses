from models.quiz import Quiz

class QuizController:
    @staticmethod
    def submit_quiz(lesson_id, student_id, answers):
        return Quiz.process_quiz(lesson_id, student_id, answers)