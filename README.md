# CEX提币器

一个支持多个中心化交易所的批量提币工具，目前支持 **欧易(OKX)**、**币安(Binance)** 和 **Gate.io**。

---

## 功能特点

- 支持多个交易所（OKX、Binance、Gate.io）
- 批量提币，支持多达 1000 个地址
- 余额查询功能
- 可配置代理
- Windows 11 风格界面

---

## 使用方法

### 1. 下载并运行程序
- 从 [Releases](https://github.com/yourusername/repo-name/releases) 页面下载最新版本。
- 直接运行 `CEX提币器.exe`。

### 2. 配置 API 设置
1. 选择目标交易所。
2. 在 **API设置** 选项卡中填入以下信息：
   - API Key 和 Secret。
   - **欧易(OKX)** 用户需要额外填写 **Passphrase**。
3. （可选）配置代理设置以优化连接。

### 3. 查询余额
1. 打开 **查询余额** 选项卡。
2. 点击 **查询按钮** 查看账户当前的所有币种余额。

### 4. 批量提币
1. 打开 **提币** 选项卡。
2. 填写以下信息：
   - 每行输入一个提币地址（最多 1000 个）。
   - 设置代币名称、提币网络、数量范围等。
   - 配置提币间隔时间。
3. 点击 **开始提币** 执行批量操作。
4. 可随时点击 **停止按钮** 终止提币操作。

---

## 开发环境配置

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 运行项目
```bash
python main.py
```

### 3. 打包程序
```bash
pip install pyinstaller
pyinstaller -F -w -i icon.ico main.py
```

## 项目结构

```
project/
├── main.py               # 主程序入口
├── build.spec            # 打包配置文件
├── app.ico               # 应用程序图标
├── requirements.txt      # 依赖列表
├── gui/                  # GUI 相关代码
│   └── app_window.py     # 主窗口实现
└── api/                  # API 相关代码
    └── exchange_client.py # 交易所 API 实现
```

## 依赖要求

- Python 3.7+
- 第三方库：
  - requests
  - tkinter（Python 标准库）
  - 其他依赖见 requirements.txt

## 注意事项

### API 密钥安全
- 程序仅在内存中临时保存 API 密钥，请妥善保管
- 为避免损失，建议设置 IP 白名单及限制 API 权限

### 提币前核对信息
- 提币地址、网络和数量需确认无误
- 参考交易所文档获取正确的提币网络格式
- 小额测试：首次使用建议先进行小额测试

## 安全建议

### API权限设置
- 仅启用提币和查询权限
- 配置 IP 白名单以增强安全性
- 定期更新 API 密钥

### 使用建议
- 定期检查提币地址和网络配置
- 确保使用最新版本软件

## 更新日志

### v1.0.0
- 支持欧易(OKX)、币安(Binance)、Gate.io
- 实现批量提币和余额查询功能
- 添加代理配置支持
- 提供 Windows 11 风格 UI

## 免责声明

本程序仅供学习交流使用，任何使用本程序导致的后果由用户自行承担。使用本程序即表示同意本免责声明。