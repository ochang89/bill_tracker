Bill tracker created using tkinter & pandas. Able to read in .xlsx files, output list of ills to .xlsx files.

    Updates:
    Able to add single items with monthly costs
    *Open file feature disabled for now - FIXED see below*
    Save as file feature exports current list to an .xslx file
    *Sqlite3 db coming soon
    Now displays total amount of monthly costs
    Revamped GUI, resized window, added title bar icon, added colors
    *Fixed open file feature:
        - issue: Upon opening file, it displayed the primary ID number instead of the actual Bill Name in GUI     treeview
        - solution: specified inclusive columns as argument for 'usecols' in read_excel(file, usecols = "B:C"). Both sides are inclusive
    
    