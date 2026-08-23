import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import csv
from datetime import datetime
import matplotlib.pyplot as plt


# ============================================================
# DATABASE
# ============================================================

conn = sqlite3.connect("expense_tracker.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS expenses(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount REAL NOT NULL,
    category TEXT NOT NULL,
    description TEXT,
    date TEXT NOT NULL
)
""")

conn.commit()


# ============================================================
# APPLICATION SETTINGS
# ============================================================

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Expense Tracker")
app.geometry("1200x750")
app.minsize(1000, 650)

app.configure(fg_color="#F5F7FB")

editing_id = None


# ============================================================
# COLORS
# ============================================================

BG = "#F5F7FB"
SIDEBAR = "#1E293B"
HEADER = "#FFFFFF"
CARD = "#FFFFFF"

BLUE = "#2563EB"
GREEN = "#16A34A"
ORANGE = "#F59E0B"
RED = "#DC2626"
PURPLE = "#7C3AED"

TEXT = "#1E293B"
SECONDARY = "#64748B"


# ============================================================
# MAIN LAYOUT
# ============================================================

sidebar = ctk.CTkFrame(
    app,
    width=220,
    corner_radius=0,
    fg_color=SIDEBAR
)

sidebar.pack(
    side="left",
    fill="y"
)

main_area = ctk.CTkFrame(
    app,
    fg_color=BG,
    corner_radius=0
)

main_area.pack(
    side="right",
    fill="both",
    expand=True
)


# ============================================================
# SIDEBAR
# ============================================================

logo = ctk.CTkLabel(
    sidebar,
    text="💰 Expense\nTracker",
    font=("Arial", 26, "bold"),
    text_color="white",
    justify="left"
)

logo.pack(
    padx=25,
    pady=(35, 50),
    anchor="w"
)


dashboard_btn = ctk.CTkButton(
    sidebar,
    text="🏠  Dashboard",
    height=45,
    corner_radius=10,
    fg_color=BLUE,
    hover_color="#1D4ED8",
    anchor="w",
    font=("Arial", 14, "bold"),
    command=lambda: show_expenses()
)

dashboard_btn.pack(
    fill="x",
    padx=20,
    pady=5
)


expenses_btn = ctk.CTkButton(
    sidebar,
    text="💳  Expenses",
    height=45,
    corner_radius=10,
    fg_color="transparent",
    hover_color="#334155",
    anchor="w",
    font=("Arial", 14),
    command=lambda: show_expenses()
)

expenses_btn.pack(
    fill="x",
    padx=20,
    pady=5
)


reports_btn = ctk.CTkButton(
    sidebar,
    text="📊  Reports",
    height=45,
    corner_radius=10,
    fg_color="transparent",
    hover_color="#334155",
    anchor="w",
    font=("Arial", 14),
    command=lambda: show_chart()
)

reports_btn.pack(
    fill="x",
    padx=20,
    pady=5
)


# ============================================================
# HEADER
# ============================================================

header = ctk.CTkFrame(
    main_area,
    height=80,
    fg_color=HEADER,
    corner_radius=0
)

header.pack(
    fill="x"
)


title = ctk.CTkLabel(
    header,
    text="Expense Dashboard",
    font=("Arial", 28, "bold"),
    text_color=TEXT
)

title.pack(
    side="left",
    padx=30,
    pady=20
)


today_label = ctk.CTkLabel(
    header,
    text=datetime.now().strftime("%d %B %Y"),
    font=("Arial", 14),
    text_color=SECONDARY
)

today_label.pack(
    side="right",
    padx=30
)


# ============================================================
# CONTENT
# ============================================================

content = ctk.CTkFrame(
    main_area,
    fg_color=BG,
    corner_radius=0
)

content.pack(
    fill="both",
    expand=True,
    padx=25,
    pady=20
)


# ============================================================
# DASHBOARD CARDS
# ============================================================

cards_frame = ctk.CTkFrame(
    content,
    fg_color="transparent"
)

cards_frame.pack(
    fill="x",
    pady=(0, 20)
)


# TOTAL EXPENSE CARD

total_card = ctk.CTkFrame(
    cards_frame,
    fg_color=CARD,
    corner_radius=15,
    height=120
)

total_card.pack(
    side="left",
    fill="both",
    expand=True,
    padx=(0, 10)
)


ctk.CTkLabel(
    total_card,
    text="💰  Total Expenses",
    font=("Arial", 14),
    text_color=SECONDARY
).pack(
    anchor="w",
    padx=20,
    pady=(18, 5)
)


total_value = ctk.CTkLabel(
    total_card,
    text="₹0.00",
    font=("Arial", 25, "bold"),
    text_color=GREEN
)

total_value.pack(
    anchor="w",
    padx=20
)


# TRANSACTION CARD

transaction_card = ctk.CTkFrame(
    cards_frame,
    fg_color=CARD,
    corner_radius=15,
    height=120
)

transaction_card.pack(
    side="left",
    fill="both",
    expand=True,
    padx=10
)


ctk.CTkLabel(
    transaction_card,
    text="🧾  Transactions",
    font=("Arial", 14),
    text_color=SECONDARY
).pack(
    anchor="w",
    padx=20,
    pady=(18, 5)
)


transaction_value = ctk.CTkLabel(
    transaction_card,
    text="0",
    font=("Arial", 25, "bold"),
    text_color=BLUE
)

transaction_value.pack(
    anchor="w",
    padx=20
)


# AVERAGE CARD

average_card = ctk.CTkFrame(
    cards_frame,
    fg_color=CARD,
    corner_radius=15,
    height=120
)

average_card.pack(
    side="left",
    fill="both",
    expand=True,
    padx=(10, 0)
)


ctk.CTkLabel(
    average_card,
    text="📈  Average Expense",
    font=("Arial", 14),
    text_color=SECONDARY
).pack(
    anchor="w",
    padx=20,
    pady=(18, 5)
)


average_value = ctk.CTkLabel(
    average_card,
    text="₹0.00",
    font=("Arial", 25, "bold"),
    text_color=PURPLE
)

average_value.pack(
    anchor="w",
    padx=20
)


# ============================================================
# INPUT SECTION
# ============================================================

input_frame = ctk.CTkFrame(
    content,
    fg_color=CARD,
    corner_radius=15
)

input_frame.pack(
    fill="x",
    pady=(0, 15)
)


ctk.CTkLabel(
    input_frame,
    text="Add / Edit Expense",
    font=("Arial", 18, "bold"),
    text_color=TEXT
).grid(
    row=0,
    column=0,
    columnspan=4,
    padx=20,
    pady=(15, 10),
    sticky="w"
)


# AMOUNT

ctk.CTkLabel(
    input_frame,
    text="Amount",
    text_color=SECONDARY
).grid(
    row=1,
    column=0,
    padx=20,
    pady=5,
    sticky="w"
)


amount_entry = ctk.CTkEntry(
    input_frame,
    placeholder_text="Enter amount",
    height=38
)

amount_entry.grid(
    row=2,
    column=0,
    padx=20,
    pady=(0, 15),
    sticky="ew"
)


# CATEGORY

ctk.CTkLabel(
    input_frame,
    text="Category",
    text_color=SECONDARY
).grid(
    row=1,
    column=1,
    padx=20,
    pady=5,
    sticky="w"
)


category_combo = ctk.CTkComboBox(
    input_frame,
    values=[
        "Food",
        "Travel",
        "Shopping",
        "Bills",
        "Entertainment",
        "Education",
        "Health",
        "Other"
    ],
    height=38
)

category_combo.set("Food")

category_combo.grid(
    row=2,
    column=1,
    padx=20,
    pady=(0, 15),
    sticky="ew"
)


# DESCRIPTION

ctk.CTkLabel(
    input_frame,
    text="Description",
    text_color=SECONDARY
).grid(
    row=1,
    column=2,
    padx=20,
    pady=5,
    sticky="w"
)


description_entry = ctk.CTkEntry(
    input_frame,
    placeholder_text="What was this expense for?",
    height=38
)

description_entry.grid(
    row=2,
    column=2,
    padx=20,
    pady=(0, 15),
    sticky="ew"
)


# DATE

ctk.CTkLabel(
    input_frame,
    text="Date",
    text_color=SECONDARY
).grid(
    row=1,
    column=3,
    padx=20,
    pady=5,
    sticky="w"
)


date_entry = ctk.CTkEntry(
    input_frame,
    placeholder_text="DD-MM-YYYY",
    height=38
)

date_entry.insert(
    0,
    datetime.now().strftime("%d-%m-%Y")
)

date_entry.grid(
    row=2,
    column=3,
    padx=20,
    pady=(0, 15),
    sticky="ew"
)


for i in range(4):
    input_frame.grid_columnconfigure(
        i,
        weight=1
    )


# ============================================================
# BUTTON FRAME
# ============================================================

button_frame = ctk.CTkFrame(
    input_frame,
    fg_color="transparent"
)

button_frame.grid(
    row=3,
    column=0,
    columnspan=4,
    pady=(0, 15)
)


# ============================================================
# DATABASE / DASHBOARD FUNCTIONS
# ============================================================

def update_dashboard():

    cursor.execute(
        "SELECT SUM(amount) FROM expenses"
    )

    total = cursor.fetchone()[0]

    if total is None:
        total = 0


    cursor.execute(
        "SELECT COUNT(*) FROM expenses"
    )

    count = cursor.fetchone()[0]


    if count > 0:
        average = total / count
    else:
        average = 0


    total_value.configure(
        text=f"₹{total:,.2f}"
    )

    transaction_value.configure(
        text=str(count)
    )

    average_value.configure(
        text=f"₹{average:,.2f}"
    )


# ============================================================
# SHOW ALL EXPENSES
# ============================================================

def show_expenses():

    for item in tree.get_children():
        tree.delete(item)


    cursor.execute(
        """
        SELECT *
        FROM expenses
        ORDER BY id DESC
        """
    )

    rows = cursor.fetchall()


    # Displayed ID starts from 1.
    # Database ID remains hidden internally.

    for display_id, row in enumerate(
        rows,
        start=1
    ):

        database_id = row[0]

        amount = row[1]
        category = row[2]
        description = row[3]
        date = row[4]


        tree.insert(
            "",
            "end",
            iid=str(database_id),
            values=(
                display_id,
                amount,
                category,
                description,
                date
            )
        )


    update_dashboard()


# ============================================================
# CLEAR INPUT FIELDS
# ============================================================

def clear_fields():

    global editing_id

    editing_id = None


    amount_entry.delete(
        0,
        "end"
    )


    category_combo.set(
        "Food"
    )


    description_entry.delete(
        0,
        "end"
    )


    date_entry.delete(
        0,
        "end"
    )


    date_entry.insert(
        0,
        datetime.now().strftime("%d-%m-%Y")
    )


# ============================================================
# ADD / UPDATE EXPENSE
# ============================================================

def add_expense():

    global editing_id


    amount = amount_entry.get().strip()

    category = category_combo.get().strip()

    description = description_entry.get().strip()

    date = date_entry.get().strip()


    # Validation

    if not amount or not category or not date:

        messagebox.showwarning(
            "Missing Information",
            "Please enter amount, category and date."
        )

        return


    try:

        amount = float(amount)

        if amount <= 0:
            raise ValueError

    except ValueError:

        messagebox.showerror(
            "Invalid Amount",
            "Please enter a valid positive amount."
        )

        return


    # ADD NEW EXPENSE

    if editing_id is None:

        cursor.execute(
            """
            INSERT INTO expenses
            (
                amount,
                category,
                description,
                date
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                amount,
                category,
                description,
                date
            )
        )


        messagebox.showinfo(
            "Success",
            "Expense added successfully!"
        )


    # UPDATE EXISTING EXPENSE

    else:

        cursor.execute(
            """
            UPDATE expenses

            SET
                amount=?,
                category=?,
                description=?,
                date=?

            WHERE id=?
            """,
            (
                amount,
                category,
                description,
                date,
                editing_id
            )
        )


        messagebox.showinfo(
            "Success",
            "Expense updated successfully!"
        )


        editing_id = None


    conn.commit()


    clear_fields()

    show_expenses()


# ============================================================
# DELETE EXPENSE
# ============================================================

def delete_expense():

    selected = tree.selection()


    if not selected:

        messagebox.showwarning(
            "No Selection",
            "Please select an expense to delete."
        )

        return


    # Get REAL database ID

    database_id = tree.item(
        selected[0]
    )["iid"]


    confirm = messagebox.askyesno(
        "Confirm Delete",
        "Are you sure you want to delete this expense?"
    )


    if not confirm:
        return


    cursor.execute(
        """
        DELETE FROM expenses
        WHERE id=?
        """,
        (database_id,)
    )


    conn.commit()


    show_expenses()


    messagebox.showinfo(
        "Deleted",
        "Expense deleted successfully!"
    )


# ============================================================
# EDIT EXPENSE
# ============================================================

def edit_expense():

    global editing_id


    selected = tree.selection()


    if not selected:

        messagebox.showwarning(
            "No Selection",
            "Please select an expense to edit."
        )

        return


    # Get actual database ID

    editing_id = tree.item(
        selected[0]
    )["iid"]


    values = tree.item(
        selected[0]
    )["values"]


    amount_entry.delete(
        0,
        "end"
    )

    amount_entry.insert(
        0,
        values[1]
    )


    category_combo.set(
        values[2]
    )


    description_entry.delete(
        0,
        "end"
    )

    description_entry.insert(
        0,
        values[3]
    )


    date_entry.delete(
        0,
        "end"
    )

    date_entry.insert(
        0,
        values[4]
    )


# ============================================================
# SEARCH BY CATEGORY
# ============================================================

def search_expense():

    category = search_entry.get().strip()


    for item in tree.get_children():
        tree.delete(item)


    # Empty search = show everything

    if category == "":

        show_expenses()

        return


    cursor.execute(
        """
        SELECT *
        FROM expenses

        WHERE category LIKE ?

        ORDER BY id DESC
        """,
        (
            "%" + category + "%",
        )
    )


    rows = cursor.fetchall()


    # Sequential displayed IDs

    for display_id, row in enumerate(
        rows,
        start=1
    ):

        database_id = row[0]


        tree.insert(
            "",
            "end",
            iid=str(database_id),
            values=(
                display_id,
                row[1],
                row[2],
                row[3],
                row[4]
            )
        )


    # Update dashboard for search results

    if rows:

        total = sum(
            float(row[1])
            for row in rows
        )

        average = (
            total / len(rows)
        )

    else:

        total = 0
        average = 0


    total_value.configure(
        text=f"₹{total:,.2f}"
    )

    transaction_value.configure(
        text=str(len(rows))
    )

    average_value.configure(
        text=f"₹{average:,.2f}"
    )


# ============================================================
# SHOW ALL
# ============================================================

def show_all():

    search_entry.delete(
        0,
        "end"
    )

    show_expenses()


# ============================================================
# EXPORT CSV
# ============================================================

def export_csv():

    cursor.execute(
        """
        SELECT *
        FROM expenses
        ORDER BY id DESC
        """
    )

    rows = cursor.fetchall()


    if not rows:

        messagebox.showinfo(
            "No Data",
            "There are no expenses to export."
        )

        return


    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",

        filetypes=[
            ("CSV Files", "*.csv"),
            ("All Files", "*.*")
        ],

        title="Save Expense Report"
    )


    if not file_path:
        return


    with open(
        file_path,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)


        writer.writerow(
            [
                "ID",
                "Amount",
                "Category",
                "Description",
                "Date"
            ]
        )


        # Export with sequential IDs

        for display_id, row in enumerate(
            rows,
            start=1
        ):

            writer.writerow(
                [
                    display_id,
                    row[1],
                    row[2],
                    row[3],
                    row[4]
                ]
            )


    messagebox.showinfo(
        "Export Complete",
        "Expense report exported successfully!"
    )


# ============================================================
# REPORT / PIE CHART
# ============================================================

def show_chart():

    cursor.execute(
        """
        SELECT
            category,
            SUM(amount)

        FROM expenses

        GROUP BY category
        """
    )


    data = cursor.fetchall()


    if not data:

        messagebox.showinfo(
            "No Data",
            "Add some expenses before viewing the report."
        )

        return


    categories = [
        row[0]
        for row in data
    ]


    amounts = [
        row[1]
        for row in data
    ]


    # Calculate total

    total = sum(amounts)


    # Create chart

    plt.figure(
        figsize=(9, 6)
    )


    plt.pie(
        amounts,
        labels=categories,
        autopct="%1.1f%%",
        startangle=90
    )


    plt.title(
        f"Expense Distribution\nTotal: ₹{total:,.2f}",
        fontsize=16,
        fontweight="bold"
    )


    plt.tight_layout()

    plt.show()


# ============================================================
# BUTTONS
# ============================================================

save_button = ctk.CTkButton(
    button_frame,
    text="💾  Save Expense",
    width=150,
    height=40,
    fg_color=GREEN,
    hover_color="#15803D",
    command=add_expense
)

save_button.pack(
    side="left",
    padx=5
)


edit_button = ctk.CTkButton(
    button_frame,
    text="✏️  Edit",
    width=120,
    height=40,
    fg_color=ORANGE,
    hover_color="#D97706",
    command=edit_expense
)

edit_button.pack(
    side="left",
    padx=5
)


delete_button = ctk.CTkButton(
    button_frame,
    text="🗑️  Delete",
    width=120,
    height=40,
    fg_color=RED,
    hover_color="#B91C1C",
    command=delete_expense
)

delete_button.pack(
    side="left",
    padx=5
)


clear_button = ctk.CTkButton(
    button_frame,
    text="Clear",
    width=100,
    height=40,
    fg_color="#64748B",
    hover_color="#475569",
    command=clear_fields
)

clear_button.pack(
    side="left",
    padx=5
)


# ============================================================
# SEARCH SECTION
# ============================================================

search_frame = ctk.CTkFrame(
    content,
    fg_color="transparent"
)

search_frame.pack(
    fill="x",
    pady=(0, 10)
)


ctk.CTkLabel(
    search_frame,
    text="🔍 Search by Category",
    font=("Arial", 15, "bold"),
    text_color=TEXT
).pack(
    side="left",
    padx=(0, 10)
)


search_entry = ctk.CTkEntry(
    search_frame,
    width=220,
    height=38,
    placeholder_text="Food, Travel, Bills..."
)

search_entry.pack(
    side="left"
)


search_button = ctk.CTkButton(
    search_frame,
    text="Search",
    width=100,
    height=38,
    command=search_expense
)

search_button.pack(
    side="left",
    padx=8
)


show_all_button = ctk.CTkButton(
    search_frame,
    text="Show All",
    width=100,
    height=38,
    fg_color="#64748B",
    hover_color="#475569",
    command=show_all
)

show_all_button.pack(
    side="left"
)


chart_button = ctk.CTkButton(
    search_frame,
    text="📊 View Chart",
    width=120,
    height=38,
    fg_color=PURPLE,
    hover_color="#6D28D9",
    command=show_chart
)

chart_button.pack(
    side="right",
    padx=5
)


export_button = ctk.CTkButton(
    search_frame,
    text="📄 Export CSV",
    width=120,
    height=38,
    fg_color=BLUE,
    hover_color="#1D4ED8",
    command=export_csv
)

export_button.pack(
    side="right",
    padx=5
)


# ============================================================
# EXPENSE TABLE
# ============================================================

table_frame = ctk.CTkFrame(
    content,
    fg_color=CARD,
    corner_radius=15
)

table_frame.pack(
    fill="both",
    expand=True
)


ctk.CTkLabel(
    table_frame,
    text="Recent Expenses",
    font=("Arial", 18, "bold"),
    text_color=TEXT
).pack(
    anchor="w",
    padx=20,
    pady=(15, 10)
)


# ============================================================
# TREEVIEW STYLE
# ============================================================

style = ttk.Style()


try:
    style.theme_use("clam")

except:
    pass


style.configure(
    "Treeview",
    background="white",
    foreground=TEXT,
    rowheight=38,
    fieldbackground="white",
    font=("Arial", 11)
)


style.configure(
    "Treeview.Heading",
    background="#E2E8F0",
    foreground=TEXT,
    font=("Arial", 11, "bold"),
    padding=8
)


style.map(
    "Treeview",
    background=[
        ("selected", "#DBEAFE")
    ],
    foreground=[
        ("selected", TEXT)
    ]
)


# ============================================================
# TREEVIEW
# ============================================================

tree = ttk.Treeview(
    table_frame,

    columns=(
        "ID",
        "Amount",
        "Category",
        "Description",
        "Date"
    ),

    show="headings"
)


tree.heading(
    "ID",
    text="ID"
)

tree.heading(
    "Amount",
    text="Amount"
)

tree.heading(
    "Category",
    text="Category"
)

tree.heading(
    "Description",
    text="Description"
)

tree.heading(
    "Date",
    text="Date"
)


tree.column(
    "ID",
    width=60,
    anchor="center"
)

tree.column(
    "Amount",
    width=140,
    anchor="center"
)

tree.column(
    "Category",
    width=160,
    anchor="center"
)

tree.column(
    "Description",
    width=350,
    anchor="w"
)

tree.column(
    "Date",
    width=150,
    anchor="center"
)


tree.pack(
    fill="both",
    expand=True,
    padx=20,
    pady=(0, 15)
)


# ============================================================
# SEARCH WITH ENTER KEY
# ============================================================

search_entry.bind(
    "<Return>",
    lambda event: search_expense()
)


# ============================================================
# LOAD EXISTING EXPENSES
# ============================================================

show_expenses()


# ============================================================
# CLOSE APPLICATION SAFELY
# ============================================================

def close_app():

    try:
        conn.commit()
        conn.close()

    except:
        pass

    app.destroy()


app.protocol(
    "WM_DELETE_WINDOW",
    close_app
)


# ============================================================
# START APPLICATION
# ============================================================

app.mainloop()