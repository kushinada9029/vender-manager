# 🧭 Vender Manager

Tkinterで作成したベンダー管理アプリです。  
GUIで簡単に「1次ベンダー」「2次ベンダー」「氏名」「年齢」「電話番号」「バッジID」などの情報を登録・編集・検索できます。  
CSVでの保存・読み込みにも対応しています。

---

## 🌟 主な機能

- ✅ **データ追加・編集・削除**
- ✅ **CSVファイルへの保存 / 読み込み**
- ✅ **並べ替え機能（クリックで昇順・降順）**
- ✅ **検索機能（名前・バッジID・ベンダー名対応）**
- ✅ **検索結果を背景色でハイライト**
- ✅ **ファイル選択ダイアログからCSVを読み込み**

---

## 🖥️ 画面イメージ

![アプリ画面例](https://raw.githubusercontent.com/kushinada9029/vender-manager/main/docs/screenshot.png)

---

## 🚀 実行方法

### ① ダウンロード

```bash
git clone https://github.com/kushinada9029/vender-manager.git
cd vender-manager
```

### ② 実行

```bash
python src/main.py
```

> 💡 Python 3.9以上推奨  
> Tkinterは標準で入っています（特別なライブラリは不要）

---

## 📂 フォルダ構成

```bash
vender-manager/
├── src/
│   ├── main.py         # アプリ本体
│   └── vendors.csv     # サンプルデータ
├── docs/
│   └── screenshot.png  # アプリのスクリーンショット
└── README.md           # このファイル
```

---

## 🧩 使用技術

| 項目 | 内容 |
|------|------|
| 言語 | Python 3 |
| GUI | Tkinter |
| データ保存 | CSV（標準ライブラリ） |
| 実行環境 | Windows

---

🪄 開発の背景

現職でユーザーデータをExcelで管理していた際、
データ量が多くファイルの読み込みに1〜2分を要していたため、
業務効率化と時間短縮を目的に、自己学習も兼ねてPython（Tkinter）でデータ管理アプリを開発しました。

## 💡 開発のポイント

- TkinterでGUI構築を学びながら作成しました。  
- 検索や並べ替えなど、実務でよくある操作を意識しています。  
- 初心者でも読めるよう、コードはコメント付きで整理しました。  

---

## 📎 作者

**kushinada9029**  
👉 [GitHubプロフィールはこちら](https://github.com/kushinada9029)
