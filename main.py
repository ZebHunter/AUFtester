import tkinter as tk
from tkinter import messagebox
from random import randint, shuffle
from data import *
import os
from PIL import Image, ImageTk

tests = {
    1: [i for i in range(1, 350)],
    2: [i for i in range(351, 1211)]
}


class QuizApp:
    def __init__(self, questions):
        self.questions = questions
        self.current_question_index = 0
        self.window = tk.Tk()
        self.window.title("Quiz Application")
        self.window.geometry("640x480")

        self.question_label = tk.Label(self.window, text="", font=("Arial", 14), wraplength=1000)
        self.question_label.pack(pady=20)

        self.answer_var = tk.StringVar()
        self.answer_options = []

        self.selected_answers = []

        self.image_label = 0
        self.image = None

        self.right_answers = []

        self.next_button = tk.Button(self.window, text="Next", command=self.next_question)
        self.next_button.pack(pady=10)

        self.quit_button = tk.Button(self.window, text="Quit", command=self.window.destroy)
        self.quit_button.pack(pady=10)

        self.display_question()
        self.window.mainloop()

    def display_question(self):
        if self.current_question_index < len(self.questions):
            question = self.questions[self.current_question_index]
            self.question_label.config(text=question.question)
            self.right_answers = question.true_answers()
            for option in self.answer_options:
                option.destroy()
            self.answer_options = []

            self.answer_var.set(None)

            if "<img" in question.question:
                src = question.question[question.question.find("src='") + 5: question.question.find("'>")].replace("\\",
                                                                                                                   "/")
                if not os.path.exists(src):
                    src = src.replace("JPG", "jpg").replace("PNG", "png")
                if not os.path.exists(src):
                    src = src.replace("jpg", "JPG").replace("png", "PNG")
                image = Image.open(src)
                photo = ImageTk.PhotoImage(image)
                self.image_label = photo

                # Create a label to display the image
                self.image = tk.Label(self.window, image=photo)
                self.image.pack(side="bottom", fill="both", expand=True)

            if question.type_ == 1:  # Для вопросов с одним правильным ответом
                shuffle(question.answers)
                for i, answer in enumerate(question.answers):
                    option = tk.Radiobutton(self.window, text=answer.text, variable=self.answer_var, value=i)
                    option.pack(anchor="w")
                    self.answer_options.append(option)
                submit_button = tk.Button(self.window, text="Submit", command=self.submit_answer)
                submit_button.pack(pady=10)
                self.answer_options.append(submit_button)
            elif question.type_ == 2:
                shuffle(question.answers)
                self.selected_answers = []  # Создаем список переменных состояния
                for i, answer in enumerate(question.answers):
                    self.answer_var = tk.IntVar()
                    option = tk.Checkbutton(self.window, text=answer.text, variable=self.answer_var, onvalue=1,
                                            offvalue=0)
                    option.pack(anchor="w")
                    self.selected_answers.append(self.answer_var)
                    self.answer_options.append(option)

                submit_button = tk.Button(self.window, text="Submit", command=self.submit_answer)
                submit_button.pack(pady=10)
                self.answer_options.append(submit_button)
            elif question.type_ == 7:
                shuffle(question.answers)
                buf = self.answer_var
                self.answer_var = tk.Entry(self.window)
                self.answer_var.pack(pady=10)
                self.answer_options.append(self.answer_var)

                submit_button = tk.Button(self.window, text="Submit", command=self.submit_answer)
                submit_button.pack(pady=10)
                self.answer_options.append(submit_button)
                self.answer_var = buf
            elif question.type_ == 6:
                fixed_part = []
                changed_answers = []
                for i in question.answers:
                    fix, var_part = i.text.split(":::")
                    changed_answers.append(var_part)
                    fixed_part.append(fix)
                shuffle(changed_answers)
                for i, answer in enumerate(question.answers):
                    # Отображаем неизменяемую часть как текст
                    fixed_label = tk.Label(self.window, text=fixed_part[i], font=("Arial", 14))
                    fixed_label.pack(anchor="w")
                    self.answer_options.append(fixed_label)
                    # Создаем выпадающее меню для изменяемой части
                    option_var = tk.StringVar()
                    option = tk.OptionMenu(self.window, option_var, *changed_answers)
                    option.pack(anchor="w")
                    self.answer_options.append(option)
                    self.selected_answers.append(option_var)
                submit_button = tk.Button(self.window, text="Submit", command=self.submit_answer)
                submit_button.pack(pady=10)
                self.answer_options.append(submit_button)

        else:
            messagebox.showinfo("Quiz Completed", "Congratulations! You've completed the quiz.")
            self.window.destroy()

    def color_answers(self, selected_answers, correct_answers):
        for i, option in enumerate(self.answer_options[:-1]):
            if isinstance(option, tk.Checkbutton) or isinstance(option, tk.Radiobutton):
                if self.questions[self.current_question_index].answers[i].text in selected_answers:
                    if self.questions[self.current_question_index].answers[i].text in correct_answers:
                        option.config(fg="green")  # Правильный ответ
                    else:
                        option.config(fg="red")  # Неправильный ответ

    def check_answers(self, selected: list[str]):
        correct_answers = self.right_answers
        if (sorted(correct_answers) == sorted(selected)
                and self.questions[self.current_question_index].type_ != 7):
            messagebox.showinfo("Уведомление", "Сомнительно, но окэй!")
            self.color_answers(selected, correct_answers)
            self.next_question()
        elif (self.questions[self.current_question_index].type_ == 7 and
              selected[0] in correct_answers):
            messagebox.showinfo("Уведомление", "Сомнительно, но окэй!")
            self.color_answers(selected, correct_answers)
            self.next_question()
        elif self.questions[self.current_question_index].type_ == 6:
            extract_right_part = lambda x: x.split(":::")[1]
            new_array = list(map(extract_right_part, correct_answers))
            if selected == new_array:
                messagebox.showinfo("Уведомление", "Сомнительно, но окэй!")
                self.color_answers(selected, correct_answers)
                self.next_question()
            else:
                messagebox.showinfo("Уведомление", "Неправильно, попробуй еще раз")
                self.color_answers(selected, correct_answers)
        else:
            messagebox.showinfo("Уведомление", "Неправильно, попробуй еще раз")
            self.color_answers(selected, correct_answers)

    def submit_answer(self):
        selected_answers_text = []
        for i, option in enumerate(self.answer_options[:-1]):
            if isinstance(option, tk.Checkbutton):
                if self.selected_answers[i].get() == 1:
                    selected_answers_text.append(self.questions[self.current_question_index].answers[i].text)
            elif isinstance(option, tk.Radiobutton):
                selected_answers_text.append(
                    self.questions[self.current_question_index].answers[self.answer_var.get()].text)
                break
            elif isinstance(option, tk.Entry):
                selected_answers_text.append(option.get())
            elif isinstance(option, tk.OptionMenu):
                for option_var in self.selected_answers:
                    selected_value = option_var.get()
                    selected_answers_text.append(selected_value)
                break
        if selected_answers_text:
            print(f"Selected answers: {selected_answers_text}")
            self.check_answers(selected_answers_text)
        else:
            print("No answers selected.")

    def next_question(self):
        self.image_label = 0
        if self.image is not None:
            self.image.destroy()
        self.selected_answers = []
        self.current_question_index += 1
        self.display_question()


if __name__ == "__main__":
    app = QuizApp(mas_question(1))
