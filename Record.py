import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkcalendar import DateEntry

import openpyxl as xl
import os
import platform

import datetime

if platform.system() == 'Windows':
    icon_path = 'stag.ico'
else:
    icon_path = 'stag.icns'

def num_to_str(num):
    if num < 10:
        return '0' + str(num)
    else:
        return str(num)

hours = list(range(0, 24, 1))
hours = [num_to_str(hour) for hour in hours]
mints = list(range(0, 60, 5))
mints = [num_to_str(mint) for mint in mints]

def load_config(filename):
    if os.path.exists(filename):
        try:
            config = xl.load_workbook(filename=filename)
        except PermissionError:
            answer = messagebox.askretrycancel(message='Unable to load the config file. Please try again.')
            if answer:
                load_config(filename)
            else:
                window.destroy()
    else:
        answer = messagebox.showerror(message='No config file found.')
        if answer:
            window.destroy()
    return config, filename

def load_data(filename):
    if os.path.exists(filename):
        try:
            data = xl.load_workbook(filename=filename)
        except PermissionError:
            answer = messagebox.askretrycancel(message='Unable to load the data file. Please try again.')
            if answer:
                load_data(filename)
            else:
                window.destroy()
    else:
        data = xl.Workbook()
        data.security.lockStructure = True
        data.active.protection.enable()
        data.active.append(list(get_vars().keys()))
    return data, filename

def save_file(file, filename):
    file.save(filename=filename)
    file.close()

filename_config = 'config.xlsx'
filename_data   = 'data.xlsx'

config, filename = load_config(filename=filename_config)
fields = []
for col in config.active.iter_cols():
            fields.append({'name' : col[0].value, 'default' : col[1].value, 'values' : list(filter(None, [cell.value for cell in col[1:]]))})
save_file(config, filename)

window = tk.Tk()
window.title('Record')
window.iconbitmap(icon_path)
window.resizable(False, False)

date = tk.StringVar()
ttk.Label(text='Date:').grid(row=0, column=0, sticky='e')
DateEntry(textvariable=date, date_pattern='dd/mm/yyyy', state='readonly', selectmode = 'day').grid(row=0, column=1, columnspan=3, sticky='we')

start_hour = tk.StringVar()
start_mint = tk.StringVar()
ttk.Label(text='Time In:').grid(row=1, column=0, sticky='e')
ttk.Spinbox(textvariable=start_hour, values=hours, state='readonly', wrap=True, width=3).grid(row=1, column=1, sticky='w')
ttk.Spinbox(textvariable=start_mint, values=mints, state='readonly', wrap=True, width=3).grid(row=1, column=2, columnspan=2, sticky='w')

end_hour = tk.StringVar()
end_mint = tk.StringVar()
ttk.Label(text='Time Out:').grid(row=2, column=0, sticky='e')
ttk.Spinbox(textvariable=end_hour, values=hours, state='readonly', wrap=True, width=3).grid(row=2, column=1, sticky='w')
ttk.Spinbox(textvariable=end_mint, values=mints, state='readonly', wrap=True, width=3).grid(row=2, column=2, columnspan=2, sticky='w')

for pos, field in enumerate(fields):
    field['var'] = tk.StringVar()
    ttk.Label(text=field['name']+':').grid(row=3+pos, column=0, sticky='e')
    ttk.Combobox(textvariable=field['var'], values=field['values'], state='readonly').grid(row=3+pos, column=1, columnspan=3, sticky='ew')

students = tk.IntVar()
ttk.Label(text='No. of Students:').grid(row=4+pos, column=0, sticky='e')
ttk.Spinbox(textvariable=students, from_=1, to=9, state='readonly', width=2).grid(row=4+pos, column=1, sticky='w')

full_room = tk.StringVar()
ttk.Label(text='Was the room full?').grid(row=4+pos, column=2, sticky='e')
ttk.Checkbutton(variable=full_room, offvalue='No', onvalue='Yes').grid(row=4+pos, column=3, sticky='e')

def submit_func():
    if '' in get_vars().values():
        messagebox.showinfo(message='Please fill in all the fields.')
    else:
        data, filename = load_data(filename=filename_data)
        data.active.append(list(get_vars().values()))
        save_file(data, filename)
        init_vars()        
submit_button = ttk.Button(text='Submit', command=submit_func)
submit_button.grid(row=5+pos, column=0, columnspan=2)

def del_func():
    del_window = tk.Toplevel(window)
    del_window.title('Data')
    del_window.iconbitmap(icon_path)
    del_window.resizable(False, False)
    del_window.attributes('-topmost', 'true')
    del_window.grab_set()

    data, filename = load_data(filename=filename_data)
    columns = [cell.value for cell in data.active[1]]
    table = ttk.Treeview(del_window, columns=columns, show='headings', selectmode='browse')
    for col in columns:
        table.heading(col, text=col, anchor=tk.CENTER)
        table.column(col, stretch=False, anchor=tk.CENTER, width=100)
    for row in data.active.iter_rows(min_row=2):
        table.insert(parent='', index='end', values=[cell.value for cell in row])
    save_file(data, filename)
    table.grid(row=0, column=0)

    vsb = ttk.Scrollbar(del_window, orient="vertical", command=table.yview)
    vsb.grid(row=0, column=1, sticky='ns')
    table.configure(yscrollcommand=vsb.set)

    def del_selection(event):
        confirmation = messagebox.askquestion(parent=del_window, message='Are you sure you would like to delete this entry?')
        if confirmation == 'no':
            pass
        else:
            row_num = table.index(table.selection()) + 2
            data, filename = load_data(filename=filename_data)
            data.active.delete_rows(row_num, 1)
            save_file(data, filename)
            del_window.destroy()
    table.bind("<<TreeviewSelect>>", del_selection)
del_button = ttk.Button(text='Delete...', command=del_func)
del_button.grid(row=5+pos, column=2, columnspan=2)

def init_vars():
    date.set(datetime.datetime.now().strftime("%d/%m/%Y"))
    start_hour.set('12')
    start_mint.set('00')
    end_hour.set('12')
    end_mint.set('00')
    for field in fields:
        field['var'].set(field['default'] or '')
    students.set(1)
    full_room.set('No')

def get_vars():
    start_time = datetime.datetime.strptime(start_hour.get() +':' + start_mint.get(), '%H:%M')
    end_time = datetime.datetime.strptime(end_hour.get() +':' + end_mint.get(), '%H:%M')
    diff_time = end_time - start_time
    vars = {'Date' : date.get(), 'Time In' : start_time.strftime('%H:%M'), 'Time Out' : end_time.strftime('%H:%M'), 'Time of Session' : str(diff_time)[:-3], 'Number of identical queries' : students.get(), 'Room Full?' : full_room.get()}
    for field in fields:
        vars[field['name']] = field['var'].get()
    return vars

init_vars()
window.mainloop()