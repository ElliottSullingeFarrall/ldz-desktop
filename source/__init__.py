from imports import *

from app import *

# -------------------------------- Create App -------------------------------- #

app = App()

import os
logging.debug(os.getcwd())

if __name__ == "__main__":
    app.run()
