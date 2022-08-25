# Installation

Download the **Record** program (**.exe** for windows or **.app** for Mac OS) from the **dist** folder, along with the desired **config.xlsx** file from the **configs** folder. Note that **Record** and **config.xlsx** must be located in the same directory for the program to work. Once downloaded, **Record** may be renamed. 

If you would like to be able to combine multiple spreadsheets into one master spreadsheet, then download the **Sync** program from the **dist** folder. Unfortunately, syncing spreadhseets is not currently supported on Mac OS.

# Usage (Record)

### Submitting Data

Once you have entered all the required information into the fields, simply press **Submit** to submit that data into the record sheet.

### Viewing & Deleting Data

To view all the submitted the submitted data, go to **Data\View/Edit Data**. You will now be able to see all the data that has been submitted in a table in a new window. Clicking a row of the table will delete that entry from the record sheet and close the window.

### Changing Field Options

To change the available field options, go to **Config\Load Config...** in the menu bar. This will allow you to choose an appropriate config file that will alter the available field options.

### Importing Data

To import data from an existing record sheet, go to **Data\Import Data...** in the menu bar. You will be asked if you want to clear any existing data and then you will be able to choose an excel file containging the record sheet that will then be appended to any existing data.

### Exporting Data

To export data from an existing record sheet, go to **Data\Export Data...** in the menu bar. You will be asked if you want to clear any existing data flowwing the import and then you will be able to choose a location/file to export the current data to.

### Clearing Data

There is no dedicated button for clearing the record sheet. If you wish to do so, please see the previous section.

### Saving & Loading

The record sheet and active config will all be saved internally when the app is closed nad reloaded automatically on launch. If the app is ever update or reinstalled, this information will not be retained. However, you can always import your old data and reload in the config file.

# Troubleshooting

In the event of any issues, please contact [me](elliott.sullinge-farrall@surrey.ac.uk) with the **error.log** file attached (if applicable).