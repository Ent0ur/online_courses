import json
from core.database import Database
from core.logger import log_action

class Quiz:
    @staticmethod
    def check_answer(question, user_answer, correct_answer):
        return user_answer.strip().lower() == correct_answer.strip().lower()

    @staticmethod
    def process_quiz(lesson_id, student_id, answers):
        db = Database()
        lesson = db.fetch_one("SELECT content, course_id FROM lessons WHERE id = ? AND lesson_type='quiz'", (lesson_id,))
        if not lesson:
            return 0
        
        # Проверяем, не проходил ли студент уже этот тест
        existing = db.fetch_one(
            "SELECT completed, score FROM lesson_progress WHERE student_id = ? AND lesson_id = ?",
            (student_id, lesson_id)
        )
        if existing and existing['completed']:
            return existing['score']  # Возвращаем уже полученный балл
        
        questions = json.loads(lesson['content'])
        score = 0
        total = len(questions)
        
        for i, q in enumerate(questions):
            if q['type'] == 'single':
                if str(answers.get(str(i))) == str(q['correct']):
                    score += 1
            elif q['type'] == 'text':
                if Quiz.check_answer(q['question'], answers.get(str(i), ''), q['correct']):
                    score += 1
        
        # Сохраняем результат
        db.execute(
            "INSERT OR REPLACE INTO lesson_progress (student_id, lesson_id, completed, score, completed_at) VALUES (?, ?, 1, ?, CURRENT_TIMESTAMP)",
            (student_id, lesson_id, score)
        )
        
        # Начисляем баллы студенту (баллы за тест)
        db.execute("UPDATE students SET total_points = total_points + ? WHERE user_id = ?", (score, student_id))
        log_action(student_id, f"Completed quiz {lesson_id} with score {score}")
        
        # Обновляем общий прогресс курса
        from models.enrollment import Enrollment
        Enrollment.update_progress(student_id, lesson['course_id'])
        
        return score