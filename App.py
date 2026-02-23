import tkinter as tk
from tkinter import messagebox, ttk
import json
import os
from datetime import datetime

FILE_NAME = "tasks.json"

class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Task Manager")
        self.root.geometry("750x500")
        self.root.resizable(False, False)

        self.tasks = []
        self.load_tasks()

        self.setup_ui()
        self.refresh_tasks()

    def setup_ui(self):
        frame_top = tk.Frame(self.root)
        frame_top.pack(pady=10)

        tk.Label(frame_top, text="Title").grid(row=0, column=0, padx=5)
        self.title_entry = tk.Entry(frame_top, width=20)
        self.title_entry.grid(row=0, column=1, padx=5)

        tk.Label(frame_top, text="Due Date (YYYY-MM-DD)").grid(row=0, column=2, padx=5)
        self.date_entry = tk.Entry(frame_top, width=15)
        self.date_entry.grid(row=0, column=3, padx=5)

        tk.Label(frame_top, text="Priority").grid(row=0, column=4, padx=5)
        self.priority_combo = ttk.Combobox(frame_top, values=["Low", "Medium", "High"], width=10)
        self.priority_combo.current(1)
        self.priority_combo.grid(row=0, column=5, padx=5)

        tk.Button(frame_top, text="Add Task", command=self.add_task).grid(row=0, column=6, padx=5)

        frame_middle = tk.Frame(self.root)
        frame_middle.pack()

        columns = ("ID", "Title", "Due Date", "Priority", "Status")
        self.tree = ttk.Treeview(frame_middle, columns=columns, show="headings", height=15)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=130)

        self.tree.pack()

        frame_bottom = tk.Frame(self.root)
        frame_bottom.pack(pady=10)

        tk.Button(frame_bottom, text="Mark Complete", command=self.mark_complete).grid(row=0, column=0, padx=10)
        tk.Button(frame_bottom, text="Delete Task", command=self.delete_task).grid(row=0, column=1, padx=10)

    def load_tasks(self):
        if os.path.exists(FILE_NAME):
            try:
                with open(FILE_NAME, "r") as f:
                    self.tasks = json.load(f)
            except:
                self.tasks = []

    def save_tasks(self):
        with open(FILE_NAME, "w") as f:
            json.dump(self.tasks, f, indent=4)

    def generate_id(self):
        if not self.tasks:
            return 1
        return max(task["id"] for task in self.tasks) + 1

    def add_task(self):
        title = self.title_entry.get().strip()
        due_date = self.date_entry.get().strip()
        priority = self.priority_combo.get()

        if not title:
            messagebox.showerror("Error", "Title is required")
            return

        if due_date:
            try:
                datetime.strptime(due_date, "%Y-%m-%d")
            except:
                messagebox.showerror("Error", "Invalid date format")
                return

        task = {
            "id": self.generate_id(),
            "title": title,
            "due_date": due_date,
            "priority": priority,
            "completed": False
        }

        self.tasks.append(task)
        self.save_tasks()
        self.refresh_tasks()

        self.title_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)

    def refresh_tasks(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for task in sorted(self.tasks, key=lambda x: (x["completed"], x["due_date"] or "9999-99-99")):
            status = "Completed" if task["completed"] else "Pending"

            tag = ""
            if not task["completed"] and task["due_date"]:
                try:
                    due = datetime.strptime(task["due_date"], "%Y-%m-%d")
                    if due.date() < datetime.now().date():
                        tag = "overdue"
                except:
                    pass

            self.tree.insert("", tk.END, values=(
                task["id"],
                task["title"],
                task["due_date"],
                task["priority"],
                status
            ), tags=(tag,))

        self.tree.tag_configure("overdue", background="#ffcccc")

    def get_selected_task(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Select a task")
            return None
        values = self.tree.item(selected[0])["values"]
        return values[0]

    def mark_complete(self):
        task_id = self.get_selected_task()
        if task_id is None:
            return

        for task in self.tasks:
            if task["id"] == task_id:
                task["completed"] = True

        self.save_tasks()
        self.refresh_tasks()

    def delete_task(self):
        task_id = self.get_selected_task()
        if task_id is None:
            return

        self.tasks = [task for task in self.tasks if task["id"] != task_id]
        self.save_tasks()
        self.refresh_tasks()


if __name__ == "__main__":
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()
