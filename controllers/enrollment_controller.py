from models.enrollment import Enrollment

class EnrollmentController:
    def enroll(self, student_id, course_id):
        return Enrollment.enroll(student_id, course_id)