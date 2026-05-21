import tkinter as tk
from tkinter import ttk, messagebox
from views.catalog_view import CatalogView
from views.my_courses_view import MyCoursesView
from views.course_editor_view import CourseEditorView
from views.analytics_view import AnalyticsView
from views.ranking_view import RankingView
from views.profile_view import ProfileView

class MainWindow:
    def __init__(self, user):
        self.user = user
        self.root = tk.Tk()
        self.root.title("Курсограф")
        self.root.geometry("1000x700")
        self.root.state('zoomed')

        self.create_menu()
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.show_catalog()

        self.root.mainloop()

    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        courses_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Курсы", menu=courses_menu)
        courses_menu.add_command(label="Каталог", command=self.show_catalog)
        if self.user['role'] in ['student']:
            courses_menu.add_command(label="Мои курсы", command=self.show_my_courses)
        if self.user['role'] in ['teacher', 'admin']:
            courses_menu.add_command(label="Создать курс", command=self.show_course_editor)

        stats_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Статистика", menu=stats_menu)
        if self.user['role'] in ['admin', 'teacher']:
            stats_menu.add_command(label="Аналитика", command=self.show_analytics)
            stats_menu.add_command(label="Рейтинги", command=self.show_ranking)

        menubar.add_command(label="Профиль", command=self.show_profile)
        menubar.add_command(label="Выход", command=self.logout)

    def clear_main(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def show_catalog(self):
        self.clear_main()
        CatalogView(self.main_frame, self.user)

    def show_my_courses(self):
        self.clear_main()
        MyCoursesView(self.main_frame, self.user)

    def show_course_editor(self):
        self.clear_main()
        CourseEditorView(self.main_frame, self.user)

    def show_analytics(self):
        self.clear_main()
        AnalyticsView(self.main_frame, self.user)

    def show_ranking(self):
        self.clear_main()
        RankingView(self.main_frame, self.user)

    def show_profile(self):
        self.clear_main()
        ProfileView(self.main_frame, self.user)

    def logout(self):
        self.root.destroy()
        from views.auth_view import AuthWindow
        AuthWindow().run()
    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        courses_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Курсы", menu=courses_menu)
        courses_menu.add_command(label="Каталог", command=self.show_catalog)
        if self.user['role'] in ['student']:
            courses_menu.add_command(label="Мои курсы", command=self.show_my_courses)
        if self.user['role'] in ['teacher', 'admin']:
            courses_menu.add_command(label="Создать курс", command=self.show_course_editor)

        ranking_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Рейтинги", menu=ranking_menu)
        ranking_menu.add_command(label="Рейтинг студентов", command=self.show_ranking)
        ranking_menu.add_command(label="Рейтинг преподавателей", command=self.show_ranking)
        ranking_menu.add_command(label="Рейтинг курсов", command=self.show_ranking)
        
        if self.user['role'] in ['admin', 'teacher']:
            stats_menu = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label="Статистика", menu=stats_menu)
            stats_menu.add_command(label="Аналитика", command=self.show_analytics)

        menubar.add_command(label="Профиль", command=self.show_profile)
        menubar.add_command(label="Выход", command=self.logout)