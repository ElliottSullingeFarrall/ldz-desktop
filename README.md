# LDZ-Desktop

## Installation

### Windows

Download `ldz.exe` from the [Releases](https://github.com/ElliottSullingeFarrall/ldz-desktop/releases/latest) page and save it somewhere accessible on your PC. Run the program and accept any of the required permissions.

### MacOS

Download `ldz.zip` from the [Releases](https://github.com/ElliottSullingeFarrall/ldz-desktop/releases/latest) page and unzip it. This should create a MacOS app named `ldz.app`. Save this somewhere accessible on your PC. Run the program and accept any of the required permissions.

## Usage

### Selecting a Profile

When running the program, you will be given an option to select which profile you wish to record data for.

### Changing Profile

To change the the profile, go to **Profile → Switch Profile** in the menu bar. This will take you back to the profile selection window.

### Submitting Data

Once you have entered all the required information into the fields, simply press **Submit** to submit that data into the record sheet for the current profile.

### Viewing & Deleting Data

To view all the submitted data for the current profile, go to **Data → View\\Delete Data**. You will now be able to see all the data that has been submitted in a table in a new window. Clicking a row of the table will delete that entry from the record sheet and close the window.

### Importing Data

To import data from an existing record sheet, go to **Data → Import Data...** in the menu bar. You will be asked to choose an excel sheet(s) to import the data from and then asked if you would like to clear the existing data you have submitted from the record.

### Exporting Data

To export data to an excel spreadsheet, go to **Data → Export Data...** in the menu bar. You will be asked to pick a name for the created spreadsheet and then asked if you would like to clear the existing data you have submitted from the record.

### Clearing Data

There is no dedicated button for clearing the record sheet. If you wish to do so, please see the sections on [Importing Data](#importing-data) and [Exporting Data](#exporting-data).

### Syncing Multiple Sheets of Data

If you wish to merge multiple record sheets, go to **Data → Export Data...** in the menu bar and highlight all the sheets you would like to sync. For further details, consult the section on [Importing Data](#importing-data).

## Development

This project is written in Python with dependencies managed via Poetry. A development environment is available for Nix users via the `flake.nix`. For non-Nix users, a NixOS devcontainer is also available.
