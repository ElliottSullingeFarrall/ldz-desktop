import openpyxl as xl
import sys

class output_file:
    def __init__(self, filename):
        self.filename = filename

    def __enter__(self):
        try:
            self.wb = xl.Workbook()
            self.table = self.wb.active
        except PermissionError:
            raise Exception("Unable to load the data file. Please try again.")
        return self.table

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.wb.save(filename=self.filename)
        self.wb.close()

class data_file:
    def __init__(self, filename):
        self.filename = filename

    def __enter__(self):
        try:
            self.wb = xl.load_workbook(filename=self.filename)
            self.table = self.wb.active
        except PermissionError:
            raise Exception("Unable to load the data file. Please try again.")
        return self.table

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.wb.save(filename=self.filename)
        self.wb.close()


files = sys.argv[1:]

with output_file("Output.xlsx") as output:
    for idx, filename in enumerate(files):
        with data_file(filename) as data:
            for row in data.iter_rows(min_row=1 if idx == 0 else 2):
                output.append([cell.value for cell in row])