# classroom
Tool for teachers (and others) to quickly and easily show and randomize classroom layouts. Additionally comes with exporting to .png and options for saving and loading layouts and lists of names.

## "Installation"
Download the .zip from the latest release and extract it. To run, simply launch classroom.exe.
The .py is for developing purposes, you may have to use pip to get some imports.

## Use
To start editing a layout, start by adding a row. You can then use the select-button to select a row and make a toolbar appear to add tables and whitespace. By clicking a table or whitespace, the toolbar will change to showing options relevant for tables.
Table names can be shuffled using that button. Locked tables will not partake in this shuffling and keep their text. The flip button flips the classroom up-down.

### Hotkeys
* Middle-mouse button: lock a table
* Right-mouse button: swap the name of this table with the name of the focussed table

### File managing
Layouts can be exported and imported using the dropdown menu. They use a .txt file format.
A name file is a .txt where the first line is either "fill" or "layout". "fill" expects enter-separated and/or semicolon separated names and tries to fill as many tables as possible. "layout" can be used to put names on a layout in a specific way, but you are responsible for making it fit on the loaded layout. The export-function always exports to "layout" (which of course fits on the current layout), but you can easily change the word "layout" to say "fill" without further changes to the file.

The classroom can be exported to .png with that button.

## Disclaimer
This program runs on my machine (on some Windows 11 build). I do not guarantee it working on yours.
