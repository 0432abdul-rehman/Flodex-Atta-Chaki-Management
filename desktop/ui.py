import tkinter as tk
from datetime import date
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

try:
    from .database import FlodexDatabase
    from .reports import export_transactions_excel, save_receipt
    from .voice_handler import VoiceCommandParser
except ImportError:  # direct script execution support
    from database import FlodexDatabase
    from reports import export_transactions_excel, save_receipt
    from voice_handler import VoiceCommandParser


class FlodexApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Flodex - Atta Chaki Management")
        self.geometry("1050x700")
        self.db = FlodexDatabase()
        self.parser = VoiceCommandParser()
        self.selected_customer_id = None
        self.bg_color = "#f5f5f5"

        self.configure(bg=self.bg_color)
        self._build_ui()
        self.refresh_customers()
        self.refresh_analytics()

    def _build_ui(self) -> None:
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.customer_tab = ttk.Frame(notebook)
        self.transaction_tab = ttk.Frame(notebook)
        self.analytics_tab = ttk.Frame(notebook)
        self.voice_tab = ttk.Frame(notebook)
        self.settings_tab = ttk.Frame(notebook)

        notebook.add(self.customer_tab, text="Customers")
        notebook.add(self.transaction_tab, text="Transactions")
        notebook.add(self.analytics_tab, text="Reports")
        notebook.add(self.voice_tab, text="Flodex Voice")
        notebook.add(self.settings_tab, text="Customization")

        self._build_customer_tab()
        self._build_transaction_tab()
        self._build_analytics_tab()
        self._build_voice_tab()
        self._build_settings_tab()

    def _build_customer_tab(self) -> None:
        form = ttk.LabelFrame(self.customer_tab, text="Customer Profile")
        form.pack(fill="x", padx=10, pady=10)

        self.name_var = tk.StringVar()
        self.phone_var = tk.StringVar()
        self.address_var = tk.StringVar()
        self.photo_var = tk.StringVar()

        self._labeled_entry(form, "Name", self.name_var, 0)
        self._labeled_entry(form, "Phone", self.phone_var, 1)
        self._labeled_entry(form, "Address", self.address_var, 2)
        self._labeled_entry(form, "Photo Path", self.photo_var, 3)

        ttk.Button(form, text="Browse Photo", command=self.pick_photo).grid(row=3, column=2, padx=5, pady=5)
        ttk.Button(form, text="Save / Reuse Customer", command=self.save_customer).grid(row=4, column=0, padx=5, pady=10)

        self.customers_tree = ttk.Treeview(
            self.customer_tab,
            columns=("id", "name", "phone", "address"),
            show="headings",
            height=12,
        )
        for col in ("id", "name", "phone", "address"):
            self.customers_tree.heading(col, text=col.capitalize())
            self.customers_tree.column(col, width=200 if col != "id" else 80)
        self.customers_tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.customers_tree.bind("<<TreeviewSelect>>", self.on_customer_select)

    def _build_transaction_tab(self) -> None:
        form = ttk.LabelFrame(self.transaction_tab, text="Manual Transaction Entry")
        form.pack(fill="x", padx=10, pady=10)

        self.wheat_var = tk.StringVar()
        self.flour_var = tk.StringVar()
        self.amount_var = tk.StringVar()
        self.status_var = tk.StringVar(value="PAID")
        self.notes_var = tk.StringVar()

        self._labeled_entry(form, "Wheat Weight (KG)", self.wheat_var, 0)
        self._labeled_entry(form, "Flour Weight (KG)", self.flour_var, 1)
        self._labeled_entry(form, "Amount", self.amount_var, 2)
        self._labeled_entry(form, "Notes", self.notes_var, 3)

        ttk.Label(form, text="Payment Status").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        ttk.Combobox(form, textvariable=self.status_var, values=["PAID", "UNPAID"], state="readonly").grid(
            row=4, column=1, sticky="ew", padx=5, pady=5
        )

        ttk.Button(form, text="Add Transaction", command=self.add_transaction).grid(row=5, column=0, padx=5, pady=10)

        self.txn_tree = ttk.Treeview(
            self.transaction_tab,
            columns=("date", "wheat", "flour", "amount", "status", "notes"),
            show="headings",
            height=14,
        )
        for col in ("date", "wheat", "flour", "amount", "status", "notes"):
            self.txn_tree.heading(col, text=col.capitalize())
            self.txn_tree.column(col, width=150)
        self.txn_tree.pack(fill="both", expand=True, padx=10, pady=10)

        btn_frame = ttk.Frame(self.transaction_tab)
        btn_frame.pack(fill="x", padx=10, pady=4)
        ttk.Button(btn_frame, text="Export This Month (Excel)", command=self.export_monthly).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Generate Selected Receipt", command=self.generate_receipt).pack(side="left", padx=5)

    def _build_analytics_tab(self) -> None:
        self.analytics_text = tk.Text(self.analytics_tab, height=22)
        self.analytics_text.pack(fill="both", expand=True, padx=10, pady=10)
        ttk.Button(self.analytics_tab, text="Refresh Reports", command=self.refresh_analytics).pack(pady=5)

    def _build_voice_tab(self) -> None:
        ttk.Label(self.voice_tab, text="Type voice command (Urdu/Punjabi/English)").pack(anchor="w", padx=10, pady=5)
        self.voice_text = tk.Text(self.voice_tab, height=4)
        self.voice_text.pack(fill="x", padx=10)
        ttk.Button(self.voice_tab, text="Run Flodex Command", command=self.run_voice_command).pack(padx=10, pady=8, anchor="w")

        self.voice_output = tk.Text(self.voice_tab, height=20)
        self.voice_output.pack(fill="both", expand=True, padx=10, pady=10)

    def _build_settings_tab(self) -> None:
        ttk.Label(self.settings_tab, text="Background Color Hex (e.g. #f5f5f5)").pack(anchor="w", padx=10, pady=6)
        self.color_var = tk.StringVar(value=self.bg_color)
        ttk.Entry(self.settings_tab, textvariable=self.color_var).pack(fill="x", padx=10)
        ttk.Button(self.settings_tab, text="Apply Color", command=self.apply_theme).pack(anchor="w", padx=10, pady=8)

    def _labeled_entry(self, parent: ttk.LabelFrame, text: str, variable: tk.StringVar, row: int) -> None:
        ttk.Label(parent, text=text).grid(row=row, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(parent, textvariable=variable).grid(row=row, column=1, sticky="ew", padx=5, pady=5)
        parent.columnconfigure(1, weight=1)

    def pick_photo(self) -> None:
        path = filedialog.askopenfilename(title="Select customer photo")
        if path:
            self.photo_var.set(path)

    def save_customer(self) -> None:
        if not self.name_var.get().strip() or not self.phone_var.get().strip():
            messagebox.showerror("Required", "Name and phone are required")
            return
        customer = self.db.add_or_get_customer(
            self.name_var.get(), self.phone_var.get(), self.address_var.get(), self.photo_var.get() or None
        )
        self.selected_customer_id = customer.id
        self.refresh_customers()
        self.load_customer_transactions(customer.id)
        messagebox.showinfo("Saved", f"Customer ready: {customer.name}")

    def refresh_customers(self) -> None:
        for row in self.customers_tree.get_children():
            self.customers_tree.delete(row)
        for c in self.db.list_customers():
            self.customers_tree.insert("", "end", values=(c.id, c.name, c.phone, c.address))

    def on_customer_select(self, _event=None) -> None:
        selected = self.customers_tree.selection()
        if not selected:
            return
        vals = self.customers_tree.item(selected[0], "values")
        customer_id = int(vals[0])
        self.selected_customer_id = customer_id
        self.name_var.set(vals[1])
        self.phone_var.set(vals[2])
        self.address_var.set(vals[3])
        self.load_customer_transactions(customer_id)

    def load_customer_transactions(self, customer_id: int) -> None:
        for row in self.txn_tree.get_children():
            self.txn_tree.delete(row)
        for txn in self.db.list_customer_transactions(customer_id):
            self.txn_tree.insert(
                "",
                "end",
                values=(txn.txn_date, txn.wheat_weight, txn.flour_weight, txn.amount, txn.payment_status, txn.notes),
            )

    def add_transaction(self) -> None:
        if not self.selected_customer_id:
            messagebox.showerror("Select customer", "Please select a customer first")
            return
        try:
            txn = self.db.add_transaction(
                self.selected_customer_id,
                float(self.wheat_var.get()),
                float(self.flour_var.get()),
                float(self.amount_var.get()),
                self.status_var.get(),
                notes=self.notes_var.get(),
            )
        except ValueError:
            messagebox.showerror("Invalid", "Please provide numeric weights and amount")
            return

        self.load_customer_transactions(self.selected_customer_id)
        self.refresh_analytics()
        messagebox.showinfo("Recorded", f"Transaction #{txn.id} saved")

    def refresh_analytics(self) -> None:
        today = date.today().isoformat()
        daily = self.db.daily_summary(today)
        weekly = self.db.weekly_summary()
        monthly = self.db.monthly_summary(date.today().year, date.today().month)
        loans = self.db.loan_report()

        lines = [
            daily["label"],
            f"Wheat: {daily['total_wheat']:.2f} KG | Flour: {daily['total_flour']:.2f} KG | Amount: {daily['total_amount']:.2f}",
            "",
            weekly["label"],
            f"Wheat: {weekly['total_wheat']:.2f} KG | Flour: {weekly['total_flour']:.2f} KG | Amount: {weekly['total_amount']:.2f}",
            "",
            monthly["label"],
            f"Wheat: {monthly['total_wheat']:.2f} KG | Flour: {monthly['total_flour']:.2f} KG | Amount: {monthly['total_amount']:.2f}",
            "",
            "Loan / Unpaid Customers:",
        ]

        if loans:
            lines.extend([f"- {row['name']} ({row['phone']}): {row['unpaid_total']:.2f}" for row in loans])
        else:
            lines.append("- No unpaid balances")

        self.analytics_text.delete("1.0", "end")
        self.analytics_text.insert("1.0", "\n".join(lines))

    def run_voice_command(self) -> None:
        command = self.voice_text.get("1.0", "end").strip()
        if not command:
            return

        intent = self.parser.parse(command)
        if intent.action == "find_customer" and intent.customer_query:
            customer = self.db.find_customer(intent.customer_query)
            if customer:
                self.voice_output.insert("end", f"✔ {customer.name} found.\n")
                self.selected_customer_id = customer.id
                self.load_customer_transactions(customer.id)
            else:
                self.voice_output.insert("end", f"✘ {intent.customer_query} not found.\n")
        elif intent.action == "add_transaction":
            if intent.weight:
                self.wheat_var.set(str(intent.weight))
                self.voice_output.insert("end", f"Weight captured: {intent.weight} KG. Complete remaining fields manually.\n")
            if intent.customer_query:
                customer = self.db.find_customer(intent.customer_query)
                if customer:
                    self.selected_customer_id = customer.id
                    self.load_customer_transactions(customer.id)
                    self.voice_output.insert("end", f"Customer loaded: {customer.name}.\n")
        elif intent.action == "summary":
            if intent.period == "daily":
                summary = self.db.daily_summary()
            elif intent.period == "weekly":
                summary = self.db.weekly_summary()
            else:
                summary = self.db.monthly_summary(date.today().year, date.today().month)
            self.voice_output.insert(
                "end",
                f"{summary['label']}: Wheat {summary['total_wheat']:.2f}, Flour {summary['total_flour']:.2f}, Amount {summary['total_amount']:.2f}\n",
            )
        else:
            self.voice_output.insert("end", "Command not understood. Try manual entry.\n")

    def export_monthly(self) -> None:
        today = date.today()
        start = today.replace(day=1).isoformat()
        end = today.isoformat()
        rows = self.db.list_transactions_by_range(start, end)
        output = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx")])
        if not output:
            return
        path = export_transactions_excel(rows, output)
        messagebox.showinfo("Exported", f"Report saved at {path}")

    def generate_receipt(self) -> None:
        selected = self.txn_tree.selection()
        if not selected or not self.selected_customer_id:
            messagebox.showerror("Select transaction", "Select a transaction first")
            return

        row_values = self.txn_tree.item(selected[0], "values")
        txns = self.db.list_customer_transactions(self.selected_customer_id)
        txn = next((t for t in txns if str(t.txn_date) == str(row_values[0]) and str(t.amount) == str(row_values[3])), None)
        customer_name = self.name_var.get() or "Customer"
        if not txn:
            messagebox.showerror("Not found", "Could not find matching transaction")
            return

        receipt_path = save_receipt(customer_name, txn.__dict__)
        messagebox.showinfo("Receipt", f"Receipt generated: {Path(receipt_path).resolve()}")

    def apply_theme(self) -> None:
        new_color = self.color_var.get().strip()
        if not new_color.startswith("#"):
            messagebox.showerror("Invalid color", "Use hex color format, e.g. #f5f5f5")
            return
        self.bg_color = new_color
        self.configure(bg=new_color)


if __name__ == "__main__":
    app = FlodexApp()
    app.mainloop()
