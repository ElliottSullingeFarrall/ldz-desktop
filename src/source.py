from utils import *

#TODO: Add 'Staff' field with options LDA, LDL, MASA, FY (tick boxes)
#TODO: Uninstaller?

# ---------------------------------------------------------------------------- #
#                                 Base Classes                                 #
# ---------------------------------------------------------------------------- #

class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.profile: Profile = None

        self.style: ttk.Style = ttk.Style()
        self.style.theme_use('clam')

        self.title('Select Profile')
        self.iconphoto(True, tk.PhotoImage(file=resource_path('images/stag.png')))
        self.resizable(False, False)
        self.geometry('250x100')

        self.profiles: dict[str, Profile] = {profile.name : profile for profile in Profile.__subclasses__()}

        table: ttk.Treeview = ttk.Treeview(self, columns='Profile', show='headings', selectmode='browse')
        for col in table['columns']:
            table.heading(col,  anchor=tk.CENTER, text=col)
            table.column(col,   anchor=tk.CENTER, stretch=False, width=250)
        for profile in self.profiles:
            table.insert(parent='', index='end', values=(profile,))
        table.bind('<Motion>', 'break')
        table.pack(fill='both', expand='True')

        def select_profile(event: tk.Event):
            profile_name: str = table.item(table.focus())['values'][0]
            self.withdraw()
            self.profile: Profile = self.profiles[profile_name](self)
            self.profile.mainloop()
        table.bind("<<TreeviewSelect>>", select_profile)

class Profile(tk.Tk):
    def __init__(self, app) -> None:
        super().__init__()
        self.name: str = '' if not hasattr(self, 'name') else self.name
        self.app: App = app

        self.title(f'LDZ - {self.name}')
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", lambda: [self.destroy(), app.destroy()])

        menubar: tk.Menu  = tk.Menu(self)
        profmenu: tk.Menu = tk.Menu(menubar, tearoff=False)
        datamenu: tk.Menu = tk.Menu(menubar, tearoff=False)
        profmenu.add_command(label='Switch Profile',    command=self.switch_profile)
        datamenu.add_command(label='View/Delete Data',  command=self.view_data)
        datamenu.add_separator()
        datamenu.add_command(label='Import Data...',    command=self.import_data)
        datamenu.add_command(label='Export Data...',    command=self.export_data)
        menubar.add_cascade(label='Profile',            menu=profmenu)
        menubar.add_cascade(label='Data',               menu=datamenu)
        self.config(menu=menubar)

    def layout(self):
        pass

    def mainloop(self) -> None:
        self.fields: list[Field] = []
        self.df_curr: dict[str, str] = {}

        self.layout()
        Submit(self)

        for field in self.fields:
            field.update()

        self.filename: str = os.path.join(DATA_DIR, self.name + os.extsep + 'csv')
        try:
            self.df_save: pd.DataFrame = pd.read_csv(self.filename, dtype=str, na_filter=False)
        except (FileNotFoundError, pd.errors.EmptyDataError):
            self.df_save: pd.DataFrame = pd.DataFrame(columns=self.df_curr.keys())

        super().mainloop()

    def save_data(self) -> None:
        self.df_save.to_csv(self.filename, index=False)

    def view_data(self) -> None:
        window: tk.Toplevel = tk.Toplevel(self)
        window.title('View Data')
        window.resizable(False, False)
        window.attributes('-topmost', 'true')
        window.grab_set()

        table: ttk.Treeview = ttk.Treeview(window, columns=tuple(self.df_save.columns), show='headings', selectmode='browse')
        for col in table['columns']:
            table.heading(col, text=col, anchor=tk.CENTER)
            table.column(col, stretch=False, anchor=tk.CENTER, width=100)
        for _, row in self.df_save.iterrows():
            table.insert(parent='', index='end', values=tuple(row.values))
        table.bind('<Motion>', 'break')
        table.gridx(row=0, column=0)

        vsb: ttk.Scrollbar = ttk.Scrollbar(window, orient="vertical", command=table.yview)
        vsb.gridx(row=0, column=1, sticky='ns')
        table.configure(yscrollcommand=vsb.set)

        def delete_data(event: tk.Event) -> None:
            answer: str = messagebox.askquestion(parent=window, title='Delete Data', message='Are you sure you would like to delete this entry?')
            if answer == 'no':
                pass
            else:
                row_num: int = table.index(table.selection())
                self.df_save: pd.DataFrame = self.df_save.drop(row_num)
                self.save_data()
                window.destroy()
        table.bind("<<TreeviewSelect>>", delete_data)

    def import_data(self) -> None:
        paths: tuple[str] = filedialog.askopenfilenames(parent=self, title='Import Data', initialdir='/', filetypes=[('excel files', '*.xlsx')])
        if paths:
            answer: Union[bool, None] = messagebox.askyesnocancel(parent=self, title='Import Data', message='Would you like to clear the existing data? This action cannot be undone!')
            if answer:
                self.df_save: pd.DataFrame = pd.DataFrame(columns=self.df_curr.keys())
            if answer is not None:
                self.df_save: pd.DataFrame = pd.concat([self.df_save] + [pd.read_excel(path, dtype=str, na_filter=False) for path in paths])

    def export_data(self) -> None:
        path: str = filedialog.asksaveasfile(parent=self, title='Export Data', initialdir='/', filetypes=[('excel files', '*.xlsx')], defaultextension=('excel files', '*.xlsx'), mode='wb')
        if path:
            answer: Union[bool, None] = messagebox.askyesnocancel(parent=self, title='Export Data', message='Would you like to clear the existing data? This action cannot be undone!')
            if answer is not None:
                self.df_save.to_excel(path, index=False)
            if answer:
                self.df_save: pd.DataFrame = pd.DataFrame(columns=self.df_curr.keys())

    def switch_profile(self) -> None:
        self.destroy()
        self.app.deiconify()


class Field():
    def __init__(self, profile: Profile, names: tuple[str] = (''), defaults: tuple[str] = ('')) -> None:
        self.profile: Profile = profile
        self.names: tuple[str] = names
        self.defaults: tuple[str] = defaults

        self.vars: tuple[tk.StringVar] = [tk.StringVar(self.profile, value=default) for default in defaults]
        for var in self.vars:
            var.trace_add('write', self.update)

        self.row: int = len(self.profile.fields)
        self.profile.fields.append(self)

    def update(self, variable: str = '', index: str = '', mode: str = '') -> None:
        for var, name in zip(self.vars, self.names):
            self.profile.df_curr[name] = var.get()

    def reset(self) -> None:
        for var, default in zip(self.vars, self.defaults):
            var.set(default)

class Submit():
    def __init__(self, profile: Profile) -> None:
        self.profile: Profile = profile
        self.name: str = 'Submit'

        self.row: int = len(self.profile.fields)

        ttk.Button(profile, text=self.name, command=self.command, width=20).gridx(row=self.row, column=0, columnspan=5)

    def command(self) -> None:
        if '' in self.profile.df_curr.values():
            messagebox.showinfo(parent=self.profile, message='Please fill in all the fields.')
        else:
            self.profile.df_save: pd.DataFrame = pd.concat([self.profile.df_save, pd.DataFrame([self.profile.df_curr])], ignore_index=True)
            self.profile.save_data()
            for field in self.profile.fields:
                field.reset()

# ---------------------------------------------------------------------------- #
#                             Custom Field Classes                             #
# ---------------------------------------------------------------------------- #

class Date(Field):
    def __init__(self, profile: Profile, name: str = '') -> None:
        super().__init__(profile, names=(name,), defaults=(f'{datetime.now():%d/%m/%Y}',))
    
        ttk.Label(self.profile, text=f'{self.names[0]}:').gridx(row=self.row, column=0, sticky='e')
        DateEntry(self.profile, textvariable=self.vars[0], date_pattern='dd/mm/yyyy', selectmode='day', state='readonly').gridx(row=self.row, column=1, sticky='we', columnspan=5)

class Times(Field):
    def __init__(self, profile: Profile, names: tuple[str] = ('', ''), label: str = '') -> None:
        super().__init__(profile, names=names, defaults=('12', '00', '12', '00'))

        frame = ttk.Frame(self.profile)
        frame.gridx(row=self.row, column=1, sticky='w', columnspan=5)

        ttk.Label(self.profile, text=f'{label} ').gridx(row=self.row, column=0, sticky='e')
        ttk.Label(frame, text=f'{self.names[0]}:').pack(side=tk.LEFT)
        ttk.Spinbox(frame, textvariable=self.vars[0], values=[f"{hour:02}" for hour in range(0, 24, 1)], state='readonly', wrap=True, width=3).pack(side=tk.LEFT)
        ttk.Spinbox(frame, textvariable=self.vars[1], values=[f'{mint:02}' for mint in range(0, 60, 5)], state='readonly', wrap=True, width=3).pack(side=tk.LEFT)
        ttk.Label(frame, text=f'{self.names[1]}:').pack(side=tk.LEFT)
        ttk.Spinbox(frame, textvariable=self.vars[2], values=[f"{hour:02}" for hour in range(0, 24, 1)], state='readonly', wrap=True, width=3).pack(side=tk.LEFT)
        ttk.Spinbox(frame, textvariable=self.vars[3], values=[f'{mint:02}' for mint in range(0, 60, 5)], state='readonly', wrap=True, width=3).pack(side=tk.LEFT)

    def update(self, variable: str = '', index: str = '', mode: str = '') -> None:
        self.profile.df_curr[self.names[0]] = f'{datetime.strptime(f"{self.vars[0].get()}:{self.vars[1].get()}", "%H:%M"):%H:%M}'
        self.profile.df_curr[self.names[1]] = f'{datetime.strptime(f"{self.vars[2].get()}:{self.vars[3].get()}", "%H:%M"):%H:%M}'

class Nums(Field):
    def __init__(self, profile: Profile, names: tuple[str] = ('', ''), defaults: tuple[int] = (1, 1), values: tuple[list[int]] = (list(range(1, 1000)), list(range(1, 1000)))) -> None:
        super().__init__(profile, names=names, defaults=defaults)
        self.values = values

        ttk.Label(self.profile, text=f'{self.names[0]}:').gridx(row=self.row, column=0, sticky='e')
        ttk.Spinbox(self.profile, textvariable=self.vars[0], values=self.values[0], state='readonly', width=4).gridx(row=self.row, column=1, sticky='w')
        ttk.Label(self.profile, text=f'{self.names[1]}:').gridx(row=self.row, column=2, sticky='e')
        ttk.Spinbox(self.profile, textvariable=self.vars[1], values=self.values[1], state='readonly', width=4).gridx(row=self.row, column=3, sticky='w', columnspan=3)

class Text(Field):
    def __init__(self, profile: Profile, name: str = '') -> None:
        super().__init__(profile, names=(name,), defaults=('',))

        ttk.Label(self.profile, text=f'{self.names[0]}:').gridx(row=self.row, column=0, sticky='e')
        ttk.Entry(self.profile, textvariable=self.vars[0]).gridx(row=self.row, column=1, sticky='ew', columnspan=5)

class Choice(Field):
    def __init__(self, profile: Profile, name: str = '', default: str = '', values: list[str] = ['']) -> None:
        super().__init__(profile, names=(name,), defaults=(default,))
        self.values = values

        ttk.Label(self.profile, text=f'{self.names[0]}:').gridx(row=self.row, column=0, sticky='e')
        ttk.Combobox(self.profile, textvariable=self.vars[0], values=self.values, state='readonly').gridx(row=self.row, column=1, sticky='ew', columnspan=5)

class ChoCho(Field):
    def __init__(self, profile: Profile, names: tuple[str] = ('', ''), default: str = '', off_value: str = '', on_value: str = '', values: tuple[list[str]] = ([''], [''])) -> None:
        super().__init__(profile, names=names, defaults=(default, off_value))
        self.default = default
        self.off_value = off_value
        self.on_value = on_value
        self.values = values

        ttk.Label(self.profile, text=f'{self.names[0]}:').gridx(row=self.row, column=0, sticky='e')
        self.field0 = ttk.Combobox(self.profile, textvariable=self.vars[0], values=self.values[0], state='readonly', width=12).gridx(row=self.row, column=1, sticky='w')
        ttk.Label(self.profile, text=f'{self.names[1]}:').gridx(row=self.row, column=2, sticky='e')
        self.field1 = ttk.Combobox(self.profile, textvariable=self.vars[1], values=self.values[1], state='readonly', width=10).gridx(row=self.row, column=3, sticky='ew', columnspan=3)

    def update(self, variable: str = '', index: str = '', mode: str = '') -> None:
        self.profile.df_curr[self.names[0]] = self.vars[0].get()
        if self.vars[0].get() == self.default:
            self.field1['state']  = 'readonly'
            if self.vars[1].get() == self.on_value:
                self.vars[1].set(self.off_value)
        else:
            self.field1['state'] = 'disabled'
            self.vars[1].set(self.on_value)
        self.profile.df_curr[self.names[1]] = self.vars[1].get()

class ChkCho(Field):
    def __init__(self, profile: Profile, names: tuple[str] = ('', ''), default: str = 'No', off_value: str = 'N/A', on_value: str = '', values: list[str] = ['']) -> None:
        super().__init__(profile, names=names, defaults=(default, off_value))
        self.default = default
        self.off_value = off_value
        self.on_value = on_value
        self.values = values

        ttk.Label(self.profile, text=f'{self.names[0]}:').gridx(row=self.row, column=0, sticky='e')
        self.field0 = ttk.Checkbutton(self.profile, variable=self.vars[0], offvalue='No', onvalue='Yes').gridx(row=self.row, column=1, sticky='w')
        ttk.Label(self.profile, text=f'{self.names[1]}:').gridx(row=self.row, column=2, sticky='e')
        self.field1 = ttk.Combobox(self.profile, textvariable=self.vars[1], values=self.values, state='readonly', width=10).gridx(row=self.row, column=3, sticky='ew', columnspan=3)

    def update(self, variable: str = '', index: str = '', mode: str = '') -> None:
        self.profile.df_curr[self.names[0]] = self.vars[0].get()
        if self.vars[0].get() == self.default:
            self.field1['state']  = 'disabled'
            self.vars[1].set(self.off_value)
        else:
            self.field1['state'] = 'readonly'
            if self.vars[1].get() == self.off_value:
                self.vars[1].set(self.on_value)
        self.profile.df_curr[self.names[1]] = self.vars[1].get()

class NumChk(Field):
    def __init__(self, profile: Profile, names: tuple[str] = ('', ''), defaults: tuple[int, str] = (1, 'No')):
        super().__init__(profile, names=names, defaults=defaults)

        ttk.Label(self.profile, text=f'{self.names[0]}:').gridx(row=self.row, column=0, sticky='e')
        ttk.Spinbox(self.profile, textvariable=self.vars[0], values=tuple(range(1,1000)), state='readonly', width=4).gridx(row=self.row, column=1, sticky='w')
        ttk.Label(self.profile, text=f'{self.names[1]}:').gridx(row=self.row, column=4, sticky='e')
        ttk.Checkbutton(self.profile, variable=self.vars[1], offvalue='No', onvalue='Yes').gridx(row=self.row, column=5, sticky='w')

# ---------------------------------------------------------------------------- #
#                            Custom Profile Classes                            #
# ---------------------------------------------------------------------------- #

class MASA(Profile):
    name = 'MASA'

    def layout(self) -> None:
        Date(self,      name  =  'Date'),
        Times(self,     names = ('In', 'Out'), label = 'Time'),
        Choice(self,    name  =  'Department',              values =  [
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
        'Veterinary Medicine']),
        Choice(self,    name  =  'Query 1',                 values =  [
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
        'Statistics: Other']),
        Choice(self,    name  =  'Query 2',                 values =  [
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
        'Statistics: Other'], default = 'N/A'),
        Choice(self,    name  =  'Level',                   values =  [
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
        'Not collected']),
        ChoCho(self,    names = ('Format', 'Location'),     values = ([
        'In Person',
        'Online'], [
        'Stag Hill',
        'Manor Park',
        'Off-Campus',
        'Kate Granger']), default = 'In Person', off_value = 'Stag Hill', on_value = 'Online'),
        ChkCho(self,    names = ('Appointment', 'Status'),  values =  [
        'Attended',
        'No Show',
        'Cancelled'], on_value = 'Attended'),
        NumChk(self,    names = ('# Students', 'Project'))

class ASND(Profile):
    name = 'AS&D'

    def layout(self):
        Date(self,      name  =  'Date')
        Times(self,     names = ('In', 'Out'), label = 'Time')
        Choice(self,    name  =  'Department',              values = [
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
        Choice(self,    name  =  'Query 1',                 values =  [
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
        Choice(self,    name  =  'Query 2',                 values =  [
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
            'Learning journey: Transition to university/UK academic setting'], default = 'N/A')
        Choice(self,    name  =  'Level',                   values =  [
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
        ChoCho(self,    names = ('Format', 'Location'),     values = ([
            'In Person',
            'Online'], [
            'Stag Hill',
            'Manor Park',
            'Off-Campus',
            'Kate Granger']), default = 'In Person', off_value = 'Stag Hill', on_value = 'Online')
        ChkCho(self,    names = ('Appointment', 'Status'),  values =  [
            'Attended',
            'No Show',
            'Cancelled'], on_value = 'Attended')
        NumChk(self,    names = ('# Students', 'Project'))

class Embd(Profile):
    name = 'Embedded'

    def layout(self):
        Date(self,      name  =  'Date')
        Nums(self,      names = ('Workshop Length', 'Preparation Time'),    values = ([
            f'{0.25*i:.2f}' for i in range(1, 11)], [
            f'{0.50*i:.2f}' for i in range(1, 11)]), defaults = ('0.25', '0.50'))
        Text(self,      name  =  'Workshop Name')
        Text(self,      name  =  'Module')
        Choice(self,    name  =  'Department',                              values =  [
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
        Choice(self,    name  =  'Topic 1',                                 values =  [
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
        Choice(self,    name  =  'Topic 2',                                 values =  [
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
            'Learning journey: Transition to university/UK academic setting'], default = 'N/A')
        Choice(self,    name  =  'Level',                                   values =  [
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
        Choice(self,    name  =  'Location',                                values =  [
            'Stag Hill',
            'Manor Park',
            'Off-Campus',
            'Kate Granger'], default = 'Stag Hill')
        Choice(self,    name  =  'Type',                                    values =  [
            'Department - synchronous taught',
            'Department - synchronous Q+A',
            'Department - asynchronous (panopto recording)',
            'Discussion Forum',
            'Professional Service',
            'WPO'])
        Choice(self,    name  =  'Contextualisation',                       values =  [
            'None',
            'Minimal',
            'Significant',
            'Full'
        ])
        Choice(self,    name  =  'Assessment Related',                      values =  [
            'No',
            'Partially',
            'Directly'
        ])
        ChkCho(self,    names = ('Resources', 'Applications'),              values =  [
            'Not applicable to other workshops',
            'Is applicable to other workshops'], on_value = 'Not applicable to other workshops')
        Nums(self,      names = ('Expected', 'Arrived'))

# ---------------------------------------------------------------------------- #
#                                    Script                                    #
# ---------------------------------------------------------------------------- #

FILE_EXT = os.path.splitext(sys.argv[0])[1]

if __name__ == '__main__':
    if FILE_EXT == '.py':
        DATA_DIR = os.getcwd()
    os.makedirs(DATA_DIR, exist_ok=True); os.chdir(DATA_DIR)
    App().mainloop()