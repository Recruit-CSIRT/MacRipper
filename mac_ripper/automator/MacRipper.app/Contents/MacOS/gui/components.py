import tkinter as tk
from tkinter import ttk
from tkinter import filedialog


class ButtonWithCheckbox:
    def __init__(self, parent, x, y, text):
        self._parent = parent
        self._x = x
        self._y = y
        self._button = None
        self._checkbox = None
        self._checkbox_text = text
        self._background = "white smoke"

    def build(self):
        self._button = tk.BooleanVar()
        self._checkbox = ttk.Checkbutton(variable=self._button, text=self._checkbox_text)
        self._checkbox.place(x=self._x, y=self._y)
        return self._button

    def get(self):
        return self._button


class SimpleSelector(ButtonWithCheckbox):
    def __init__(self, parent, x, y, text):
        super().__init__(parent, x, y)
        self._checkbox_text = text


class AllSelector(SimpleSelector):
    def build(self):
        super().build()
        self._button.set(True)
        return self._button


class DirectorySelector:
    def __init__(self, parent, x, y, name, value):
        self._parent = parent
        self._x = x
        self._y = y
        self._label_text = name
        self._background = "#E2E2E2"
        self._default_entry_value = value
        self._entry = None

    def build(self):
        label = tk.Label(text=self._label_text)
        label.place(x=self._x, y=self._y)
        label['bg'] = self._background
        ent = tk.Entry(self._parent, borderwidth=2, highlightbackground="#E0E0E0")
        ent.place(x=self._x, y=self._y + 25)
        ent.focus_set()
        ent.insert(0, string=self._default_entry_value)
        self._entry = ent

        def on_click():
            path = filedialog.askdirectory(initialdir="/", title="Select folder")
            ent.delete(0, tk.END)
            ent.insert(0, string=path)
            self._evidence_root = path

        button = ttk.Button(self._parent, text='Browse', width=5, command=on_click)
        button.place(x=self._x + 195, y=self._y + 25)
        return self

    def get_value(self):
        return self._entry.get()
