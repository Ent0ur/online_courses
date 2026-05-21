from models.course import Course

class CourseController:
    def get_catalog(self, level=None, search=None):
        return Course.get_all(level, search)