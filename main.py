import sys
import os
import os
os.add_dll_directory("C:\\Windows\\System32")

def resource_path(relative_path):
    """获取资源的绝对路径"""
    try:
        # PyInstaller创建临时文件夹,将路径存储在_MEIPASS中
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# 添加模块搜索路径
if getattr(sys, 'frozen', False):
    # 运行于打包环境
    module_path = resource_path('')
else:
    # 运行于开发环境
    module_path = os.path.dirname(os.path.abspath(__file__))

sys.path.append(module_path)

from gui.app_window import CryptoApp

def main():
    app = CryptoApp()
    app.mainloop()

if __name__ == "__main__":
    # 设置环境变量
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['LANG'] = 'zh_CN.UTF-8'
    
    # 安全地设置编码
    try:
        if sys.stdout and sys.stdout.encoding != 'utf-8':
            sys.stdout.reconfigure(encoding='utf-8')
        if sys.stderr and sys.stderr.encoding != 'utf-8':
            sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass
    
    main()