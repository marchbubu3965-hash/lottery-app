# LotteryApp

## 專案介紹
**LotteryApp** 是一個單機版抽籤系統，適合公司活動或抽獎使用。  
主要特色：
- 支援多種獎項設定（一般獎 / 特別獎）
- 特別獎有輪盤動畫效果
- 管理界面：獎項管理、名單管理、歷史中獎紀錄
- 本地 SQLite 資料庫永久儲存抽獎資料
- 預設管理者帳號（首次啟動可登入）
- GUI 使用 Tkinter 開發

---

## 專案結構

lottery_app/
├─ app/
│ ├─ main.py # 程式入口
│ ├─ db/
│ │ ├─ database.py # 資料庫操作
│ │ └─ schema.sql # 資料表 schema
│ ├─ ui/ # 各視窗 UI
│ ├─ services/ # 商業邏輯
│ └─ core/ # 狀態機、核心邏輯
├─ assets/
│ ├─ icons/ # 公司 Logo
│ └─ images/ # 背景、介面資源
├─ dist/ # PyInstaller 打包後的產物
└─ README.md


---

## 環境需求

- Python 3.12
- macOS（目前已測試）
- 主要套件：
  - `tkinter`（GUI）
  - `sqlite3`（資料庫）
  - `hashlib`（密碼雜湊）
  - 標準 Python 套件（無額外安裝需求）

---

## 安裝與執行（開發模式）

- 1.進入專案目錄：
   ```bash
   cd lottery_app
- 2.建議使用虛擬環境：
    python -m venv venv
    source venv/bin/activate   # macOS
- 3.執行程式：
    python -m app.main
- 4.首次啟動會自動建立本地資料庫：
    ~/Library/Application Support/LotteryApp/lottery.db

- 打包（macOS）
    使用 PyInstaller 打包（單目錄模式）：
    pyinstaller app/main.py \
    --name LotteryApp \
    --windowed \
    --onedir \
    --clean \
    --add-data "app/db/schema.sql:db" \
    --add-data "assets:assets"

    
- 使用說明

    登入：

    預設管理者帳號：

    使用者名稱：admin

    密碼：admin123

    首次登入後建議修改密碼

    管理設定：

    「獎項管理」：新增 / 編輯 / 刪除獎項

    「名單管理」：維護員工名單

    抽獎控制：

    開始抽籤、暫停、下一個獎項

    特別獎會觸發輪盤動畫

    查看歷史：

    查看過去的中獎紀錄

    清空測試：

    僅在測試環境使用「清空中獎名單」