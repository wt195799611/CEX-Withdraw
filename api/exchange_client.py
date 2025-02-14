import time
import random
import hmac
import base64
import json
import requests
import hashlib
from datetime import datetime
from abc import ABC, abstractmethod

class ExchangeClient(ABC):
    def __init__(self, api_settings):
        self.api_key = api_settings['api_key']
        self.api_secret = api_settings['api_secret']
        self.passphrase = api_settings.get('passphrase', '')
        self.proxy_settings = api_settings.get('proxy', {})
        
    def get_proxies(self):
        """获取代理设置"""
        if not self.proxy_settings.get('enabled', False):
            return None
            
        protocol = self.proxy_settings.get('protocol', 'http')
        ip = self.proxy_settings.get('ip', '')
        port = self.proxy_settings.get('port', '')
        username = self.proxy_settings.get('username', '')
        password = self.proxy_settings.get('password', '')
        
        if not all([ip, port]):
            return None
            
        # 构建代理URL
        if username and password:
            proxy_url = f"{protocol}://{username}:{password}@{ip}:{port}"
        else:
            proxy_url = f"{protocol}://{ip}:{port}"
            
        return {
            'http': proxy_url,
            'https': proxy_url
        }
        
    @abstractmethod
    def get_balances(self):
        pass
        
    @abstractmethod
    def withdraw(self, address, coin, amount, network, fee, min_interval, max_interval, fund_password=None):
        pass

class OKEClient(ExchangeClient):
    def __init__(self, api_settings):
        super().__init__(api_settings)
        self.base_url = 'https://www.okx.com'
        
    def _send_request(self, method, url, headers=None, data=None):
        """统一的请求发送方法"""
        try:
            if headers is None:
                headers = {}
            
            # 确保数据使用UTF-8编码
            if isinstance(data, dict):
                data = json.dumps(data, ensure_ascii=False).encode('utf-8')
            elif isinstance(data, str):
                data = data.encode('utf-8')
                
            headers.update({
                'Content-Type': 'application/json; charset=utf-8',
                'Accept': 'application/json',
                'Accept-Charset': 'utf-8'
            })
            
            proxies = self.get_proxies()
            response = requests.request(
                method,
                url,
                headers=headers,
                data=data,
                proxies=proxies
            )
            
            # 强制设置响应编码
            response.encoding = 'utf-8'
            return response
        except Exception as e:
            raise Exception(f"请求失败: {str(e)}")

    def get_balances(self):
        """查询账户余额"""
        try:
            timestamp = datetime.utcnow().isoformat(timespec='seconds') + 'Z'
            method = 'GET'
            request_path = '/api/v5/account/balance'
            
            # 生成签名
            message = timestamp + method + request_path
            mac = hmac.new(
                self.api_secret.encode('utf-8'),
                message.encode('utf-8'),
                digestmod='sha256'
            )
            sign = base64.b64encode(mac.digest()).decode('utf-8')
            
            headers = {
                'OK-ACCESS-KEY': self.api_key,
                'OK-ACCESS-SIGN': sign,
                'OK-ACCESS-TIMESTAMP': timestamp,
                'OK-ACCESS-PASSPHRASE': self.passphrase
            }
            
            url = self.base_url + request_path
            response = self._send_request('GET', url, headers=headers)
            return response.json()
        except Exception as e:
            raise Exception(f"获取余额失败: {str(e)}")

    def withdraw(self, address, coin, amount, network, fee, min_interval, max_interval, fund_password=None):
        """提币操作"""
        # 等待随机时间
        sleep_time = random.uniform(float(min_interval), float(max_interval))
        time.sleep(sleep_time)
        
        timestamp = datetime.utcnow().isoformat(timespec='seconds') + 'Z'
        method = 'POST'
        request_path = '/api/v5/asset/withdrawal'

        # 构建请求体
        body = {
            'ccy': coin.upper(),          # 币种需要大写
            'amt': str(amount),           # 数量
            'dest': '4',                  # 4=链上提币
            'toAddr': address.strip(),    # 提币地址
            'fee': str(fee),             # 提币手续费
            'chain': f"{coin.upper()}-{network}",  # 例如: 'ETH-Base'，需要特定格式
        }

        if fund_password:
            body['pwd'] = fund_password   # 资金密码，如果有的话

        # 序列化请求体
        serialized_body = json.dumps(body, separators=(',', ':'))

        # 生成签名
        message = timestamp + method + request_path + serialized_body
        mac = hmac.new(
            bytes(self.api_secret, encoding='utf8'),
            bytes(message, encoding='utf-8'),
            digestmod='sha256'
        )
        sign = base64.b64encode(mac.digest()).decode()

        # 设置请求头
        headers = {
            'OK-ACCESS-KEY': self.api_key,
            'OK-ACCESS-SIGN': sign,
            'OK-ACCESS-TIMESTAMP': timestamp,
            'OK-ACCESS-PASSPHRASE': self.passphrase,
            'Content-Type': 'application/json'
        }

        # 发送请求
        proxies = self.get_proxies()
        url = self.base_url + request_path
        response = requests.post(url, headers=headers, data=serialized_body, proxies=proxies)
        return response.json()

class BinanceClient(ExchangeClient):
    def __init__(self, api_settings):
        super().__init__(api_settings)
        self.base_url = 'https://api.binance.com'
        
    def get_balances(self):
        """查询币安账户余额"""
        # 获取服务器时间
        server_time_url = self.base_url + '/api/v3/time'
        response = requests.get(server_time_url)
        server_time = response.json()['serverTime']

        # 创建查询字符串
        query_string = 'timestamp=' + str(server_time)

        # 创建签名
        signature = hmac.new(
            bytes(self.api_secret, 'utf-8'),
            bytes(query_string, 'utf-8'),
            hashlib.sha256
        ).hexdigest()

        # 创建请求URL
        wallet_balance_url = f"{self.base_url}/sapi/v1/asset/wallet/balance?{query_string}&signature={signature}"

        # 设置请求头
        headers = {"X-MBX-APIKEY": self.api_key}

        # 发送请求
        proxies = self.get_proxies()
        response = requests.get(wallet_balance_url, headers=headers, proxies=proxies)

        # 检查响应状态
        if response.status_code != 200:
            raise Exception(f"API请求失败: {response.text}")

        # 获取结果
        balances = response.json()
        
        # 过滤零余额
        non_zero_balances = []
        # 直接遍历返回的数据，不假设具体的数据结构
        if isinstance(balances, list):
            # 如果返回的是列表
            for balance in balances:
                total = float(balance.get('free', 0)) + float(balance.get('locked', 0))
                if total > 0:
                    non_zero_balances.append({
                        'asset': balance.get('asset', ''),
                        'free': str(balance.get('free', '0')),
                        'locked': str(balance.get('locked', '0')),
                        'total': str(total)
                    })
        else:
            # 如果返回的是字典
            for asset, balance in balances.items():
                if isinstance(balance, dict):
                    total = float(balance.get('free', 0)) + float(balance.get('locked', 0))
                    if total > 0:
                        non_zero_balances.append({
                            'asset': asset,
                            'free': str(balance.get('free', '0')),
                            'locked': str(balance.get('locked', '0')),
                            'total': str(total)
                        })

        return {
            'wallet': non_zero_balances
        }

    def withdraw(self, address, coin, amount, network, fee, min_interval, max_interval, fund_password=None):
        """币安提币操作
        参数:
            address: 提币地址
            coin: 币种
            amount: 提币数量
            network: 网络
            fee: 手续费
            min_interval: 最小间隔时间
            max_interval: 最大间隔时间
            fund_password: 资金密码（币安不需要，但保持接口一致）
        """
        # 等待随机时间
        sleep_time = random.uniform(float(min_interval), float(max_interval))
        time.sleep(sleep_time)
        
        # 获取服务器时间
        server_time_url = self.base_url + '/api/v3/time'
        response = requests.get(server_time_url)
        server_time = response.json()['serverTime']

        # 创建查询字符串
        query_string = (
            f'coin={coin.upper()}'  # 币种转大写
            f'&network={network}'
            f'&address={address.strip()}'
            f'&amount={str(amount)}'  # 确保amount是字符串
            f'&timestamp={server_time}'
        )

        # 创建签名
        signature = hmac.new(
            bytes(self.api_secret, 'utf-8'),
            bytes(query_string, 'utf-8'),
            hashlib.sha256
        ).hexdigest()

        # 创建请求URL
        request_url = f"{self.base_url}/sapi/v1/capital/withdraw/apply?{query_string}&signature={signature}"

        try:
            # 发送请求
            proxies = self.get_proxies()
            headers = {"X-MBX-APIKEY": self.api_key}
            response = requests.post(request_url, headers=headers, proxies=proxies)
            
            # 检查响应状态
            if response.status_code != 200:
                return {
                    'success': False,
                    'message': f'提币请求失败: {response.text}'
                }
            
            result = response.json()
            
            # 返回标准化的结果
            return {
                'success': True,
                'id': result.get('id', ''),
                'message': '提币请求成功'
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'提币异常: {str(e)}'
            }

class GateClient(ExchangeClient):
    def __init__(self, api_settings):
        super().__init__(api_settings)
        self.host = "https://api.gateio.ws"
        self.prefix = "/api/v4"
        
    def gen_sign(self, method, url, query_string='', body=''):
        """生成Gate.io API签名"""
        t = time.time()
        m = hashlib.sha512()
        m.update((query_string + body).encode('utf-8'))
        hashed_payload = m.hexdigest()
        s = '%s\n%s\n%s\n%s\n%s' % (method, url, query_string, hashed_payload, t)
        sign = hmac.new(
            self.api_secret.encode('utf-8'),
            s.encode('utf-8'),
            hashlib.sha512
        ).hexdigest()
        return {
            'KEY': self.api_key,
            'Timestamp': str(t),
            'SIGN': sign
        }
        
    def get_balances(self):
        """查询Gate.io账户余额"""
        url = f"{self.prefix}/wallet/sub_account_balances"
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        # 生成签名并更新请求头
        sign_headers = self.gen_sign('GET', url)
        headers.update(sign_headers)
        
        # 发送请求
        proxies = self.get_proxies()
        response = requests.get(f"{self.host}{url}", headers=headers, proxies=proxies)
        
        if response.status_code != 200:
            raise Exception("API请求失败")
            
        return response.json()

    def withdraw(self, address, coin, amount, network, fee, min_interval, max_interval):
        """Gate.io提币操作"""
        # 等待随机时间
        sleep_time = random.uniform(float(min_interval), float(max_interval))
        time.sleep(sleep_time)
        
        url = f"{self.prefix}/withdrawals"
        
        # 构建请求体
        body = {
            'currency': coin,
            'amount': str(amount),
            'address': address.strip(),
            'chain': network,
            'fee': str(fee)
        }
        
        # 序列化请求体
        body_str = json.dumps(body)
        
        # 设置请求头
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        # 生成签名并更新请求头
        sign_headers = self.gen_sign('POST', url, body=body_str)
        headers.update(sign_headers)
        
        # 发送请求
        proxies = self.get_proxies()
        response = requests.post(
            f"{self.host}{url}",
            headers=headers,
            json=body,
            proxies=proxies
        )
        
        if response.status_code != 200:
            raise Exception(f"提币请求失败: {response.text}")
            
        result = response.json()
        
        # 检查提币结果
        if 'id' in result:
            return {
                'success': True,
                'withdrawal_id': result['id'],
                'message': '提币请求成功'
            }
        else:
            return {
                'success': False,
                'message': f'提币失败: {result.get("message", "未知错误")}'
            }

    def process_address(self, address):
        try:
            # 确保地址字符串使用UTF-8编码
            if isinstance(address, str):
                address = address.encode('utf-8').decode('utf-8')
            return address
        except Exception as e:
            raise Exception(f"地址处理错误: {str(e)}")

    def _send_request(self, method, url, headers=None, data=None):
        """统一的请求发送方法"""
        try:
            if headers is None:
                headers = {}
            
            # 确保数据使用UTF-8编码
            if isinstance(data, dict):
                data = json.dumps(data, ensure_ascii=False).encode('utf-8')
            elif isinstance(data, str):
                data = data.encode('utf-8')
                
            headers.update({
                'Content-Type': 'application/json; charset=utf-8',
                'Accept': 'application/json',
                'Accept-Charset': 'utf-8'
            })
            
            proxies = self.get_proxies()
            response = requests.request(
                method,
                url,
                headers=headers,
                data=data,
                proxies=proxies
            )
            
            # 强制设置响应编码
            response.encoding = 'utf-8'
            return response
        except Exception as e:
            raise Exception(f"请求失败: {str(e)}")