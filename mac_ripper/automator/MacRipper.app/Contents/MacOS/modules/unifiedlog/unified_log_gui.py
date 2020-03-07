# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals
from tkinter import filedialog
import tkinter.messagebox as messagebox
import tkinter as tk

import unified_log


class UnifiedlogGui(tk.Frame):

    def __init__(self, master=None):
        super().__init__(master)

        # crate frame
        main_frame = self.master
        main_frame.geometry()
        main_frame.title('Unifiedlog_Ripper')
        main_frame['height'] = 450
        main_frame['width'] = 400

        self.menu_bar = tk.Menu(main_frame)
        main_frame.config(menu=self.menu_bar)

        file_menu = tk.Menu(self.menu_bar)
        file_menu.add_command(label='Exit', command=self.master.quit)
        self.menu_bar.add_cascade(label='File', menu=file_menu)

        #Input evidence_root conf
        self.Label_evi = tk.Label(text=u"[+]Evidence root path")
        self.Label_evi.place(x=10, y=0)

        self.entry_evi = tk.Entry(main_frame)
        self.entry_evi.place(x=10, y=25)
        self.entry_evi.focus_set()

        #Input output conf
        self.Label_out = tk.Label(text=u"[+]Output path")
        self.Label_out.place(x=10, y=65)

        self.entry_out = tk.Entry(main_frame)
        self.entry_out.place(x=10, y=90)
        self.entry_out.focus_set()

        #st conf
        self.st = tk.Label(
            text=u"[+]please input the start datetime you want to filter.\n e.g. '2018-05-14 10:00:00', '2018-05-14'")
        self.st.place(x=10, y=130)

        self.entry_st = tk.Entry(main_frame)
        self.entry_st.place(x=10, y=170)

        # ed conf
        self.ed = tk.Label(
            text=u"[+]please input the end datetime you want to filter.\n e.g. '2018-05-14 10:00:00', '2018-05-14'")
        self.ed.place(x=10, y=210)

        self.entry_ed = tk.Entry(main_frame)
        self.entry_ed.place(x=10, y=250)

        # format conf
        fr = tk.Label(
            text=u"[+]please input the output format.\n  'json' or 'csv'")
        fr.place(x=10, y=290)

        self.flg_format = tk.StringVar(value="0")
        self.flg_format.set('0')
        # ラジオ1
        self.rb1 = tk.Radiobutton(text='csv', value="0", variable=self.flg_format)
        self.rb1.place(x=10, y=330)
        # ラジオ2
        self.rb2 = tk.Radiobutton(text='json',  value="1", variable=self.flg_format)
        self.rb2.place(x=70, y=330)

        # Checkbutton conf
        Browse_button = tk.Button(self.master, text='Browse', width=5,
                                  command=lambda: self.Browse_clicked_evi()).place(x=205, y=25)

        Browse_button_out = tk.Button(self.master, text='Browse', width=5,
                                  command=lambda: self.Browse_clicked_out()).place(x=205, y=90)

        rip_button = tk.Button(self.master, text='rip', width=3,
                               command=lambda: self.rip()).place(x=155, y=390)

        quit_button = tk.Button(self.master, text='quit', width=3,
                                command=lambda: self.master.destroy()).place(x=210, y=390)

    def Browse_clicked_evi(self):
        folderpath = filedialog.askdirectory(initialdir="/", title="Select folder")
        self.entry_evi.insert(0, string=folderpath)

    def Browse_clicked_out(self):
        folderpath = filedialog.askdirectory(initialdir="/", title="Select folder")
        self.entry_out.insert(0, string=folderpath)

    def rip(self):
        evidence_root = self.entry_evi.get()
        st = self.entry_st.get()
        ed = self.entry_ed.get()
        format_rb = self.flg_format.get()
        format_rb_result = []
        if format_rb == "0":
            format_rb_result = "csv"
        elif format_rb == "1":
            format_rb_result = "json"
        else:
            print("format_result:error")
        outputpath = self.entry_out.get()

        print(f"format_result:{format_rb_result}")
        print(f"outputpath:{outputpath}")
        print(f"st:{st}")
        print(f"ed:{ed}")

        #あとはここだけ
        unified_logs = unified_log.UnifiedLogs(evidence_root, outputpath)
        unified_logs.parse_unifiedlog(start=st, end=ed, predicate="all", output_format=format_rb_result, timezone="asia/tokyo",
                                      name="")
        messagebox.showinfo("infomation message",
                            "Finish\nOutput is crated in same directory of unified_log.py")


if __name__ == '__main__':
    root = tk.Tk()
    mrg = UnifiedlogGui(master=root)
    mrg.mainloop()

"""
・TODO
Outputpass
error handrings
progress bar
Outputpass

・Memo
In Mojave,
Python 3.7.2 is necessary.
That is occurred by tkinter's bags.
"""