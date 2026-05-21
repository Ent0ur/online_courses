import tkinter as tk
from tkinter import ttk, messagebox
from utils.export import export_to_csv, export_to_json
from controllers.analytics_controller import AnalyticsController
from utils.charts import create_bar_chart, create_pie_chart, create_line_chart
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class AnalyticsView:
    def __init__(self, parent, user):
        self.parent = parent
        self.user = user
        self.controller = AnalyticsController()
        self.create_widgets()

    def create_widgets(self):
        notebook = ttk.Notebook(self.parent)
        notebook.pack(fill=tk.BOTH, expand=True)

        # Вкладка с графиками
        graphs_frame = ttk.Frame(notebook)
        notebook.add(graphs_frame, text="📊 Графики")
        self.create_graphs_tab(graphs_frame)

        # Вкладка с таблицей успеваемости
        performance_frame = ttk.Frame(notebook)
        notebook.add(performance_frame, text="📈 Успеваемость по курсам")
        self.create_performance_tab(performance_frame)

        # Вкладка экспорта
        export_frame = ttk.Frame(notebook)
        notebook.add(export_frame, text="📎 Экспорт")
        self.create_export_tab(export_frame)

    def create_graphs_tab(self, parent):
        """Вкладка с графиками"""
        # Кнопки для генерации графиков
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X, pady=10, padx=10)
        
        ttk.Button(btn_frame, text="📊 Популярные курсы", command=self.show_top_courses).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🥧 Распределение по уровням", command=self.show_level_distribution).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="📈 Средняя успеваемость", command=self.show_avg_performance).pack(side=tk.LEFT, padx=5)
        
        # Область для отображения графика
        self.graph_canvas = ttk.Frame(parent)
        self.graph_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def create_performance_tab(self, parent):
        """Вкладка с таблицей успеваемости по курсам"""
        # Заголовок
        ttk.Label(parent, text="Средняя успеваемость по курсам", font=("Arial", 14)).pack(pady=10)
        
        # Таблица
        columns = ("course", "avg_score", "grade")
        tree = ttk.Treeview(parent, columns=columns, show="headings", height=15)
        
        tree.heading("course", text="Название курса")
        tree.heading("avg_score", text="Средний балл")
        tree.heading("grade", text="Оценка")
        
        tree.column("course", width=350)
        tree.column("avg_score", width=120, anchor=tk.CENTER)
        tree.column("grade", width=120, anchor=tk.CENTER)
        
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Загрузка данных
        performances = self.controller.get_avg_performance()
        
        for course_name, avg_score in performances:
            # Определяем оценку на основе среднего балла
            if avg_score >= 8.5:
                grade = "🟢 Отлично (5)"
            elif avg_score >= 6.5:
                grade = "🔵 Хорошо (4)"
            elif avg_score >= 4:
                grade = "🟡 Удовлетворительно (3)"
            elif avg_score > 0:
                grade = "🟠 Низкий результат"
            else:
                grade = "⚪ Нет данных"
            
            tree.insert("", tk.END, values=(
                course_name,
                f"{avg_score:.1f} / 10" if avg_score > 0 else "Нет данных",
                grade
            ))
        
        # Пояснение
        info_frame = ttk.Frame(parent)
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(info_frame, text="💡 Средний балл рассчитывается на основе результатов тестов студентов",
                  foreground="gray", font=("Arial", 9)).pack()

    def create_export_tab(self, parent):
        """Вкладка экспорта"""
        frame = ttk.Frame(parent, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="📎 Экспорт отчётов", font=("Arial", 16)).pack(pady=10)
        ttk.Label(frame, text="Экспортируйте данные об успеваемости в различных форматах",
                  foreground="gray").pack(pady=5)
        
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=30)
        
        ttk.Button(btn_frame, text="📄 Экспорт в CSV", command=lambda: self.export_data('csv'),
                  width=20).pack(pady=5)
        ttk.Button(btn_frame, text="📄 Экспорт в JSON", command=lambda: self.export_data('json'),
                  width=20).pack(pady=5)
        
        ttk.Label(frame, text="Отчёт включает:\n• Список всех курсов\n• Успеваемость по курсам\n• Рейтинг студентов\n• Популярные курсы",
                  foreground="gray", justify=tk.CENTER).pack(pady=20)

    def export_data(self, format_type):
        """Экспорт данных"""
        report = self.controller.get_full_report()
        if format_type == 'csv':
            export_to_csv(report)
        else:
            export_to_json(report)

    def clear_canvas(self):
        """Очищает область с графиком"""
        for widget in self.graph_canvas.winfo_children():
            widget.destroy()

    def show_top_courses(self):
        """Показывает график популярных курсов"""
        self.clear_canvas()
        data = self.controller.get_top_courses(5)
        
        if not data or len(data) == 0:
            ttk.Label(self.graph_canvas, text="Нет данных о курсах", font=("Arial", 12)).pack(pady=50)
            return
        
        courses = [row['title'][:20] + "..." if len(row['title']) > 20 else row['title'] for row in data]
        students_count = [row['cnt'] for row in data]
        
        fig = create_bar_chart(courses, students_count, 
                               "Топ-5 популярных курсов", 
                               "Курсы", 
                               "Количество студентов")
        canvas = FigureCanvasTkAgg(fig, master=self.graph_canvas)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def show_level_distribution(self):
        """Показывает круговую диаграмму распределения курсов по уровням"""
        self.clear_canvas()
        data = self.controller.get_level_distribution()
        
        if not data or len(data) == 0:
            ttk.Label(self.graph_canvas, text="Нет данных о курсах", font=("Arial", 12)).pack(pady=50)
            return
        
        level_names = {
            'beginner': '🌱 Начальный',
            'intermediate': '📘 Средний', 
            'advanced': '🔥 Продвинутый'
        }
        
        labels = [level_names.get(row['level'], row['level']) for row in data]
        values = [row['cnt'] for row in data]
        
        fig = create_pie_chart(values, labels, "Распределение курсов по уровням сложности")
        canvas = FigureCanvasTkAgg(fig, master=self.graph_canvas)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def show_avg_performance(self):
        """Показывает линейный график средней успеваемости по курсам"""
        self.clear_canvas()
        data = self.controller.get_avg_performance()
        
        if not data or len(data) == 0:
            ttk.Label(self.graph_canvas, text="Нет данных об успеваемости", font=("Arial", 12)).pack(pady=50)
            return
        
        # Фильтруем курсы с ненулевыми баллами для графика
        courses_with_scores = [(name, score) for name, score in data if score > 0]
        
        if len(courses_with_scores) == 0:
            ttk.Label(self.graph_canvas, 
                      text="Пока нет данных об успеваемости.\nСтуденты ещё не прошли тесты.",
                      font=("Arial", 12), foreground="gray").pack(pady=50)
            return
        
        courses = [name[:25] + "..." if len(name) > 25 else name for name, _ in courses_with_scores]
        scores = [score for _, score in courses_with_scores]
        
        fig = create_line_chart(courses, scores,
                                "Средняя успеваемость по курсам",
                                "Курсы",
                                "Средний балл (из 10)")
        
        # Добавляем горизонтальную линию для среднего значения
        ax = fig.gca()
        avg_score = sum(scores) / len(scores)
        ax.axhline(y=avg_score, color='r', linestyle='--', alpha=0.7, label=f'Среднее: {avg_score:.1f}')
        ax.legend()
        
        canvas = FigureCanvasTkAgg(fig, master=self.graph_canvas)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)