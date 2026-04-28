import tkinter as tk
from tkinter import messagebox, ttk
import random
import json
import os
from datetime import datetime

# Константы
TASKS_FILE = "tasks.json"
DEFAULT_TASKS = [
    {"name": "Прочитать статью", "type": "учёба"},
    {"name": "Сделать зарядку", "type": "спорт"},
    {"name": "Написать отчёт", "type": "работа"},
    {"name": "Прочитать книгу", "type": "учёба"},
    {"name": "Пробежка 5 км", "type": "спорт"},
    {"name": "Закончить проект", "type": "работа"},
    {"name": "Изучить новый язык программирования", "type": "учёба"},
    {"name": "Приседания 20 раз", "type": "спорт"},
    {"name": "Провести встречу", "type": "работа"}
]


class TaskGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Task Generator")
        self.root.geometry("650x550")
        self.root.resizable(False, False)
        
        # Данные приложения
        self.tasks = []           # Список словарей {"name": "...", "type": "..."}
        self.history = []         # Список задач с временем генерации
        self.filter_type = "все"
        
        # Загрузка данных из файла
        self.load_data()
        
        # Создание интерфейса
        self.create_widgets()
        
    def load_data(self):
        """Загружает задачи из JSON-файла"""
        if os.path.exists(TASKS_FILE):
            try:
                with open(TASKS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.tasks = data.get("tasks", [])
                    self.history = data.get("history", [])
                    # Преобразуем старый формат (если нужно)
                    for task in self.tasks:
                        if isinstance(task, str):
                            task = {"name": task, "type": "другое"}
            except Exception as e:
                print(f"Ошибка загрузки: {e}")
                self.tasks = DEFAULT_TASKS.copy()
                self.history = []
        else:
            self.tasks = DEFAULT_TASKS.copy()
            self.history = []
    
    def save_data(self):
        """Сохраняет задачи и историю в JSON-файл"""
        data = {
            "tasks": self.tasks,
            "history": self.history
        }
        with open(TASKS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    
    def create_widgets(self):
        """Создаёт все элементы интерфейса"""
        # Заголовок
        title_label = tk.Label(self.root, text="🎲 Random Task Generator 🎲", 
                               font=("Arial", 18, "bold"), fg="#2C3E50")
        title_label.pack(pady=10)
        
        # --- Панель для генерации задачи ---
        frame_generate = tk.Frame(self.root, bd=2, relief=tk.RIDGE, padx=10, pady=10)
        frame_generate.pack(fill=tk.X, padx=10, pady=5)
        
        self.generate_btn = tk.Button(frame_generate, text="✨ Сгенерировать задачу ✨", 
                                      font=("Arial", 12), bg="#3498DB", fg="white",
                                      command=self.generate_task)
        self.generate_btn.pack(pady=5)
        
        # Текущая сгенерированная задача
        self.current_task_label = tk.Label(frame_generate, text="", font=("Arial", 14, "bold"), 
                                           fg="#E67E22", wraplength=580)
        self.current_task_label.pack(pady=5)
        
        # --- Фильтрация ---
        frame_filter = tk.Frame(self.root, bd=2, relief=tk.RIDGE, padx=10, pady=5)
        frame_filter.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(frame_filter, text="🔍 Фильтр по типу:", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        
        self.filter_var = tk.StringVar(value="все")
        filter_options = ["все", "учёба", "спорт", "работа", "другое"]
        filter_menu = ttk.Combobox(frame_filter, textvariable=self.filter_var, values=filter_options, 
                                   state="readonly", width=15)
        filter_menu.pack(side=tk.LEFT, padx=5)
        filter_menu.bind("<<ComboboxSelected>>", self.on_filter_change)
        
        # --- Добавление новой задачи ---
        frame_add = tk.Frame(self.root, bd=2, relief=tk.RIDGE, padx=10, pady=5)
        frame_add.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(frame_add, text="📝 Добавить новую задачу:", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        self.new_task_entry = tk.Entry(frame_add, font=("Arial", 10), width=30)
        self.new_task_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(frame_add, text="Тип:", font=("Arial", 10)).grid(row=0, column=2, padx=5, pady=5)
        self.new_task_type = ttk.Combobox(frame_add, values=["учёба", "спорт", "работа", "другое"], 
                                          state="readonly", width=10)
        self.new_task_type.set("другое")
        self.new_task_type.grid(row=0, column=3, padx=5, pady=5)
        
        add_btn = tk.Button(frame_add, text="➕ Добавить", bg="#2ECC71", fg="white", command=self.add_task)
        add_btn.grid(row=0, column=4, padx=5, pady=5)
        
        # Кнопка сброса истории
        clear_history_btn = tk.Button(frame_add, text="🗑️ Очистить историю", bg="#E74C3C", fg="white", 
                                      command=self.clear_history)
        clear_history_btn.grid(row=0, column=5, padx=5, pady=5)
        
        # --- История задач (список) ---
        frame_history = tk.Frame(self.root, bd=2, relief=tk.RIDGE, padx=10, pady=5)
        frame_history.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        tk.Label(frame_history, text="📜 История сгенерированных задач:", font=("Arial", 12, "bold")).pack(anchor="w", pady=5)
        
        # Создаём фрейм со скроллом для списка
        list_frame = tk.Frame(frame_history)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.history_listbox = tk.Listbox(list_frame, font=("Arial", 10), yscrollcommand=scrollbar.set, height=12)
        self.history_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.history_listbox.yview)
        
        # Кнопка для очистки списка задач (базы задач)
        tk.Button(frame_history, text="🗑️ Очистить все задачи (кроме истории)", 
                 bg="#F39C12", fg="white", command=self.clear_all_tasks).pack(pady=5)
        
        # Обновляем список задач в интерфейсе
        self.refresh_history_display()
    
    def on_filter_change(self, event=None):
        """Обрабатывает изменение фильтра"""
        self.filter_type = self.filter_var.get()
        self.refresh_history_display()
    
    def get_filtered_tasks(self):
        """Возвращает список задач с учётом текущего фильтра"""
        if self.filter_type == "все":
            return self.tasks
        else:
            return [t for t in self.tasks if t.get("type", "другое") == self.filter_type]
    
    def generate_task(self):
        """Генерирует случайную задачу из отфильтрованного списка"""
        filtered_tasks = self.get_filtered_tasks()
        if not filtered_tasks:
            messagebox.showwarning("Нет задач", "Нет задач для выбранного фильтра. Добавьте новые задачи!")
            self.current_task_label.config(text="❌ Нет доступных задач")
            return
        
        selected_task = random.choice(filtered_tasks)
        task_name = selected_task["name"]
        task_type = selected_task["type"]
        
        # Добавляем в историю с временем
        timestamp = datetime.now().strftime("%H:%M:%S %d.%m.%Y")
        history_entry = {
            "task": task_name,
            "type": task_type,
            "timestamp": timestamp
        }
        self.history.append(history_entry)
        
        # Отображаем текущую задачу
        self.current_task_label.config(text=f"🎯 Ваша задача: {task_name}  [Тип: {task_type}]")
        
        # Сохраняем и обновляем интерфейс
        self.save_data()
        self.refresh_history_display()
    
    def add_task(self):
        """Добавляет новую задачу"""
        task_name = self.new_task_entry.get().strip()
        task_type = self.new_task_type.get()
        
        if not task_name:
            messagebox.showerror("Ошибка", "Название задачи не может быть пустым!")
            return
        
        # Проверка на дубликат
        for task in self.tasks:
            if task["name"].lower() == task_name.lower():
                messagebox.showwarning("Предупреждение", "Такая задача уже существует!")
                return
        
        self.tasks.append({"name": task_name, "type": task_type})
        self.save_data()
        
        # Очищаем поля ввода
        self.new_task_entry.delete(0, tk.END)
        messagebox.showinfo("Успех", f"Задача '{task_name}' добавлена!")
    
    def clear_history(self):
        """Очищает историю генерации"""
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите очистить всю историю?"):
            self.history = []
            self.save_data()
            self.refresh_history_display()
            self.current_task_label.config(text="")
    
    def clear_all_tasks(self):
        """Очищает список всех задач (базу задач)"""
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить ВСЕ задачи (кроме истории)?\nПосле этого нужно будет добавлять задачи заново!"):
            self.tasks = []
            self.save_data()
            # Очищаем историю? Нет, оставляем историю, но она может ссылаться на несуществующие задачи.
            # Лучше тоже очистить историю для консистентности
            self.history = []
            self.save_data()
            self.refresh_history_display()
            self.current_task_label.config(text="")
            messagebox.showinfo("Готово", "Все задачи и история очищены!")
    
    def refresh_history_display(self):
        """Обновляет отображение истории в Listbox"""
        self.history_listbox.delete(0, tk.END)
        
        if not self.history:
            self.history_listbox.insert(tk.END, "История пуста")
        else:
            # Отображаем в обратном порядке (новые сверху)
            for entry in reversed(self.history):
                display_text = f"[{entry['timestamp']}] {entry['task']}  ({entry['type']})"
                self.history_listbox.insert(tk.END, display_text)


if __name__ == "__main__":
    root = tk.Tk()
    app = TaskGeneratorApp(root)
    root.mainloop()