from tkinter import *
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import simpledialog
from ttkthemes import themed_tk as ttkt
import random
from datetime import datetime
from datetime import timedelta
from datetime import date
from dateutil.parser import parse
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import tkcalendar
from tkcalendar import Calendar, DateEntry

import db

#Sign in to task-diary
password_root = Tk()
password_root.withdraw()
password = simpledialog.askstring("Password", "Enter password:", show="*")
password_root.destroy()

if password is None:
    sys.exit()

#Load tables
db.initialize_db(password)
db.create_table()
db.create_table2()
db.create_table3()
db.create_table4()
db.create_table5()
tasks_due=[]


def SignUp():
    global SignUp_screen
    SignUp_screen = Toplevel(main_root)
    SignUp_screen.title("SignUp")
    SignUp_screen.geometry("300x250")

    global username
    global password
    global username_entry
    global password_entry
    username = StringVar()
    password = StringVar()

    Label(SignUp_screen, text="Please enter details below", bg="green").pack()
    Label(SignUp_screen, text="").pack()
    username_label = Label(SignUp_screen, text="Username * ")
    username_label.pack()
    username_entry = Entry(SignUp_screen, textvariable=username)
    username_entry.pack()
    password_label = Label(SignUp_screen, text="Password * ")
    password_label.pack()
    password_entry = Entry(SignUp_screen, textvariable=password)
    password_entry.pack()
    Label(SignUp_screen, text="").pack()
    Button(SignUp_screen, text="SignUp", width=10, height=1, bg="green", command = SignUp_user).pack()

def SignIn():
    global SignIn_screen
    SignIn_screen = Toplevel(main_root)
    SignIn_screen.title("SignIn")
    SignIn_screen.geometry("300x250")
    Label(SignIn_screen, text="Please enter details below to SignIn").pack()
    Label(SignIn_screen, text="").pack()

    global username_verify
    global password_verify

    username_verify = StringVar()
    password_verify = StringVar()

    global username_SignIn_entry
    global password_SignIn_entry

    Label(SignIn_screen, text="Username * ").pack()
    username_SignIn_entry = Entry(SignIn_screen, textvariable=username_verify)
    username_SignIn_entry.pack()
    Label(SignIn_screen, text="").pack()
    Label(SignIn_screen, text="Password * ").pack()
    password_SignIn_entry = Entry(SignIn_screen, textvariable=password_verify)
    password_SignIn_entry.pack()
    Label(SignIn_screen, text="").pack()
    Button(SignIn_screen, text="SignIn", width=10, height=1, command = SignIn_verify).pack()

def SignUp_user():
    username_value = username.get()
    occur=0
    for i in db.get_users():# i represents element of info which is list itself
        if username_value==i[0]:#to access the username of the "i" list and compare with the username entered by user
            occur=1 # if username already exists in database
    if occur==1:
        messagebox.showerror('Username',"User already xeists")
    else:
        password_value = password.get()#input password if username doesn't already exists
        length=len(password_value)# taking the length of password
        if  length>=5 and length<=10:#To check all the conditions on the password are satisfied
            t=(username_value,password_value)#create a tuple "t" containing name and password
            db.add_user(t)# add to database
            Label(SignUp_screen, text="Registration Success", fg="green", font=("calibri", 11)).pack()
        else:
           
            if(length<8 or length>15):
                messagebox.showerror('Password',"Your password should have 8-15 characters")
    username_entry.delete(0, END)
    password_entry.delete(0, END)


def SignIn_verify():
    username_value1 = username_verify.get()
    password_value1=password_verify.get()
    log=0#to check the sign-in success
    for g in db.get_users():
        if g[0]==username_value1:#comparing the name
            if g[1]==password_value1:#if name is present comparing the name
                messagebox.showinfo('Login','Logged in successfully!')
                log=1#sign-in successful
            else:
                messagebox.showerror('Login','Password incorrect!Try again')   
    if log==0:
        messagebox.showerror('Login','Failed to SignIn')
        # sys.exit()
    
def main_frame_screen():
    global main_root
    main_root = ttkt.ThemedTk()
    main_root.set_theme('radiance')
    main_root.geometry("300x250")
    main_root.title("Account SignIn")
    Label(text="Select Your Choice", bg="green", width="300", height="2", font=("Calibri", 13)).pack()
    Label(text="").pack()
    Button(text="SignIn", height="2", width="30", command = SignIn).pack()
    Label(text="").pack()
    Button(text="SignUp", height="2", width="30", command=SignUp).pack()

main_frame_screen()


root = ttkt.ThemedTk()     #Main window
tname=db.get_theme()
if len(tname)==0 :         #If youare opening for the first time default theme will be appear.
    root.set_theme('radiance')
else:                      #else the theme last you change will be appear.
    root.set_theme(tname[0][0])
root.title("Task Manager")
columns = ("task_name", "priority_of_task", "category", "is_done","deadline")
#Table for the task
tree = ttk.Treeview(root, height=36, selectmode="browse", columns=columns, show="headings")
scrollbar = ttk.Scrollbar(root, orient=VERTICAL, command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)
tree.grid(row=0, column=0, rowspan=2)
scrollbar.grid(row=0, column=1, rowspan=2, sticky=(W, N, E, S))

def already_notified(taskn):
    for item in db.get_notified_tasks():
        if taskn[0]==item[0]:
            return True
    return False

def notify():
    #check the task date if its deadline is after 1 day, then notify user via email.
    for item in db.get_tasks():
        #check that the task is not notfied already
        if not already_notified(item):
            dd=datetime.strptime(item[5], "%d-%m-%Y")
            dd2= dd -timedelta(days=1)
            dd3=dd2.strftime('%d-%m-%Y')
            today=datetime.today().strftime('%d-%m-%Y')
            if (dd3==today) and (item[4]=="false"):   #check whether the task is not completed
                email_notify(item)
                db.add_notify_date(item)
                print("Email notification sent sucessfully")


def email_notify(item):
    row=db.get_email()
    if(len(row)==0):
        email ="task.diary534@gmail.com" #add your gmail id from which u want to sent (only gmail account)
        password ="task@diary"#add your email password
        send_to_email ="task.diary534@gmail.com"#add your email id where u want to sent (any mail account)
    else:    
        email = row[0][0]#add your gmail id from which u want to sent (only gmail account)
        password = row[0][1]#add your email password
        send_to_email = row[0][2]#add your email id where u want to sent (any mail account)
    subject = 'Task Notifier'# The subject line
    message ='Category of task: '+item[3]+'\n\nYour Task:'+ item[1]
    msg = MIMEMultipart()
    msg['From'] = email
    msg['To'] = send_to_email
    msg['Subject'] = subject

    # Attach the message to the MIMEMultipart object
    msg.attach(MIMEText(message, 'plain'))
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(email, password)
    text = msg.as_string() # You now need to convert the MIMEMultipart object to a string to send
    server.sendmail(email, send_to_email, text)
    server.quit()

def treeview_sort_column(treeview, column, reverse):
    children_list = [(treeview.set(child, column), child) for child in treeview.get_children("")]
    if(column=="priority_of_task"):
        children_list.sort(key=lambda column:int(column[0]),reverse=reverse)
    elif(column=="deadline"):
        children_list.sort(key=lambda column:datetime.strptime(column[0],'%d-%m-%Y'),reverse=reverse)
    else:
        children_list.sort(reverse=reverse)
    for index, (value, child) in enumerate(children_list):
        treeview.move(child, "", index)

    treeview.heading(column, command=lambda: treeview_sort_column(treeview, column, not reverse))

for column in columns:
    tree.heading(column, text=column, command=lambda col=column: treeview_sort_column(tree, col, False))

width, height = root.winfo_screenwidth(), root.winfo_screenheight()
root.geometry("{0}x{1}+0+0".format(width, height))

width_task_name = int(width * 0.20)
tree.column("task_name", width=width_task_name, anchor="center")
tree.heading("task_name", text="Tasks")

width_priority_of_task = int(width * 0.08)
tree.column("priority_of_task", width=width_priority_of_task, anchor="center")
tree.heading("priority_of_task", text="Priority")

width_category = int(width * 0.15)
tree.column("category", width=width_category, anchor="center")
tree.heading("category", text="Category")

width_is_done = int(width * 0.11)
tree.column("is_done", width=width_is_done, anchor="center")
tree.heading("is_done", text="Is Finished")

width_deadline = int(width * 0.11)
tree.column("deadline", width=width_is_done, anchor="center")
tree.heading("deadline", text="Due date")

mainframe = ttk.Frame(root, padding="25 25 100 50")
mainframe.grid(row=0, column=2, sticky=(N, S, W, E))
mainframe.rowconfigure(0, weight=1)
mainframe.columnconfigure(0, weight=1)

task_name = StringVar()
ttk.Label(mainframe, text="Task name:").grid(column=1, row=1, sticky=(W, E))
task_name_widget = ttk.Entry(mainframe, width=20, textvariable=task_name)
task_name_widget.grid(column=2, row=1, sticky=(W, E))

priority_of_task = StringVar()
ttk.Label(mainframe, text="Priority of task \n(E.g 1 to 10):").grid(column=1, row=2, sticky=(W, E))
priority_of_task_widget = ttk.Entry(mainframe, width=20, textvariable=priority_of_task)
priority_of_task_widget.grid(column=2, row=2, sticky=(W, E))

category = StringVar()
ttk.Label(mainframe, text="Category:").grid(column=1, row=3, sticky=(W, E))
category_widget = ttk.Entry(mainframe, width=20, textvariable=category)
category_widget.grid(column=2, row=3, sticky=(W, E))

deadline = StringVar()
ttk.Label(mainframe, text="Deadline: \n(Format:dd-mm-yyyy)").grid(column=1, row=4, sticky=(W, E))
deadline_widget = ttk.Entry(mainframe, width=20, textvariable=deadline)
deadline_widget.grid(column=2, row=4, sticky=(W, E))

is_done = BooleanVar()
ttk.Label(mainframe, text="Is Done:").grid(column=1, row=5, sticky=(W, E))
is_done_widget = ttk.Checkbutton(mainframe, variable=is_done,
                                     onvalue=True, offvalue=False)
is_done_widget.grid(column=2, row=5, sticky=(W, E))




def create_task_item():
    #get the task details 
    task_name_value = task_name.get()
    priority_of_task_value = priority_of_task.get()
    category_value = category.get()
    is_done_value = is_done.get()
    deadline_value=deadline.get()

    if inputs_validation():
        item_values = (task_name_value,
                       priority_of_task_value,
                       category_value,
                       is_done_value,
                       deadline_value)

        item_id = db.add_task(item_values)

        tree.insert("", "end", item_id, text=item_id, values=(item_values[0],
                                                              item_values[1],
                                                              item_values[2],
                                                              item_values[3],
                                                              item_values[4]))

        task_name.set("")
        priority_of_task.set("")
        category.set("")
        deadline.set("")
        is_done.set(False)

        create_button["state"] = "normal"
        change_button["state"] = "disabled"
        notify()


def inputs_validation():
    task_name_value = task_name.get()
    priority_of_task_value = priority_of_task.get()
    category_value = category.get()
    deadline_value=deadline.get()

    today=datetime.today().strftime('%d-%m-%Y')
    today1=datetime.strptime(today,"%d-%m-%Y")

    try:
        dd=datetime.strptime(deadline_value,"%d-%m-%Y")
        isNotValidDate = False
    except ValueError :
        isNotValidDate = True 
    

    try:
        if not(len(task_name_value) <=25):
            messagebox.showerror("Task name", "Task name limit exceeded")
            return False
        if not(len(task_name_value) > 0 and len(task_name_value) <=25):
            messagebox.showerror("Task name", "Task name cannot be null")
            return False        
        if not(int(priority_of_task_value) > 0 and int(priority_of_task_value) <= 10):
            messagebox.showerror("Priority", "Priority is not valid")
            return False

        if not( len(category_value) <= 15):
            messagebox.showerror("Category", "Category limit exceeded")
            return False

        if (isNotValidDate):
            messagebox.showwarning("Due date", "Not valid date!")
            return False

        if (dd<today1):#deadline should be from today onwards
            messagebox.showwarning("Due date", "Deadline is gone!")
            return False  
    except:
        messagebox.showwarning("ADD TASK", "Not valid entry!")
        return False
          
    return True


create_button = ttk.Button(mainframe, text="Create Task", command=create_task_item)
create_button.grid(column=1, row=6, sticky=(W, E))

z=0
def change_theme():
    global z
    themes=root.get_themes()
    length=int(len(themes))
    while(True):
        z=z%length
        root.set_theme(themes[z])
        cal.tag_config('reminder', background='red', foreground='yellow')
        db.delete_theme()
        db.add_theme(themes[z])
        top.destroy()       
        z+=1
        break

changeTheme_button = ttk.Button(mainframe, text="Change Theme",command=change_theme)
changeTheme_button.grid(column=2, row=7, sticky=(W, E))


top = tk.Toplevel(root)
cal = Calendar(top, selectmode='none')  
date = cal.datetime.today()
cal.calevent_create(date, 'Today', 'message')
cal.pack(fill="both", expand=True)
def calendar_events():  
    top = tk.Toplevel(root)
    cal = Calendar(top, selectmode='none') 
    date = cal.datetime.today()
    cal.calevent_create(date, 'Today', 'message') 
    for item in db.get_tasks():
        dd=datetime.strptime(item[5], "%d-%m-%Y")
        cal.calevent_create(dd,item[1], 'reminder')
        cal.tag_config('reminder', background='red', foreground='yellow')
        cal.pack(fill="both", expand=True)
   
cal_events_btn=ttk.Button(mainframe, text='Calendar with Due Dates', command=calendar_events)
cal_events_btn.grid(column=1, row=7, sticky=(W, E))


search_task = StringVar()
search_task_widget = ttk.Entry(mainframe, width=20, textvariable=search_task)
search_task_widget.grid(column=2, row=9, sticky=(W, E))

def show_search_result():
    global data
    search_task_value= search_task.get()
    data=db.search_task(search_task_value)
    data.sort(key=lambda e: e[1], reverse=True)
    if(len(data)==0):
       textMsg="Search Result(Task not found)"
    else:
        textMsg="Search Result"
    search_result = tk.Toplevel(root)
    tk.Label(search_result, text=textMsg,bg="light steel blue" ,font=("Comic Sans MS",27)).grid(row=0, columnspan=3)
    # create Treeview with 3 columns
    cols = ('Sr no.','Category', 'Task', 'Due date')
    tree_search = ttk.Treeview(search_result, columns=cols, show='headings')
    for i in range(4):
        tree_search.column(i, anchor="center")    
    # set column headings
    for col in cols:
        tree_search.heading(col, text=col)    
    tree_search.grid(row=1, column=0, columnspan=2)
    for i, (category,task_name,deadline) in enumerate(data, start=1):
        tree_search.insert("", "end", values=(i,category,task_name,deadline))
    tk.Button(search_result, text="Close", width=15, command=search_result.destroy).grid(row=4, column=1)


Search_btn=ttk.Button(mainframe, text='Search', command=show_search_result)
Search_btn.grid(column=1, row=9, sticky=(W, E))


from_email=StringVar()
to_email = StringVar()
password=StringVar()
def Notify_email_func():
    row=db.get_email()
    print(row)
    if(len(row)==0):
        from_email.set("task.diary534@gmail.com")
        password.set("task@diary")
        to_email.set("task.diary534@gmail.com")
    else:    
        from_email.set(row[0][0])
        password.set(row[0][1])
        to_email.set(row[0][2])
    global email_wd1
    email_wd= tk.Toplevel(root)
    email_wd.geometry("300x200")
    email_wd1= ttk.Frame(email_wd, padding="25 25 100 50")
    email_wd1.grid(row=0, column=2, sticky=(N, S, W, E))
    email_wd1.rowconfigure(0, weight=1)
    email_wd1.columnconfigure(0, weight=1)
    tk.Label(email_wd1, text="Enter email details",bg="light steel blue",font=("Comic Sans MS",17)).grid(row=0, columnspan=3)
    ttk.Label(email_wd1, text="From email:").grid(column=1, row=2, sticky=(W, E))
    ttk.Label(email_wd1, text="password:").grid(column=1, row=3, sticky=(W, E))
    ttk.Label(email_wd1, text="To email:").grid(column=1, row=4, sticky=(W, E))
    from_email_widget = ttk.Entry(email_wd1, width=20, textvariable=from_email)
    from_email_widget.grid(column=2, row=2, sticky=(W, E))
    password_widget = ttk.Entry(email_wd1, width=20, textvariable=password)
    password_widget.grid(column=2, row=3, sticky=(W, E))
    to_email_widget = ttk.Entry(email_wd1, width=20, textvariable=to_email)
    to_email_widget.grid(column=2, row=4, sticky=(W, E))

    submit_btn=ttk.Button(email_wd1, text='Submit', command=submit_email)
    submit_btn.grid(column=2, row=5, sticky=(W, E))

def submit_email():
    from_email_value = from_email.get()
    password_value=password.get()
    to_email_value = to_email.get()
    item_values = (from_email_value,password_value,to_email_value,datetime.now())
    db.add_email(item_values)
    tk.Label(email_wd1,text="Email added Successfully",fg="green",font=("calibri",11)).grid(row=5, columnspan=3)
    from_email.set("")
    password.set("")
    to_email.set("")
        
Notify_email_btn=ttk.Button(mainframe, text='Change email', command=Notify_email_func)
Notify_email_btn.grid(column=2, row=10, sticky=(W, E))



def TaskDueToday_Tomorrow():
    notifyTrack=db.get_tasks()
    tasks_due=[]
    for item in notifyTrack:
        dd=datetime.strptime(item[5], "%d-%m-%Y")
        dd2= dd -timedelta(days=1)
        dd3=dd2.strftime('%d-%m-%Y')
        dd_c=dd.strftime('%d-%m-%Y')
        today=datetime.today().strftime('%d-%m-%Y')
        if (dd3==today or dd_c==today):
            i=(item[1],item[3],item[2],item[5])
            tasks_due.append(i)

    tasks_due.sort(key=lambda e: e[1], reverse=True)
    if(len(tasks_due)==0):
       textMsg="No tasks due today/tomorrow"
    else:
        textMsg="Tasks due today/tomorrow"
    tasks_due_result = tk.Toplevel(root)
    tk.Label(tasks_due_result, text=textMsg ,bg="light steel blue",font=("Comic Sans MS",27)).grid(row=0, columnspan=3)
    # create Treeview with 5 columns
    cols = ('Sr no.','Task', 'Category', 'Priority','Due on')
    tree_search = ttk.Treeview(tasks_due_result, columns=cols, show='headings')
    for i in range(5):
        tree_search.column(i, anchor="center")    
    # set column headings
    for col in cols:
        tree_search.heading(col, text=col)    
    tree_search.grid(row=1, column=0, columnspan=2)
    for i, (task_name,category,priority_of_task,deadline) in enumerate(tasks_due, start=1):
        tree_search.insert("", "end", values=(i,task_name,category,priority_of_task,deadline))
    tk.Button(tasks_due_result, text="Close", width=15, command=tasks_due_result.destroy).grid(row=4, column=1)


TasksDue_btn=ttk.Button(mainframe, text='Tasks Due Today/Tomorrow', command=TaskDueToday_Tomorrow)
TasksDue_btn.grid(column=1, row=10, sticky=(W, E))



def change_item():
    task_name_value = task_name.get()
    priority_of_task_value = priority_of_task.get()
    category_value = category.get()
    is_done_value = is_done.get()
    deadline_value=deadline.get()

    if inputs_validation():
        item_id = tree.item(tree.selection()[0], "text")
        item_values = (task_name_value,
                       priority_of_task_value,
                       category_value,
                       is_done_value,
                       deadline_value)

        db.edit_task(item_id, item_values)
        tree.item(tree.selection()[0], values=item_values)

        task_name.set("")
        priority_of_task.set("")
        category.set("")
        deadline.set("")
        is_done.set(False)

        create_button["state"] = "normal"
        change_button["state"] = "disabled"
        db.remove_item_notification_tracker(item_id)
        notify()

change_button = ttk.Button(mainframe, text="Change Task", command=change_item)
change_button.grid(column=2, row=6, sticky=(W, E))
change_button["state"] = "disabled"

for child in mainframe.winfo_children():
    child.grid_configure(padx=25, pady=25)

for item in db.get_tasks():
    tree.insert("", "end", item[0], text=item[0],values=(item[1], item[2], item[3], item[4],item[5]))

menu = Menu(root, tearoff=0)


def remove_task_item():
    item_id = tree.item(tree.selection()[0], "text")
    db.delete_task(item_id)
    tree.delete(item_id)

    task_name.set("")
    priority_of_task.set("")
    category.set("")
    deadline.set("")
    is_done.set(False)

    create_button["state"] = "normal"
    change_button["state"] = "disabled"


menu.add_command(label="Remove Task", command=remove_task_item)


def change_task_item_helper():
    item_values = tree.item(tree.selection()[0], "values")

    task_name.set(item_values[0])
    priority_of_task.set(item_values[1])
    category.set(item_values[2])
    is_done.set(item_values[3])
    deadline.set(item_values[4])

    create_button["state"] = "disabled"
    change_button["state"] = "normal"


menu.add_command(label="Change Task", command=change_task_item_helper)

def right_click_handler(event):
    show_contextual_menu(event)


def show_contextual_menu(event):
    if tree.focus():
        menu.post(event.x + 65, event.y)


tree.bind("<3>", right_click_handler)


def left_click_handler(event):
    menu.unpost()


tree.bind("<1>", left_click_handler)
notify()

def shutdown_hook():
    if messagebox.askyesno(message="Are you sure you want to quit?",
                           icon="question", title="Quit"):
        db.shutdown_db()
        root.destroy()

root.protocol("WM_DELETE_WINDOW", shutdown_hook)

root.mainloop()