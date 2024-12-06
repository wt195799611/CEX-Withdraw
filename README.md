# CEX提币器

一个支持多个中心化交易所的批量提币工具。目前支持欧易(OKX)、币安(Binance)和Gate.io交易所。

## 功能特点

- 支持多个交易所
- 批量提币功能
- 余额查询功能
- 代理设置支持
- Windows 11风格界面

## 使用方法

1. 下载并运行程序
   - 从 [Releases](https://github.com/yourusername/repo-name/releases) 下载最新版本
   - 直接运行 `CEX提币器.exe`

2. API设置
   - 选择交易所
   - 在API设置选项卡中填入API Key和Secret
   - 欧易交易所需要额外填写Passphrase
   - 可选择配置代理设置

3. 查询余额
   - 在查询余额选项卡中点击查询按钮
   - 显示当前账户所有币种余额

4. 批量提币
   - 在提币选项卡中填写提币信息
   - 每行输入一个提币地址（最多1000个）
   - 设置代币名称、提币网络、数量范围等
   - 设置提币间隔时间
   - 点击开始提币
   - 可随时点击停止按钮终止提币操作

## 开发环境配置

1. 安装依赖：
   bash
   pip install -r requirements.txt
2.运行程序：
   bash
   python main.py
