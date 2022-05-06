from tkinter import *
from tkinter import ttk, messagebox
from tkinter import filedialog as fd
from tkinter.font import Font
from ttkthemes import ThemedTk
from PIL import ImageTk, Image
import pandas as pd
import numpy
import time
import datetime

'''
    Coming soon:
        - create separate module file for functions, then import them to bill_tracker.py
        - add scroll bar
        - fix column heading name output to excel sheet + include total
        - bug: saving excel file, re-opening it and then re-saving it outputs a blank sheet.
        - total_label should read in from db or treeview
        - add try/except for line 181, add_bill_func and delete_bill_func
    Fixed:
        - Open file now loads .xlsx file (assuming correct format) into the appropriate columns
        - Save file now outputs to xlsx list in proper format
        - clear_all() function now resets display_total properly (previously kept display_total value even after clearing values from treeview)
'''
db = {}
item_costs = []
count = 0
display_total = 0.0

# instantiate tkinter window and theme
root = ThemedTk()
tree = ttk.Treeview(root, show='headings')
frame = ttk.Frame(root, width=20, height=20)
style = ttk.Style()
style.theme_use('equilux')

# must initialize after root object has been created
error_msg = StringVar()

# convert .png image into a .ico image for icon use
ico = Image.open('logo.png')
photo = ImageTk.PhotoImage(ico)
root.wm_iconphoto(False, photo)

root.title("Handy Bill Handler")
root.geometry('500x350')
root.configure(bg='#303330')

def open_file():
    '''
        Reads and inputs .xslx file contents into the program's treeview in appropriate columns.

        **Does not insert values from excel sheet into db, only treeview. Needs to insert data into db for it to be tracked
    '''
    global db
    global bill_desc
    global bill_add_cost
    clear_error()
    db.clear()

    file = fd.askopenfilename(title='Select A File')
    clear_all()
    # usecols parameter defines which columns are targeted; inclusive
    rf = pd.read_excel(file, usecols= "B:C")

    # drops null value columns (null = 'NaN' values)
    nan_val = float("NaN")                              # define NaN value to search for
    rf.replace('', nan_val, inplace=True)
    rf.dropna(how='all',axis='columns', inplace=True)   # dropna(how= 'any or 'all' where it has at least one NA, axis= 'columns',0 or 'index',1 Drop columns or rows, inplace=True)
    
    # iterates through columns and displays the column names onto the treeview
    tree["column"] = list(rf.columns)
    tree["show"] = "headings"

    # For Headings iterate over the columns
    for col in tree["column"]:
        tree.heading(col, text=col)

   # Put data in rows in treeview
    rf_rows = rf.to_numpy().tolist()
    for row in rf_rows:
        db[row[0]] = row[1]
        tree.insert("", "end", values=row)
        rf.dropna(how='all',axis='columns',inplace=True)
    # reset tree_view to display opened file contents
    tree_view()

def save_file():
    '''
        Prompts user with save file dialog when save_btn is clicked. Writes/outputs dataframe gathered from db to xlsx file.
    '''
    f = fd.asksaveasfilename()
    df = pd.DataFrame.from_dict(db,orient='columns')
    clear_error()

    # output validation so that file extension isn't appended for every file save (when replacing file that exists)
    if '.xlsx' in f:
        writer = pd.ExcelWriter(f)
    else:
        writer = pd.ExcelWriter(f'{f}.xlsx')

    df.to_excel(writer,sheet_name=f'{datetime.date.today()}')
    writer.save()
    
def add_bill_func():
    ''' 
    add_bill_func() grabs entries from input fields, adds them to db, and adds user typed bill/cost to columns in treeview display.
    Attached to add_btn.
    '''
    global bill_desc
    global bill_add_cost
    global count
    global display_total
    global db
    global error_msg
        
    # checks if either fields are empty, does not store values if one or the other is empty
    # if bill_desc != '' and bill_add_cost != '':
    bill_desc = bill.get()
    bill_add_cost = add_cost.get()
    
    # check needed to avoid float value error
    if bill_desc == '' or bill_add_cost == '':
        error_msg = "Oops.. both fields must be filled"
        error_label.configure(text=error_msg)
        return
    # if entry field is not empty, converts bill_add_cost to float to be added or subtracted from display_total
    if bill_desc == '' and bill_add_cost == '':
        error_msg = "Oops.. both fields must be filled"
        error_label.configure(text=error_msg)
        return
    else:
        bill_desc = bill.get()
        bill_add_cost = float(add_cost.get())
        error_msg = 'Enter values into the field(s)'
        bill.delete(0, END)
        add_cost.delete(0, END)
    
    # check types for each entry field
    if isinstance(bill_add_cost, float) == False:
        error_msg = f'Error: Only numbers allowed in Monthly Cost entry field.'
        bill.delete(0, END)
        add_cost.delete(0, END)
    if isinstance(bill_desc, str) == False:
        error_msg = f'Error: Only letters allowed in Bill Name entry field.'
        bill.delete(0, END)
        add_cost.delete(0, END)
    else:
        # inserts values directly from entry fields bill and add_cost, not from db
        clear_error()
        db[count] = [bill_desc, bill_add_cost]
        count+=1
        display_total = display_total+bill_add_cost
        
        total_label.config(text=f'Total: ${format(f"{display_total:.2f}")}')
        tree.insert(parent='',index=0, text=f'{bill_desc}',values=(bill_desc, format(f"{bill_add_cost:.2f}")))
        bill.delete(0, END)
        add_cost.delete(0, END)
    return [bill_desc, bill_add_cost]
    
def delete_bill_func():
    '''
        Delete function attached to delete_btn. Deletes only one selected item from treeview.
    '''
    global display_total
    global db
    clear_error()

    # grab selected item and access its value which returns a list -> [bill name, cost], store list in record
    selected = tree.selection()
    item = tree.item(selected)
    record = item['values']

    # delete selected item from db -> {k: [bill name, cost], ...}
    for k, v in list(db.items()):
        if record[0] in v:
            del db[k]
    
    # subtract selected items cost from display_total
    display_total = display_total - float(record[1])
    tree.delete(selected)

    # update label
    total_label.config(text=f'Total: ${format(f"{display_total:.2f}")}')
    
def clear_all():
    global display_total
    clear_error()

    # delete all items in treeview
    for i in tree.get_children():
        tree.delete(i)

    # must clear db to reset display_total to 0
    db.clear()

    # must reset display_total from add_bill_func
    display_total = 0
    db_val = list(db.values())

    # show the dictionary's values are cleared. convert to list and sum list which should be 0
    total_label.config(text=f'Total: ${format(f"{sum(db_val):.2f}")}')

def tree_view():
    '''
        Generates tree_view box and columns.
    '''
    tree['columns']=('Bill Name','Cost')
    tree.column("Bill Name", anchor=CENTER, width=193, stretch=False)
    tree.column("Cost", anchor=CENTER, width=143, stretch=False)

    tree.heading('Bill Name', text='Bill Name', anchor=CENTER)
    tree.heading('Cost', text='Cost', anchor=CENTER)
    tree.place(relx=.3,rely=.22)
    style.configure("Treeview",background='#3b403b', fieldbackground='#3b403b', fg='#ffffff')
    style.map('Treeview', background=[('selected', '#303330')])

def clear_error():
    '''
        Clears any error messages upon call. 
    '''
    error_msg = ''
    error_label.configure(text=error_msg)
    return

def disable_btn():
    '''
        Function to disable buttons for testing.
    '''
    file_menu.entryconfig("Open File", state="disabled")

'''
    Generate GUI.
'''
# initialize treeview in GUI
tree_view()

# initialize open file and save file buttons within menu object
m = Menu(root)
root.config(menu=m)
file_menu = Menu(m, tearoff=False)
m.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="Open File", command=open_file)
file_menu.add_command(label="Save File As", command=save_file)

# define fonts for use in GUI
my_font = Font(family='Noto Sans', size=11, weight='bold')
label_font = Font(family='Noto Sans', size=10, weight='bold')

# displays current total cost below treeview
total_label = Label(root, text=f'Total: ${format(f"{display_total:.2f}")}', bg='#303330', font=label_font, fg='#ffffff')
total_label.place(relx=.75,rely=.89)

# label and entry field for bill name
bill_label = Label(root, text="BILL NAME", bg='#303330', font = label_font, fg='#ffffff')
bill_label.place(relx=.020, rely=.10)
bill = Entry(root, bd=0, fg='#ffffff', font=Font(family='Noto Sans', size=9), width=18)
bill.place(relx=.02, rely=.17,height=28)
bill.configure(bg='#484f48')

# label and entry field for monthly cost
add_cost_label = Label(root, text="MONTHLY COST", bg='#303330', font = label_font, fg='#ffffff')
add_cost_label.place(relx=.02, rely=.27)
add_cost = Entry(root, bd=0, fg='#ffffff', font=Font(family='Noto Sans', size=9), width=18)
add_cost.place(relx=.02, rely=.34,height=28)
add_cost.configure(bg='#484f48')

# error_label displays errors after checking input validation above treeview
error_label = Label(root, bg='#303330', font=Font(family='Noto Sans', size=9), fg='#ffffff')
error_label.place(relx=.32,rely=.12)

# version label, displays version: .1 for each fix/git push
vlabel = Label(root, text="v2.1", font=Font(family='Noto Sans', size=7), bg='#303330', fg='#ffffff')
vlabel.place(relx=.01,rely=.94)

# add button
add_btn = Button(root, padx=36, pady=6, text='   ADD  ', font = my_font, bd=0, bg='#3b403b',fg='#ffffff',activeforeground='#080808', activebackground='#424d42', command=add_bill_func)
add_btn.place(relx=.015,rely=.47)

# delete button
delete_btn = Button(root, padx=36, pady=6, text='DELETE', font=my_font, bd=0, bg='#3b403b',fg='#ffffff',activeforeground='#080808', activebackground='#424d42', command=delete_bill_func)
delete_btn.place(relx=.015,rely=.62)

# clear all button
clear_btn = Button(root, padx=35, pady=6, text=' CLEAR ', font=my_font, bd=0, bg='#3b403b',fg='#ffffff',activeforeground='#080808', activebackground='#424d42', command=clear_all)
clear_btn.place(relx=.015,rely=.77)

root.resizable(width=False, height=False)
root.mainloop()
