import os
import sys

# ファイルの絶対パスを取得
current_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_path)

from app import app as application



