import sys
from pathlib import Path

# 將專案根目錄加入 Python module 搜尋路徑
ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR))
