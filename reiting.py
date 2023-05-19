import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3

# Создаем базу данных
conn = sqlite3.connect('grades.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS grades
             (course text, month text, grade real)''')
conn.commit()

# Создаем окно входа
class LoginWindow:
    def __init__(self, master):
        self.master = master
        self.master.title("Login")
        self.master.geometry("300x200")

        self.label_username = tk.Label(self.master, text="Username:")
        self.label_password = tk.Label(self.master, text="Password:")

        self.entry_username = tk.Entry(self.master)
        self.entry_password = tk.Entry(self.master, show="*")

        self.label_username.grid(row=0, sticky=tk.E)
        self.label_password.grid(row=1, sticky=tk.E)
        self.entry_username.grid(row=0, column=1)
        self.entry_password.grid(row=1, column=1)

        self.logbtn = tk.Button(self.master, text="Login", command=self._login_btn_clicked)
        self.logbtn.grid(columnspan=2)

    def _login_btn_clicked(self):
        username = self.entry_username.get()
        password = self.entry_password.get()

        if username == "administrator" and password == "123":
            messagebox.showinfo("Login", "Welcome, administrator!")
            self.master.destroy()
        else:
            messagebox.showerror("Login error", "Invalid username or password")

root = tk.Tk()
app = LoginWindow(root)
root.mainloop()

# Создаем окно приложения
root = tk.Tk()
root.title('Приложение для отображения средней оценки по курсам ДПО')

# Добавляем метку для отображения выбранного файла
file_label = tk.Label(root, text='Выберите файл Excel с оценками студентов')
file_label.pack()

# Добавляем кнопку для выбора файла
def choose_file():
    file_path = filedialog.askopenfilename()
    file_label.config(text='Выбранный файл: ' + file_path)
    show_data(file_path)

choose_file_button = tk.Button(root, text="Выбрать файл", command=choose_file)
choose_file_button.pack()

# Создаем функцию для отображения данных
def show_data(file_path):
    df = pd.read_excel(file_path)

    # Группируем данные по курсам DPO и месяцам и считаем среднюю оценку по каждому курсу и месяцу
    grouped_data = df.groupby(['DPO Course', df['Дата'].dt.month])['Grade'].mean()

    # Сохраняем данные в базу данных
    for index, value in grouped_data.items():
        course, month = index
        grade = value
        c.execute("INSERT INTO grades VALUES (?, ?, ?)", (course, month, grade))
    conn.commit()

    # Создаем фрейм данных и добавляем кнопки для переключения между режимами представления
    data_frame = tk.Frame(root)
    data_frame.pack()

    # Создаем выпадающий список для выбора месяца
    months = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']
    month_var = tk.StringVar()
    month_var.set(months[0])
    month_dropdown = tk.OptionMenu(data_frame, month_var, *months)
    month_dropdown.pack()

    def show_chart():
        # Получаем данные из базы данных и создаем диаграмму средней оценки по каждому курсу за выбранный месяц
        c.execute("SELECT course, grade FROM grades WHERE month=?", (months.index(month_var.get()) + 1,))
        data = c.fetchall()
        grouped_data = pd.DataFrame(data, columns=['course', 'grade']).groupby('course')['grade'].mean()
        plt.bar(grouped_data.index, grouped_data.values)
        plt.title('Средняя оценка по курсам ДПО в ' + month_var.get())
        plt.xlabel('Курс')
        plt.ylabel('Оценка')
        plt.show()

    def show_table():
        # Получаем данные из базы данных и создаем таблицу средней оценки по каждому курсу за выбранный месяц
        c.execute("SELECT course, grade FROM grades WHERE month=?", (months.index(month_var.get()) + 1,))
        data = c.fetchall()
        grouped_data = pd.DataFrame(data, columns=['course', 'grade']).groupby('course')['grade'].mean()
        table = tk.Text(data_frame)
        table.insert(tk.END, str(grouped_data))
        table.pack()

    chart_button = tk.Button(data_frame, text="Показать диаграмму", command=show_chart)
    chart_button.pack(side=tk.LEFT)

    table_button = tk.Button(data_frame, text="Показать таблицу", command=show_table)
    table_button.pack(side=tk.LEFT)

# Запускаем главный цикл программы
root.mainloop()
 
 # закрываю соед
conn.close()
