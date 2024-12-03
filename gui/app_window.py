import tkinter as tk
from tkinter import ttk, messagebox, Text, scrolledtext
import json
import os
from api.exchange_client import OKEClient, BinanceClient, GateClient
import random
import threading
import sys

class CryptoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CEX提币器")
        self.geometry("650x900")
        
        # 设置应用程序图标
        try:
            # 获取图标文件的路径
            if getattr(sys, 'frozen', False):
                # 如果是打包后的exe
                icon_path = os.path.join(sys._MEIPASS, 'app.ico')
            else:
                # 如果是开发环境
                icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app.ico')
            
            # 设置窗口图标
            self.iconbitmap(icon_path)
            
            # 设置任务栏图标
            import ctypes
            myappid = 'mycompany.cexwithdraw.v1.0'  # 可以自定义
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
            
        except Exception as e:
            print(f"设置图标失败: {e}")
        
        # 设置主题颜色
        self.bg_color = "#FFFFFF"       # 白色背景
        self.input_bg = "#FFFFFF"       # 输入框背景色
        self.primary_color = "#1e90ff"  # 主题色
        self.hover_color = "#3aa0ff"    # 悬停色
        self.text_color = "#333333"     # 文字颜色
        
        # 设置默认字体
        self.default_font = "Microsoft YaHei UI"  # 微软雅黑
        
        # 设置窗口背景色
        self.configure(bg=self.bg_color)
        self.style = ttk.Style()
        self.setup_theme()
        
        # 缓存API信息
        self.api_cache = {
            'api_key': '',
            'api_secret': '',
            'passphrase': ''
        }
        
        # 添加提币控制标志
        self.is_withdrawing = False
        
        # 初始化代理设置
        self.api_cache['proxy'] = {
            'enabled': False,
            'use_local': True  # 默认使用本地连接
        }
        
        self.setup_ui()
    
    def setup_theme(self):
        """设置Windows 11风格主题"""
        # Windows 11主题颜色
        self.win11_colors = {
            'bg': '#FFFFFF',
            'fg': '#202020',
            'accent': '#0067C0',  # Windows 11默认强调色
            'hover': '#0078D4',
            'pressed': '#005BA1',
            'border': '#E5E5E5',
            'input_bg': '#FFFFFF',
            'disabled': '#F0F0F0'
        }

        # 基础框架样式
        self.style.configure(
            "TFrame",
            background=self.win11_colors['bg']
        )
        
        # 标签框样式 - Windows 11圆角效果
        self.style.configure(
            "TLabelframe",
            background=self.win11_colors['bg'],
            foreground=self.win11_colors['fg'],
            bordercolor=self.win11_colors['border'],
            relief="solid",
            borderwidth=1
        )
        self.style.configure(
            "TLabelframe.Label",
            background=self.win11_colors['bg'],
            foreground=self.win11_colors['fg'],
            font=('Segoe UI', 10),
            padding=10
        )
        
        # 标签样式
        self.style.configure(
            "TLabel",
            background=self.win11_colors['bg'],
            foreground=self.win11_colors['fg'],
            font=('Segoe UI', 10)
        )
        
        # 按钮样式 - Windows 11风格
        self.style.configure(
            "Modern.TButton",
            background=self.win11_colors['accent'],
            foreground='white',
            padding=(15, 8),
            font=('Segoe UI', 10),
            relief="flat",
            borderwidth=0
        )
        self.style.map(
            "Modern.TButton",
            background=[
                ('pressed', self.win11_colors['pressed']),
                ('active', self.win11_colors['hover'])
            ],
            relief=[('pressed', 'flat')]
        )
        
        # 输入框样式 - Windows 11风格
        self.style.configure(
            "Modern.TEntry",
            fieldbackground=self.win11_colors['input_bg'],
            foreground=self.win11_colors['fg'],
            bordercolor=self.win11_colors['border'],
            lightcolor=self.win11_colors['border'],
            darkcolor=self.win11_colors['border'],
            relief="solid",
            borderwidth=1,
            padding=8,
            font=('Segoe UI', 10)
        )
        self.style.map(
            "Modern.TEntry",
            bordercolor=[('focus', self.win11_colors['accent'])]
        )
        
        # 选项卡样式 - Windows 11风格
        self.style.configure(
            "Modern.TNotebook",
            background=self.win11_colors['bg'],
            bordercolor=self.win11_colors['border'],
            tabmargins=[0, 4, 0, 0]
        )
        self.style.configure(
            "Modern.TNotebook.Tab",
            background=self.win11_colors['bg'],
            foreground=self.win11_colors['fg'],
            padding=[20, 8],
            font=('Segoe UI', 10),
            borderwidth=0
        )
        self.style.map(
            "Modern.TNotebook.Tab",
            background=[
                ('selected', self.win11_colors['bg']),
                ('active', self.win11_colors['hover'])
            ],
            foreground=[
                ('selected', self.win11_colors['accent']),
                ('active', self.win11_colors['accent'])
            ],
            bordercolor=[('selected', self.win11_colors['accent'])]
        )
        
        # 单选按钮样式 - Windows 11风格
        self.style.configure(
            "Modern.TRadiobutton",
            background=self.win11_colors['bg'],
            foreground=self.win11_colors['fg'],
            font=('Segoe UI', 10)
        )
        self.style.map(
            "Modern.TRadiobutton",
            background=[('active', self.win11_colors['bg'])],
            foreground=[('active', self.win11_colors['accent'])]
        )
        
        # 复选框样式 - Windows 11风格
        self.style.configure(
            "Modern.TCheckbutton",
            background=self.win11_colors['bg'],
            foreground=self.win11_colors['fg'],
            font=('Segoe UI', 10)
        )
        self.style.map(
            "Modern.TCheckbutton",
            background=[('active', self.win11_colors['bg'])],
            foreground=[('active', self.win11_colors['accent'])]
        )
        
        # 下拉框样式 - Windows 11风格
        self.style.configure(
            "TCombobox",
            background=self.win11_colors['input_bg'],
            foreground=self.win11_colors['fg'],
            arrowcolor=self.win11_colors['fg'],
            bordercolor=self.win11_colors['border'],
            lightcolor=self.win11_colors['border'],
            darkcolor=self.win11_colors['border'],
            relief="solid",
            borderwidth=1,
            padding=8,
            font=('Segoe UI', 10)
        )
    
    def setup_ui(self):
        # 创建主框架
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建交易所选择框架
        exchange_frame = ttk.LabelFrame(main_frame, text="选择交易所")
        exchange_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 交易所选择
        exchanges = ["欧易", "币安", "Gate"]
        self.exchange_var = tk.StringVar()
        for exchange in exchanges:
            rb = ttk.Radiobutton(
                exchange_frame,
                text=exchange,
                variable=self.exchange_var,
                value=exchange,
                command=self.on_exchange_select,
                style="Modern.TRadiobutton"
            )
            rb.pack(side=tk.LEFT, padx=30, pady=10)
        
        # 创建选项卡容器
        self.notebook = ttk.Notebook(main_frame, style="Modern.TNotebook")
        
        # 创建三个选项卡页面
        self.balance_frame = ttk.Frame(self.notebook)
        self.withdraw_frame = ttk.Frame(self.notebook)
        self.api_frame = ttk.Frame(self.notebook)
        
        # 添加选项卡
        self.notebook.add(self.balance_frame, text="查询余额")
        self.notebook.add(self.withdraw_frame, text="提币")
        self.notebook.add(self.api_frame, text="API设置")
        
        # 初始隐藏选项卡
        # self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 设置各个选项卡的内容
        self.setup_balance_tab()
        self.setup_withdraw_tab()
        self.setup_api_tab()
    
    def setup_balance_tab(self):
        # 创建余额显示文本框
        self.balance_text = scrolledtext.ScrolledText(self.balance_frame, height=20)
        self.balance_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 添加查���按钮
        ttk.Button(
            self.balance_frame,
            text="查询余额",
            command=self.query_balance
        ).pack(pady=5)
        
    def setup_withdraw_tab(self):
        # 地址输入区域
        address_frame = ttk.LabelFrame(self.withdraw_frame, text="提币地址（每行一个，最多1000个）")
        address_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.address_text = scrolledtext.ScrolledText(address_frame, height=10)
        self.address_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 参数设置区域
        param_frame = ttk.Frame(self.withdraw_frame)
        param_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # 初始化变量
        self.coin_var = tk.StringVar()
        self.network_var = tk.StringVar()
        self.min_amount_var = tk.StringVar()
        self.max_amount_var = tk.StringVar()
        self.fee_var = tk.StringVar()
        self.min_interval_var = tk.StringVar(value="1")
        self.max_interval_var = tk.StringVar(value="3")
        self.fund_password_var = tk.StringVar()
        
        # 创建输入框
        inputs = [
            ("代币名称:", self.coin_var),
            ("提币网络:", self.network_var),
            ("最小数量:", self.min_amount_var),
            ("最大数量:", self.max_amount_var),
            ("手续费:", self.fee_var),
            ("最小间隔(秒):", self.min_interval_var),
            ("最大间隔(秒):", self.max_interval_var),
        ]
        
        for i, (label, var) in enumerate(inputs):
            ttk.Label(param_frame, text=label).grid(row=i//2, column=i%2*2, padx=10, pady=8)
            ttk.Entry(
                param_frame,
                textvariable=var,
                style="Modern.TEntry"
            ).grid(row=i//2, column=i%2*2+1, padx=10, pady=8, sticky="ew")
        
        # 资金密码框（初始隐藏）
        self.fund_password_frame = ttk.Frame(param_frame)
        self.fund_password_frame.grid(row=4, column=0, columnspan=4, sticky="ew")
        ttk.Label(self.fund_password_frame, text="资金密码:").pack(side=tk.LEFT, padx=10)
        ttk.Entry(
            self.fund_password_frame,
            textvariable=self.fund_password_var,
            show="*",
            style="Modern.TEntry"
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        self.fund_password_frame.grid_remove()
        
        # 创建按钮框架
        button_frame = ttk.Frame(self.withdraw_frame)
        button_frame.pack(pady=10)
        
        # 提币按钮
        self.withdraw_button = ttk.Button(
            button_frame,
            text="开始提币",
            command=self.start_withdraw,
            style="Modern.TButton"
        )
        self.withdraw_button.pack(side=tk.LEFT, padx=5)
        
        # 停止按钮
        self.stop_button = ttk.Button(
            button_frame,
            text="停止提币",
            command=self.stop_withdraw,
            style="Modern.TButton"
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)
        self.stop_button.configure(state='disabled')  # 初始状态为禁用
        
        # 结果显示区域
        result_frame = ttk.LabelFrame(self.withdraw_frame, text="提币结果")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.result_text = scrolledtext.ScrolledText(result_frame, height=10)
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def setup_api_tab(self):
        settings_frame = ttk.Frame(self.api_frame)
        settings_frame.pack(padx=20, pady=20)
        
        # API设置区域
        api_settings = ttk.LabelFrame(settings_frame, text="API设置")
        api_settings.pack(fill=tk.X, padx=5, pady=5)
        
        # API Key
        ttk.Label(api_settings, text="API Key:").grid(row=0, column=0, padx=10, pady=10)
        self.api_key_var = tk.StringVar()
        ttk.Entry(api_settings, textvariable=self.api_key_var, width=50, style="Modern.TEntry").grid(row=0, column=1, padx=10)
        
        # API Secret
        ttk.Label(api_settings, text="API Secret:").grid(row=1, column=0, padx=10, pady=10)
        self.api_secret_var = tk.StringVar()
        ttk.Entry(api_settings, textvariable=self.api_secret_var, width=50, show="*", style="Modern.TEntry").grid(row=1, column=1, padx=10)
        
        # Passphrase（可隐藏）
        self.passphrase_frame = ttk.Frame(api_settings)
        self.passphrase_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=10)
        ttk.Label(self.passphrase_frame, text="Passphrase:").pack(side=tk.LEFT, padx=10)
        self.passphrase_var = tk.StringVar()
        ttk.Entry(
            self.passphrase_frame,
            textvariable=self.passphrase_var,
            width=50,
            show="*",
            style="Modern.TEntry"
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        
        # 代理设置区域
        proxy_frame = ttk.LabelFrame(settings_frame, text="代理设置")
        proxy_frame.pack(fill=tk.X, padx=5, pady=10)
        
        # 代理选项
        proxy_options = ttk.Frame(proxy_frame)
        proxy_options.pack(fill=tk.X, padx=5, pady=5)
        
        self.use_proxy_var = tk.BooleanVar(value=False)
        self.use_local_var = tk.BooleanVar(value=True)  # 默认选中本地连接
        
        self.proxy_checkbox = ttk.Checkbutton(
            proxy_options,
            text="使用代理",
            variable=self.use_proxy_var,
            command=self.toggle_proxy_settings
        )
        self.proxy_checkbox.pack(side=tk.LEFT, padx=10)
        
        self.local_checkbox = ttk.Checkbutton(
            proxy_options,
            text="使用本地连接",
            variable=self.use_local_var,
            command=self.toggle_local_settings
        )
        self.local_checkbox.pack(side=tk.LEFT, padx=10)
        
        # 代理详细设置（初始隐藏）
        self.proxy_details_frame = ttk.Frame(proxy_frame)
        self.proxy_details_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 代理IP
        ttk.Label(self.proxy_details_frame, text="代理IP:").grid(row=0, column=0, padx=5, pady=5)
        self.proxy_ip_var = tk.StringVar()
        ttk.Entry(self.proxy_details_frame, textvariable=self.proxy_ip_var, style="Modern.TEntry").grid(row=0, column=1, padx=5)
        
        # 代理端口
        ttk.Label(self.proxy_details_frame, text="端口:").grid(row=0, column=2, padx=5, pady=5)
        self.proxy_port_var = tk.StringVar()
        ttk.Entry(self.proxy_details_frame, textvariable=self.proxy_port_var, style="Modern.TEntry", width=10).grid(row=0, column=3, padx=5)
        
        # 代理账号
        ttk.Label(self.proxy_details_frame, text="账号:").grid(row=1, column=0, padx=5, pady=5)
        self.proxy_user_var = tk.StringVar()
        ttk.Entry(self.proxy_details_frame, textvariable=self.proxy_user_var, style="Modern.TEntry").grid(row=1, column=1, padx=5)
        
        # 代理密码
        ttk.Label(self.proxy_details_frame, text="密码:").grid(row=1, column=2, padx=5, pady=5)
        self.proxy_pass_var = tk.StringVar()
        ttk.Entry(self.proxy_details_frame, textvariable=self.proxy_pass_var, show="*", style="Modern.TEntry").grid(row=1, column=3, padx=5)
        
        # 代理协议
        ttk.Label(self.proxy_details_frame, text="协议:").grid(row=2, column=0, padx=5, pady=5)
        self.proxy_protocol_var = tk.StringVar(value="http")
        protocol_combo = ttk.Combobox(
            self.proxy_details_frame,
            textvariable=self.proxy_protocol_var,
            values=["http", "socks5", "https"],
            state="readonly",
            width=10
        )
        protocol_combo.grid(row=2, column=1, padx=5, pady=5)
        
        # 初始隐藏代理设置
        self.proxy_details_frame.pack_forget()
        
        # 保存按钮
        ttk.Button(
            settings_frame,
            text="保存设置",
            command=self.save_settings,
            style="Modern.TButton"
        ).pack(pady=20)
    
    def toggle_proxy_settings(self):
        """切换代理设置的显示/隐藏"""
        if self.use_proxy_var.get():
            self.proxy_details_frame.pack(fill=tk.X, padx=5, pady=5)
            self.use_local_var.set(False)
            self.local_checkbox.state(['disabled'])  # 禁用本地连接选项
        else:
            self.proxy_details_frame.pack_forget()
            self.use_local_var.set(True)
            self.local_checkbox.state(['!disabled'])  # 启用本地连接选项
    
    def toggle_local_settings(self):
        """切换本地连接设置"""
        if self.use_local_var.get():
            self.use_proxy_var.set(False)
            self.proxy_details_frame.pack_forget()
            self.proxy_checkbox.state(['disabled'])  # 禁用代理选项
        else:
            self.proxy_checkbox.state(['!disabled'])  # 启用代理选项
    
    def save_settings(self):
        """保存API和代理设置"""
        # 保存API设置
        self.api_cache['api_key'] = self.api_key_var.get()
        self.api_cache['api_secret'] = self.api_secret_var.get()
        self.api_cache['passphrase'] = self.passphrase_var.get()
        
        # 保存代理设置
        self.api_cache['proxy'] = {
            'enabled': self.use_proxy_var.get(),
            'use_local': self.use_local_var.get(),
            'ip': self.proxy_ip_var.get(),
            'port': self.proxy_port_var.get(),
            'username': self.proxy_user_var.get(),
            'password': self.proxy_pass_var.get(),
            'protocol': self.proxy_protocol_var.get()
        }
        
        # 只清空安全相关的输入框
        self.api_key_var.set('')
        self.api_secret_var.set('')
        self.passphrase_var.set('')
        
        messagebox.showinfo("成功", "设置已保存")
    
    def on_exchange_select(self):
        """当选择交易所时的处理"""
        exchange = self.exchange_var.get()
        
        # 显示选项卡
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 处理资金密码框的显示/隐藏
        if hasattr(self, 'fund_password_frame'):
            if exchange == "欧易":
                self.fund_password_frame.grid()
            else:
                self.fund_password_frame.grid_remove()
        
        # 处理Passphrase输入框的显示/隐藏
        if hasattr(self, 'passphrase_frame'):
            if exchange == "欧易":
                self.passphrase_frame.grid()
            else:
                self.passphrase_frame.grid_remove()
    
    def query_balance(self):
        if not self.check_api_settings():
            return
        
        try:
            client = self.get_exchange_client()
            balances = client.get_balances()
            self.balance_text.delete(1.0, tk.END)
            self.balance_text.insert(tk.END, json.dumps(balances, indent=2))
        except Exception as e:
            messagebox.showerror("错误", f"查询余额失败: {str(e)}")
            
    def start_withdraw(self):
        if not self.check_api_settings():
            return
            
        # 获取并清理地址列表
        addresses = self.address_text.get(1.0, tk.END).strip().split('\n')
        addresses = [addr.strip() for addr in addresses if addr.strip()]
        
        if len(addresses) > 1000:
            messagebox.showerror("错误", "地址数量超过1000个限制")
            return
            
        # 获取参数
        try:
            coin = self.coin_var.get().strip()
            network = self.network_var.get().strip()
            min_amount = float(self.min_amount_var.get().strip())
            max_amount = float(self.max_amount_var.get().strip())
            fee = self.fee_var.get().strip()
            min_interval = float(self.min_interval_var.get())
            max_interval = float(self.max_interval_var.get())
        except ValueError as e:
            messagebox.showerror("错误", "请输入有效的数值")
            return
        
        # 检查必填参数
        if not all([coin, network, min_amount, max_amount, fee]):
            messagebox.showerror("错误", "请填写完整信息")
            return
        
        # 检查欧易的资金密码
        if self.exchange_var.get() == "欧易" and not self.fund_password_var.get().strip():
            messagebox.showerror("错误", "请输入资金密码")
            return

        # 设置提币状态和按钮状态
        self.is_withdrawing = True
        self.withdraw_button.configure(state='disabled')
        self.stop_button.configure(state='normal')

        # 创建客户端
        client = self.get_exchange_client()
        
        # 开始循环提币
        def process_withdrawals():
            for address in addresses:
                # 检查是否需要停止
                if not self.is_withdrawing:
                    self.update_withdraw_result("系统", "提币已手动停止")
                    break
                    
                try:
                    # 生成随机提币数量
                    amount = round(random.uniform(min_amount, max_amount), 6)
                    
                    # 执行提币
                    result = client.withdraw(
                        address=address,
                        coin=coin,
                        amount=amount,
                        network=network,
                        fee=fee,
                        min_interval=min_interval,
                        max_interval=max_interval,
                        fund_password=self.fund_password_var.get() if self.exchange_var.get() == "欧易" else None
                    )
                    
                    # 更新结果显示
                    self.update_withdraw_result(address, result)
                    
                    # 如果提币失败，停止循环
                    if isinstance(result, dict) and not result.get('success', False):
                        self.is_withdrawing = False
                        break
                        
                except Exception as e:
                    self.update_withdraw_result(address, f"错误: {str(e)}")
                    self.is_withdrawing = False
                    break
            
            # 恢复按钮状态
            self.after(0, self.reset_withdraw_buttons)
        
        # 在新线程中执行提币操作
        withdraw_thread = threading.Thread(target=process_withdrawals)
        withdraw_thread.daemon = True
        withdraw_thread.start()

    def stop_withdraw(self):
        """停止提币操作"""
        self.is_withdrawing = False
        self.stop_button.configure(state='disabled')
    
    def reset_withdraw_buttons(self):
        """重置按钮状态"""
        self.is_withdrawing = False
        self.withdraw_button.configure(state='normal')
        self.stop_button.configure(state='disabled')
    
    def update_withdraw_result(self, address, result):
        """更新提币结果显示"""
        # 使用 after 方法确保在主线程中更新 UI
        self.after(0, lambda: self._update_result_text(address, result))

    def _update_result_text(self, address, result):
        """在主线程中更新文本显示"""
        self.result_text.insert(tk.END, f"地址: {address}\n结果: {result}\n\n")
        self.result_text.see(tk.END)
        
    def check_api_settings(self):
        if not all([self.api_cache['api_key'], self.api_cache['api_secret']]):
            messagebox.showerror("错误", "请先设置API信息")
            return False
        return True
        
    def get_exchange_client(self):
        exchange = self.exchange_var.get()
        if exchange == "欧易":
            return OKEClient(self.api_cache)
        elif exchange == "币安":
            return BinanceClient(self.api_cache)
        elif exchange == "Gate":
            return GateClient(self.api_cache) 