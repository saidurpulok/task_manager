import tkinter as tk
from tkinter import simpledialog

def populate_listbox(listbox, data):
    for item in data:
        listbox.insert(tk.END, item)

def create_button(parent, text, command):
    button = tk.Button(parent, text=text, command=command)
    button.pack(side=tk.LEFT, padx=20)

def get_selected_tab(notebook):
    return notebook.tab(notebook.select(), "text")

def handle_tab_change(selected_tab, buttons_frame):
    if selected_tab == "Completed Tasks":
        hide_buttons(buttons_frame, ["Add Task", "Mark Complete", "Delete Task"])
        show_button(buttons_frame, "Delete Completed Task")
    else:
        show_buttons(buttons_frame, ["Add Task", "Mark Complete", "Delete Task"])
        hide_button(buttons_frame, "Delete Completed Task")

def get_user_input(root, title, prompt):
    return simpledialog.askstring(title, prompt)

def add_task_to_listbox(listbox, data_list, new_task):
    data_list.append(new_task)
    listbox.insert(tk.END, new_task)

def get_selected_task(listbox):
    selected_index = listbox.curselection()
    if selected_index:
        return listbox.get(selected_index)

def move_task(source_listbox, source_data, task, dest_listbox, dest_data):
    source_index = source_listbox.curselection()
    if source_index:
        source_listbox.delete(source_index)
        source_data.remove(task)
        dest_data.append(task)
        dest_listbox.insert(tk.END, task)

def delete_task_from_listbox(listbox, data_list, task):
    selected_index = listbox.curselection()
    if selected_index:
        listbox.delete(selected_index)
        del data_list[selected_index[0]]

def hide_button(parent, button_text):
    button = get_button_by_text(parent, button_text)
    if button:
        button.pack_forget()

def show_button(parent, button_text):
    button = get_button_by_text(parent, button_text)
    if button:
        button.pack()

def hide_buttons(parent, button_texts):
    for button_text in button_texts:
        hide_button(parent, button_text)

def show_buttons(parent, button_texts):
    for button_text in button_texts:
        show_button(parent, button_text)

def get_button_by_text(parent, button_text):
    for child in parent.winfo_children():
        if isinstance(child, tk.Button) and child.cget("text") == button_text:
            return child
