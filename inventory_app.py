import os
import sys
import tkinter as tk
from tkinter import messagebox, filedialog
import sqlite3
import csv


class InventoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Inventory App")
        self.root.configure(bg="#f0f0f0")

        # Koneksi ke SQLite
        # Koneksi ke SQLite (default, simpan di direktori kerja)
        self.conn = sqlite3.connect("inventory.db")

        self.cursor = self.conn.cursor()
        self.create_table()

        # Frame utama
        frame = tk.Frame(root, bg="#f0f0f0", padx=20, pady=20)
        frame.pack(expand=True)

        # Label & Entry
        tk.Label(frame, text="Item:", bg="#f0f0f0",fg="black", font=("Segoe UI", 10)).grid(row=0, column=0, sticky="w")
        self.entry_item = tk.Entry(frame, bg="#CCCCCC", fg="black", width=30)
        self.entry_item.grid(row=0, column=1, pady=5)

        tk.Label(frame, text="Quantity:", bg="#f0f0f0", fg="black", font=("Segoe UI", 10)).grid(row=1, column=0, sticky="w")
        self.entry_quantity = tk.Entry(frame, bg="#CCCCCC", fg="black", width=30)
        self.entry_quantity.grid(row=1, column=1, pady=5)

        # Tombol utama
        button_frame = tk.Frame(frame, bg="#f0f0f0")
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)

        tk.Button(button_frame, bg="#4da6ff", fg="white",text="Add Item", width=12, command=self.add_item).grid(row=0, column=0, padx=5)
        tk.Button(button_frame, bg="#4da6ff", fg="white",text="Remove Item", width=12, command=self.remove_item).grid(row=0, column=1, padx=5)
        tk.Button(button_frame, bg="#4da6ff", fg="white",text="View Inventory", width=12, command=self.view_inventory).grid(row=0, column=2, padx=5)

        # Tombol tambahan
        extra_button_frame = tk.Frame(frame, bg="#f0f0f0")
        extra_button_frame.grid(row=3, column=0, columnspan=2, pady=5)

        tk.Button(extra_button_frame, bg="#4da6ff", fg="white",text="Search Item", width=12, command=self.search_item).grid(row=0, column=0, padx=5)
        tk.Button(extra_button_frame, bg="#4da6ff", fg="white",text="Export to CSV", width=12, command=self.export_to_csv).grid(row=0, column=1, padx=5)

        # Textbox untuk inventory
        self.text_inventory = tk.Text(
            frame,
            height=12,
            width=50,
            font=("Consolas", 10),
            bg="white",
            fg="black",
            insertbackground="black"  # warna kursor teks
        )
        self.text_inventory.grid(row=4, column=0, columnspan=2, pady=10)

    def create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                item TEXT PRIMARY KEY,
                quantity INTEGER
            )
        """)
        self.conn.commit()

    def add_item(self):
        item = self.entry_item.get().strip()
        quantity = self.entry_quantity.get()

        if item and quantity.isdigit():
            quantity = int(quantity)

            self.cursor.execute("SELECT quantity FROM inventory WHERE item = ?", (item,))
            result = self.cursor.fetchone()

            if result:
                self.cursor.execute("UPDATE inventory SET quantity = ? WHERE item = ?", (result[0] + quantity, item))
            else:
                self.cursor.execute("INSERT INTO inventory (item, quantity) VALUES (?, ?)", (item, quantity))
            self.conn.commit()

            messagebox.showinfo("Berhasil", f"Menambahkan {quantity} {item}")
            self.clear_entries()
        else:
            messagebox.showerror("Gagal", "Masukkan jumlah dan item yang valid!")

    def remove_item(self):
        item = self.entry_item.get().strip()
        quantity = self.entry_quantity.get()

        if quantity.isdigit():
            quantity = int(quantity)
            self.cursor.execute("SELECT quantity FROM inventory WHERE item = ?", (item,))
            result = self.cursor.fetchone()

            if result and result[0] >= quantity:
                new_quantity = result[0] - quantity
                if new_quantity > 0:
                    self.cursor.execute("UPDATE inventory SET quantity = ? WHERE item = ?", (new_quantity, item))
                else:
                    self.cursor.execute("DELETE FROM inventory WHERE item = ?", (item,))
                self.conn.commit()

                messagebox.showinfo("Berhasil", f"Menghapus {quantity} {item}")
                self.clear_entries()
            else:
                messagebox.showerror("Gagal", "Jumlah tidak sesuai atau item tidak ditemukan.")
        else:
            messagebox.showerror("Gagal", "Masukkan item dan jumlah yang sesuai!")

    def view_inventory(self):
        self.text_inventory.delete(1.0, tk.END)
        self.cursor.execute("SELECT item, quantity FROM inventory")
        rows = self.cursor.fetchall()
        if rows:
            for item, quantity in rows:
                self.text_inventory.insert(tk.END, f"{item:<20} {quantity}\n")
        else:
            self.text_inventory.insert(tk.END, "No inventory data.\n")

    def search_item(self):
        search = self.entry_item.get().strip()
        self.text_inventory.delete(1.0, tk.END)

        if search:
            self.cursor.execute("SELECT item, quantity FROM inventory WHERE item LIKE ?", (f"%{search}%",))
            rows = self.cursor.fetchall()

            if rows:
                for item, quantity in rows:
                    self.text_inventory.insert(tk.END, f"{item:<20} {quantity}\n")
            else:
                self.text_inventory.insert(tk.END, "Item tidak ditemukan!.\n")
        else:
            messagebox.showerror("Gagal", "Masukkan item yang valid!")

    def export_to_csv(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                 filetypes=[("CSV files", "*.csv")],
                                                 title="Save Inventory As")
        if file_path:
            self.cursor.execute("SELECT item, quantity FROM inventory")
            rows = self.cursor.fetchall()

            try:
                with open(file_path, mode="w", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(["Item", "Quantity"])
                    writer.writerows(rows)
                messagebox.showinfo("Success", f"Inventory exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {e}")

    def clear_entries(self):
        self.entry_item.delete(0, tk.END)
        self.entry_quantity.delete(0, tk.END)

    def __del__(self):
        self.conn.close()


if __name__ == "__main__":
    root = tk.Tk()
    app = InventoryApp(root)
    root.mainloop()
