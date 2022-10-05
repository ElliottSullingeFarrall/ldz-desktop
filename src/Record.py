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

class App(tk.Tk):
    def __init__(self, cfg):
        super().__init__()

        self.df = pd.DataFrame(columns=['Date', 'Time In', 'Time Out', 'Time of Session'] + [col for col in cfg.df] + ['Number of Identical Queries', 'Room Full?'])
        if cfg.df.empty:
            self.add_fields_defs = []
        else:
            self.add_fields_defs = list(cfg.df.loc[0])

        self.title(get_app_name())
        self.iconphoto(True, tk.PhotoImage(file=resource_path('images/stag.png')))
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        menubar = tk.Menu(self)
        cfgmenu = tk.Menu(menubar, tearoff=False)
        datmenu = tk.Menu(menubar, tearoff=False)
        cfgmenu.add_command(label='Load Config...', command=self.load_cfg)
        datmenu.add_command(label='View/Edit Data', command=self.edit_dat)
        datmenu.add_separator()
        datmenu.add_command(label='Import Data...', command=self.import_dat)
        datmenu.add_command(label='Export Data...', command=self.export_dat)
        menubar.add_cascade(label="Config", menu=cfgmenu)
        menubar.add_cascade(label="Data", menu=datmenu)
        self.config(menu=menubar)

        self.date       =  tk.StringVar(value=f"{datetime.now():%d/%m/%Y}")
        self.start_hour =  tk.StringVar(value='12')
        self.start_mint =  tk.StringVar(value='00')
        self.end_hour   =  tk.StringVar(value='12')
        self.end_mint   =  tk.StringVar(value='00')
        self.add_fields = [tk.StringVar(value=default) for default in self.add_fields_defs]
        self.students   =  tk.IntVar(value=1)
        self.full       =  tk.StringVar(value='No')

        self.date.trace_add('write', self.update_fields)
        self.start_hour.trace_add('write', self.update_fields)
        self.start_mint.trace_add('write', self.update_fields)
        self.end_hour.trace_add('write', self.update_fields)
        self.end_mint.trace_add('write', self.update_fields)
        for field in self.add_fields:
            field.trace_add('write', self.update_fields)
        self.students.trace_add('write', self.update_fields)
        self.full.trace_add('write', self.update_fields)

        ttk.Label(text='Date:').grid(row=0, column=0, sticky='e')
        DateEntry(textvariable=self.date, date_pattern='dd/mm/yyyy', selectmode = 'day', state='readonly').grid(row=0, column=1, columnspan=3, sticky='we')

        ttk.Label(text='Time In:').grid(row=1, column=0, sticky='e')
        ttk.Spinbox(textvariable=self.start_hour, values=[f"{hour:02}" for hour in range(0, 24, 1)], state='readonly', wrap=True, width=3).grid(row=1, column=1, sticky='w')
        ttk.Spinbox(textvariable=self.start_mint, values=[f"{mint:02}" for mint in range(0, 60, 5)], state='readonly', wrap=True, width=3).grid(row=1, column=2, columnspan=2, sticky='w')
    
        ttk.Label(text='Time Out:').grid(row=2, column=0, sticky='e')
        ttk.Spinbox(textvariable=self.end_hour, values=[f"{hour:02}" for hour in range(0, 24, 1)], state='readonly', wrap=True, width=3).grid(row=2, column=1, sticky='w')
        ttk.Spinbox(textvariable=self.end_mint, values=[f"{mint:02}" for mint in range(0, 60, 5)], state='readonly', wrap=True, width=3).grid(row=2, column=2, columnspan=2, sticky='w')

        pos = 0
        for pos, col in enumerate(cfg.df):
            ttk.Label(text=f"{col}:").grid(row=3+pos, column=0, sticky='e')
            ttk.Combobox(textvariable=self.add_fields[pos], values=list(filter(None, cfg.df[col].values)), state='readonly').grid(row=3+pos, column=1, columnspan=3, sticky='ew')

        ttk.Label(text='No. of Students:').grid(row=4+pos, column=0, sticky='e')
        ttk.Spinbox(textvariable=self.students, values=tuple(range(1,10)), state='readonly', width=2).grid(row=4+pos, column=1, sticky='w')

        ttk.Label(text='Was the room full?').grid(row=4+pos, column=2, sticky='e')
        ttk.Checkbutton(variable=self.full, offvalue='No', onvalue='Yes').grid(row=4+pos, column=3, sticky='e')

        ttk.Button(text='Submit', command=self.submit).grid(row=5+pos, column=0, columnspan=4)

    def update_fields(self, var, index, mode):
        start_time = datetime.strptime(f"{self.start_hour.get()}:{self.start_mint.get()}", '%H:%M')
        end_time   = datetime.strptime(f"{self.end_hour.get()}:{self.end_mint.get()}", '%H:%M')
        diff_time  = end_time - start_time
        self.df.loc[0] = [self.date.get(), f"{start_time:%H:%M}", f"{end_time:%H:%M}", str(diff_time)[:-3]] + [field.get() for field in self.add_fields] + [self.students.get(), self.full.get()]

    def reset_fields(self):
        self.date.set(f"{datetime.now():%d/%m/%Y}")
        self.start_hour.set('12')
        self.start_mint.set('00')
        self.end_hour.set('12')
        self.end_mint.set('00')
        for field, default in zip(self.add_fields, self.add_fields_defs):
            field.set(default or '')
        self.students.set(1)
        self.full.set('No')

    def load_cfg(self):
        path = filedialog.askopenfilename(parent=self, title='Load Config', initialdir='/', filetypes=[('excel files', '*.xlsx')])
        if path:
            cfg.df = pd.read_excel(path, dtype=str, na_filter=False)
            self.destroy()
            self.__init__(cfg)
            self.mainloop()

    def edit_dat(self):
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

        def del_selection(event):
            confirmation = messagebox.askquestion(parent=dat_window, title='Delete Data', message='Are you sure you would like to delete this entry?')
            if confirmation == 'no':
                pass
            else:
                row_num = table.index(table.selection())
                dat.df = dat.df.drop(row_num)
                dat_window.destroy()
        table.bind("<<TreeviewSelect>>", del_selection)

    def import_dat(self):
        path = filedialog.askopenfilename(parent=self, title='Import Data', initialdir='/', filetypes=[('excel files', '*.xlsx')])
        if path:
            answer = messagebox.askyesnocancel(parent=self, title='Import Data', message='Would you like to clear the existing data? This action cannot be undone!')
            if answer:
                dat.df = pd.read_excel(path, dtype=str, na_filter=False)
            else:
                dat.df = pd.concat([dat.df, pd.read_excel(path, dtype=str, na_filter=False)])

    def export_dat(self):
        path = filedialog.asksaveasfile(parent=self, title='Export Data', initialdir='/', filetypes=[('excel files', '*.xlsx')], defaultextension=('excel files', '*.xlsx'), mode='wb')
        if path:
            answer = messagebox.askyesnocancel(parent=self, title='Export Data', message='Would you like to clear the existing data? This action cannot be undone!')
            if answer:
                dat.df.to_excel(path, index=False)
                dat.df = pd.DataFrame(columns=['Date', 'Time In', 'Time Out', 'Time of Session'] + [col for col in cfg.df] + ['Number of Identical Queries', 'Room Full?'])
            else:
                dat.df.to_excel(path, index=False)

    def submit(self):
        if '' in tuple(self.df.loc[0]):
            messagebox.showinfo(parent=self, message='Please fill in all the fields.')
        else:
            dat.df = pd.concat([dat.df, self.df])
            self.reset_fields()

    def on_close(self):
        cfg.df.to_csv(resource_path('resources/cfg.csv'), index=False)
        dat.df.to_csv(resource_path('resources/dat.csv'), index=False)
        self.destroy()

class CFG():
    def __init__(self):
        try:
            self.df = pd.read_csv(resource_path('resources/cfg.csv'), dtype=str, na_filter=False)
        except pd.errors.EmptyDataError:
            self.df = pd.DataFrame()

class DAT():
    def __init__(self):
        self.df = pd.read_csv(resource_path('resources/dat.csv'), dtype=str, na_filter=False)

if __name__ == '__main__':
    os.chdir(os.path.dirname(sys.argv[0]))
    if os.path.exists('error.log'):
        os.remove('error.log')
    cfg = CFG()
    dat = DAT()
    try:
        app = App(cfg)
        app.mainloop()
    except Exception as error:
        logging.basicConfig(filename='error.log', filemode='w', level=logging.DEBUG)
        logging.error(error)