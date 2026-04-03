from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from io import StringIO
import random
from math import floor
from PIL import Image, ImageGrab, ImageTk
import ctypes

ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(u"KylianvD.classroom.1.0.0")

# Part of the patch for grid_size
class GridMixin(ttk.Widget):
    def grid(self, *args, **kwargs):
        super().grid(*args, **kwargs)
        # Try to reduce grid_size offset
        try:
            self.grid_info()["in"].onset()
        except AttributeError:
            pass

# ---------

# Forcing the button widget to include GridMixin as well
class Button(ttk.Button, GridMixin):
    pass

# ---------

# Label with additional utility functions to use as a table
class Table(ttk.Label, GridMixin):
    def __init__(self, *args, **kwargs):
        if "size" in kwargs:
            self.size = kwargs.pop("size")
            kwargs["font"] = ('TkDefaultFont', self.size)
        super().__init__(*args, **kwargs)
        self.locked = False

    # Get the content
    def get(self):
        return self.cget("text")

    # Set the content
    def set(self, txt):
        self.config(text=txt)

    # Change the colour
    def color(self, clr):
        self.config(background=clr)

    # Apply focus-styling
    def focus(self):
        self.color("antiquewhite3")

    # Apply regular styling
    def unfocus(self):
        self.color("antiquewhite1")

    # Switch lock-state
    def lock(self):
        if self.locked:
            self.locked = False
            self.config(relief="solid")
        else:
            self.locked = True
            self.config(relief="sunken")
        return self.locked

    # Increase the font size by 10% or 1pt
    def fontUp(self):
        self.size = self.size + max(round(self.size * 0.1), 1)
        self.config(font=('TkDefaultFont', self.size))

    # Decrease the font size by 10% or 1pt
    def fontDown(self):
        self.size = max(self.size - round(max(self.size * 0.1, 1)), 1)
        self.config(font=('TkDefaultFont', self.size))

# ---------

# Label with additional utility functions to use as whitespace
class Space(ttk.Label, GridMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    # Change the colour
    def color(self, clr):
        self.config(background=clr)

    # Apply focus-styling
    def focus(self):
        self.color("white")

    # Apply regular styling
    def unfocus(self):
        self.color("SystemButtonFace")

# ---------

# Frame with a patch for grid_size to make it behave as expected
class Frame(ttk.Frame, GridMixin):
    # Direction can be passed to specify in which direction to fix grid_size
    def __init__(self, *args, **kwargs):
        if "direction" in kwargs:
            self.dir = kwargs.pop("direction")
        else:
            self.dir = -1
        super().__init__(*args, **kwargs)
        self.off = 0

    # This function is turbo-broken, as it cannot deal with the removal of widgets if configures have been set. To fix this, we keep an offset from removed widgets.
    def grid_size(self, *args, **kwargs):
        size = list(super().grid_size(*args, **kwargs))
        if self.dir >= 0:
            size[self.dir] = size[self.dir] - self.off
        return tuple(size)

    # Increase offset from deleted widgets
    def offset(self):
        self.off = self.off + 1

    # Decrease offset from deleted widgets
    def onset(self):
        self.off = max(self.off - 1, 0)

    # Shift all widgets index i or bigger in a row or column 1 spot down; this functions expects no holes
    def shift(self, i):
        size = self.grid_size()[self.dir]
        if self.dir == 0:
            self.columnconfigure(self.grid_size()[0]-1, weight=0, uniform=0)
        else:
            self.rowconfigure(self.grid_size()[1]-1, weight=0, uniform=0)
        for i in range(i+1, size):
            if self.dir == 0:
                self.grid_slaves(column=i, row=0)[0].grid_configure(column=i-1)
            else:
                self.grid_slaves(column=0, row=i)[0].grid_configure(row=i-1)
        if size == self.grid_size()[self.dir]:
            self.offset()

    # Flip the all widgets inside the frame over a given direction
    def flip(self, dir=-1):
        if dir == -1:
            dir = self.dir
        if dir != -1:
            length = self.grid_size()[dir]
            for i in range(0, floor(length / 2)):
                if self.dir == 0:
                    temp = self.grid_slaves(column=i, row=0)[0]
                    self.grid_slaves(column=length-1-i, row=0)[0].grid_configure(column=i)
                    temp.grid_configure(column=length-1-i)
                else:
                    temp = self.grid_slaves(row=i, column=0)[0]
                    self.grid_slaves(row=length-1-i, column=0)[0].grid_configure(row=i)
                    temp.grid_configure(row=length-1-i)
        else:
            raise AttributeError("Invalid flipping direction")
                

    # Destroy this widget and all its grid_slaves()
    def destroy(self, *args, **kwargs):
        for widget in self.grid_slaves():
            widget.destroy()
        super().destroy(*args, **kwargs)

# ---------

# Frame with utility
class Row(Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config(borderwidth=1)

    # Apply focus-styling
    def focus(self):
        self.config(relief="solid")

    # Apply regular styling
    def unfocus(self):
        self.config(relief="flat")

# ---------

# Utility to turn dropdowns into instant function callers
class Dropdown(ttk.Combobox):
    # Expects values and callbacks as lists in kwargs, zips them into a dictionary; use None to specify a lack of callback; values[0] will become the default value so setting None there is recommended
    def __init__(self, *args, **kwargs):
        self.selected = StringVar()
        self.callbacks = dict(zip(kwargs["values"], kwargs.pop("callbacks")))
        self.default = kwargs["values"][0]
        super().__init__(*args, **kwargs, textvariable=self.selected)
        self.selected.set(self.default)
        self.bind('<<ComboboxSelected>>', self.callback)

    # Call the relevant callback and set the box back to default value
    def callback(self, event):
        if self.callbacks[self.selected.get()] != None:
            self.callbacks[self.selected.get()]()
        self.selected.set(self.default)

# ---------

# Class to actually make the classroom
class Classroom:
    # Append a row and a select-button for selecting the row
    def addRow(self, *args, **kwargs):
        i = self.rowframe.grid_size()[1]
        r = Row(self.rowframe, direction=0, *args, **kwargs)
        r.grid(column=0, row=i, sticky=NSEW)
        r.rowconfigure(0, weight=1)
        self.rowframe.rowconfigure(i, weight=1, uniform="row")
        Button(self.rowselectframe, text="Select", command=(lambda x = r: self.focus(x))).grid(row=self.rowselectframe.grid_size()[1], column=0, sticky=NSEW)
        self.rowselectframe.rowconfigure(i, weight=1, uniform="select")
        return r

    # Append a table to the selected row
    def addTable(self, *args, **kwargs):
        if "row" in kwargs:
            frame = kwargs.pop("row")
        else:
            frame = self.focused
        if frame != None and type(frame) == Row:
            t = Table(frame, text="", anchor=CENTER, relief="solid", size=14, *args, **kwargs)
            i = frame.grid_size()[0]
            t.grid(column=i, row=0, sticky=NSEW)
            t.bind("<ButtonPress-1>", lambda event: self.focus(event.widget))
            t.bind("<ButtonPress-2>", lambda event: self.lock(event.widget))
            t.bind("<ButtonPress-3>", lambda event: self.swap(event.widget))
            self.tables.add(t)
            t.unfocus()
            frame.columnconfigure(i, weight=1, uniform="table")
            return t
        else:
            raise attributeError("Cannot add table to invalid frame")

    # Append whitespace to the selected row
    def addSpace(self, *args, **kwargs):
        if "row" in kwargs:
            frame = kwargs.pop("row")
        else:
            frame = self.focused
        if frame != None and type(frame) == Row:
            s = Space(frame, text = "", anchor=CENTER, *args, **kwargs)
            i = frame.grid_size()[0]
            s.grid(column=i, row=0, sticky=NSEW)
            s.bind("<ButtonRelease-1>", lambda event: self.focus(event.widget))
            s.unfocus()
            frame.columnconfigure(i, weight=1, uniform="table")
        else:
            raise attributeError("Cannot add space to invalid frame")

    # Focus on the widget passed to this, change menu if necessary
    def focus(self, widget):
        if self.focused == widget:
            self.unfocus()
        else:
            self.unfocus()
            self.focused = widget
            self.focused.focus()
            # Change which toolframe is shown
            if type(self.focused) == Row:
                self.toolcframe.grid(column=0,row=1, sticky=NSEW, columnspan=2)
            elif type(self.focused) == Table or type(self.focused) == Space:
                self.tooltframe.grid(column=0,row=1, sticky=NSEW, columnspan=2)

    # Unfocus all widgets
    def unfocus(self):
        if self.focused != None:
            # Remove the thing-specific toolframe
            if type(self.focused) == Row:
                self.toolcframe.grid_forget()
            elif type(self.focused) == Table or type(self.focused) == Space:
                self.tooltframe.grid_forget()
            self.focused.unfocus()
            self.focused = None

    # Rename the passed of focussed table
    def rename(self, table = None):
        if table == None:
            table = self.focused
        if self.focused != None and type(self.focused) == Table:
            self.focused.config(text=self.entrybox.get())
        else:
            raise AttributeError("Cannot change name of invalid table")

    # Shuffle all non-locked table names
    def shuffle(self):
        if len(self.tables) != 0:
            names = list(map(lambda t: t.get(), self.tables))
            random.shuffle(names)
            for t in self.tables:
                t.set(names.pop())
        else:
            print("No tables to randomize.")

    # Delete the passed or focussed row and all its contents
    def delRow(self, row=None):
        if row == None:
            row = self.focused
        if row != None and type(row) == Row:
            self.unfocus()
            info = row.grid_info()
            frame = info["in"]

            # Remove from set of tables
            for tab in [i for i in row.grid_slaves() if type(i) == Table]:
                self.tables.discard(tab)
            # Destroy row and underlings, shift all rows to fill the gap
            row.destroy()
            index = info["row"]
            frame.shift(index)
            self.rowselectframe.grid_slaves(column=0, row=index)[0].destroy()
            self.rowselectframe.shift(index)

    # Delete the passed or focused table/space
    def delTab(self, widget=None):
        if widget == None:
            widget = self.focused
        if widget != None and (type(widget) == Table or type(widget) == Space):
            self.unfocus()
            # Remove from set of tables
            if type(widget) == Table:
                self.tables.discard(widget)
            info = widget.grid_info()
            row = info["in"]

            # Destroy the widget, make the column take up no space, shift all things to fill the gap
            widget.destroy()
            row.shift(info["column"])
        else:
            raise AttributeError("Cannot delete invalid table or space")

    # Lock the passed or focused table
    def lock(self, table = None):
        if table == None:
            table = self.focused
        if table != None:
            if type(table) == Table:
                # Add or remove the table from the set of tables
                if table.lock():
                    self.tables.remove(table)
                else:
                    self.tables.add(table)
        else:
            raise AttributeError("Cannot (un)lock invalid table")

    def fontUp(self, table = None):
        if table == None:
            table = self.focused
        if table != None:
            if type(table) == Table:
                table.fontUp()
        else:
            raise AttributeError("Cannot change font of invalid table")

    def fontDown(self, table = None):
        if table == None:
            table = self.focused
        if table != None:
            if type(table) == Table:
                table.fontDown()
        else:
            raise AttributeError("Cannot change font of invalid table")

    # Swap the name of the passed table with the name of the focused table
    def swap(self, table):
        table2 = self.focused
        if table != None and table2 != None and type(table) == Table and type(table2) == Table:
            temp = table.get()
            table.set(table2.get())
            table2.set(temp)
        else:
            raise AttributeError("Cannot swap invalid table(s)")

    # Flip the classroom up-down
    def flipClassroom(self):
        self.rowframe.flip()
        self.rowselectframe.flip()

    # Export image of the classroom to a file
    def export(self, unfocus=True):
        if unfocus:
            # Don't leave focus in the image
            self.unfocus()
            root.update()
        img = self.ImageManager.capture(self.rowframe)
        if self.ImageManager.save(img):
            messagebox.showinfo("Success!", "The image has been saved.")

    # Set up the classroom
    def __init__(self, root):
        self.focused = None
        # Stores which tables partake in the shuffle of names
        self.tables = set()

        # Set up the main frame to put everything in
        mainframe = ttk.Frame(root, padding=10)
        mainframe.grid(sticky=NSEW)
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        # Set up the menuframe (always-there buttons), toolframes (focused-thing-specific buttons)
        menuframe = ttk.Frame(mainframe)
        menuframe.grid(column=0,row=0, sticky=NSEW, columnspan=2)
        mainframe.rowconfigure(0, uniform="menu")
        self.toolcframe = ttk.Frame(mainframe)
        self.tooltframe = ttk.Frame(mainframe)
        mainframe.rowconfigure(1, uniform="menu")

        # Set up the rowframe (the actual classroom) and rowselectframe (to select active row)
        self.rowselectframe = Frame(mainframe, direction=1)
        self.rowselectframe.grid(column=0, row=2, sticky=NSEW, pady=(20, 0))
        self.rowframe = Frame(mainframe, direction=1)
        self.rowframe.grid(column=1, row=2, sticky=NSEW, pady=(20, 0))
        self.rowframe.columnconfigure(0, weight=1)
        mainframe.columnconfigure(1, weight=1)
        mainframe.rowconfigure(2, weight=1)

        # Make buttons
        ttk.Button(menuframe, text="+ Row", command=self.addRow).grid(column=menuframe.grid_size()[0], row=0)
        ttk.Button(menuframe, text="Shuffle", command=self.shuffle).grid(column=menuframe.grid_size()[0], row=0, sticky=E)
        ttk.Button(menuframe, text="Flip", command=self.flipClassroom).grid(column=menuframe.grid_size()[0], row=0, sticky=E)
        ttk.Button(menuframe, text="To .png", command=self.export).grid(column=menuframe.grid_size()[0], row=0, sticky=E)

        # Dropdown for file interaction, callbacks as lambdas
        Dropdown(menuframe, state="readonly", values=["File management...", "Open layout", "Open names", "Export layout", "Export names"],
                         callbacks=[None, lambda: self.FileManager.importLayout(self), lambda: self.FileManager.importNames(self), lambda: self.FileManager.exportLayout(self), lambda: self.FileManager.exportNames(self)]
                 ).grid(column=menuframe.grid_size()[0], row=0, sticky=E)
        ttk.Button(menuframe, text="Exit", command=root.destroy).grid(column=menuframe.grid_size()[0], row=0, sticky=E, padx=(20, 0))
        menuframe.columnconfigure(menuframe.grid_size()[0]-1, weight=1)
        
        ttk.Button(self.tooltframe, text="Lock", command=self.lock).grid(column=self.tooltframe.grid_size()[0], row=0)
        ttk.Button(self.tooltframe, text="Fontsize +", command=self.fontUp).grid(column=self.tooltframe.grid_size()[0], row=0)
        ttk.Button(self.tooltframe, text="Fontsize -", command=self.fontDown).grid(column=self.tooltframe.grid_size()[0], row=0)
        ttk.Button(self.tooltframe, text="(Re)name", command=self.rename).grid(column=self.tooltframe.grid_size()[0], row=0)
        # Box for changing table label name
        self.entrybox= StringVar()
        ttk.Entry(self.tooltframe, textvariable=self.entrybox).grid(column=self.tooltframe.grid_size()[0], row=0, sticky=EW)
        self.tooltframe.columnconfigure(self.tooltframe.grid_size()[0]-1, weight=1)
        ttk.Button(self.tooltframe, text="- Thing", command=self.delTab).grid(column=self.tooltframe.grid_size()[0], row=0, sticky=E, padx=(20, 0))

        ttk.Button(self.toolcframe, text="+ Table", command=self.addTable).grid(column=self.toolcframe.grid_size()[0], row=0)
        ttk.Button(self.toolcframe, text="+ Space", command=self.addSpace).grid(column=self.toolcframe.grid_size()[0], row=0)
        ttk.Button(self.toolcframe, text="- Row", command=self.delRow).grid(column=self.toolcframe.grid_size()[0], row=0, sticky=E, padx=(20, 0))
        self.toolcframe.columnconfigure(self.toolcframe.grid_size()[0]-1, weight=1)

    # Class with static functions that handle importing and exporting layouts and names
    class FileManager:
        def importLayout(classroom):
            file = filedialog.askopenfile(filetypes=(["text", "txt"], ["*", "*"]))
            if file != None:
                try:
                    while classroom.rowframe.grid_size()[1] > 0:
                        classroom.delRow(classroom.rowframe.grid_slaves()[0])
                    row = classroom.addRow()
                    while True:
                        match file.read(1):
                            case "0":
                                classroom.addSpace(row=row)
                            case "1":
                                classroom.addTable(row=row)
                            case "\n":
                                row = classroom.addRow()
                            case _:
                                break
                finally:
                    file.close()
                classroom.unfocus()

        def importNames(classroom):
            file = filedialog.askopenfile(filetypes=(["text", "txt"], ["*", "*"]))
            if file != None:
                try:
                    option = file.readline().strip()
                    match option:
                        case "layout":
                            for i in range(0, classroom.rowframe.grid_size()[1]):
                                row = classroom.rowframe.grid_slaves(column=0, row=i)[0]
                                tables = []
                                for i in range(0, row.grid_size()[0]):
                                    t = row.grid_slaves(row=0, column=i)[0]
                                    if type(t) == Table and not t.locked:
                                        tables.append(t)
                                names = file.readline().strip().split(";")
                                if len(tables) != len(names):
                                    if len(names) != 1 or names[0] != "":
                                        print("Layout does not fit. Names may be lost.")
                                for j in range(0, min(len(tables), len(names))):
                                    if names[j].strip().startswith("#"):
                                        classroom.lock(tables[j])
                                        names[j] = names[j].strip()[1:]
                                    tables[j].set(names[j].strip())
                        case "fill":
                            names = file.read().strip().split("\n")
                            for i in names:
                                names.extend(names.pop(0).strip().split(";"))
                            rows = classroom.rowframe.grid_slaves(column=0)
                            while len(rows) > 0 and len(names) > 0:
                                r = rows.pop()
                                tables = [t for t in r.grid_slaves(row=0) if type(t) == Table]
                                while len(tables) > 0 and len(names) > 0:
                                    tables.pop().set(names.pop().strip())
                            if len(names) != 0:
                                print("Could not fit all names. Names are lost.")
                finally:
                    file.close()

        def exportLayout(classroom):
            file = filedialog.asksaveasfile(filetypes=(["text", "txt"], ["*", "*"]), defaultextension=".txt")
            if file != None:
                try:
                    for i in range(0, classroom.rowframe.grid_size()[1]):
                        if i != 0:
                            file.write('\n')
                        row = classroom.rowframe.grid_slaves(column=0, row=i)[0]
                        for i in range(0, row.grid_size()[0]):
                            file.write(str(int(type(row.grid_slaves(row=0, column=i)[0]) == Table)))
                finally:
                    file.close()

        def exportNames(classroom):
            file = filedialog.asksaveasfile(filetypes=(["Plain Text", "txt"], ["*", "*"]), defaultextension=".txt")
            if file != None:
                try:
                    file.write("layout")
                    for i in range(0, classroom.rowframe.grid_size()[1]):
                        file.write("\n")
                        row = classroom.rowframe.grid_slaves(column=0, row=i)[0]
                        first = True
                        for i in range(0, row.grid_size()[0]):
                            thing = row.grid_slaves(row=0, column=i)[0]
                            if type(thing) == Table:
                                if first:
                                    first = False
                                else:
                                    file.write("; ")
                                if thing.locked:
                                    file.write("#")
                                file.write(thing.get())
                finally:
                    file.close()

    # Class with static functions to export the classroom to png
    class ImageManager():
        def capture(widget):
            x0 = widget.winfo_rootx()
            y0 = widget.winfo_rooty()
            x1 = x0 + widget.winfo_width()
            y1 = y0 + widget.winfo_height()

            img = ImageGrab.grab((x0, y0, x1, y1))
            return img

        def save(img):
            file = filedialog.asksaveasfilename(filetypes=(["Portable Network Graphics", "png"], ["*", "*"]), defaultextension="png")
            if not file:
                return False
            img.save(file)
            return True


root = Tk()
Classroom(root)
root.title("Classroom")
root.state('zoomed')

try:
    icon = Image.open("teaching.ico")
    icon = ImageTk.PhotoImage(icon)
    root.iconphoto(True, icon)
except FileNotFoundError:
    pass

root.mainloop()
