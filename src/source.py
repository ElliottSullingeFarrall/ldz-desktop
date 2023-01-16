import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from tkcalendar import DateEntry

from datetime import datetime

import pandas as pd
import os
import sys
import logging
from path_utils import get_app_name, resource_path

class PROFILE():
    # class to store active profile
    def __init__(self):
        self.file = os.path.join(user_dir, '.ldz/profile.txt')
        try:
            self.load()
        except FileNotFoundError:
            self.active = '_Default'
    
    def load(self):
        with open(self.file, 'r') as profile_file:
                self.active = profile_file.readline()

    def save(self):
        with open(self.file, 'w') as profile_file:
                profile_file.writelines(self.active)

class CFG():
    # class to store dataframe for config
    def __init__(self):
        self.file = resource_path(os.path.join('cfg', profile.active + os.extsep + 'csv'))
        try:
            self.df = pd.read_csv(self.file, dtype=str, na_filter=False)
        except (FileNotFoundError, pd.errors.EmptyDataError):
            self.df = pd.DataFrame()

class DAT():
    # class to store dataframe for data
    def __init__(self):
        self.file = os.path.join(user_dir, '.ldz', profile.active + os.extsep + 'csv')
        try:
            self.df = pd.read_csv(self.file, dtype=str, na_filter=False)
        except (FileNotFoundError, pd.errors.EmptyDataError):
            self.df = pd.DataFrame(columns=['Date','Time In','Time Out','Time of Session','Number of Identical Queries','Room Full?'])

    def save(self):
        self.df.to_csv(self.file, index=False)

    def import_dat(self):
        # import data from excel file(s)
        paths = filedialog.askopenfilenames(parent=self, title='Import Data', initialdir='/', filetypes=[('excel files', '*.xlsx')])
        if paths:
            answer = messagebox.askyesnocancel(parent=self, title='Import Data', message='Would you like to clear the existing data? This action cannot be undone!')
            if answer:
                self.df = pd.DataFrame()
            for path in paths:
                self.df = pd.concat([self.df, pd.read_excel(path, dtype=str, na_filter=False)])

    def export_dat(self):
        # export data to excel file
        path = filedialog.asksaveasfile(parent=self, title='Export Data', initialdir='/', filetypes=[('excel files', '*.xlsx')], defaultextension=('excel files', '*.xlsx'), mode='wb')
        if path:
            answer = messagebox.askyesnocancel(parent=self, title='Export Data', message='Would you like to clear the existing data? This action cannot be undone!')
            if answer:
                self.df.to_excel(path, index=False)
                self.df = pd.DataFrame(columns=['Date', 'Time In', 'Time Out', 'Time of Session'] + [col for col in cfg.df] + ['Number of Identical Queries', 'Room Full?'])
            else:
                self.df.to_excel(path, index=False)

class App(tk.Tk):
    def __init__(self, cfg):
        # create main interface
        super().__init__()
        
        if profile.active != 'Embedded':
            self.df = pd.DataFrame(columns=['Date', 'Time In', 'Time Out', 'Time of Session'] + [col for col in cfg.df] + ['Number of Identical Queries', 'Room Full?'])
        else:
            self.df = pd.DataFrame(columns=['Date'] + [col for col in cfg.df] + ['Students Expected', 'Students Arrived'])

        if cfg.df.empty:
            self.add_fields_defs = []
        else:
            self.add_fields_defs = list(cfg.df.loc[0])

        get_app_name()
        self.title(f"LDZ - {profile.active}")
        self.iconphoto(True, tk.PhotoImage(file=resource_path('images/stag.png')))
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        menubar = tk.Menu(self)
        cfgmenu = tk.Menu(menubar, tearoff=False)
        datmenu = tk.Menu(menubar, tearoff=False)
        cfgmenu.add_command(label='Change Profile', command=self.load_cfg)
        datmenu.add_command(label='View/Edit Data', command=self.edit_dat)
        datmenu.add_separator()
        datmenu.add_command(label='Import Data...', command=dat.import_dat)
        datmenu.add_command(label='Export Data...', command=dat.export_dat)
        menubar.add_cascade(label="Profile", menu=cfgmenu)
        menubar.add_cascade(label="Data", menu=datmenu)
        self.config(menu=menubar)

        self.date = tk.StringVar(value=f"{datetime.now():%d/%m/%Y}")
        self.start_hour = tk.StringVar(value='12')
        self.start_mint = tk.StringVar(value='00')
        self.end_hour = tk.StringVar(value='12')
        self.end_mint = tk.StringVar(value='00')
        self.students = tk.IntVar(value=1)
        self.full = tk.StringVar(value='No')
        self.expected  = tk.IntVar(value=1)
        self.arrived = tk.StringVar(value=1)
        self.add_fields = [tk.StringVar(value=default) for default in self.add_fields_defs]

        self.date.trace_add('write', self.update_fields)
        self.start_hour.trace_add('write', self.update_fields)
        self.start_mint.trace_add('write', self.update_fields)
        self.end_hour.trace_add('write', self.update_fields)
        self.end_mint.trace_add('write', self.update_fields)
        self.students.trace_add('write', self.update_fields)
        self.full.trace_add('write', self.update_fields)
        self.expected.trace_add('write', self.update_fields)
        self.arrived.trace_add('write', self.update_fields)
        [field.trace_add('write', self.update_fields) for field in self.add_fields]

        row_num = 0

        ttk.Label(text='Date:').grid(row=row_num, column=0, sticky='e')
        DateEntry(textvariable=self.date, date_pattern='dd/mm/yyyy', selectmode='day', state='readonly').grid(row=row_num, column=1, columnspan=3, sticky='we')
        row_num = row_num + 1

        if profile.active != 'Embedded':
            ttk.Label(text='Time In:').grid(row=row_num, column=0, sticky='e')
            ttk.Spinbox(textvariable=self.start_hour, values=[f"{hour:02}" for hour in range(0, 24, 1)], state='readonly', wrap=True, width=3).grid(row=row_num, column=1, sticky='w')
            ttk.Spinbox(textvariable=self.start_mint, values=[f"{mint:02}" for mint in range(0, 60, 5)], state='readonly', wrap=True, width=3).grid(row=row_num, column=2, columnspan=2, sticky='w')
            row_num = row_num + 1

            ttk.Label(text='Time Out:').grid(row=row_num, column=0, sticky='e')
            ttk.Spinbox(textvariable=self.end_hour, values=[f"{hour:02}" for hour in range(0, 24, 1)], state='readonly', wrap=True, width=3).grid(row=row_num, column=1, sticky='w')
            ttk.Spinbox(textvariable=self.end_mint, values=[f"{mint:02}" for mint in range(0, 60, 5)], state='readonly', wrap=True, width=3).grid(row=row_num, column=2, columnspan=2, sticky='w')
            row_num = row_num + 1

        for row, col in enumerate(cfg.df):
            ttk.Label(text=f"{col}:").grid(row=row_num, column=0, sticky='e')
            if '-' in cfg.df[col].values:
                ttk.Entry(textvariable=self.add_fields[row]).grid(row=row_num, column=1, columnspan=3, sticky='ew')
            else:
                ttk.Combobox(textvariable=self.add_fields[row], values=list(filter(None, cfg.df[col].values)), state='readonly').grid(row=row_num, column=1, columnspan=3, sticky='ew')
            row_num = row_num + 1

        if profile.active != 'Embedded':
            ttk.Label(text='No. of Students:').grid(row=row_num, column=0, sticky='e')
            ttk.Spinbox(textvariable=self.students, values=tuple(range(1,10)), state='readonly', width=2).grid(row=row_num, column=1, sticky='w')

            ttk.Label(text='Was the room full?').grid(row=row_num, column=2, sticky='e')
            ttk.Checkbutton(variable=self.full, offvalue='No', onvalue='Yes').grid(row=row_num, column=3, sticky='e')
            row_num = row_num + 1
        else:
            ttk.Label(text='Students Expected:').grid(row=row_num, column=0, sticky='e')
            ttk.Spinbox(textvariable=self.expected, values=tuple(range(1,50)), state='readonly', width=2).grid(row=row_num, column=1, sticky='w')

            ttk.Label(text='Arrived:').grid(row=row_num, column=2, sticky='e')
            ttk.Spinbox(textvariable=self.arrived, values=tuple(range(1,50)), state='readonly', width=2).grid(row=row_num, column=3, sticky='e')
            row_num = row_num + 1

        ttk.Button(text='Submit', command=self.submit_fields).grid(row=row_num, column=0, columnspan=4)

    def load_cfg(self):
        # open cfg selection window
        cfg_window = tk.Toplevel(self)
        cfg_window.title('Select Config')
        cfg_window.resizable(False, False)
        cfg_window.attributes('-topmost', 'true')
        cfg_window.grab_set()  

        table = ttk.Treeview(cfg_window, columns='Config', show='headings', selectmode='browse')
        for col in table['columns']:
            table.heading(col, text=col, anchor=tk.CENTER)
            table.column(col, stretch=False, anchor=tk.CENTER, width=100)
        for file in os.listdir(resource_path('cfg')):
            table.insert(parent='', index='end', values=os.path.splitext(file)[0])
        table.bind('<Motion>', 'break')
        table.grid(row=0, column=0)

        vsb = ttk.Scrollbar(cfg_window, orient="vertical", command=table.yview)
        vsb.grid(row=0, column=1, sticky='ns')
        table.configure(yscrollcommand=vsb.set)

        def on_click(event):
            # load selected cfg
            profile.active = table.item(table.focus())['values'][0]
            cfg.__init__()
            dat.__init__()
            cfg_window.destroy()
            self.destroy()
            self.__init__(cfg)
            self.mainloop()
        table.bind("<<TreeviewSelect>>", on_click)

    def edit_dat(self):
        # open data deletion window
        dat_window = tk.Toplevel(self)
        dat_window.title('View Data')
        dat_window.resizable(False, False)
        dat_window.attributes('-topmost', 'true')
        dat_window.grab_set()

        table = ttk.Treeview(dat_window, columns=tuple(self.df.columns), show='headings', selectmode='browse')
        for col in table['columns']:
            table.heading(col, text=col, anchor=tk.CENTER)
            table.column(col, stretch=False, anchor=tk.CENTER, width=100)
        for idx, row in dat.df[self.df.columns].iterrows():
            table.insert(parent='', index='end', values=tuple(row.values))
        table.bind('<Motion>', 'break')
        table.grid(row=0, column=0)

        vsb = ttk.Scrollbar(dat_window, orient="vertical", command=table.yview)
        vsb.grid(row=0, column=1, sticky='ns')
        table.configure(yscrollcommand=vsb.set)

        def on_click(event):
            # delete data entry
            answer = messagebox.askquestion(parent=dat_window, title='Delete Data', message='Are you sure you would like to delete this entry?')
            if answer == 'no':
                pass
            else:
                row_num = table.index(table.selection())
                dat.df = dat.df.drop(row_num)
                dat.save()
                dat_window.destroy()
        table.bind("<<TreeviewSelect>>", on_click)

    def update_fields(self, var, index, mode):
        # update internal dataframe based on fields
        if profile.active != 'Embedded':
            start_time = datetime.strptime(f"{self.start_hour.get()}:{self.start_mint.get()}", '%H:%M')
            end_time   = datetime.strptime(f"{self.end_hour.get()}:{self.end_mint.get()}", '%H:%M')
            diff_time  = end_time - start_time
            self.df.loc[0] = [self.date.get(), f"{start_time:%H:%M}", f"{end_time:%H:%M}", str(diff_time)[:-3]] + [field.get() for field in self.add_fields] + [self.students.get(), self.full.get()]
        else:
            self.df.loc[0] = [self.date.get()] + [field.get() for field in self.add_fields] + [self.expected.get(), self.arrived.get()]

    def reset_fields(self):
        # reset all fields to default values
        self.date.set(f"{datetime.now():%d/%m/%Y}")
        self.start_hour.set('12')
        self.start_mint.set('00')
        self.end_hour.set('12')
        self.end_mint.set('00')
        for field, default in zip(self.add_fields, self.add_fields_defs):
            field.set(default or '')
        self.students.set(1)
        self.full.set('No')

    def submit_fields(self):
        # submit internal dataframe to memory
        if '' in tuple(self.df.loc[0]):
            messagebox.showinfo(parent=self, message='Please fill in all the fields.')
        else:
            dat.df = pd.concat([dat.df, self.df])
            dat.save()
            self.reset_fields()

    def on_close(self):
        # save on close
        dat.save()
        profile.save()
        self.destroy()

if __name__ == '__main__':
    # setup directories
    user_dir = os.path.expanduser("~")
    os.makedirs(os.path.join(user_dir, '.ldz'), exist_ok=True)

    # initialise error logging
    os.chdir(os.path.dirname(sys.argv[0]))
    if os.path.exists('error.log'):
        os.remove('error.log')

    try:
        # initialise classes and main interface
        profile = PROFILE()
        cfg = CFG()
        dat = DAT()
        app = App(cfg)
        app.mainloop()
    except Exception as error:
        # catch and log errors
        logging.basicConfig(filename='error.log', filemode='w', level=logging.DEBUG)
        logging.error(error)