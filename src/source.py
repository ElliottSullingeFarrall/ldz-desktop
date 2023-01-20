import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from tkcalendar import DateEntry

from datetime import datetime

import pandas as pd

import os
import sys
import appdirs

from utils import *

from compiler import compile

#TODO: Add 'Staff' field with options LDA, LDL, MASA, FY (tick boxes)
#TODO: Switch 'Department' to 'School'
#TODO: Update README
#TODO: Uninstaller?

# -------------------------------- UI Elements ------------------------------- #

class FieldDate():
    def __init__(self, profile, name=''):
        self.name = name

        self.date = tk.StringVar(value=f'{datetime.now():%d/%m/%Y}')

        self.date.trace_add('write', lambda var, index, mode : self.update(profile))

        ttk.Label(text=f'{self.name}:').gridx(row=len(profile.fields), column=0, sticky='e')
        DateEntry(textvariable=self, date_pattern='dd/mm/yyyy', selectmode='day', state='readonly').gridx(row=len(profile.fields), column=1, sticky='we', columnspan=5)

        profile.fields.append(self)

    def update(self, profile):
        profile.df_curr[self.name] = self.date.get()

    def reset(self):
        self.date.set(f"{datetime.now():%d/%m/%Y}")

class FieldTimes():
    def __init__(self, profile, name=('', ''), label=''):
        self.name1, self.name2 = name
        self.label = label

        self.hour1 = tk.StringVar(value='12')
        self.mint1 = tk.StringVar(value='00')
        self.hour2 = tk.StringVar(value='12')
        self.mint2 = tk.StringVar(value='00')

        self.hour1.trace_add('write', lambda var, index, mode : self.update(profile))
        self.mint1.trace_add('write', lambda var, index, mode : self.update(profile))
        self.hour2.trace_add('write', lambda var, index, mode : self.update(profile))
        self.mint2.trace_add('write', lambda var, index, mode : self.update(profile))

        frame = ttk.Frame(profile)
        frame.gridx(row=len(profile.fields), column=1, sticky='w', columnspan=5)

        ttk.Label(text=f'{self.label} ').gridx(row=len(profile.fields), column=0, sticky='e')
        ttk.Label(frame, text=f'{self.name1}:').pack(side=tk.LEFT)
        ttk.Spinbox(frame, textvariable=self.hour1, values=[f"{hour:02}" for hour in range(0, 24, 1)], state='readonly', wrap=True, width=3).pack(side=tk.LEFT)
        ttk.Spinbox(frame, textvariable=self.mint1, values=[f'{mint:02}' for mint in range(0, 60, 5)], state='readonly', wrap=True, width=3).pack(side=tk.LEFT)
        ttk.Label(frame, text=f'{self.name2}:').pack(side=tk.LEFT)
        ttk.Spinbox(frame, textvariable=self.hour2, values=[f"{hour:02}" for hour in range(0, 24, 1)], state='readonly', wrap=True, width=3).pack(side=tk.LEFT)
        ttk.Spinbox(frame, textvariable=self.mint2, values=[f'{mint:02}' for mint in range(0, 60, 5)], state='readonly', wrap=True, width=3).pack(side=tk.LEFT)

        profile.fields.append(self)

    def update(self, profile):
        profile.df_curr[self.name1] = f'{datetime.strptime(f"{self.hour1.get()}:{self.mint1.get()}", "%H:%M"):%H:%M}'
        profile.df_curr[self.name2] = f'{datetime.strptime(f"{self.hour2.get()}:{self.mint2.get()}", "%H:%M"):%H:%M}'

    def reset(self):
        self.hour1.set('12')
        self.mint1.set('00')
        self.hour2.set('12')
        self.mint2.set('00')

class FieldNums():
    def __init__(self, profile, name=('', ''), default=(1, 1), values=(list(range(1, 1000)), list(range(1, 1000)))):
        self.name1, self.name2 = name
        self.values1, self.values2 = values
        self.default1, self.default2 = default

        self.var1 = tk.StringVar(value=self.default1)
        self.var2 = tk.StringVar(value=self.default2)

        self.var1.trace_add('write', lambda var, index, mode : self.update(profile))
        self.var2.trace_add('write', lambda var, index, mode : self.update(profile))

        ttk.Label(text=f'{self.name1}:').gridx(row=len(profile.fields), column=0, sticky='e')
        ttk.Spinbox(textvariable=self.var1, values=self.values1, state='readonly', width=4).gridx(row=len(profile.fields), column=1, sticky='w')
        ttk.Label(text=f'{self.name2}:').gridx(row=len(profile.fields), column=2, sticky='e')
        ttk.Spinbox(textvariable=self.var2, values=self.values2, state='readonly', width=4).gridx(row=len(profile.fields), column=3, sticky='w', columnspan=3)

        profile.fields.append(self)

    def update(self, profile):
        profile.df_curr[self.name1] = self.var1.get()
        profile.df_curr[self.name2] = self.var2.get()

    def reset(self):
        self.var1.set(self.default1)
        self.var2.set(self.default2)

class FieldText():
    def __init__(self, profile, name=''):
        self.name = name

        self.var = tk.StringVar('')

        self.var.trace_add('write', lambda var, index, mode : self.update(profile))

        ttk.Label(text=f'{self.name}:').gridx(row=len(profile.fields), column=0, sticky='e')
        ttk.Entry(textvariable=self.var).gridx(row=len(profile.fields), column=1, sticky='ew', columnspan=5)

        profile.fields.append(self)

    def update(self, profile):
        profile.df_curr[self.name] = self.var.get()
        
    def reset(self):
        self.var.set('')

class FieldChoice():
    def __init__(self, profile, name='', default='', values=[], link_fun=lambda : None):
        self.name = name
        self.values = values
        self.default = default
        self.link_fun = link_fun

        self.var = tk.StringVar(value=self.default)

        self.var.trace_add('write', lambda var, index, mode : self.update(profile))

        ttk.Label(text=f'{self.name}:').gridx(row=len(profile.fields), column=0, sticky='e')
        ttk.Combobox(textvariable=self.var, values=self.values, state='readonly').gridx(row=len(profile.fields), column=1, sticky='ew', columnspan=5)

        profile.fields.append(self)

    def update(self, profile):
        self.link_fun()
        profile.df_curr[self.name] = self.var.get()

    def reset(self):
        self.var.set(self.default)

class FieldChoCho():
    def __init__(self, profile, name=('', ''), default='', off_value='', on_value='', values=([], [])):
        self.name1, self.name2 = name
        self.values1, self.values2 = values
        self.default = default
        self.off_value = off_value
        self.on_value = on_value

        self.var1 = tk.StringVar(value=self.default)
        self.var2 = tk.StringVar(value=self.off_value)

        self.var1.trace_add('write', lambda var, index, mode : self.update1(profile))
        self.var2.trace_add('write', lambda var, index, mode : self.update2(profile))

        ttk.Label(text=f'{self.name1}:').gridx(row=len(profile.fields), column=0, sticky='e')
        self.field1 = ttk.Combobox(textvariable=self.var1, values=self.values1, state='readonly', width=12).gridx(row=len(profile.fields), column=1, sticky='w')
        ttk.Label(text=f'{self.name2}:').gridx(row=len(profile.fields), column=2, sticky='e')
        self.field2 = ttk.Combobox(textvariable=self.var2, values=self.values2, state='readonly', width=10).gridx(row=len(profile.fields), column=3, sticky='ew', columnspan=3)

        profile.fields.append(self)

    def update(self, profile):
        self.update1(profile)
        self.update2(profile)

    def update1(self, profile):
        profile.df_curr[self.name1] = self.var1.get()
        if self.var1.get() == self.default:
            self.field2['state']  = 'readonly'
            self.var2.set(self.off_value)
        else:
            self.field2['state'] = 'disabled'
            self.var2.set(self.on_value)

    def update2(self, profile):
        profile.df_curr[self.name2] = self.var2.get()

    def reset(self):
        self.var1.set(self.default)
        self.var2.set(self.off_value)

class FieldChkCho():
    def __init__(self, profile, name=('', ''), default='No', off_value='N/A', on_value='', values=[]):
        self.name1, self.name2 = name
        self.values = values
        self.default = default
        self.off_value = off_value
        self.on_value = on_value

        self.var1 = tk.StringVar(value=self.default)
        self.var2 = tk.StringVar(value=self.off_value)

        self.var1.trace_add('write', lambda var, index, mode : self.update1(profile))
        self.var2.trace_add('write', lambda var, index, mode : self.update2(profile))

        ttk.Label(text=f'{self.name1}:').gridx(row=len(profile.fields), column=0, sticky='e')
        self.field1 = ttk.Checkbutton(variable=self.var1, offvalue='No', onvalue='Yes').gridx(row=len(profile.fields), column=1, sticky='w')
        ttk.Label(text=f'{self.name2}:').gridx(row=len(profile.fields), column=2, sticky='e')
        self.field2 = ttk.Combobox(textvariable=self.var2, values=self.values, state='readonly', width=10).gridx(row=len(profile.fields), column=3, sticky='ew', columnspan=3)

        profile.fields.append(self)

    def update(self, profile):
        self.update1(profile)
        self.update2(profile)

    def update1(self, profile):
        profile.df_curr[self.name1] = self.var1.get()
        if self.var1.get() == self.default:
            self.field2['state']  = 'disabled'
            self.var2.set(self.off_value)
        else:
            self.field2['state'] = 'readonly'
            self.var2.set(self.on_value)

    def update2(self, profile):
        profile.df_curr[self.name2] = self.var2.get()

    def reset(self):
        self.var1.set(self.default)
        self.var2.set(self.off_value)

class FieldNumChkChk():
    def __init__(self, profile, name=('', '', ''), default=(1, 'No', 'No')):
        self.name1, self.name2, self.name3 = name
        self.default1, self.default2, self.default3 = default

        self.var1 = tk.StringVar(value=self.default1)
        self.var2 = tk.StringVar(value=self.default2)
        self.var3 = tk.StringVar(value=self.default3)

        self.var1.trace_add('write', lambda var, index, mode : self.update(profile))
        self.var2.trace_add('write', lambda var, index, mode : self.update(profile))
        self.var3.trace_add('write', lambda var, index, mode : self.update(profile))

        ttk.Label(text=f'{self.name1}:').gridx(row=len(profile.fields), column=0, sticky='e')
        ttk.Spinbox(textvariable=self.var1, values=tuple(range(1,1000)), state='readonly', width=4).gridx(row=len(profile.fields), column=1, sticky='w')
        ttk.Label(text=f'{self.name2}:').gridx(row=len(profile.fields), column=2, sticky='e')
        ttk.Checkbutton(variable=self.var2, offvalue='No', onvalue='Yes').gridx(row=len(profile.fields), column=3, sticky='w')
        ttk.Label(text=f'{self.name3}:').gridx(row=len(profile.fields), column=4, sticky='e')
        ttk.Checkbutton(variable=self.var3, offvalue='No', onvalue='Yes').gridx(row=len(profile.fields), column=5, sticky='w')

        profile.fields.append(self)

    def update(self, profile):
        profile.df_curr[self.name1] = self.var1.get()
        profile.df_curr[self.name2] = self.var2.get()
        profile.df_curr[self.name3] = self.var3.get()

    def reset(self):
        self.var1.set(self.default1)
        self.var2.set(self.default2)
        self.var3.set(self.default3)

class ActionSubmit():
    def __init__(self, profile):
        self.name = 'Submit'

        ttk.Button(text=self.name, command=lambda : self.command(profile)).gridx(row=profile.grid_size()[1], column=0, columnspan=5)

    def command(self, profile):
        if '' in profile.df_curr.values():
            messagebox.showinfo(parent=profile, message='Please fill in all the fields.')
        else:
            profile.df_save = pd.concat([profile.df_save, pd.DataFrame([profile.df_curr])], ignore_index=True)
            profile.save()
        for field in profile.fields:
            field.reset()

# -------------------------------- Interfaces -------------------------------- #

class ProfileSwitcher(tk.Tk):
    def __init__(self):
        super().__init__()

        self.style = ttk.Style()
        self.style.theme_use('clam')

        self.title('Select Profile')
        self.iconphoto(True, tk.PhotoImage(file=resource_path('images/stag.png')))
        self.resizable(False, False)
        self.geometry('250x100')

        table = ttk.Treeview(self, columns='Profile', show='headings', selectmode='browse')
        for col in table['columns']:
            table.heading(col,  anchor=tk.CENTER, text=col)
            table.column(col,   anchor=tk.CENTER, stretch=False, width=250)
        for profile in profiles:
            table.insert(parent='', index='end', values=(profile,))
        table.bind('<Motion>', 'break')
        table.pack(fill='both', expand='True')

        def select(event):
            profile_name = table.item(table.focus())['values'][0]
            self.destroy()
            profile = profiles[profile_name]()
            profile.mainloop()
        table.bind("<<TreeviewSelect>>", select)

class ProfileMaster(tk.Tk):
    def __init__(self):
        super().__init__()

        self.fields = []

        self.title(f'LDZ - {self.name}')
        self.iconphoto(True, tk.PhotoImage(file=resource_path('images/stag.png')))
        self.resizable(False, False)

        menubar = tk.Menu(self)
        profmenu = tk.Menu(menubar, tearoff=False)
        datamenu = tk.Menu(menubar, tearoff=False)
        profmenu.add_command(label='Switch Profile',    command=self.switch)
        datamenu.add_command(label='View/Delete Data',  command=self.view)
        datamenu.add_separator()
        datamenu.add_command(label='Import Data...',    command=self.import_data)
        datamenu.add_command(label='Export Data...',    command=self.export_data)
        menubar.add_cascade(label='Profile',            menu=profmenu)
        menubar.add_cascade(label='Data',               menu=datamenu)
        self.config(menu=menubar)

    def layout(self):
        self.submit = ActionSubmit(self)

    def data(self):
        self.df_curr = {}
        for field in self.fields:
            field.update(self)

        self.filename = os.path.join(data_dir, self.name + os.extsep + 'csv')
        print(self.filename)
        try:
            self.df_save = pd.read_csv(self.filename, dtype=str, na_filter=False)
        except (FileNotFoundError, pd.errors.EmptyDataError):
            self.df_save = pd.DataFrame(columns=self.df_curr.keys())

    def view(self):
        window = tk.Toplevel(self)
        window.title('View Data')
        window.resizable(False, False)
        window.attributes('-topmost', 'true')
        window.grab_set()

        table = ttk.Treeview(window, columns=tuple(self.df_save.columns), show='headings', selectmode='browse')
        for col in table['columns']:
            table.heading(col, text=col, anchor=tk.CENTER)
            table.column(col, stretch=False, anchor=tk.CENTER, width=100)
        for idx, row in self.df_save.iterrows():
            table.insert(parent='', index='end', values=tuple(row.values))
        table.bind('<Motion>', 'break')
        table.gridx(row=0, column=0)

        vsb = ttk.Scrollbar(window, orient="vertical", command=table.yview)
        vsb.gridx(row=0, column=1, sticky='ns')
        table.configure(yscrollcommand=vsb.set)

        def delete(event):
            answer = messagebox.askquestion(parent=window, title='Delete Data', message='Are you sure you would like to delete this entry?')
            if answer == 'no':
                pass
            else:
                row_num = table.index(table.selection())
                self.df_save = self.df_save.drop(row_num)
                self.save()
                window.destroy()
        table.bind("<<TreeviewSelect>>", delete)

    def import_data(self):
        paths = filedialog.askopenfilenames(parent=self, title='Import Data', initialdir='/', filetypes=[('excel files', '*.xlsx')])
        if paths:
            answer = messagebox.askyesnocancel(parent=self, title='Import Data', message='Would you like to clear the existing data? This action cannot be undone!')
            if answer:
                self.df_save = pd.DataFrame(columns=self.df_curr.keys())
            if answer is not None:
                self.df_save = pd.concat([self.df_save] + [pd.read_excel(path, dtype=str, na_filter=False) for path in paths])

    def export_data(self):
        path = filedialog.asksaveasfile(parent=self, title='Export Data', initialdir='/', filetypes=[('excel files', '*.xlsx')], defaultextension=('excel files', '*.xlsx'), mode='wb')
        if path:
            answer = messagebox.askyesnocancel(parent=self, title='Export Data', message='Would you like to clear the existing data? This action cannot be undone!')
            if answer is not None:
                self.df_save.to_excel(path, index=False)
            if answer:
                self.df_save = pd.DataFrame(columns=self.df_curr.keys())
                
    def save(self):
        self.df_save.to_csv(self.filename, index=False)

    def switch(self):
        self.destroy()
        profile = ProfileSwitcher()
        profile.mainloop()

class ProfileMASA(ProfileMaster):
    def __init__(self):
        self.name = 'MASA'
        super().__init__()

        self.layout()
        super().data()

    def layout(self):
        self.date       = FieldDate(self,       name='Date')
        self.time       = FieldTimes(self,      name=('In', 'Out'), label='Time')
        self.department = FieldChoice(self,     name='Department',              values=[
            'Unknown',
            'Careers',
            'Biosciences and Medicine',
            'Business School',
            'Centre for Environment and Sustainability',
            'Chemical and Process Engineering',
            'Chemistry',
            'Civil and Environmental Engineering',
            'Computer Science',
            'Economics',
            'Electrical and Electronic Engineering',
            'Guildford School of Acting',
            'Health Sciences',
            'Higher Education',
            'Hospitality and Tourism Management',
            'Law',
            'Literature and Languages',
            'Mathematics',
            'Mechanical Engineering Sciences',
            'Music and Media',
            'Physics',
            'Politics',
            'Psychology',
            'Sociology',
            'Technology Enhanced Learning',
            'Veterinary Medicine'])
        self.query1     = FieldChoice(self,     name='Query 1',                 values=[
            'Maths: Algebra',
            'Maths: Calculus',
            'Maths: Complex Numbers',
            'Maths: Numeracy',
            'Maths: Trigonometry',
            'Maths: Vector Calculus',
            'Maths: Other',
            'Software: Excel',
            'Software: LaTeX',
            'Software: Matlab',
            'Software: R',
            'Software: SPSS',
            'Software: Other',
            'Statistics: Data Collection',
            'Statistics: Data Presentation',
            'Statistics: Statistical Testing',
            'Statistics: Statistical Theory',
            'Statistics: Other'])
        self.query2     = FieldChoice(self,     name='Query 2',                 values=[
            'N/A',
            'Maths: Algebra',
            'Maths: Calculus',
            'Maths: Complex Numbers',
            'Maths: Numeracy',
            'Maths: Trigonometry',
            'Maths: Vector Calculus',
            'Maths: Other',
            'Software: Excel',
            'Software: LaTeX',
            'Software: Matlab',
            'Software: R',
            'Software: SPSS',
            'Software: Other',
            'Statistics: Data Collection',
            'Statistics: Data Presentation',
            'Statistics: Statistical Testing',
            'Statistics: Statistical Theory',
            'Statistics: Other'], default='N/A')
        self.level      = FieldChoice(self,     name='Level',                   values=[
            'Pre-Entry (SISC)',
            'Level 3 - Foundation',
            'Level 4 - 1st year',
            'Level 5 - 2nd year',
            'Level 6 - 3rd to final year',
            'Placement Year',
            'Level 7 - Masters',
            'Level 8 - PhD',
            'Staff',
            'Other',
            'Not collected'])
        self.format     = FieldChoCho(self,     name=('Format', 'Location'),    values=([
            'Face-to-Face',
            'Online'], [
            'Stag Hill',
            'Manor Park',
            'Off-Campus']), default='Face-to-Face', off_value='Stag Hill', on_value='Online')
        self.type       = FieldChkCho(self,     name=('Appointment', 'Status'), values=[
            'Attended',
            'No Show',
            'Cancelled'], on_value='Attended')
        self.panel      = FieldNumChkChk(self,  name=('# Students', 'Project', 'Kate Granger'))
        super().layout()

class ProfileASND(ProfileMaster):
    def __init__(self):
        self.name = 'AS&D'
        super().__init__()

        self.layout()
        super().data()

    def layout(self):
        self.date       = FieldDate(self,       name='Date')
        self.time       = FieldTimes(self,      name=('In', 'Out'), label='Time')
        self.department = FieldChoice(self,     name='Department',              values=[
            'Unknown',
            'Careers',
            'Biosciences and Medicine',
            'Business School',
            'Centre for Environment and Sustainability',
            'Chemical and Process Engineering',
            'Chemistry',
            'Civil and Environmental Engineering',
            'Computer Science',
            'Economics',
            'Electrical and Electronic Engineering',
            'Guildford School of Acting',
            'Health Sciences',
            'Higher Education',
            'Hospitality and Tourism Management',
            'Law',
            'Literature and Languages',
            'Mathematics',
            'Mechanical Engineering Sciences',
            'Music and Media',
            'Physics',
            'Politics',
            'Psychology',
            'Sociology',
            'Technology Enhanced Learning',
            'Veterinary Medicine'])
        self.query1     = FieldChoice(self,     name='Query 1',                 values=[
            'Assessment: Annotated bibliography',
            'Assessment: Research proposal',
            'Assessment: Critical Article review',
            'Assessment: Presentations, Posters and digital assessment (videos etc.)',
            'Assessment: Reflective writing',
            'Assessment: Writing (reports, essays, etc.), incl. structure, paraphrasing, linking, clarity, concision, citation)',
            'Assessment: Writing a literature review',
            'Assessment process/task: Assignment planning',
            'Assessment process/task: Choosing topic/finding focus (dissertations)',
            'Assessment process/task: Interpreting criteria',
            'Assessment process/task: Interpreting feedback',
            'Assessment process/task: Interpreting Turnitin reports',
            'Assessment process/task: Literature surveys and systematic reviews',
            'Assessment process/task: Referencing',
            'Assessment process/task: Search strategies/identifying literature',
            'Assessment process/task: Sourcing and selecting evidence',
            'Academic Skills: Academic integrity referral',
            'Academic Skills: Group or teamworking, peer-based learning',
            'Academic Skills: Planning and organising time',
            'Academic Skills: Reading and note-making strategies',
            'Academic Skills: Using referencing software',
            'Academic Skills: Research design / methods/ology',
            'Academic Skills: Revision and exam strategies',
            'Critical thinking: Analysis/Writing (synthesis, evaluation, argument, position, voice)',
            'Critical thinking: Evaluating information/engaging with literature',
            'Critical thinking: Using evaluative judgement (making sense, making meaning)',
            'Learning journey: Service introduction for new students',
            'Learning journey: Transition between years/PTY/professional statements or applications',
            'Learning journey: Transition to university/UK academic setting'])
        self.query2     = FieldChoice(self,     name='Query 2',                 values=[
            'N/A'
            'Assessment: Annotated bibliography',
            'Assessment: Research proposal',
            'Assessment: Critical Article review',
            'Assessment: Presentations, Posters and digital assessment (videos etc.)',
            'Assessment: Reflective writing',
            'Assessment: Writing (reports, essays, etc.), incl. structure, paraphrasing, linking, clarity, concision, citation)',
            'Assessment: Writing a literature review',
            'Assessment process/task: Assignment planning',
            'Assessment process/task: Choosing topic/finding focus (dissertations)',
            'Assessment process/task: Interpreting criteria',
            'Assessment process/task: Interpreting feedback',
            'Assessment process/task: Interpreting Turnitin reports',
            'Assessment process/task: Literature surveys and systematic reviews',
            'Assessment process/task: Referencing',
            'Assessment process/task: Search strategies/identifying literature',
            'Assessment process/task: Sourcing and selecting evidence',
            'Academic Skills: Academic integrity referral',
            'Academic Skills: Group or teamworking, peer-based learning',
            'Academic Skills: Planning and organising time',
            'Academic Skills: Reading and note-making strategies',
            'Academic Skills: Using referencing software',
            'Academic Skills: Research design / methods/ology',
            'Academic Skills: Revision and exam strategies',
            'Critical thinking: Analysis/Writing (synthesis, evaluation, argument, position, voice)',
            'Critical thinking: Evaluating information/engaging with literature',
            'Critical thinking: Using evaluative judgement (making sense, making meaning)',
            'Learning journey: Service introduction for new students',
            'Learning journey: Transition between years/PTY/professional statements or applications',
            'Learning journey: Transition to university/UK academic setting'], default='N/A')
        self.level      = FieldChoice(self,     name='Level',                   values=[
            'Pre-Entry (SISC)',
            'Level 3 - Foundation',
            'Level 4 - 1st year',
            'Level 5 - 2nd year',
            'Level 6 - 3rd to final year',
            'Placement Year',
            'Level 7 - Masters',
            'Level 8 - PhD',
            'Staff',
            'Other',
            'Not collected'])
        self.format     = FieldChoCho(self,     name=('Format', 'Location'),    values=([
            'Face-to-Face',
            'Online'], [
            'Stag Hill',
            'Manor Park',
            'Off-Campus']), default='Face-to-Face', off_value='Stag Hill', on_value='Online')
        self.type       = FieldChkCho(self,     name=('Appointment', 'Status'), values=[
            'Attended',
            'No Show',
            'Cancelled'], on_value='Attended')
        self.panel      = FieldNumChkChk(self,  name=('# Students', 'Project', 'Kate Granger'))
        super().layout()

class ProfileEmbed(ProfileMaster):
    def __init__(self):
        self.name = 'Embedded'
        super().__init__()

        self.layout()
        super().data()

    def layout(self):
        self.date       = FieldDate(self,   name='Date')
        self.lengths    = FieldNums(self,   name=('Workshop Length', 'Preparation Time'),   values=([
            '15',
            '30',
            '45',
            '60',
            '90',
            '120',
            '180',
            '180+'], [
            '0.5',
            '1',
            '2',
            '3',
            '4',
            '5',
            '6',
            '7',
            '8'
            ]), default=('15', '0.5'))
        self.wsname     = FieldText(self,   name='Workshop Name')
        self.code       = FieldText(self,   name='Module')
        self.department = FieldChoice(self, name='Department',                              values=[
            'Unknown',
            'Careers',
            'Biosciences and Medicine',
            'Business School',
            'Centre for Environment and Sustainability',
            'Chemical and Process Engineering',
            'Chemistry',
            'Civil and Environmental Engineering',
            'Computer Science',
            'Economics',
            'Electrical and Electronic Engineering',
            'Guildford School of Acting',
            'Health Sciences',
            'Higher Education',
            'Hospitality and Tourism Management',
            'Law',
            'Literature and Languages',
            'Mathematics',
            'Mechanical Engineering Sciences',
            'Music and Media',
            'Physics',
            'Politics',
            'Psychology',
            'Sociology',
            'Technology Enhanced Learning',
            'Veterinary Medicine'])
        self.topic1     = FieldChoice(self, name='Topic 1',                                 values=[
            'Assessment: Annotated bibliography',
            'Assessment: Research proposal',
            'Assessment: Critical Article review',
            'Assessment: Presentations, Posters and digital assessment (videos etc.)',
            'Assessment: Reflective writing',
            'Assessment: Writing (reports, essays, etc.), incl. structure, paraphrasing, linking, clarity, concision, citation)',
            'Assessment: Writing a literature review',
            'Assessment process/task: Assignment planning',
            'Assessment process/task: Choosing topic/finding focus (dissertations)',
            'Assessment process/task: Interpreting criteria',
            'Assessment process/task: Interpreting feedback',
            'Assessment process/task: Interpreting Turnitin reports',
            'Assessment process/task: Literature surveys and systematic reviews',
            'Assessment process/task: Referencing',
            'Assessment process/task: Search strategies/identifying literature',
            'Assessment process/task: Sourcing and selecting evidence',
            'Academic Skills: Academic integrity referral',
            'Academic Skills: Group or teamworking, peer-based learning',
            'Academic Skills: Planning and organising time',
            'Academic Skills: Reading and note-making strategies',
            'Academic Skills: Using referencing software',
            'Academic Skills: Research design / methods/ology',
            'Academic Skills: Revision and exam strategies',
            'Critical thinking: Analysis/Writing (synthesis, evaluation, argument, position, voice)',
            'Critical thinking: Evaluating information/engaging with literature',
            'Critical thinking: Using evaluative judgement (making sense, making meaning)',
            'Learning journey: Service introduction for new students',
            'Learning journey: Transition between years/PTY/professional statements or applications',
            'Learning journey: Transition to university/UK academic setting'])
        self.topic2     = FieldChoice(self, name='Topic 2',                                 values=[
            'N/A'
            'Assessment: Annotated bibliography',
            'Assessment: Research proposal',
            'Assessment: Critical Article review',
            'Assessment: Presentations, Posters and digital assessment (videos etc.)',
            'Assessment: Reflective writing',
            'Assessment: Writing (reports, essays, etc.), incl. structure, paraphrasing, linking, clarity, concision, citation)',
            'Assessment: Writing a literature review',
            'Assessment process/task: Assignment planning',
            'Assessment process/task: Choosing topic/finding focus (dissertations)',
            'Assessment process/task: Interpreting criteria',
            'Assessment process/task: Interpreting feedback',
            'Assessment process/task: Interpreting Turnitin reports',
            'Assessment process/task: Literature surveys and systematic reviews',
            'Assessment process/task: Referencing',
            'Assessment process/task: Search strategies/identifying literature',
            'Assessment process/task: Sourcing and selecting evidence',
            'Academic Skills: Academic integrity referral',
            'Academic Skills: Group or teamworking, peer-based learning',
            'Academic Skills: Planning and organising time',
            'Academic Skills: Reading and note-making strategies',
            'Academic Skills: Using referencing software',
            'Academic Skills: Research design / methods/ology',
            'Academic Skills: Revision and exam strategies',
            'Critical thinking: Analysis/Writing (synthesis, evaluation, argument, position, voice)',
            'Critical thinking: Evaluating information/engaging with literature',
            'Critical thinking: Using evaluative judgement (making sense, making meaning)',
            'Learning journey: Service introduction for new students',
            'Learning journey: Transition between years/PTY/professional statements or applications',
            'Learning journey: Transition to university/UK academic setting'], default='N/A')
        self.level      = FieldChoice(self, name='Level',                                   values=[
            'Pre-Entry (SISC)',
            'Level 3 - Foundation',
            'Level 4 - 1st year',
            'Level 5 - 2nd year',
            'Level 6 - 3rd to final year',
            'Placement Year',
            'Level 7 - Masters',
            'Level 8 - PhD',
            'Staff',
            'Other',
            'Not collected'])
        self.location   = FieldChoice(self, name='Location',                                values=[
            'Stag Hill',
            'Manor Park',
            'Off-Campus'], default='Stag Hill')
        self.type       = FieldChoice(self, name='Type',                                    values=[
            'Department - synchronous taught',
            'Department - synchronous Q+A',
            'Department - asynchronous (panopto recording)',
            'Discussion Forum',
            'Professional Service',
            'WPO'])
        self.context    = FieldChoice(self, name='Contextualisation',                       values=[
            'None',
            'Minimal',
            'Significant',
            'Full'
        ])
        self.assess     = FieldChoice(self, name='Assessment Related',                      values=[
            'No',
            'Partially',
            'Directly'
        ])
        self.resources  = FieldChkCho(self, name=('Resources', 'Applications'),             values=[
            'Not applicable to other workshops',
            'Is applicable to other workshops'], on_value='Not applicable to other workshops')
        self.students   = FieldNums(self,   name=('Arrived', 'Expected'))

        super().layout()

# ---------------------------------- Script ---------------------------------- #

if __name__ == '__main__':
    if os.path.splitext(sys.argv[0])[1] == '.exe':
        # setup directories
        data_dir = appdirs.user_data_dir('LDZ', 'ElliottSF', roaming=True)
        os.makedirs(data_dir, exist_ok=True)
        os.chdir(data_dir)

        # initialise profile switcher
        profiles = {
            'MASA'      : ProfileMASA,
            'AS&D'      : ProfileASND,
            'Embedded'  : ProfileEmbed
            }
        profile = ProfileSwitcher()
        profile.mainloop()
    else:
        compile()