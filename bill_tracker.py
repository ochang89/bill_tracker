from tkinter import *
from tkinter import ttk, messagebox
from tkinter import filedialog as fd
from tkinter.font import Font
from tkinter import font
from ttkthemes import ThemedTk
from PIL import ImageTk, Image
import pandas as pd
import numpy
import datetime

'''
    Future features:
        - checkboxes that will pertain to weekly, bi-weekly, annual costs (already have monthly)
            - checking one of these boxes will trigger a field to pop up with the respective field from above
        - hot keys: use DEL key to delete directly from tree view.
                    Add (alt + A), Delete (alt + D), Clear (alt + C) hot keys

    Current fixes:
        - File menu 'open' function
        - Output total to xlsx list
'''
db = {}
item_costs = []
count = 0
t = 0.0


# instantiate tkinter window and theme
root = ThemedTk()
tree = ttk.Treeview(root, show='headings')
frame = ttk.Frame(root, width=20, height=20)
style = ttk.Style()
style.theme_use('equilux')

# convert .png image into a .ico image for icon use
ico = Image.open('logo.png')
photo = ImageTk.PhotoImage(ico)
root.wm_iconphoto(False, photo)

root.title("Handy Bill Handler")
root.geometry('500x350')
root.configure(bg='#303330')

var = StringVar()

def open_file():
    '''
        Reads and inputs .xslx file contents into the program's treeview in appropriate columns.
    '''

    global db
    global bill_desc
    global bill_add_cost
    file = fd.askopenfilename(title='Select A File')
    clear_all()
    rf = pd.read_excel(file, usecols= "B:C")

    # drops null value columns (null = 'NaN' values)
    nan_val = float("NaN")                              # define NaN value to search for
    rf.replace('', nan_val, inplace=True)
    rf.dropna(how='all',axis='columns', inplace=True)   # dropna(how= 'any or 'all' where it has at least one NA, axis= 'columns',0 or 'index',1 Drop columns or rows, inplace=True)
    
    # iterates through columns and displays the column names onto the treeview
    tree["column"] = list(rf.columns)
    tree["show"] = "headings"
    print(tree["column"])

    # For Headings iterate over the columns
    for col in tree["columns"]:
        tree.heading(col, text=col)

   # Put data in rows in treeview
    rf_rows = rf.to_numpy().tolist()
    for row in rf_rows:
        tree.insert("", "end", values=row)
        rf.dropna(how='all',axis='columns',inplace=True)
    
    tree_view()

def save_file():
    '''
        Prompts user with save file dialog when save_btn is clicked. Writes/outputs dataframe gathered from db to xlsx file.
    '''
    f = fd.asksaveasfilename()
    df = pd.DataFrame.from_dict(db,orient='index')

    # output validation so that file extension isn't added every file save (when replacing file)
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
    global t
    global db
    b = 0
    
    bill_desc = bill.get()
    bill_add_cost = float(add_cost.get())
    
    # checks if either fields are empty, does not store values if one or the other is empty
    if bill_desc != '' and bill_add_cost != '':
        db[count] = [bill_desc, bill_add_cost]
        count+=1
        t = t+bill_add_cost
        
    total_label.config(text=f'Total: ${format(f"{t:.2f}")}')

    if bill_desc == '' or bill_add_cost == '':
        bill.delete(0, END)
        add_cost.delete(0, END)
    elif isinstance(bill_add_cost, float) == False:
        bill.delete(0, END)
        add_cost.delete(0, END)
    elif isinstance(bill_desc, str) == False:
        b = 1
        bill.delete(0, END)
        add_cost.delete(0, END)
    else:
        # inserts values directly from entry fields bill and add_cost, not from db
        # if b == 1, warning is triggered above. if b == 0 if warning is not triggered, continue with program
        if b == 0:
            tree.insert(parent='',index=0, text=f'{bill_desc}',values=(bill_desc, format(f"{bill_add_cost:.2f}")))
            bill.delete(0, END)
            add_cost.delete(0, END)
            
def delete_bill_func():
    '''
        Delete function attached to delete_btn. Deletes selected item from treeview.
    '''
    global t
    global db

    selected = tree.selection()
    item = tree.item(selected)
    record = item['values']
    for k, v in list(db.items()):
        if record[0] in v:
            del db[k]

    t = t - float(record[1])
    tree.delete(selected)
    # update label
    total_label.config(text=f'Total: ${format(f"{t:.2f}")}')
    
def clear_all():
    for i in tree.get_children():
        tree.delete(i)
    for i in list(db.keys()):
        db.pop(i)

    # line below connects to db directly, and shows the databases' values are cleared
    total_label.config(text=f'Total: ${format(f"{sum(list(db)):.2f}")}')

def tree_view():
    '''
        Generates tree_view box and columns that lists
    '''
    tree['columns']=('Bill Name','Cost')
    tree.column("Bill Name", anchor=CENTER, width=193, stretch=False)
    tree.column("Cost", anchor=CENTER, width=143, stretch=False)

    tree.heading('Bill Name', text='Bill Name', anchor=CENTER)
    tree.heading('Cost', text='Cost', anchor=CENTER)
    tree.place(relx=.3,rely=.22)
    style.configure("Treeview",background='#3b403b', fieldbackground='#3b403b', fg='#ffffff')
    style.map('Treeview', background=[('selected', '#303330')])

def disable_btn():
    '''
        Function to disable features for testing
    '''
    file_menu.entryconfig("Open File", state="disabled")

'''
    Generate GUI
'''
# put tree function here
tree_view()

# initialize open file and save file buttons within menu
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
total_label = Label(root, text=f'Total: ${format(f"{t:.2f}")}', bg='#303330', font = label_font, fg='#ffffff')
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

# version label
vlabel = Label(root, text="v1.7", font=Font(family='Noto Sans', size=7), bg='#303330', fg='#ffffff')
vlabel.place(relx=.01,rely=.94)

# add add button
add_btn = Button(root, padx=36, pady=6, text='   ADD  ', font = my_font, bd=0, bg='#3b403b',fg='#ffffff',activeforeground='#080808', activebackground='#424d42', command=add_bill_func)
add_btn.place(relx=.015,rely=.47)

# add delete button
delete_btn = Button(root, padx=36, pady=6, text='DELETE', font=my_font, bd=0, bg='#3b403b',fg='#ffffff',activeforeground='#080808', activebackground='#424d42', command=delete_bill_func)
delete_btn.place(relx=.015,rely=.62)

# add clear all button
clear_btn = Button(root, padx=35, pady=6, text=' CLEAR ', font=my_font, bd=0, bg='#3b403b',fg='#ffffff',activeforeground='#080808', activebackground='#424d42', command=clear_all)
clear_btn.place(relx=.015,rely=.77)

root.resizable(width=False, height=False)
root.mainloop()
