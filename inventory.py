import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import random
import os

# Predefined Grocery Items
grocery_items = ["Rice", "Wheat", "Milk", "Eggs", "Soap", "Sugar", "Salt", "Tea", "Coffee", "Oil"]

# Create Database & Table
# ✅ Create Database & Tables
conn = sqlite3.connect("inventory.db")
cursor = conn.cursor()

# Inventory Table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        qty INTEGER NOT NULL,
        price REAL NOT NULL
    )
""")

# ✅ Ensure "delivered" table exists
cursor.execute("""
    CREATE TABLE IF NOT EXISTS delivered (
        delivery_id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id TEXT NOT NULL,
        name TEXT NOT NULL,
        qty INTEGER NOT NULL,
        delivery_date TEXT NOT NULL
    )
""")

conn.commit()
conn.close()

# Create main window
root = tk.Tk()
root.title("Inventory Management")
root.geometry("650x500")
root.configure(bg="#E6E6FA")  # Light Lavender Background

FONT = ("Arial", 12)

# Function to generate a unique Product ID
def generate_product_id():
    return f"P{random.randint(1000, 9999)}"

# Function to add a new item to database
def add_item():
    name = item_dropdown.get()
    qty = qty_entry.get()
    price = price_entry.get()
    product_id = generate_product_id()

    if name and qty.isdigit() and price.replace('.', '', 1).isdigit():
        conn = sqlite3.connect("inventory.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO inventory (product_id, name, qty, price) VALUES (?, ?, ?, ?)",
                       (product_id, name, int(qty), float(price)))
        conn.commit()
        conn.close()

        update_listbox()
        export_to_excel()
        clear_fields()
    else:
        messagebox.showerror("Input Error", "Please enter valid details!")

# Function to delete an item from database
def delete_item():
    selected = inventory_list.curselection()
    if selected:
        index = inventory_list.get(selected[0]).split(" - ")[0]  # Extract ID
        conn = sqlite3.connect("inventory.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM inventory WHERE id=?", (index,))
        conn.commit()
        conn.close()

        update_listbox()
        export_to_excel()
    else:
        messagebox.showwarning("Selection Error", "No item selected!")

# Function to fetch and display inventory items
def update_listbox():
    inventory_list.delete(0, tk.END)
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM inventory")
    rows = cursor.fetchall()
    conn.close()

    for row in rows:
        print("DEBUG:", row)  # Print row to check its content
        if len(row) < 5:  # Prevent index errors
            continue
        inventory_list.insert(tk.END, f"{row[0]} - {row[1]} - {row[2]} - Qty: {row[3]} - ${row[4]:.2f}")


# Function to clear entry fields
def clear_fields():
    qty_entry.delete(0, tk.END)
    price_entry.delete(0, tk.END)

# Function to export data to Excel
def export_to_excel():
    conn = sqlite3.connect("inventory.db")

    df = pd.read_sql_query("SELECT * FROM inventory", conn)  # ✅ Get latest data from database
    conn.close()

    excel_file = "inventory.xlsx"

    # Ensure file is not open before writing
    if os.path.exists(excel_file):
        try:
            os.remove(excel_file)
        except PermissionError:
            messagebox.showerror("File Error", "Please close inventory.xlsx before exporting.")
            return

    df.to_excel(excel_file, index=False)
    messagebox.showinfo("Export Successful", "Data exported to inventory.xlsx")


# Function to add a new item to the dropdown list
def add_new_item():
    new_item = new_item_entry.get()
    if new_item and new_item not in grocery_items:
        grocery_items.append(new_item)
        item_dropdown['values'] = grocery_items  # Update dropdown values
        new_item_entry.delete(0, tk.END)
        messagebox.showinfo("Success", f"'{new_item}' added to the list!")
    elif new_item in grocery_items:
        messagebox.showwarning("Duplicate", f"'{new_item}' is already in the list.")
    else:
        messagebox.showerror("Input Error", "Please enter a valid item name.")

# UI Components
frame = tk.Frame(root, bg="#FFD700")  # Gold Header
frame.pack(fill=tk.X)

title_label = tk.Label(frame, text="Inventory Management", font=("Arial", 16, "bold"), bg="#FFD700", fg="black")
title_label.pack(pady=5)

form_frame = tk.Frame(root, bg="#ADD8E6")  # Light Blue Form Background
form_frame.pack(pady=10, fill=tk.X)

# Dropdown for Item Selection
tk.Label(form_frame, text="Item Name:", font=FONT, bg="#ADD8E6").grid(row=0, column=0, padx=10, pady=5, sticky="w")
item_dropdown = ttk.Combobox(form_frame, font=FONT, values=grocery_items)
item_dropdown.grid(row=0, column=1, padx=10, pady=5)
item_dropdown.current(0)  # Set default value

# Quantity Entry
tk.Label(form_frame, text="Quantity:", font=FONT, bg="#ADD8E6").grid(row=1, column=0, padx=10, pady=5, sticky="w")
qty_entry = tk.Entry(form_frame, font=FONT)
qty_entry.grid(row=1, column=1, padx=10, pady=5)

# Price Entry
tk.Label(form_frame, text="Price:", font=FONT, bg="#ADD8E6").grid(row=2, column=0, padx=10, pady=5, sticky="w")
price_entry = tk.Entry(form_frame, font=FONT)
price_entry.grid(row=2, column=1, padx=10, pady=5)

# Buttons
button_frame = tk.Frame(root, bg="#90EE90")  # Light Green Button Background
button_frame.pack(pady=10, fill=tk.X)

add_btn = tk.Button(button_frame, text="Add Item", font=FONT, bg="#32CD32", fg="white", command=add_item)
add_btn.pack(side=tk.LEFT, padx=10, pady=5)

delete_btn = tk.Button(button_frame, text="Delete Item", font=FONT, bg="#FF4500", fg="white", command=delete_item)
delete_btn.pack(side=tk.LEFT, padx=10, pady=5)

export_btn = tk.Button(button_frame, text="Export to Excel", font=FONT, bg="#4682B4", fg="white", command=export_to_excel)
export_btn.pack(side=tk.LEFT, padx=10, pady=5)

# New Item Entry and Button
new_item_frame = tk.Frame(root, bg="#E6E6FA")
new_item_frame.pack(pady=5, fill=tk.X)

new_item_entry = tk.Entry(new_item_frame, font=FONT)
new_item_entry.pack(side=tk.LEFT, padx=10, pady=5)

new_item_btn = tk.Button(new_item_frame, text="Add New Item", font=FONT, bg="#8A2BE2", fg="white", command=add_new_item)
new_item_btn.pack(side=tk.LEFT, padx=10, pady=5)

# Inventory List
list_frame = tk.Frame(root)
list_frame.pack(fill=tk.BOTH, expand=True)

inventory_list = tk.Listbox(list_frame, font=FONT)
inventory_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Load items on startup
update_listbox()

# Run the application
root.mainloop()
