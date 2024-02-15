import tkinter as tk
import pandas as pd
from tkinter import messagebox

BACKGROUND_COLOR = "#B1DDC6"
LANGUAGE_FONT = ('Arial', 40, 'italic')
WORD_FONT = ('Arial', 60, 'bold')
START_FONT = ('Arial', 80, 'bold')
END_FONT = ('Arial', 40, 'bold')

class Main(tk.Tk):

    def __init__(self):
        super().__init__()

        self.title('Flashy')
        self.config(padx=50, pady=50, bg=BACKGROUND_COLOR)

        frame = StartMenu(self, bg=BACKGROUND_COLOR)
        frame.grid()

        self.mainloop()


class StartMenu(tk.Frame):

    def __init__(self, master=None, cnf={}, **kw):
        super().__init__(master, cnf, **kw)

        self.canvas = tk.Canvas(self, width=800, height=526, bg=BACKGROUND_COLOR, highlightthickness=0)
        self.start_text = self.canvas.create_text(400, 263, text='Click anywhere\nto start', font=START_FONT, justify='center')

        self.canvas.grid()

        master.bind("<Button-1>", lambda event, master=master: self.start(master))

    def start(self, master):
        self.grid_forget()
        frame = Application(master, bg=BACKGROUND_COLOR)
        frame.grid()
        master.unbind("<Button-1>")


class Application(tk.Frame):

    def __init__(self, master=None, cnf={}, **kw):
        super().__init__(master, cnf, **kw)

        # Data reading
        try:
            with open('./data/words_to_learn.csv', 'r') as file:
                self.data = pd.read_csv(file)
            self.current_word = self.data.sample()
        except (FileNotFoundError, KeyError, ValueError):
            try:
                with open('./data/french_words.csv', 'r') as file:
                    self.data = pd.read_csv(file)
            except FileNotFoundError:
                messagebox.showerror(title='Data File Not Found', message='Unable to find a data file. Please check the data folder and ensure that your desired words are there.')
                master.destroy()
            else:
                self.current_word = self.data.sample()

        # UI Setup
        ## Card
        self.canvas = tk.Canvas(self, width=800, height=526, bg=BACKGROUND_COLOR, highlightthickness=0)
        self.card_front = tk.PhotoImage(file='./images/card_front.png')
        self.card_back = tk.PhotoImage(file='./images/card_back.png')
        self.card_img = self.canvas.create_image(400, 263, image=self.card_front)
        self.language_text = self.canvas.create_text(400, 150, text='French', font=LANGUAGE_FONT)
        self.word_text = self.canvas.create_text(400, 263, text=self.current_word.French.item(), font=WORD_FONT)
        self.canvas.grid(row=0, column=0, columnspan=2)

        ## Right/Wrong
        master.right_img = right_img = tk.PhotoImage(file='./images/right.png')
        self.right_button = tk.Button(self, image=right_img, command=lambda: self.right(master))
        self.right_button.grid(row=1, column=0)

        master.wrong_img = wrong_img = tk.PhotoImage(file='./images/wrong.png')
        self.wrong_button = tk.Button(self, image=wrong_img, command=lambda: self.wrong(master))
        self.wrong_button.grid(row=1, column=1)

        self.flip_timer = master.after(3000, self.flip_card)
        
    def right(self, master):
        self.data = self.data.drop(self.current_word.index)
        self.data.to_csv('./data/words_to_learn.csv', index=False)
        self.new_word(master)

    def wrong(self, master):
        self.new_word(master)

    def new_word(self, master):
        # Select new word
        try:
            self.current_word = self.data.sample()
        except (KeyError, ValueError):
            self.end_screen()

        # Reset card and timer with new word
        master.after_cancel(self.flip_timer)
        self.canvas.itemconfig(self.card_img, image=self.card_front)
        self.canvas.itemconfig(self.language_text, fill='black', text='French')
        self.canvas.itemconfig(self.word_text, fill='black', text=self.current_word.French.item())
        self.flip_timer = master.after(3000, self.flip_card)

    def flip_card(self):
        self.canvas.itemconfig(self.card_img, image=self.card_back)
        self.canvas.itemconfig(self.language_text, fill='white', text='English')
        self.canvas.itemconfig(self.word_text, fill='white', text=self.current_word.English.item())

    def end_screen(self):
        self.canvas.delete('all')
        self.right_button.grid_forget()
        self.wrong_button.grid_forget()
        self.end_text = self.canvas.create_text(400, 263, text='Congratulations!\nYou finished all of the words.\nClose and reopen to start over!',
                                                font=END_FONT, justify='center')