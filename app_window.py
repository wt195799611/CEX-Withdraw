import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

class CryptoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("加密货币数据提取器")
        self.geometry("600x400")
        
        # 加载保存的数据
        self.data_file = "crypto_data.json"
        self.crypto_list = self.load_data()
        
        self.setup_ui()

    # ... (其余代码保持不变) 