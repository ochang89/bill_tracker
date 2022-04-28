from re import T
from sqlite3 import dbapi2
from tkinter import *
from tkinter import ttk, messagebox
from tkinter import filedialog as fd
import sqlite3
import pandas as pd
import os
import numpy
import datetime

'''
    Future features:
        - checkboxes that will pertain to weekly, bi-weekly, annual costs (already have monthly)
            - checking one of these boxes will trigger a field to pop up with the respective field from above
        - hot keys: use DEL key to delete directly from tree view.
                    Add (alt + A), Delete (alt + D), Clear (alt + C) hot keys
'''

root = Tk()
tree = ttk.Treeview(root, show='headings')

# frame = ttk.Frame(root, padding=10)
# frame.grid()
root.title("Handy Bill Handler")
root.geometry('500x500')

db = {}
item_costs = []
count = 0
t = 0.0

def open_file():
    global db
    global bill_desc
    global bill_add_cost
    bill_desc = bill.get()
    bill_add_cost = float(add_cost.get())
    db[count] = (bill_desc, bill_add_cost)
    file = fd.askopenfilename(title='Select A File')
    clear_all()
    rf = pd.read_excel(file)

    # drops null value columns (null = 'NaN' values)
    nan_val = float("NaN")                              # define NaN value to search for
    rf.replace('', nan_val, inplace=True)
    rf.dropna(how='all',axis='columns', inplace=True)   # dropna(how= 'any or 'all' where it has at least one NA, axis= 'columns',0 or 'index',1 Drop columns or rows, inplace=True)

    tree["column"] = list(rf.columns)
    tree["show"] = "headings"

    # For Headings iterate over the columns
    for col in tree["column"]:
        if col in tree['displaycolumns']:
            tree.heading(col, text=col)

   # Put Data in Rows
    rf_rows = rf.to_numpy().tolist()
    for row in rf_rows:
        tree.insert("", "end", values=row)
        rf.dropna(how='all',axis='columns',inplace=True)
    
    tree_view()

def add_bill_func():
    ''' 
    add_bill_func() grabs entries from input fields, adds them to db, and adds user typed bill/cost to columns in treeview display.
    Attached to add_btn.
    '''
    
    # conn = sqlite3.connect('bill_tracker.db')
    # c = conn.cursor()
    global bill_desc
    global bill_add_cost
    global count
    global t
    global db

    b = 0
    ms = 0
    
    bill_desc = bill.get()
    bill_add_cost = float(add_cost.get())
    
    db[count] = (bill_desc, bill_add_cost)
    count+=1
    t = t+bill_add_cost
    total_label.config(text=f'Total: ${format(f"{t:.2f}")}')

    if bill_desc == '' or bill_add_cost == '':
        ms = 1
    if isinstance(bill_add_cost, float) == False:
        ms = 2
        bill.delete(0, END)
        add_cost.delete(0, END)
    if isinstance(bill_add_cost, str) == True:
        ms = 3
        b = 1
        bill.delete(0, END)
        add_cost.delete(0, END)
        
    # each number in 'ms' represents a different warning, as seen below.
    if ms == 1:
        messagebox.showwarning('Warning', "Can't leave field blank")
    if ms == 2:
        messagebox.showwarning('Warning', "Cannot use numbers in Bill Name field")
        bill.delete(0, END)
        add_cost.delete(0, END)
    if ms == 3:
        messagebox.showwarning('Warning', "Cannot use text in Monthly Cost field")
        bill.delete(0, END)
        add_cost.delete(0, END)
    else:
        # inserts values directly from entry fields bill and add_cost, not from db
        # if b == 1, warning is triggered above. if b == 0 if warning is not triggered, continue with program
        if b == 0:
            tree.insert(parent='',index=0, text=f'{bill_desc}',values=(bill_desc, format(f"{bill_add_cost:.2f}")))
            
            # lbox.insert(0, [bill_desc, bill_add_cost])
            # Entry.delete() must be put before database conn.commit() and conn.close() to work

            bill.delete(0, END)
            add_cost.delete(0, END)
            # add bill_name and cost to sqlite db
            # c.execute("INSERT INTO bills VALUES (:bill_desc, :bill_add_cost)",
            #         {
            #             'bill_desc': bill_desc,
            #             'bill_add_cost': bill_add_cost
            #         }
            # )
            # c.execute(""" SELECT oid, * FROM bills""")
            # conn.commit()
            # conn.close()
            # clear field after pressing add bill button
    

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
    # print(f"Deleted bill: {record[0]} - ${record[1]}")
    tree.delete(selected)

    # update label
    total_label.config(text=f'Total: ${format(f"{t:.2f}")}')
    
    # conn = sqlite3.connect('bill_tracker.db')
    # c = conn.cursor()
    # c.execute("DELETE FROM bills WHERE bill_name = ?", (selected,))
    # conn.commit()
    # conn.close()

# def table_exists():
#     '''
#         Checks if table exists, if not it creates table 'bills' in bill_tracker.db
#     '''
#     conn = sqlite3.connect('bill_tracker.db')
#     c = conn.cursor()

#     # create table with data types, sqlite automatically sets primary key
#     # in sqlite3, all tables are enlisted in the ** sqlite_master table **
#     table_exists = c.execute("""SELECT count(name) FROM sqlite_master WHERE type='table' AND name='bills'; """).fetchall()

#     # check to see if table exists, creates bills table if not
#     if table_exists == []:
#         c.execute("""CREATE TABLE bills (
#         bill_name text,
#         cost integer
#         )""")
#     else:
#         pass
#     c.execute("""SELECT * FROM sqlite_master WHERE type='table' AND name='bills'; """)
#     conn.commit()
#     conn.close()

def clear_all():
    for i in tree.get_children():
        tree.delete(i)
        item = tree.item(i)
        record = item['values']
        t = t - float(record[1])
        # print(f"Deleted bill: {record[0]} - ${record[1]}")

    total_label.config(text=f'Total: ${format(f"{t:.2f}")}')

def tree_view():
    '''
        Generates tree_view box and columns that lists
    '''
    tree['columns']=('Bill Name','Cost')
    tree.column("Bill Name", anchor=CENTER, width=175, stretch=False)
    tree.column("Cost", anchor=CENTER, width=129, stretch=False)

    tree.heading('Bill Name', text='Bill Name', anchor=CENTER)
    tree.heading('Cost', text='Cost', anchor=CENTER)
    tree.place(relx=.3,rely=.40)

def save_file():
    '''
        Prompts user with save file dialog when save_btn is clicked. Writes/outputs dataframe gathered from db to xlsx file.
        
    '''
    f = fd.asksaveasfilename()
    df = pd.DataFrame.from_dict(db,orient='index')
    writer = pd.ExcelWriter(f'{f}.xlsx')
    df.to_excel(writer,sheet_name=f'{datetime.date.today()}')
    writer.save()

def disable_btn():
    '''
        Tool to disable features
    '''
    file_menu.entryconfig("Open File", state="disabled")

'''
    Code below generates GUI
'''
# put tree function here
tree_view()

m = Menu(root)
root.config(menu=m)

file_menu = Menu(m, tearoff=False)
m.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="Open File", command=disable_btn)
file_menu.add_command(label="Save File As", command=save_file)

# lbox = Listbox(root, width = 35, selectmode=BROWSE, relief=SUNKEN)
# lbox.place(relx=.52,rely=.05)

total_label = Label(root, text=f'Total: ${format(f"{t:.2f}")}')
total_label.place(relx=.68,rely=.88)

bill_label = Label(root, text="Bill Name:")
bill_label.place(relx=.05, rely=.15)
bill = Entry(root, bd=1)
bill.place(relx=.22, rely=.15)

add_cost_label = Label(root, text="Monthly Cost:")
add_cost_label.place(relx=.05, rely=.2)
add_cost = Entry(root, bd=1)
add_cost.place(relx=.22, rely=.2)

vlabel = Label(root, text="v1.3", font=('Arial', 8))
vlabel.place(relx=.01,rely=.96)

# add add button
add_btn = Button(root, padx=15, pady=6, text='  Add  ', bd=.5, bg='#e8e8e8', activebackground='#f0efed', command=add_bill_func)
add_btn.place(relx=.08,rely=.60)

# add delete button
delete_btn = Button(root, padx=13, pady=6, text=' Delete ', bd=.5, bg='#e8e8e8', activebackground='#f0efed', command=delete_bill_func)
delete_btn.place(relx=.08,rely=.70)

# add clear all button
clear_btn = Button(root, padx=16, pady=6, text=' Clear ', bd=.5, bg='#e8e8e8', activebackground='#f0efed', command=clear_all)
clear_btn.place(relx=.08,rely=.80)

# connect to db, creates bill_tracker.db if it doesn't exist
# table_exists()

root.resizable(width=False, height=False)
root.mainloop()
