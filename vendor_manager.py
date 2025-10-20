<<<<<<< HEAD
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import csv
import os

CSV_FILE = "vendors.csv"

class VendorForm(tk.Toplevel):
    def __init__(self, master, record=None, callback=None):
        super().__init__(master)
        self.title("ベンダー情報入力")
        self.callback = callback
        self.record = record if record else {}

        labels = ["1次ベンダー", "2次ベンダー", "性", "名", "年齢", "携帯番号", "バッジID"]
        self.entries = {}

        for i, label_text in enumerate(labels):
            lbl = tk.Label(self, text=label_text)
            lbl.grid(row=i, column=0, padx=5, pady=5, sticky="e")
            ent = tk.Entry(self, width=30)
            ent.grid(row=i, column=1, padx=5, pady=5)
            self.entries[label_text] = ent

        if self.record:
            self.entries["1次ベンダー"].insert(0, self.record.get("first_vendor", ""))
            self.entries["2次ベンダー"].insert(0, self.record.get("second_vendor", ""))
            self.entries["性"].insert(0, self.record.get("last_name", ""))
            self.entries["名"].insert(0, self.record.get("first_name", ""))
            self.entries["年齢"].insert(0, self.record.get("age", ""))
            self.entries["携帯番号"].insert(0, self.record.get("phone", ""))
            self.entries["バッジID"].insert(0, self.record.get("badge_id", ""))

        btn_frame = tk.Frame(self)
        btn_frame.grid(row=len(labels), column=0, columnspan=2, pady=10)
        tk.Button(btn_frame, text="OK", command=self.on_ok).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="キャンセル", command=self.destroy).pack(side=tk.LEFT, padx=5)

    def on_ok(self):
        first_vendor = self.entries["1次ベンダー"].get().strip()
        second_vendor = self.entries["2次ベンダー"].get().strip()
        last_name = self.entries["性"].get().strip()
        first_name = self.entries["名"].get().strip()
        age = self.entries["年齢"].get().strip()
        phone = self.entries["携帯番号"].get().strip()
        badge_id = self.entries["バッジID"].get().strip()
        update_date = datetime.today().strftime("%Y-%m-%d")

        if not age.isdigit():
            messagebox.showerror("エラー", "年齢は数字で入力してください。")
            return

        record = {
            "first_vendor": first_vendor,
            "second_vendor": second_vendor,
            "last_name": last_name,
            "first_name": first_name,
            "age": age,
            "phone": phone,
            "badge_id": badge_id,
            "update_date": update_date,
        }

        if self.callback:
            self.callback(record)
        self.destroy()

class VendorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ベンダー管理アプリ")

        # ==== 上部：タイトルと検索 ====
        top_frame = tk.Frame(root, pady=10)
        top_frame.pack(fill=tk.X)

        tk.Label(top_frame, text="🔍 ベンダー検索：", font=("Arial", 11, "bold")).pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(top_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=5)
        search_entry.bind("<Return>", lambda e: self.search_records())
        tk.Button(top_frame, text="検索", command=self.search_records).pack(side=tk.LEFT, padx=5)
        tk.Button(top_frame, text="リセット", command=self.refresh_tree).pack(side=tk.LEFT, padx=5)

        # ==== 中央：ツリービュー ====
        columns = ("first_vendor", "second_vendor", "last_name", "first_name", "age", "phone", "badge_id", "update_date")
        self.columns = columns
        tree_frame = tk.Frame(root)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        headings = {
            "first_vendor": "1次ベンダー",
            "second_vendor": "2次ベンダー",
            "last_name": "性",
            "first_name": "名",
            "age": "年齢",
            "phone": "携帯番号",
            "badge_id": "バッジID",
            "update_date": "更新日",
        }
        for col, text in headings.items():
            self.tree.heading(col, text=text, command=lambda c=col: self.sort_column(c))
            self.tree.column(col, width=100, anchor="center")

        self.data = []
        self.sort_reverse = False
        self.sort_by = None

        # ==== 下部：ボタン ====
        btn_frame = tk.Frame(root, pady=10)
        btn_frame.pack(fill=tk.X)
        tk.Button(btn_frame, text="追加", width=10, command=self.add_record).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="編集", width=10, command=self.edit_record).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="削除", width=10, command=self.delete_record).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="保存", width=10, command=self.save_to_csv).pack(side=tk.LEFT, padx=5)

        self.load_from_csv()
        self.refresh_tree()

    # ==== 検索機能 ====
    def search_records(self):
        keyword = self.search_var.get().strip().lower()
        if not keyword:
            messagebox.showinfo("検索", "検索キーワードを入力してください。")
            return

        self.tree.selection_remove(*self.tree.selection())
        matches = []

        for i, record in enumerate(self.data):
            if any(keyword in str(v).lower() for v in record.values()):
                matches.append(i)

        if not matches:
            messagebox.showinfo("検索結果", "該当するレコードがありません。")
            return

        self.refresh_tree()
        for idx in matches:
            item_id = self.tree.get_children()[idx]
            self.tree.selection_add(item_id)
            self.tree.see(item_id)

    # ==== 並べ替え ====
    def sort_column(self, col):
        if self.sort_by == col:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_reverse = False
        self.sort_by = col

        if col == "age":
            self.data.sort(key=lambda x: int(x[col]), reverse=self.sort_reverse)
        elif col == "update_date":
            self.data.sort(key=lambda x: datetime.strptime(x[col], "%Y-%m-%d"), reverse=self.sort_reverse)
        else:
            self.data.sort(key=lambda x: x[col], reverse=self.sort_reverse)
        self.refresh_tree()

    # ==== 表示更新 ====
    def refresh_tree(self):
        self.tree.delete(*self.tree.get_children())
        for row in self.data:
            self.tree.insert("", tk.END, values=tuple(row[col] for col in self.columns))
        self.tree.selection_remove(*self.tree.selection())
        self.search_var.set("")

    # ==== CRUD 操作 ====
    def add_record(self):
        VendorForm(self.root, callback=self.add_callback)

    def add_callback(self, record):
        self.data.append(record)
        self.refresh_tree()

    def edit_record(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("警告", "編集するレコードを選択してください。")
            return
        idx = self.tree.index(selected[0])
        VendorForm(self.root, record=self.data[idx], callback=lambda r: self.edit_callback(idx, r))

    def edit_callback(self, idx, record):
        self.data[idx] = record
        self.refresh_tree()

    def delete_record(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("警告", "削除するレコードを選択してください。")
            return
        idx = self.tree.index(selected[0])
        del self.data[idx]
        self.refresh_tree()

    # ==== CSV入出力 ====
    def save_to_csv(self):
        try:
            with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=self.columns)
                writer.writeheader()
                writer.writerows(self.data)
            messagebox.showinfo("保存", "データをCSVに保存しました。")
        except Exception as e:
            messagebox.showerror("エラー", f"保存に失敗しました: {e}")

    def load_from_csv(self):
        if not os.path.exists(CSV_FILE):
            return
        try:
            with open(CSV_FILE, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                self.data = list(reader)
        except Exception as e:
            messagebox.showerror("エラー", f"CSVの読み込みに失敗しました: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("900x600")
    app = VendorApp(root)
    root.mainloop()
=======
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import csv
import os

CSV_FILE = "vendors.csv"

class VendorForm(tk.Toplevel):
    def __init__(self, master, record=None, callback=None):
        super().__init__(master)
        self.title("ベンダー情報入力")
        self.callback = callback
        self.record = record if record else {}

        labels = ["1次ベンダー", "2次ベンダー", "性", "名", "年齢", "携帯番号", "バッジID"]
        self.entries = {}

        for i, label_text in enumerate(labels):
            lbl = tk.Label(self, text=label_text)
            lbl.grid(row=i, column=0, padx=5, pady=5, sticky="e")
            ent = tk.Entry(self, width=30)
            ent.grid(row=i, column=1, padx=5, pady=5)
            self.entries[label_text] = ent

        if self.record:
            self.entries["1次ベンダー"].insert(0, self.record.get("first_vendor", ""))
            self.entries["2次ベンダー"].insert(0, self.record.get("second_vendor", ""))
            self.entries["性"].insert(0, self.record.get("last_name", ""))
            self.entries["名"].insert(0, self.record.get("first_name", ""))
            self.entries["年齢"].insert(0, self.record.get("age", ""))
            self.entries["携帯番号"].insert(0, self.record.get("phone", ""))
            self.entries["バッジID"].insert(0, self.record.get("badge_id", ""))

        btn_frame = tk.Frame(self)
        btn_frame.grid(row=len(labels), column=0, columnspan=2, pady=10)
        tk.Button(btn_frame, text="OK", command=self.on_ok).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="キャンセル", command=self.destroy).pack(side=tk.LEFT, padx=5)

    def on_ok(self):
        first_vendor = self.entries["1次ベンダー"].get().strip()
        second_vendor = self.entries["2次ベンダー"].get().strip()
        last_name = self.entries["性"].get().strip()
        first_name = self.entries["名"].get().strip()
        age = self.entries["年齢"].get().strip()
        phone = self.entries["携帯番号"].get().strip()
        badge_id = self.entries["バッジID"].get().strip()
        update_date = datetime.today().strftime("%Y-%m-%d")

        if not age.isdigit():
            messagebox.showerror("エラー", "年齢は数字で入力してください。")
            return

        record = {
            "first_vendor": first_vendor,
            "second_vendor": second_vendor,
            "last_name": last_name,
            "first_name": first_name,
            "age": age,
            "phone": phone,
            "badge_id": badge_id,
            "update_date": update_date,
        }

        if self.callback:
            self.callback(record)
        self.destroy()

class VendorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ベンダー管理アプリ")

        # ==== 上部：タイトルと検索 ====
        top_frame = tk.Frame(root, pady=10)
        top_frame.pack(fill=tk.X)

        tk.Label(top_frame, text="🔍 ベンダー検索：", font=("Arial", 11, "bold")).pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(top_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=5)
        search_entry.bind("<Return>", lambda e: self.search_records())
        tk.Button(top_frame, text="検索", command=self.search_records).pack(side=tk.LEFT, padx=5)
        tk.Button(top_frame, text="リセット", command=self.refresh_tree).pack(side=tk.LEFT, padx=5)

        # ==== 中央：ツリービュー ====
        columns = ("first_vendor", "second_vendor", "last_name", "first_name", "age", "phone", "badge_id", "update_date")
        self.columns = columns
        tree_frame = tk.Frame(root)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        headings = {
            "first_vendor": "1次ベンダー",
            "second_vendor": "2次ベンダー",
            "last_name": "性",
            "first_name": "名",
            "age": "年齢",
            "phone": "携帯番号",
            "badge_id": "バッジID",
            "update_date": "更新日",
        }
        for col, text in headings.items():
            self.tree.heading(col, text=text, command=lambda c=col: self.sort_column(c))
            self.tree.column(col, width=100, anchor="center")

        self.data = []
        self.sort_reverse = False
        self.sort_by = None

        # ==== 下部：ボタン ====
        btn_frame = tk.Frame(root, pady=10)
        btn_frame.pack(fill=tk.X)
        tk.Button(btn_frame, text="追加", width=10, command=self.add_record).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="編集", width=10, command=self.edit_record).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="削除", width=10, command=self.delete_record).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="保存", width=10, command=self.save_to_csv).pack(side=tk.LEFT, padx=5)

        self.load_from_csv()
        self.refresh_tree()

    # ==== 検索機能 ====
    def search_records(self):
        keyword = self.search_var.get().strip().lower()
        if not keyword:
            messagebox.showinfo("検索", "検索キーワードを入力してください。")
            return

        self.tree.selection_remove(*self.tree.selection())
        matches = []

        for i, record in enumerate(self.data):
            if any(keyword in str(v).lower() for v in record.values()):
                matches.append(i)

        if not matches:
            messagebox.showinfo("検索結果", "該当するレコードがありません。")
            return

        self.refresh_tree()
        for idx in matches:
            item_id = self.tree.get_children()[idx]
            self.tree.selection_add(item_id)
            self.tree.see(item_id)

    # ==== 並べ替え ====
    def sort_column(self, col):
        if self.sort_by == col:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_reverse = False
        self.sort_by = col

        if col == "age":
            self.data.sort(key=lambda x: int(x[col]), reverse=self.sort_reverse)
        elif col == "update_date":
            self.data.sort(key=lambda x: datetime.strptime(x[col], "%Y-%m-%d"), reverse=self.sort_reverse)
        else:
            self.data.sort(key=lambda x: x[col], reverse=self.sort_reverse)
        self.refresh_tree()

    # ==== 表示更新 ====
    def refresh_tree(self):
        self.tree.delete(*self.tree.get_children())
        for row in self.data:
            self.tree.insert("", tk.END, values=tuple(row[col] for col in self.columns))
        self.tree.selection_remove(*self.tree.selection())
        self.search_var.set("")

    # ==== CRUD 操作 ====
    def add_record(self):
        VendorForm(self.root, callback=self.add_callback)

    def add_callback(self, record):
        self.data.append(record)
        self.refresh_tree()

    def edit_record(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("警告", "編集するレコードを選択してください。")
            return
        idx = self.tree.index(selected[0])
        VendorForm(self.root, record=self.data[idx], callback=lambda r: self.edit_callback(idx, r))

    def edit_callback(self, idx, record):
        self.data[idx] = record
        self.refresh_tree()

    def delete_record(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("警告", "削除するレコードを選択してください。")
            return
        idx = self.tree.index(selected[0])
        del self.data[idx]
        self.refresh_tree()

    # ==== CSV入出力 ====
    def save_to_csv(self):
        try:
            with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=self.columns)
                writer.writeheader()
                writer.writerows(self.data)
            messagebox.showinfo("保存", "データをCSVに保存しました。")
        except Exception as e:
            messagebox.showerror("エラー", f"保存に失敗しました: {e}")

    def load_from_csv(self):
        if not os.path.exists(CSV_FILE):
            return
        try:
            with open(CSV_FILE, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                self.data = list(reader)
        except Exception as e:
            messagebox.showerror("エラー", f"CSVの読み込みに失敗しました: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("900x600")
    app = VendorApp(root)
    root.mainloop()
>>>>>>> f24cfb7 (Initial commit)
