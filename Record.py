import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkcalendar import DateEntry

from datetime import datetime

import pandas as pd
import os
import sys
import traceback

class Config:
    def __init__(self, filename):
        self.filename = filename

    def __enter__(self):
        if os.path.exists(self.filename):
            try:
                self.df = pd.read_excel(self.filename, dtype=str, na_filter=False)
            except PermissionError:
                answer = messagebox.askretrycancel(message='Unable to load the config file. Please try again.')
                if answer:
                    self.__enter__()
                else:
                    window.destroy()
        else:
            answer = messagebox.showerror(message='No config file found.')
            if answer:
                window.destroy()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.df.to_excel(self.filename, index=False)
        except PermissionError:
            answer = messagebox.askretrycancel(message='Unable to save the config file. Please try again.')
            if answer:
                self.__exit__(exc_type, exc_val, exc_tb)
            else:
                window.destroy()

class Data:
    def __init__(self, filename):
        self.filename = filename

    def __enter__(self):
        if os.path.exists(self.filename):
            try:
                self.df = pd.read_excel(self.filename, dtype=str, na_filter=False)
            except PermissionError:
                answer = messagebox.askretrycancel(message='Unable to load the data file. Please try again.')
                if answer:
                    self.__enter__()
                else:
                    window.destroy()
        else:
            with Config('config.xlsx') as config:
                self.df = pd.DataFrame(columns=['Date', 'Time In', 'Time Out', 'Time of Session'] + [col for col in config.df] + ['Number of Identical Queries', 'Room Full?'])
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.df.to_excel(self.filename, index=False)
        except PermissionError:
            answer = messagebox.askretrycancel(message='Unable to save the data file. Please try again.')
            if answer:
                self.__exit__(exc_type, exc_val, exc_tb)
            else:
                window.destroy()

class Entries:
    def __init__(self):
        with Config('config.xlsx') as config:
            self.df = pd.DataFrame(columns=['Date', 'Time In', 'Time Out', 'Time of Session'] + [col for col in config.df] + ['Number of Identical Queries', 'Room Full?'])

    def refresh(self):
        date.set(f"{datetime.now():%d/%m/%Y}")
        start_hour.set('12')
        start_mint.set('00')
        end_hour.set('12')
        end_mint.set('00')
        for field, default in zip(add_fields, add_fields_defs):
            field.set(default or '')
        students.set(1)
        full.set('No')

    def update(self, var, index, mode):
        start_time = datetime.strptime(f"{start_hour.get()}:{start_mint.get()}", '%H:%M')
        end_time = datetime.strptime(f"{end_hour.get()}:{end_mint.get()}", '%H:%M')
        diff_time = end_time - start_time
        self.df.loc[0] = [date.get(), f"{start_time:%H:%M}", f"{end_time:%H:%M}", str(diff_time)[:-3]] + [field.get() for field in add_fields] + [students.get(), full.get()]

if __name__ == '__main__':
    path = os.path.dirname(sys.argv[0])
    os.chdir(path)
    while 'Record.app' in path:
        path = os.path.dirname(path)
        os.chdir(path)

    with open("log.txt", "w") as log:
        try:
            window = tk.Tk()
            window.title('Record')
            window.iconphoto(True, tk.PhotoImage(file='images/stag.png'))
            window.resizable(False, False)

            with Config('config.xlsx') as config:
                add_fields_defs = config.df.loc[0]
            entries = Entries()

            date = tk.StringVar(value=f"{datetime.now():%d/%m/%Y}")
            start_hour = tk.StringVar(value='12')
            start_mint = tk.StringVar(value='00')
            end_hour = tk.StringVar(value='12')
            end_mint = tk.StringVar(value='00')
            add_fields = [tk.StringVar(value=default) for default in add_fields_defs]
            students = tk.IntVar(value=1)
            full = tk.StringVar(value='No')

            date.trace_add('write', entries.update)
            start_hour.trace_add('write', entries.update)
            start_mint.trace_add('write', entries.update)
            end_hour.trace_add('write', entries.update)
            end_mint.trace_add('write', entries.update)
            for field in add_fields:
                field.trace_add('write', entries.update)
            students.trace_add('write', entries.update)
            full.trace_add('write', entries.update)

            ttk.Label(text='Date:').grid(row=0, column=0, sticky='e')
            DateEntry(textvariable=date, date_pattern='dd/mm/yyyy', selectmode = 'day', state='readonly').grid(row=0, column=1, columnspan=3, sticky='we')

            ttk.Label(text='Time In:').grid(row=1, column=0, sticky='e')
            ttk.Spinbox(textvariable=start_hour, values=[f"{hour:02}" for hour in range(0, 24, 1)], state='readonly', wrap=True, width=3).grid(row=1, column=1, sticky='w')
            ttk.Spinbox(textvariable=start_mint, values=[f"{mint:02}" for mint in range(0, 60, 5)], state='readonly', wrap=True, width=3).grid(row=1, column=2, columnspan=2, sticky='w')
        
            ttk.Label(text='Time Out:').grid(row=2, column=0, sticky='e')
            ttk.Spinbox(textvariable=end_hour, values=[f"{hour:02}" for hour in range(0, 24, 1)], state='readonly', wrap=True, width=3).grid(row=2, column=1, sticky='w')
            ttk.Spinbox(textvariable=end_mint, values=[f"{mint:02}" for mint in range(0, 60, 5)], state='readonly', wrap=True, width=3).grid(row=2, column=2, columnspan=2, sticky='w')

            with Config('config.xlsx') as config:
                for pos, col in enumerate(config.df):
                    ttk.Label(text=f"{col}:").grid(row=3+pos, column=0, sticky='e')
                    ttk.Combobox(textvariable=add_fields[pos], values=list(filter(None, config.df[col].values)), state='readonly').grid(row=3+pos, column=1, columnspan=3, sticky='ew')

            ttk.Label(text='No. of Students:').grid(row=4+pos, column=0, sticky='e')
            ttk.Spinbox(textvariable=students, values=tuple(range(1,10)), state='readonly', width=2).grid(row=4+pos, column=1, sticky='w')

            ttk.Label(text='Was the room full?').grid(row=4+pos, column=2, sticky='e')
            ttk.Checkbutton(variable=full, offvalue='No', onvalue='Yes').grid(row=4+pos, column=3, sticky='e')

            def submit_func():
                if '' in tuple(entries.df.loc[0]):
                    messagebox.showinfo(message='Please fill in all the fields.')
                else:
                    with Data('data.xlsx') as data:
                        data.df = pd.concat([data.df, entries.df])
                    entries.refresh()       
            submit_button = ttk.Button(text='Submit', command=submit_func)
            submit_button.grid(row=5+pos, column=0, columnspan=2)

            def del_func():
                del_window = tk.Toplevel(window)
                del_window.title('Data')
                del_window.resizable(False, False)
                del_window.attributes('-topmost', 'true')
                del_window.grab_set()

                with Data('data.xlsx') as data:
                    table = ttk.Treeview(del_window, columns=tuple(data.df.columns), show='headings', selectmode='browse')
                    for col in table['columns']:
                        table.heading(col, text=col, anchor=tk.CENTER)
                        table.column(col, stretch=False, anchor=tk.CENTER, width=100)
                    for idx, row in data.df.iterrows():
                        table.insert(parent='', index='end', values=tuple(row.values))
                table.bind('<Motion>', 'break')
                table.grid(row=0, column=0)

                vsb = ttk.Scrollbar(del_window, orient="vertical", command=table.yview)
                vsb.grid(row=0, column=1, sticky='ns')
                table.configure(yscrollcommand=vsb.set)

                def del_selection(event):
                    confirmation = messagebox.askquestion(parent=del_window, message='Are you sure you would like to delete this entry?')
                    if confirmation == 'no':
                        pass
                    else:
                        row_num = table.index(table.selection())
                        with Data('data.xlsx') as data:
                            data.df = data.df.drop(row_num)
                        del_window.destroy()
                table.bind("<<TreeviewSelect>>", del_selection)
            del_button = ttk.Button(text='Delete...', command=del_func)
            del_button.grid(row=5+pos, column=2, columnspan=2)

            window.mainloop()
        except Exception:
            traceback.print_exc(file=log)
