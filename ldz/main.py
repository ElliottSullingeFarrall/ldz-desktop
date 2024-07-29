'''Source code for LDZ app.
'''

from ldz.utils import *

# ---------------------------------------------------------------------------- #
#                         Base Classes - DO NOT CHANGE                         #
# ---------------------------------------------------------------------------- #

class App(tk.Tk):
    """Class for main app.

    Attributes:
        profile (Profile): Currently selected profile.
        style (ttk.Style): Tkinter style for app.
        profiles (dict[str, Profile]): Dictionary of created profiles with labels.
    """    
    def __init__(self) -> None:
        """Constructor for App class.
        """        
        super().__init__()
        self.profile: Profile = None

        self.style: ttk.Style = ttk.Style()
        self.style.theme_use('clam')

        self.title(f'Select Profile')
        self.iconphoto(True, tk.PhotoImage(file=resource_path('assets/stag.png')))
        self.resizable(False, False)
        self.geometry('250x120')

        self.profiles: dict[str, Profile] = {profile.name : profile for profile in Profile.__subclasses__()}

        table: ttk.Treeview = ttk.Treeview(self, columns='Profile', show='headings', selectmode='browse')
        for col in table['columns']:
            table.heading(col,  anchor='center', text=col)
            table.column(col,   anchor='center', stretch=False, width=250)
        for profile in self.profiles:
            table.insert(parent='', index='end', values=(profile,))
        table.bind('<Motion>', 'break')
        table.pack(fill='both', expand='True')
        raise Exception

        def select_profile(event: tk.Event):
            """Initialise profile window based on selection in treeview.

            Args:
                event (tk.Event): Tkinter event.
            """            
            profile_name: str = table.item(table.focus())['values'][0]
            self.withdraw()
            self.profile = self.profiles[profile_name](self)
            self.profile.mainloop()
        table.bind("<<TreeviewSelect>>", select_profile)

class Profile(tk.Tk):
    """Class for template profile.

    Attributes:
        name (str): Profile name.
        app (App): Main app window.
        fields (list[Field]): List of field objects for current profile.
        df_curr (dict[str, str]): Dictionary of data currently entered in fields.
        df_save (pd.DataFrame): Dataframe of data saved for current profile.
        filename (str): Path to csv file containing saved data for current profile.
    """    
    def __init__(self, app) -> None:
        """Constructor for Profile class.

        Args:
            app (_type_): Main app window.
        """        
        super().__init__()
        self.name: str = '' if not hasattr(self, 'name') else self.name
        self.app: App = app

        self.title(f'{self.name}')
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", lambda: [self.destroy(), self.app.destroy()])

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
        """Add custom widgets to window.
        """        
        pass

    def mainloop(self) -> None:
        """Add widgets to window and initialise dataframes.
        """        
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
        """Save data to csv file.
        """        
        self.df_save.to_csv(self.filename, index=False)

    def view_data(self) -> None:
        """Opens window to view data in treeview.
        """        
        window: tk.Toplevel = tk.Toplevel(self)
        window.title('View Data')
        window.resizable(False, False)
        window.geometry(f'{self.winfo_width()}x{self.winfo_height()}')
        window.attributes('-topmost', 'true')
        window.grab_set()

        window.grid_columnconfigure(0, weight=1)
        window.grid_rowconfigure(0, weight=1)

        table: ttk.Treeview = ttk.Treeview(window, columns=tuple(self.df_save.columns), show='headings', selectmode='browse')
        for col in table['columns']:
            table.heading(col, text=col, anchor='center')
            table.column(col, stretch=False, anchor='center', width=100)
        for _, row in self.df_save.iterrows():
            table.insert(parent='', index='end', values=tuple(row.values))
        table.bind('<Motion>', 'break')
        table.gridx(row=0, column=0, sticky='ns')

        vsb: ttk.Scrollbar = ttk.Scrollbar(window, orient="vertical", command=table.yview)
        vsb.gridx(row=0, column=1, sticky='ns', rowspan=2)
        table.configure(yscrollcommand=vsb.set)

        hsb: ttk.Scrollbar = ttk.Scrollbar(window, orient="horizontal", command=table.xview)
        hsb.gridx(row=1, column=0, sticky='ew')
        table.configure(xscrollcommand=hsb.set)

        def delete_data(event: tk.Event) -> None:
            """Delete data corresponding to selected row in treeview.

            Args:
                event (tk.Event): Tkinter event.
            """            
            answer: str = messagebox.askquestion(parent=window, title='Delete Data', message='Are you sure you would like to delete this entry?')
            if answer == 'no':
                pass
            else:
                row_num: int = table.index(table.selection())
                self.df_save  = self.df_save.drop(row_num)
                self.df_save = self.df_save.reset_index(drop=True)
                self.save_data()
                window.destroy()
        table.bind("<<TreeviewSelect>>", delete_data)

    def import_data(self) -> None:
        """Initialise dialog for importing data from excel.
        """        
        paths: tuple[str] = filedialog.askopenfilenames(parent=self, title='Import Data', initialdir='/', filetypes=[('excel files', '*.xlsx')])
        if paths:
            answer: Union[bool, None] = messagebox.askyesnocancel(parent=self, title='Import Data', message='Would you like to clear the existing data? This action cannot be undone!')
            if answer:
                self.df_save: pd.DataFrame = pd.DataFrame(columns=self.df_curr.keys())
            if answer is not None:
                self.df_save: pd.DataFrame = pd.concat([self.df_save] + [pd.read_excel(path, dtype=str, na_filter=False) for path in paths])

    def export_data(self) -> None:
        """Initialise dialog for exporting data to excel
        """        
        path: str = filedialog.asksaveasfile(parent=self, title='Export Data', initialdir='/', filetypes=[('excel files', '*.xlsx')], defaultextension=('excel files', '*.xlsx'), mode='wb')
        if path:
            answer: Union[bool, None] = messagebox.askyesnocancel(parent=self, title='Export Data', message='Would you like to clear the existing data? This action cannot be undone!')
            if answer is not None:
                self.df_save.to_excel(path, index=False)
            if answer:
                self.df_save: pd.DataFrame = pd.DataFrame(columns=self.df_curr.keys())

    def destroy(self) -> None:
        """Saves current data and closes window.
        """  
        self.save_data()
        super().destroy()

    def switch_profile(self) -> None:
        """Close window and open menu for switching profile.
        """        
        self.destroy()
        self.app.deiconify()


class Field():
    """Class for template field.

    Attributes:
        profile (Profile): Profile containing field.
        names (tuple[str, ...]): Names of fields.
        defaults (tuple[str, ...]): Default values for fields.
        vars (tuple[tk.StringVar, ...]): Tkinter variables for fields.
        row (int): Current row number for the profile.
    """    
    def __init__(self, profile: Profile, names: tuple[str, ...] = (), defaults: tuple[str, ...] = ()) -> None:
        """Constructor for Field class.
        Args:
            profile (Profile): Profile containing field.
            names (tuple[str], optional): Names of fields. Defaults to ().
            defaults (tuple[str], optional): Default values for fields. Defaults to ().
        """        
        self.profile: Profile = profile
        self.names: tuple[str, ...] = names
        self.defaults: tuple[str, ...] = defaults

        self.vars: tuple[tk.StringVar, ...] = [tk.StringVar(self.profile, value=default) for default in defaults]
        for var in self.vars:
            var.trace_add('write', self.update)

        self.row: int = len(self.profile.fields)
        self.profile.fields.append(self)

    def update(self, variable: str = '', index: str = '', mode: str = '') -> None:
        """Update current data of profile with field entries.

        Args:
            variable (str, optional): Variable to be traced. Defaults to ''.
            index (str, optional): Index of variable (if variable is a list). Defaults to ''.
            mode (str, optional): Trace mode ('read', 'write', etc.). Defaults to ''.
        """        
        for var, name in zip(self.vars, self.names):
            self.profile.df_curr[name] = var.get()

    def reset(self) -> None:
        """Reset fields to their default values.
        """        
        for var, default in zip(self.vars, self.defaults):
            var.set(default)

class Submit():
    """Class for submit button.

    Attributes:
        profile (Profile): Profile containing field.
        name (str): Label for button.
        row (int): Current row number for the profile.
    """    
    def __init__(self, profile: Profile) -> None:
        """Constructor for Submit class.

        Args:
            profile (Profile): Profile containing submit button.
        """        
        self.profile: Profile = profile
        self.name: str = 'Submit'

        self.row: int = len(self.profile.fields)

        ttk.Button(profile, text=self.name, command=self.command).gridx(row=self.row, column=0, columnspan=4)

    def command(self) -> None:
        """Command to be executed on button press.
        """        
        if '' in self.profile.df_curr.values():
            messagebox.showinfo(parent=self.profile, message='Please fill in all the fields.')
        else:
            self.profile.df_save = pd.concat([self.profile.df_save, pd.DataFrame([self.profile.df_curr])], ignore_index=True)
            self.profile.save_data()
            for field in self.profile.fields:
                field.reset()

# ---------------------------------------------------------------------------- #
#                             Custom Field Classes                             #
# ---------------------------------------------------------------------------- #

class Date(Field):
    """Class for date entry field.
    """  
    def __init__(self, profile: Profile, name: str = '') -> None:
        """Constructor for Date class.

        Args:
            profile (Profile): Profile containing field.
            name (str, optional): Name of field. Defaults to ''.
        """        
        super().__init__(profile, names=(name,), defaults=(f'{datetime.now():%d/%m/%Y}',))
    
        ttk.Label(self.profile, text=f'{self.names[0]}:').gridx(row=self.row, column=0, sticky='e')
        tkc.DateEntry(self.profile, textvariable=self.vars[0], date_pattern='dd/mm/yyyy', selectmode='day', state='readonly').gridx(row=self.row, column=1, sticky='ew', columnspan=3)

class Times(Field):
    """Class for dual time entry field.

    Attributes:
        frame (ttk.Frame): Frame containing widgets.
    """  
    def __init__(self, profile: Profile, names: tuple[str, str] = ('', ''), label: str = '') -> None:
        """Constructor for Times class.

        Args:
            profile (Profile): Profile containing field.
            names (tuple[str, str], optional): Names of fields. Defaults to ('', '').
            label (str, optional): Label for row. Defaults to ''.
        """        
        super().__init__(profile, names=names, defaults=(f'{datetime.now():%H}', f'{datetime.now():%M}', f'{datetime.now():%H}', f'{datetime.now():%M}'))

        frame: ttk.Frame = ttk.Frame(self.profile)
        frame.gridx(row=self.row, column=1, sticky='ew', columnspan=3)
        frame.grid_columnconfigure(tuple(range(6)), weight=1)

        ttk.Label(self.profile, text=f'{label} ').gridx(row=self.row, column=0, sticky='e')
        ttk.Label(frame, text=f'{self.names[0]}:').gridx(row=0, column=0)
        ttk.Spinbox(frame, textvariable=self.vars[0], values=[f"{hour:02}" for hour in range(0, 24, 1)], state='readonly', wrap=True, width=3).gridx(row=0, column=1)
        ttk.Spinbox(frame, textvariable=self.vars[1], values=[f'{mint:02}' for mint in range(0, 60, 5)], state='readonly', wrap=True, width=3).gridx(row=0, column=2)
        ttk.Label(frame, text=f'{self.names[1]}:').gridx(row=0, column=3)
        ttk.Spinbox(frame, textvariable=self.vars[2], values=[f"{hour:02}" for hour in range(0, 24, 1)], state='readonly', wrap=True, width=3).gridx(row=0, column=4)
        ttk.Spinbox(frame, textvariable=self.vars[3], values=[f'{mint:02}' for mint in range(0, 60, 5)], state='readonly', wrap=True, width=3).gridx(row=0, column=5)

    def update(self, variable: str = '', index: str = '', mode: str = '') -> None:
        """Update current data of profile with field entries.

        Args:
            variable (str, optional): Variable to be traced. Defaults to ''.
            index (str, optional): Index of variable (if variable is a list). Defaults to ''.
            mode (str, optional): Trace mode ('read', 'write', etc.). Defaults to ''.
        """        
        self.profile.df_curr[self.names[0]] = f'{datetime.strptime(f"{self.vars[0].get()}:{self.vars[1].get()}", "%H:%M"):%H:%M}'
        self.profile.df_curr[self.names[1]] = f'{datetime.strptime(f"{self.vars[2].get()}:{self.vars[3].get()}", "%H:%M"):%H:%M}'

class Nums(Field):
    """Class for dual number entry field.

    Attributes:
        frame (ttk.Frame): Frame conaining widgets.
        values (tupe[list[int], list[int]]): Possible values for fields.
    """  
    def __init__(self, profile: Profile, names: tuple[str, str] = ('', ''), defaults: tuple[int, int] = (1, 1), values: tuple[list[int], list[int]] = (list(range(1, 1000)), list(range(1, 1000))), label: str = '') -> None:
        """Constructor for Nums class.

        Args:
            profile (Profile): Profile containing field.
            names (tuple[str, str], optional): Names of fields. Defaults to ('', '').
            defaults (tuple[int, int], optional): Default values for fields. Defaults to (1, 1).
            values (tuple[list[int], list[int]], optional): Possible values for fields. Defaults to (list(range(1, 1000)), list(range(1, 1000))).
            label (str, optional): Label for row. Defaults to ''.
        """        
        super().__init__(profile, names=names, defaults=defaults)
        self.values: tuple[list[int], list[int]] = values

        frame: ttk.Frame = ttk.Frame(self.profile)
        frame.gridx(row=self.row, column=1, sticky='ew', columnspan=3)
        frame.grid_columnconfigure(tuple(range(4)), weight=1)

        ttk.Label(self.profile, text=f'{label} ').gridx(row=self.row, column=0, sticky='e')
        ttk.Label(frame, text=f'{self.names[0]}:').gridx(row=0, column=0, sticky='w')
        ttk.Spinbox(frame, textvariable=self.vars[0], values=self.values[0], validate='focusout', validatecommand=((self.profile.register(self.validate)), 0, '%P', '%W'), width=4).gridx(row=0, column=1, sticky='w')
        ttk.Label(frame, text=f'{self.names[1]}:').gridx(row=0, column=2, sticky='e')
        ttk.Spinbox(frame, textvariable=self.vars[1], values=self.values[1], validate='focusout', validatecommand=((self.profile.register(self.validate)), 1, '%P', '%W'), width=4).gridx(row=0, column=3, sticky='e')

    def validate(self, idx: str, P: int, W: str) -> bool:
        """Validate user entry for field.

        Args:
            idx (str): Index of field.
            P (int): Attempted entry.
            W (str): Name of widget.

        Returns:
            bool: Result of validation.
        """           
        if P in self.values[int(idx)]:
            return True
        else:
            try:
                self.profile.nametowidget(W).set(self.values[int(idx)][min(range(len(self.values[int(idx)])), key = lambda i : abs(float(self.values[int(idx)][i]) - float(P)))])
            except ValueError:
                self.profile.nametowidget(W).set(self.values[int(idx)][0])
            return False

class Text(Field):
    """Class for text entry field.
    """  
    def __init__(self, profile: Profile, name: str = '', default = None) -> None:
        """Constructor for Text class.

        Args:
            profile (Profile): Profile containing field.
            name (str, optional): Name of field. Defaults to ''.
        """        
        super().__init__(profile, names=(name,), defaults=(default,))

        if default:
            self.vars[0].set(default)

        ttk.Label(self.profile, text=f'{self.names[0]}:').gridx(row=self.row, column=0, sticky='e')
        ttk.Entry(self.profile, textvariable=self.vars[0]).gridx(row=self.row, column=1, sticky='ew', columnspan=3)

class Choice(Field):
    """Class for template field.

    Attributes:
        values (list[str]): Possible values for field.
        field0 (ttk.Combobox): Widget for dropdown entry.
    """  
    def __init__(self, profile: Profile, name: str = '', default: str = '', values: list[str] = ['']) -> None:
        """Constructor for Choice class.

        Args:
            profile (Profile): Profile containing field.
            name (str, optional): Name of field. Defaults to ''.
            default (str, optional): Default value for field. Defaults to ''.
            values (list[str], optional): Possible values for field. Defaults to [''].
        """        
        super().__init__(profile, names=(name,), defaults=(default,))
        self.values: list[str] = values

        ttk.Label(self.profile, text=f'{self.names[0]}:').gridx(row=self.row, column=0, sticky='e')
        self.field0: ttk.Combobox = ttk.Combobox(self.profile, textvariable=self.vars[0], values=self.values, state='readonly').gridx(row=self.row, column=1, sticky='ew', columnspan=3)
        self.field0.bind('<ButtonPress>', expand_dropdown)

class ChoCho(Field):
    """Class for dual dropdown entry field with linking.

    Attributes:
        default (str): Default value for first field.
        off_value (str): Default value for second field.
        on_value (str): Value to lock second field to if first field is not at its default.
        values (tuple[list[str], list[str]]): Possible values for fields.
        field0 (ttk.Combobox): First widget for dropdown entry.
        field1 (ttk.Combobox): Second widget for dropdown entry.
    """  
    def __init__(self, profile: Profile, names: tuple[str, str] = ('', ''), default: str = '', off_value: str = '', on_value: str = '', values: tuple[list[str], list[str]] = ([''], [''])) -> None:
        """Constructor for ChoCho class.

        Args:
            profile (Profile): Profile containing field.
            names (tuple[str, str], optional): Names of fields. Defaults to ('', '').
            default (str, optional): Default value for first field. Defaults to ''.
            off_value (str, optional): Default value for second field. Defaults to ''.
            on_value (str, optional): Value to lock second field to if first field is not at its default. Defaults to ''.
            values (tuple[list[str], list[str]], optional): Possible values for fields. Defaults to ([''], ['']).
        """        
        super().__init__(profile, names=names, defaults=(default, off_value))
        self.default: str = default
        self.off_value: str = off_value
        self.on_value: str = on_value
        self.values: tuple[list[str], list[str]] = values

        ttk.Label(self.profile, text=f'{self.names[0]}:').gridx(row=self.row, column=0, sticky='e')
        self.field0: ttk.Combobox = ttk.Combobox(self.profile, textvariable=self.vars[0], values=self.values[0], state='readonly', width=10).gridx(row=self.row, column=1, sticky='w')
        self.field0.bind('<ButtonPress>', expand_dropdown)
        ttk.Label(self.profile, text=f'{self.names[1]}:').gridx(row=self.row, column=2, sticky='e')
        self.field1: ttk.Combobox = ttk.Combobox(self.profile, textvariable=self.vars[1], values=self.values[1], state='readonly', width=10).gridx(row=self.row, column=3)
        self.field1.bind('<ButtonPress>', expand_dropdown)

    def update(self, variable: str = '', index: str = '', mode: str = '') -> None:
        """Update current data of profile with field entries.

        Args:
            variable (str, optional): Variable to be traced. Defaults to ''.
            index (str, optional): Index of variable (if variable is a list). Defaults to ''.
            mode (str, optional): Trace mode ('read', 'write', etc.). Defaults to ''.
        """         
        self.profile.df_curr[self.names[0]] = self.vars[0].get()
        if self.vars[0].get() == self.default:
            self.field1['state'] = 'readonly'
            if self.vars[1].get() == self.on_value:
                self.vars[1].set(self.off_value)
        else:
            self.field1['state'] = 'disabled'
            self.vars[1].set(self.on_value)
        self.profile.df_curr[self.names[1]] = self.vars[1].get()

class ChkCho(Field):
    """Class for dual ticbox/dropdown entry field with linking.

    Attributes:
        default (str): Default value for first field.
        off_value (str): Value to lock second field to if first field is at its default.
        on_value (str): Default value for second field.
        values (list[str]): _description_.
        link (bool): If False, overriding of update method will be disabled.
        field0 (ttk.Combobox): First widget for tickbox entry.
        field1 (ttk.Combobox): Second widget for dropdown entry.
    """  
    def __init__(self, profile: Profile, names: tuple[str, str] = ('', ''), default: str = 'No', off_value: str = 'N/A', on_value: str = '', values: list[str] = [''], link: bool = True) -> None:
        """Constructor for ChkCho class.

        Args:
            profile (Profile): Profile containing field.
            names (tuple[str, str], optional): Names of fields.. Defaults to ('', '').
            default (str, optional): Default value for first field. Defaults to 'No'.
            off_value (str, optional): Value to lock second field to if first field is at its default. Defaults to 'N/A'.
            on_value (str, optional): Default value for second field. Defaults to ''.
            values (list[str], optional): _description_. Defaults to [''].
            link (bool, optional): If False, overriding of update method will be disabled. Defaults to True.
        """        
        super().__init__(profile, names=names, defaults=(default, off_value))
        self.default: str = default
        self.off_value: str = off_value
        self.on_value: str = on_value
        self.values: list[str] = values
        self.link: bool = link

        ttk.Label(self.profile, text=f'{self.names[0]}:').gridx(row=self.row, column=0, sticky='e')
        self.field0: ttk.Checkbutton = ttk.Checkbutton(self.profile, variable=self.vars[0], offvalue='No', onvalue='Yes').gridx(row=self.row, column=1, sticky='w')
        ttk.Label(self.profile, text=f'{self.names[1]}:').gridx(row=self.row, column=2, sticky='e')
        self.field1: ttk.Combobox = ttk.Combobox(self.profile, textvariable=self.vars[1], values=self.values, state='readonly', width=10).gridx(row=self.row, column=3)
        self.field1.bind('<ButtonPress>', expand_dropdown)

    def update(self, variable: str = '', index: str = '', mode: str = '') -> None:
        """Update current data of profile with field entries.

        Args:
            variable (str, optional): Variable to be traced. Defaults to ''.
            index (str, optional): Index of variable (if variable is a list). Defaults to ''.
            mode (str, optional): Trace mode ('read', 'write', etc.). Defaults to ''.
        """   
        if self.link:
            self.profile.df_curr[self.names[0]] = self.vars[0].get()
            if self.vars[0].get() == self.default:
                self.field1['state'] = 'disabled'
                self.vars[1].set(self.off_value)
            else:
                self.field1['state'] = 'readonly'
                if self.vars[1].get() == self.off_value:
                    self.vars[1].set(self.on_value)
            self.profile.df_curr[self.names[1]] = self.vars[1].get()
        else:
            super().update(variable, index, mode)

class NumChk(Field):
    """Class for dual number/tickbox entry field.
    """  
    def __init__(self, profile: Profile, names: tuple[str, str] = ('', ''), defaults: tuple[int, str] = (1, 'No')):
        """Constructor for NumChk class.

        Args:
            profile (Profile): Profile containing field.
            names (tuple[str, str], optional): Names of fields. Defaults to ('', '').
            defaults (tuple[int, str], optional): Default values for fields. Defaults to (1, 'No').
        """        
        super().__init__(profile, names=names, defaults=defaults)

        ttk.Label(self.profile, text=f'{self.names[0]}:').gridx(row=self.row, column=0, sticky='e')
        ttk.Spinbox(self.profile, textvariable=self.vars[0], values=tuple(range(1,1000)), state='readonly', width=10).gridx(row=self.row, column=1, sticky='w')
        ttk.Label(self.profile, text=f'{self.names[1]}:').gridx(row=self.row, column=2, sticky='e')
        ttk.Checkbutton(self.profile, variable=self.vars[1], offvalue='No', onvalue='Yes').gridx(row=self.row, column=3, sticky='w')

class QuinChk(Field):
    """Class for dual drop down entry field with linking.

    Attributes:
        frame (ttk.Frame): Frame containing widgets.
    """  
    def __init__(self, profile: Profile, names: tuple[str, str, str, str] = ('', '', '', '', ''), defaults: tuple[str, str, str, str] = ('No', 'No', 'No', 'No', 'No'), label: str = ''):
        """Constructor for QuinChk class.

        Args:
            profile (Profile): Profile containing field.
            names (tuple[str, str, str, str], optional): Names of fields. Defaults to ('', '', '', '', '').
            defaults (tuple[str, str, str, str], optional): Default vlaues for fields. Defaults to ('No', 'No', 'No', 'No', 'No').
            label (str, optional): Label for row. Defaults to ''.
        """        
        super().__init__(profile, names=names, defaults=defaults)

        frame: ttk.Frame = ttk.Frame(self.profile)
        frame.gridx(row=self.row, column=1, sticky='ew', columnspan=3)
        frame.grid_columnconfigure(tuple(range(5)), weight=1)

        ttk.Label(self.profile, text=f'{label} ').gridx(row=self.row, column=0, sticky='e')
        ttk.Label(frame, text=f'{self.names[0]}:', anchor='center').gridx(row=0, column=0, sticky='ew')
        ttk.Checkbutton(frame, variable=self.vars[0], offvalue='No', onvalue='Yes').gridx(row=1, column=0)
        ttk.Label(frame, text=f'{self.names[1]}:', anchor='center').gridx(row=0, column=1, sticky='ew')
        ttk.Checkbutton(frame, variable=self.vars[1], offvalue='No', onvalue='Yes').gridx(row=1, column=1)
        ttk.Label(frame, text=f'{self.names[2]}:', anchor='center').gridx(row=0, column=2, sticky='ew')
        ttk.Checkbutton(frame, variable=self.vars[2], offvalue='No', onvalue='Yes').gridx(row=1, column=2)
        ttk.Label(frame, text=f'{self.names[3]}:', anchor='center').gridx(row=0, column=3, sticky='ew')
        ttk.Checkbutton(frame, variable=self.vars[3], offvalue='No', onvalue='Yes').gridx(row=1, column=3)
        ttk.Label(frame, text=f'{self.names[4]}:', anchor='center').gridx(row=0, column=4, sticky='ew')
        ttk.Checkbutton(frame, variable=self.vars[4], offvalue='No', onvalue='Yes').gridx(row=1, column=4)

# ---------------------------------------------------------------------------- #
#                            Custom Profile Classes                            #
# ---------------------------------------------------------------------------- #

class MASA(Profile):
    """Class for MASA profile.

    Attributes:
        name (str): Profile name.
    """  
    name = 'MASA'

    def layout(self) -> None:
        """Add custom widgets to window.
        """   
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
        'Maths: Other',
        'Statistics: Data Collection/Handling',
        'Statistics: Data Presentation/Writing Up Results',
        'Statistics: Statistical Testing',
        'Statistics: Statistical Theory',
        'Statistics: Probability',
        'Statistics: Sample Size Calculations',
        'Statistics: Understanding Research Papers',
        'Statistics: Other',
        'Software: Excel',
        'Software: GraphPad',
        'Software: Jamovi',
        'Software: Matlab',
        'Software: R',
        'Software: SPSS',
        'Software: Other']),
        Choice(self,    name  =  'Query 2',                 values =  [
        'Maths: Algebra',
        'Maths: Calculus',
        'Maths: Complex Numbers',
        'Maths: Numeracy',
        'Maths: Trigonometry',
        'Maths: Other',
        'Statistics: Data Collection/Handling',
        'Statistics: Data Presentation/Writing Up Results',
        'Statistics: Statistical Testing',
        'Statistics: Statistical Theory',
        'Statistics: Probability',
        'Statistics: Sample Size Calculations',
        'Statistics: Understanding Research Papers',
        'Statistics: Other',
        'Software: Excel',
        'Software: GraphPad',
        'Software: Jamovi',
        'Software: Matlab',
        'Software: R',
        'Software: SPSS',
        'Software: Other'], default = 'N/A'),
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
        Text(self,      name  =  'Notes',                   default = 'N/A')

class ASND(Profile):
    """Class for AS&D profile.

    Attributes:
        name (str): Profile name.
    """  
    name = 'AS&D'

    def layout(self):
        """Add custom widgets to window.
        """   
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
            'N/A',
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
        Text(self,      name  =  'Notes',                   default = 'N/A')

class EmbdMASA(Profile):
    """Class for MASA (Embedded) profile.

    Attributes:
        name (str): Profile name.
    """  
    name = 'Embedded (MASA)'

    def layout(self):
        """Add custom widgets to window.
        """   
        Date(self,      name  =  'Date')
        Nums(self,      names = ('Session', 'Preparation'),                 values = ([
            f'{0.25*i:.2f}' for i in range(1, 11)], [
            f'{0.50*i:.2f}' for i in range(1, 11)]), defaults = ('0.25', '0.50'), label = 'Time (Hours)')
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
            'Maths: Algebra',
            'Maths: Calculus',
            'Maths: Complex Numbers',
            'Maths: Numeracy',
            'Maths: Trigonometry',
            'Maths: Other',
            'Statistics: Data Collection/Handling',
            'Statistics: Data Presentation/Writing Up Results',
            'Statistics: Statistical Testing',
            'Statistics: Statistical Theory',
            'Statistics: Probability',
            'Statistics: Sample Size Calculations',
            'Statistics: Understanding Research Papers',
            'Statistics: Other',
            'Software: Excel',
            'Software: GraphPad',
            'Software: Jamovi',
            'Software: Matlab',
            'Software: R',
            'Software: SPSS',
            'Software: Other'])
        Choice(self,    name  =  'Topic 2',                                 values =  [
            'Maths: Algebra',
            'Maths: Calculus',
            'Maths: Complex Numbers',
            'Maths: Numeracy',
            'Maths: Trigonometry',
            'Maths: Other',
            'Statistics: Data Collection/Handling',
            'Statistics: Data Presentation/Writing Up Results',
            'Statistics: Statistical Testing',
            'Statistics: Statistical Theory',
            'Statistics: Probability',
            'Statistics: Sample Size Calculations',
            'Statistics: Understanding Research Papers',
            'Statistics: Other',
            'Software: Excel',
            'Software: GraphPad',
            'Software: Jamovi',
            'Software: Matlab',
            'Software: R',
            'Software: SPSS',
            'Software: Other'], default = 'N/A')
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
        ChkCho(self,    names = ('Online', 'Type'),                         values =  [
            'Department - synchronous taught',
            'Department - synchronous Q+A',
            'Department - asynchronous (panopto recording)',
            'Discussion Forum',
            'Professional Service',
            'WPO'], off_value = '', link = False)
        QuinChk(self,   names = ('LDA', 'LDL', 'MASA', 'FY', 'Acad'), label = 'Staff')
        Choice(self,    name  =  'Contextualisation',                       values =  [
            'None',
            'Minimal',
            'Significant',
            'Full'
        ])
        Choice(self,    name  =  'Assessment Related',                      values =  [
            'No',
            'Partially',
            'Directly',
            'Project/Dissertation'
        ])
        ChkCho(self,    names = ('Resources', 'Applications'),              values =  [
            'Not applicable to other workshops',
            'Is applicable to other workshops'], on_value = 'Not applicable to other workshops')
        Nums(self,      names = ('Expected', 'Arrived'), label = '# Students')
        Text(self,      name  =  'Notes',                   default = 'N/A')

class EmbdASND(Profile):
    """Class for AS&D (Embedded) profile.

    Attributes:
        name (str): Profile name.
    """  
    name = 'Embedded (AS&D)'

    def layout(self):
        """Add custom widgets to window.
        """     
        Date(self,      name  =  'Date')
        Nums(self,      names = ('Session', 'Preparation'),                 values = ([
            f'{0.25*i:.2f}' for i in range(1, 11)], [
            f'{0.50*i:.2f}' for i in range(1, 11)]), defaults = ('0.25', '0.50'), label = 'Time (Hours)')
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
            'N/A',
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
        ChkCho(self,    names = ('Online', 'Type'),                         values =  [
            'Department - synchronous taught',
            'Department - synchronous Q+A',
            'Department - asynchronous (panopto recording)',
            'Discussion Forum',
            'Professional Service',
            'WPO'], off_value = '', link = False)
        QuinChk(self,   names = ('LDA', 'LDL', 'MASA', 'FY', 'Acad'), label = 'Staff')
        Choice(self,    name  =  'Contextualisation',                       values =  [
            'None',
            'Minimal',
            'Significant',
            'Full'
        ])
        Choice(self,    name  =  'Assessment Related',                      values =  [
            'No',
            'Partially',
            'Directly',
            'Project/Dissertation'
        ])
        ChkCho(self,    names = ('Resources', 'Applications'),              values =  [
            'Not applicable to other workshops',
            'Is applicable to other workshops'], on_value = 'Not applicable to other workshops')
        Nums(self,      names = ('Expected', 'Arrived'), label = '# Students')
        Text(self,      name  =  'Notes',                   default = 'N/A')

# ---------------------------------------------------------------------------- #
#                            Script - DO NOT CHANGE                            #
# ---------------------------------------------------------------------------- #

def main():
    """Run app.
    """
    os.makedirs(DATA_DIR, exist_ok=True); os.chdir(DATA_DIR)
    App().mainloop()
