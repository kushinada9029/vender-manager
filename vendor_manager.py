import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import csv
import os
import unicodedata

CSV_FILE = "venders.csv"  # デフォルトのCSVファイル名


# --- 検索用のテキスト正規化関数 ---
def normalize_text(text):
    """全角・半角、ひらがな・カタカナ、濁点の違いを吸収して検索精度を上げる"""
    if not text:
        return ""
    # 全角・半角などを正規化
    text = unicodedata.normalize("NFKC", text.strip()).lower()
    # カタカナをひらがなに変換
    text = "".join(
        chr(ord(ch) - 0x60) if "ァ" <= ch <= "ン" else ch
        for ch in text
    )
    return text


class VenderForm(tk.Toplevel):
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
            self.entries["1次ベンダー"].insert(0, self.record.get("first_vender", ""))
            self.entries["2次ベンダー"].insert(0, self.record.get("second_vender", ""))
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
        first_vender = self.entries["1次ベンダー"].get().strip()
        second_vender = self.entries["2次ベンダー"].get().strip()
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
            "first_vender": first_vender,
            "second_vender": second_vender,
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


class VenderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ベンダー管理アプリ")

        self.columns = (
            "first_vender", "second_vender", "last_name", "first_name",
            "age", "phone", "badge_id", "update_date"
        )

        # 🔍 検索バー
        search_frame = tk.Frame(root)
        search_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(search_frame, text="🔍 検索:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="検索", command=self.search_records).pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="リセット", command=self.reset_search).pack(side=tk.LEFT, padx=5)

        # 表示エリア
        self.tree = ttk.Treeview(root, columns=self.columns, show="headings")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # --- ハイライト用タグ設定 ---
        self.tree.tag_configure("highlight", background="#ffff99")  # 黄色

        headings = {
            "first_vender": "1次ベンダー",
            "second_vender": "2次ベンダー",
            "last_name": "性",
            "first_name": "名",
            "age": "年齢",
            "phone": "携帯番号",
            "badge_id": "バッジID",
            "update_date": "更新日",
        }
        for col, text in headings.items():
            self.tree.heading(col, text=text, command=lambda c=col: self.sort_column(c))
            self.tree.column(col, width=100)

        self.data = []
        self.filtered_data = []
        self.sort_reverse = False
        self.sort_by = None
        self.highlight_indices = set()

        # ボタン群
        btn_frame = tk.Frame(root)
        btn_frame.pack(fill=tk.X)
        tk.Button(btn_frame, text="📂 ファイルを開く", command=self.load_from_file_dialog).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(btn_frame, text="追加", command=self.add_record).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(btn_frame, text="編集", command=self.edit_record).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(btn_frame, text="削除", command=self.delete_record).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(btn_frame, text="保存", command=self.save_to_csv).pack(side=tk.LEFT, padx=5, pady=5)

        self.load_from_csv()
        self.refresh_tree()

    def sort_column(self, col):
        if self.sort_by == col:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_reverse = False
        self.sort_by = col

        if col == "age":
            self.filtered_data.sort(key=lambda x: int(x[col]), reverse=self.sort_reverse)
        elif col == "update_date":
            self.filtered_data.sort(key=lambda x: datetime.strptime(x[col], "%Y-%m-%d"), reverse=self.sort_reverse)
        else:
            self.filtered_data.sort(key=lambda x: x[col], reverse=self.sort_reverse)
        self.refresh_tree()

    def refresh_tree(self):
        self.tree.delete(*self.tree.get_children())
        for i, row in enumerate(self.filtered_data):
            tags = ("highlight",) if i in self.highlight_indices else ()
            self.tree.insert("", tk.END, values=tuple(row[col] for col in self.columns), tags=tags)

    def add_record(self):
        VenderForm(self.root, callback=self.add_callback)

    def add_callback(self, record):
        self.data.append(record)
        self.filtered_data = list(self.data)
        self.refresh_tree()

    def edit_record(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("警告", "編集するレコードを選択してください。")
            return
        idx = self.tree.index(selected[0])
        VenderForm(self.root, record=self.filtered_data[idx], callback=lambda r: self.edit_callback(idx, r))

    def edit_callback(self, idx, record):
        target_record = self.filtered_data[idx]
        index_in_data = self.data.index(target_record)
        self.data[index_in_data] = record
        self.filtered_data[idx] = record
        self.refresh_tree()

    def delete_record(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("警告", "削除するレコードを選択してください。")
            return
        idx = self.tree.index(selected[0])
        target_record = self.filtered_data[idx]
        self.data.remove(target_record)
        self.filtered_data.remove(target_record)
        self.refresh_tree()

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
                self.filtered_data = list(self.data)
        except Exception as e:
            messagebox.showerror("エラー", f"CSVの読み込みに失敗しました: {e}")

    def load_from_file_dialog(self):
        file_path = filedialog.askopenfilename(
            title="CSVファイルを選択",
            filetypes=[("CSVファイル", "*.csv")]
        )
        if not file_path:
            return
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                self.data = list(reader)
                self.filtered_data = list(self.data)
            self.refresh_tree()
            messagebox.showinfo("完了", f"{os.path.basename(file_path)} を読み込みました。")
        except Exception as e:
            messagebox.showerror("エラー", f"CSVの読み込みに失敗しました: {e}")

    def search_records(self):
        keyword = normalize_text(self.search_var.get())
        if not keyword:
            messagebox.showinfo("検索", "検索ワードを入力してください。")
            return

        self.filtered_data = list(self.data)
        self.highlight_indices.clear()

        for i, row in enumerate(self.filtered_data):
            if (
                keyword in normalize_text(row["first_name"])
                or keyword in normalize_text(row["last_name"])
                or keyword in normalize_text(row["badge_id"])
            ):
                self.highlight_indices.add(i)

        if not self.highlight_indices:
            messagebox.showinfo("検索", "該当するデータが見つかりませんでした。")

        self.refresh_tree()

    def reset_search(self):
        self.filtered_data = list(self.data)
        self.search_var.set("")
        self.highlight_indices.clear()
        self.refresh_tree()


if __name__ == "__main__":
    root = tk.Tk()
    app = VenderApp(root)
    root.mainloop()
