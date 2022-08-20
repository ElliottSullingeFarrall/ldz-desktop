import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from tkcalendar import DateEntry

from datetime import datetime

import pandas as pd
import os
import sys
from path_utils import get_app_name, resource_path

def ui(cfg):
    # build main window with fields based on a config file
    global entries, add_fields_defs, date, start_hour, start_mint, end_hour, end_mint, add_fields, students, full
    window = tk.Tk()
    window.title(get_app_name())
    window.iconphoto(True, tk.PhotoImage(file=resource_path('images/stag.png')))
    window.resizable(False, False)

    menubar = tk.Menu(window)
    cfgmenu = tk.Menu(menubar, tearoff=False)
    datmenu = tk.Menu(menubar, tearoff=False)
    cfgmenu.add_command(label='Load Config...', command=load_cfg)
    datmenu.add_command(label='Import Data...', command=import_dat)
    datmenu.add_command(label='Export Data...', command=export_dat)
    menubar.add_cascade(label="Config", menu=cfgmenu)
    menubar.add_cascade(label="Data", menu=datmenu)
    window.config(menu=menubar)

    entries = pd.DataFrame(columns=['Date', 'Time In', 'Time Out', 'Time of Session'] + [col for col in cfg] + ['Number of Identical Queries', 'Room Full?'])

    if cfg.empty:
        add_fields_defs = []
    else:
        add_fields_defs = cfg.loc[0]

    date = tk.StringVar(value=f"{datetime.now():%d/%m/%Y}")
    start_hour = tk.StringVar(value='12')
    start_mint = tk.StringVar(value='00')
    end_hour = tk.StringVar(value='12')
    end_mint = tk.StringVar(value='00')
    add_fields = [tk.StringVar(value=default) for default in add_fields_defs]
    students = tk.IntVar(value=1)
    full = tk.StringVar(value='No')

    date.trace_add('write', update_entries)
    start_hour.trace_add('write', update_entries)
    start_mint.trace_add('write', update_entries)
    end_hour.trace_add('write', update_entries)
    end_mint.trace_add('write', update_entries)
    for field in add_fields:
        field.trace_add('write', update_entries)
    students.trace_add('write', update_entries)
    full.trace_add('write', update_entries)

    ttk.Label(text='Date:').grid(row=0, column=0, sticky='e')
    DateEntry(textvariable=date, date_pattern='dd/mm/yyyy', selectmode = 'day', state='readonly').grid(row=0, column=1, columnspan=3, sticky='we')

    ttk.Label(text='Time In:').grid(row=1, column=0, sticky='e')
    ttk.Spinbox(textvariable=start_hour, values=[f"{hour:02}" for hour in range(0, 24, 1)], state='readonly', wrap=True, width=3).grid(row=1, column=1, sticky='w')
    ttk.Spinbox(textvariable=start_mint, values=[f"{mint:02}" for mint in range(0, 60, 5)], state='readonly', wrap=True, width=3).grid(row=1, column=2, columnspan=2, sticky='w')
 
    ttk.Label(text='Time Out:').grid(row=2, column=0, sticky='e')
    ttk.Spinbox(textvariable=end_hour, values=[f"{hour:02}" for hour in range(0, 24, 1)], state='readonly', wrap=True, width=3).grid(row=2, column=1, sticky='w')
    ttk.Spinbox(textvariable=end_mint, values=[f"{mint:02}" for mint in range(0, 60, 5)], state='readonly', wrap=True, width=3).grid(row=2, column=2, columnspan=2, sticky='w')

    pos = 0
    for pos, col in enumerate(cfg):
        ttk.Label(text=f"{col}:").grid(row=3+pos, column=0, sticky='e')
        ttk.Combobox(textvariable=add_fields[pos], values=list(filter(None, cfg[col].values)), state='readonly').grid(row=3+pos, column=1, columnspan=3, sticky='ew')

    ttk.Label(text='No. of Students:').grid(row=4+pos, column=0, sticky='e')
    ttk.Spinbox(textvariable=students, values=tuple(range(1,10)), state='readonly', width=2).grid(row=4+pos, column=1, sticky='w')

    ttk.Label(text='Was the room full?').grid(row=4+pos, column=2, sticky='e')
    ttk.Checkbutton(variable=full, offvalue='No', onvalue='Yes').grid(row=4+pos, column=3, sticky='e')

    ttk.Button(text='Submit', command=submit_func).grid(row=5+pos, column=0, columnspan=2)
    ttk.Button(text='Delete...', command=del_func).grid(row=5+pos, column=2, columnspan=2)

    return window

def load_cfg():
    # load a config file to define which fields to include in the main window
    global window, cfg
    path = filedialog.askopenfilename(title='Load Config', initialdir='/', filetypes=[('excel files', '*.xlsx')])
    cfg = pd.read_excel(path, dtype=str, na_filter=False)
    window.destroy()
    window = ui(cfg)
    window.protocol("WM_DELETE_WINDOW", close)
    window.mainloop()

def import_dat():
    # import appointment data from an excel file
    global dat
    answer = messagebox.askyesnocancel(title='Import Data', message='Would you like to clear the current data? This action cannot be undone!')
    if answer:
        path = filedialog.askopenfilename(title='Import Data', initialdir='/', filetypes=[('excel files', '*.xlsx')])
        dat = dat.iloc[0:0]
        dat = pd.concat([dat, pd.read_excel(path, dtype=str, na_filter=False)])
    else:
        path = filedialog.askopenfilename(title='Import Data', initialdir='/', filetypes=[('excel files', '*.xlsx')])
        dat = pd.concat([dat, pd.read_excel(path, dtype=str, na_filter=False)])

def export_dat():
    # export appointment data to an excel file
    global dat
    answer = messagebox.askyesnocancel(title='Export Data', message='Would you like to clear the current data? This action cannot be undone!')
    if answer:
        path = filedialog.asksaveasfile(title='Export Data', initialdir='/', filetypes=[('excel files', '*.xlsx')], defaultextension=('excel files', '*.xlsx'), mode='wb')
        dat.to_excel(path, index=False)
        dat = dat.iloc[0:0]
    else:
        path = filedialog.asksaveasfile(title='Export Data', initialdir='/', filetypes=[('excel files', '*.xlsx')], defaultextension=('excel files', '*.xlsx'), mode='wb')
        dat.to_excel(path, index=False)

def submit_func():
    # submit current field entries to data sheet
    global dat
    if '' in tuple(entries.loc[0]):
        messagebox.showinfo(message='Please fill in all the fields.')
    else:
        dat = pd.concat([dat, entries])
        reset_fields()

def del_func():
    # create window to view data and delete rows on click
    global dat, entries
    del_window = tk.Toplevel(window)
    del_window.title('Data')
    del_window.resizable(False, False)
    del_window.attributes('-topmost', 'true')
    del_window.grab_set()

    table = ttk.Treeview(del_window, columns=tuple(entries.columns), show='headings', selectmode='browse')
    for col in table['columns']:
        table.heading(col, text=col, anchor=tk.CENTER)
        table.column(col, stretch=False, anchor=tk.CENTER, width=100)
    for idx, row in dat[entries.columns].iterrows():
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
            dat = dat.drop(row_num)
            del_window.destroy()
    table.bind("<<TreeviewSelect>>", del_selection)

def update_entries(var, index, mode):
    # keep data to be submitted in sync with the data in the field entries
    start_time = datetime.strptime(f"{start_hour.get()}:{start_mint.get()}", '%H:%M')
    end_time = datetime.strptime(f"{end_hour.get()}:{end_mint.get()}", '%H:%M')
    diff_time = end_time - start_time
    entries.loc[0] = [date.get(), f"{start_time:%H:%M}", f"{end_time:%H:%M}", str(diff_time)[:-3]] + [field.get() for field in add_fields] + [students.get(), full.get()]

def reset_fields():
    # reset field entries to their default values
    date.set(f"{datetime.now():%d/%m/%Y}")
    start_hour.set('12')
    start_mint.set('00')
    end_hour.set('12')
    end_mint.set('00')
    for field, default in zip(add_fields, add_fields_defs):
        field.set(default or '')
    students.set(1)
    full.set('No')

def close():
    # save on close
    cfg.to_excel(resource_path('resources/cfg.xlsx'), index=False)
    dat.to_excel(resource_path('resources/dat.xlsx'), index=False)
    window.destroy()

if __name__ == '__main__':
    os.chdir(os.path.dirname(sys.argv[0]))
    cfg = pd.read_excel(resource_path('resources/cfg.xlsx'), dtype=str, na_filter=False)
    dat = pd.read_excel(resource_path('resources/dat.xlsx'), dtype=str, na_filter=False)

    window = ui(cfg)
    window.protocol("WM_DELETE_WINDOW", close)
    window.mainloop()