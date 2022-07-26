from tkinter import messagebox
import pandas as pd
import os
import sys

class Data:
    def __init__(self, filename):
        self.filename = filename

    def __enter__(self):
        if os.path.exists(self.filename):
            try:
                self.df = pd.read_excel(self.filename, dtype=str, na_filter=False)
            except PermissionError:
                answer = messagebox.askretrycancel(message=f'Unable to load the file: {self.filename}. Please try again.')
                if answer:
                    self.__enter__()
                else:
                    exit
        else:
            self.df = pd.DataFrame()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.df.to_excel(self.filename, index=False)
        except PermissionError:
            answer = messagebox.askretrycancel(message=f'Unable to save the file: {self.filename}. Please try again.')
            if answer:
                self.__exit__(exc_type, exc_val, exc_tb)
            else:
                exit

if __name__ == '__main__':
    files = sys.argv[1:]

    with Data('output.xlsx') as output:
        for filename in files:
            with Data(filename) as data:
                output.df = pd.concat([output.df, data.df])
                print(f'Synced file: {filename}')
    exit