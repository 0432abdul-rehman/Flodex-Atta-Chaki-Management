import tkinter as tk
from datetime import date
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import List

try:
    from .database import FlodexDatabase
    from .face_helper import FaceMatcher
    from .reports import export_transactions_excel, print_receipt_file, save_receipt, save_receipt_pdf
    from .voice_handler import VoiceCommandParser, VoiceEngine
except ImportError:  # direct script execution support
    from database import FlodexDatabase
    from face_helper import FaceMatcher
    from reports import export_transactions_excel, print_receipt_file, save_receipt, save_receipt_pdf
    from voice_handler import VoiceCommandParser, VoiceEngine


class FlodexApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Flodex - Atta Chaki Management")
        self.geometry("1150x760")
        self.db = FlodexDatabase()
        self.parser = VoiceCommandParser()
        self.voice_engine = VoiceEngine()
        self.face_matcher = FaceMatcher()

        self.selected_customer_id = None
        self.bg_color = "#f5f5f5"
        self.bg_image = None
        self.bg_image_label = None
        self.last_receipt_path = None

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

        face_frame = ttk.Frame(form)
        face_frame.grid(row=4, column=1, columnspan=2, sticky="w")
        ttk.Button(face_frame, text="Match Customer by Face Photo", command=self.match_customer_by_face).pack(side="left", padx=6)
        ttk.Label(
            face_frame,
            text="(Optional: requires OpenCV; matches by detected face + photo naming)",
        ).pack(side="left")

        self.customers_tree = ttk.Treeview(
            self.customer_tab,
            columns=("id", "name", "phone", "address", "photo"),
            show="headings",
            height=12,
        )
        for col in ("id", "name", "phone", "address", "photo"):
            self.customers_tree.heading(col, text=col.capitalize())
            self.customers_tree.column(col, width=180 if col != "id" else 70)
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
        ttk.Button(form, text="Mark Selected Paid", command=self.mark_selected_paid).grid(row=5, column=1, padx=5, pady=10)

        self.txn_tree = ttk.Treeview(
            self.transaction_tab,
            columns=("id", "date", "wheat", "flour", "amount", "status", "notes"),
            show="headings",
            height=14,
        )
        for col, width in (("id", 70), ("date", 120), ("wheat", 110), ("flour", 110), ("amount", 110), ("status", 90), ("notes", 350)):
            self.txn_tree.heading(col, text=col.capitalize())
            self.txn_tree.column(col, width=width)
        self.txn_tree.pack(fill="both", expand=True, padx=10, pady=10)

        btn_frame = ttk.Frame(self.transaction_tab)
        btn_frame.pack(fill="x", padx=10, pady=4)
        ttk.Button(btn_frame, text="Export This Month (Excel)", command=self.export_monthly).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Generate TXT Receipt", command=self.generate_receipt).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Generate PDF Receipt", command=self.generate_pdf_receipt).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Print Last Receipt", command=self.print_last_receipt).pack(side="left", padx=5)

    def _build_analytics_tab(self) -> None:
        top = ttk.Frame(self.analytics_tab)
        top.pack(fill="x", padx=10, pady=6)
        ttk.Label(top, text="Custom query").pack(side="left")
        self.query_var = tk.StringVar()
        ttk.Entry(top, textvariable=self.query_var).pack(side="left", fill="x", expand=True, padx=8)
        ttk.Button(top, text="Run Query", command=self.run_custom_query).pack(side="left")

        self.analytics_text = tk.Text(self.analytics_tab, height=17)
        self.analytics_text.pack(fill="both", expand=True, padx=10, pady=8)

        ttk.Label(self.analytics_tab, text="Due Payment Reminders").pack(anchor="w", padx=10)
        self.reminders_box = tk.Listbox(self.analytics_tab, height=6)
        self.reminders_box.pack(fill="x", padx=10, pady=6)
        ttk.Button(self.analytics_tab, text="Refresh Reports", command=self.refresh_analytics).pack(pady=5)

    def _build_voice_tab(self) -> None:
        ttk.Label(self.voice_tab, text="Type voice command (Urdu/Punjabi/English)").pack(anchor="w", padx=10, pady=5)
        self.voice_text = tk.Text(self.voice_tab, height=4)
        self.voice_text.pack(fill="x", padx=10)

        actions = ttk.Frame(self.voice_tab)
        actions.pack(fill="x", padx=10, pady=8)
        ttk.Button(actions, text="Run Flodex Command", command=self.run_voice_command).pack(side="left", padx=4)
        ttk.Button(actions, text="Listen from Microphone", command=self.listen_from_microphone).pack(side="left", padx=4)
        self.speak_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(actions, text="Speak responses", variable=self.speak_var).pack(side="left", padx=10)

        support_text = "Microphone ready" if self.voice_engine.supported else "Microphone module unavailable (install SpeechRecognition + PyAudio)"
        ttk.Label(self.voice_tab, text=support_text).pack(anchor="w", padx=10)

        self.voice_output = tk.Text(self.voice_tab, height=20)
        self.voice_output.pack(fill="both", expand=True, padx=10, pady=10)

    def _build_settings_tab(self) -> None:
        ttk.Label(self.settings_tab, text="Background Color Hex (e.g. #f5f5f5)").pack(anchor="w", padx=10, pady=6)
        self.color_var = tk.StringVar(value=self.bg_color)
        ttk.Entry(self.settings_tab, textvariable=self.color_var).pack(fill="x", padx=10)
        ttk.Button(self.settings_tab, text="Apply Color", command=self.apply_theme).pack(anchor="w", padx=10, pady=8)

        ttk.Label(self.settings_tab, text="Background Image (optional .png/.gif)").pack(anchor="w", padx=10)
        self.bg_path_var = tk.StringVar()
        ttk.Entry(self.settings_tab, textvariable=self.bg_path_var).pack(fill="x", padx=10, pady=4)
        ttk.Button(self.settings_tab, text="Browse Image", command=self.pick_background_image).pack(anchor="w", padx=10)
        ttk.Button(self.settings_tab, text="Apply Image", command=self.apply_background_image).pack(anchor="w", padx=10, pady=4)

    def _labeled_entry(self, parent: ttk.LabelFrame, text: str, variable: tk.StringVar, row: int) -> None:
        ttk.Label(parent, text=text).grid(row=row, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(parent, textvariable=variable).grid(row=row, column=1, sticky="ew", padx=5, pady=5)
        parent.columnconfigure(1, weight=1)

    def pick_photo(self) -> None:
        path = filedialog.askopenfilename(title="Select customer photo")
        if path:
            self.photo_var.set(path)

    def pick_background_image(self) -> None:
        path = filedialog.askopenfilename(title="Select background image", filetypes=[("Images", "*.png *.gif")])
        if path:
            self.bg_path_var.set(path)

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
            self.customers_tree.insert("", "end", values=(c.id, c.name, c.phone, c.address, c.photo_path or ""))

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
        self.photo_var.set(vals[4])
        self.load_customer_transactions(customer_id)

    def load_customer_transactions(self, customer_id: int) -> None:
        for row in self.txn_tree.get_children():
            self.txn_tree.delete(row)
        for txn in self.db.list_customer_transactions(customer_id):
            self.txn_tree.insert(
                "",
                "end",
                values=(txn.id, txn.txn_date, txn.wheat_weight, txn.flour_weight, txn.amount, txn.payment_status, txn.notes),
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

    def mark_selected_paid(self) -> None:
        selected = self.txn_tree.selection()
        if not selected:
            messagebox.showerror("Select", "Select transaction first")
            return
        txn_id = int(self.txn_tree.item(selected[0], "values")[0])
        self.db.mark_transaction_paid(txn_id)
        if self.selected_customer_id:
            self.load_customer_transactions(self.selected_customer_id)
        self.refresh_analytics()

    def refresh_analytics(self) -> None:
        today = date.today().isoformat()
        daily = self.db.daily_summary(today)
        weekly = self.db.weekly_summary()
        monthly = self.db.monthly_summary(date.today().year, date.today().month)
        overall = self.db.all_time_summary()
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
            overall["label"],
            f"Wheat: {overall['total_wheat']:.2f} KG | Flour: {overall['total_flour']:.2f} KG | Amount: {overall['total_amount']:.2f}",
            "",
            "Loan / Unpaid Customers:",
        ]

        if loans:
            lines.extend([f"- {row['name']} ({row['phone']}): {row['unpaid_total']:.2f}" for row in loans])
        else:
            lines.append("- No unpaid balances")

        self.analytics_text.delete("1.0", "end")
        self.analytics_text.insert("1.0", "\n".join(lines))

        self.reminders_box.delete(0, "end")
        reminders = self.db.due_reminders(days_due=7)
        if reminders:
            for _, text in reminders:
                self.reminders_box.insert("end", text)
        else:
            self.reminders_box.insert("end", "No due reminders")

    def run_custom_query(self) -> None:
        query = self.query_var.get().strip()
        if not query:
            return

        result_lines = self.resolve_natural_query(query)
        self.analytics_text.insert("end", "\n\n[Custom Query]\n" + "\n".join(result_lines) + "\n")

    def resolve_natural_query(self, query: str) -> List[str]:
        q = query.lower()

        if any(w in q for w in ["today", "aaj"]):
            s = self.db.daily_summary()
            return [f"Today wheat {s['total_wheat']:.2f} KG, flour {s['total_flour']:.2f} KG, amount {s['total_amount']:.2f}"]

        if any(w in q for w in ["week", "hafta"]):
            s = self.db.weekly_summary()
            return [f"Week wheat {s['total_wheat']:.2f} KG, flour {s['total_flour']:.2f} KG, amount {s['total_amount']:.2f}"]

        if any(w in q for w in ["month", "mahina"]):
            s = self.db.monthly_summary(date.today().year, date.today().month)
            return [f"Month wheat {s['total_wheat']:.2f} KG, flour {s['total_flour']:.2f} KG, amount {s['total_amount']:.2f}"]

        if any(w in q for w in ["unpaid", "loan", "qarz", "udhaar"]):
            rows = self.db.loan_report()
            return [f"{r['name']}: {r['unpaid_total']:.2f}" for r in rows] or ["No unpaid balances"]

        customer = self.db.find_customer(query)
        if customer:
            txns = self.db.list_customer_transactions(customer.id)
            total_unpaid = sum(t.amount for t in txns if t.payment_status == "UNPAID")
            return [
                f"Customer: {customer.name} ({customer.phone})",
                f"Total visits: {len(txns)}",
                f"Total unpaid: {total_unpaid:.2f}",
            ]

        overall = self.db.all_time_summary()
        return [
            "General result:",
            f"Total wheat: {overall['total_wheat']:.2f} KG",
            f"Total amount: {overall['total_amount']:.2f}",
        ]

    def listen_from_microphone(self) -> None:
        text = self.voice_engine.listen_once()
        if not text:
            messagebox.showwarning("Voice", "Could not capture voice command")
            return
        self.voice_text.delete("1.0", "end")
        self.voice_text.insert("1.0", text)
        self.run_voice_command()

    def run_voice_command(self) -> None:
        command = self.voice_text.get("1.0", "end").strip()
        if not command:
            return

        intent = self.parser.parse(command)
        response = ""

        if intent.action == "wake_word_required":
            response = "Please say: Flodex ..."
        elif intent.action == "find_customer" and intent.customer_query:
            customer = self.db.find_customer(intent.customer_query)
            if customer:
                response = f"✔ {customer.name} found."
                self.selected_customer_id = customer.id
                self.load_customer_transactions(customer.id)
            else:
                response = f"✘ {intent.customer_query} not found."
        elif intent.action == "customer_history" and intent.customer_query:
            customer = self.db.find_customer(intent.customer_query)
            if customer:
                txns = self.db.list_customer_transactions(customer.id)
                response = f"{customer.name} history: {len(txns)} transactions."
                self.selected_customer_id = customer.id
                self.load_customer_transactions(customer.id)
            else:
                response = f"No history found for {intent.customer_query}."
        elif intent.action == "add_transaction":
            if intent.weight:
                self.wheat_var.set(str(intent.weight))
                self.flour_var.set(str(round(intent.weight * 0.9, 2)))
                response = f"Weight captured: {intent.weight} KG."
            else:
                response = "Weight not detected."
            if intent.customer_query:
                customer = self.db.find_customer(intent.customer_query)
                if customer:
                    self.selected_customer_id = customer.id
                    self.load_customer_transactions(customer.id)
                    response += f" Customer loaded: {customer.name}."
        elif intent.action == "summary":
            if intent.period == "daily":
                summary = self.db.daily_summary()
            elif intent.period == "weekly":
                summary = self.db.weekly_summary()
            elif intent.period == "monthly":
                summary = self.db.monthly_summary(date.today().year, date.today().month)
            else:
                summary = self.db.all_time_summary()
            response = (
                f"{summary['label']}: Wheat {summary['total_wheat']:.2f} KG, "
                f"Flour {summary['total_flour']:.2f} KG, Amount {summary['total_amount']:.2f}"
            )
        elif intent.action == "unpaid_report":
            loans = self.db.loan_report()
            if not loans:
                response = "No unpaid balances."
            else:
                top = loans[0]
                response = f"Unpaid customers: {len(loans)}. Highest due {top['name']} = {top['unpaid_total']:.2f}"
        else:
            result = self.resolve_natural_query(intent.raw_query or command)
            response = " ".join(result)

        self.voice_output.insert("end", response + "\n")
        if self.speak_var.get():
            self.voice_engine.speak(response)

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

    def _selected_transaction(self):
        selected = self.txn_tree.selection()
        if not selected:
            return None
        txn_id = int(self.txn_tree.item(selected[0], "values")[0])
        return self.db.get_transaction(txn_id)

    def generate_receipt(self) -> None:
        txn = self._selected_transaction()
        if not txn:
            messagebox.showerror("Select transaction", "Select a transaction first")
            return
        customer_name = self.name_var.get() or "Customer"
        receipt_path = save_receipt(customer_name, txn.__dict__)
        self.last_receipt_path = receipt_path
        messagebox.showinfo("Receipt", f"Receipt generated: {Path(receipt_path).resolve()}")

    def generate_pdf_receipt(self) -> None:
        txn = self._selected_transaction()
        if not txn:
            messagebox.showerror("Select transaction", "Select a transaction first")
            return
        customer_name = self.name_var.get() or "Customer"
        receipt_path = save_receipt_pdf(customer_name, txn.__dict__)
        self.last_receipt_path = receipt_path
        messagebox.showinfo("Receipt", f"Receipt generated: {Path(receipt_path).resolve()}")

    def print_last_receipt(self) -> None:
        if not self.last_receipt_path:
            messagebox.showerror("No receipt", "Generate a receipt first")
            return
        ok, message = print_receipt_file(self.last_receipt_path)
        if ok:
            messagebox.showinfo("Print", message)
        else:
            messagebox.showerror("Print", message)

    def match_customer_by_face(self) -> None:
        image_path = filedialog.askopenfilename(title="Select camera photo", filetypes=[("Images", "*.png *.jpg *.jpeg")])
        if not image_path:
            return

        if not self.face_matcher.supported:
            messagebox.showwarning("Face", "OpenCV not installed. Install opencv-python for face detection.")
            return

        customers = self.db.list_customers()
        known_photos = [c.photo_path for c in customers if c.photo_path]
        matched_photo = self.face_matcher.guess_match(image_path, known_photos)
        if not matched_photo:
            messagebox.showinfo("Face", "No matching customer photo found.")
            return

        for customer in customers:
            if customer.photo_path == matched_photo:
                self.selected_customer_id = customer.id
                self.name_var.set(customer.name)
                self.phone_var.set(customer.phone)
                self.address_var.set(customer.address)
                self.photo_var.set(customer.photo_path or "")
                self.load_customer_transactions(customer.id)
                messagebox.showinfo("Face", f"Matched customer: {customer.name}")
                return

    def apply_theme(self) -> None:
        new_color = self.color_var.get().strip()
        if not new_color.startswith("#"):
            messagebox.showerror("Invalid color", "Use hex color format, e.g. #f5f5f5")
            return
        self.bg_color = new_color
        self.configure(bg=new_color)

    def apply_background_image(self) -> None:
        image_path = self.bg_path_var.get().strip()
        if not image_path:
            return
        try:
            self.bg_image = tk.PhotoImage(file=image_path)
        except Exception:
            messagebox.showerror("Invalid image", "Only Tk-compatible images (.png/.gif) are supported.")
            return

        if self.bg_image_label is None:
            self.bg_image_label = tk.Label(self, image=self.bg_image)
            self.bg_image_label.place(x=0, y=0, relwidth=1, relheight=1)
            self.bg_image_label.lower()
        else:
            self.bg_image_label.configure(image=self.bg_image)
        messagebox.showinfo("Background", "Background image applied")


if __name__ == "__main__":
    app = FlodexApp()
    app.mainloop()
