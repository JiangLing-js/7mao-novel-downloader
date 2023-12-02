"""
作者：星隅（xing-yv）

版权所有（C）2023 星隅（xing-yv）

本软件根据GNU通用公共许可证第三版（GPLv3）发布；
你可以在以下位置找到该许可证的副本：
https://www.gnu.org/licenses/gpl-3.0.html

根据GPLv3的规定，您有权在遵循许可证的前提下自由使用、修改和分发本软件。
请注意，根据许可证的要求，任何对本软件的修改和分发都必须包括原始的版权声明和GPLv3的完整文本。

本软件提供的是按"原样"提供的，没有任何明示或暗示的保证，包括但不限于适销性和特定用途的适用性。作者不对任何直接或间接损害或其他责任承担任何责任。在适用法律允许的最大范围内，作者明确放弃了所有明示或暗示的担保和条件。

免责声明：
该程序仅用于学习和研究Python网络爬虫和网页处理技术，不得用于任何非法活动或侵犯他人权益的行为。使用本程序所产生的一切法律责任和风险，均由用户自行承担，与作者和项目协作者、贡献者无关。作者不对因使用该程序而导致的任何损失或损害承担任何责任。

请在使用本程序之前确保遵守相关法律法规和网站的使用政策，如有疑问，请咨询法律顾问。

无论您对程序进行了任何操作，请始终保留此信息。
"""

import re
import os
import socket
import multiprocessing
import queue
import threading
from multiprocessing import Process, Manager
import time
import qimao_api as fa
# noinspection PyPackageRequirements
from flask import Flask, request, jsonify, make_response, send_from_directory
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import datetime, timedelta
# 如果需要限制访问的时间段，请取消下一行的注释
# from functools import wraps

# 重定向HTTP请求到HTTPS使用：
# # noinspection PyPackageRequirements
# from flask import redirect


app = Flask(__name__)
CORS(app)
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]
)

# 存储被限制的IP和他们的限制解除时间
blacklist = {}

# 如果你要限制访问的时间段，可以使用下面的装饰器，将它添加到需要限制的路由上，然后将下面的注释取消掉
# 注意！该装饰器将使用服务器的本地时区时间，而不是你所在的时区的时间！
# def only_on_time_range(start_hour, end_hour):
#     def decorator(f):
#         @wraps(f)
#         def decorated_function(*args, **kwargs):
#             now = datetime.now().time()
#             if not (start_hour <= now.hour < end_hour):
#                 return f"此服务只在{start_hour}点到{end_hour}点开放。", 503
#             return f(*args, **kwargs)
#         return decorated_function
#     return decorator


@app.before_request
def block_method():
    if request.method == 'POST':
        ip = get_remote_address()
        # 检查IP是否在黑名单中
        if ip in blacklist:
            # 检查限制是否已经解除
            if datetime.now() < blacklist[ip]:
                response = make_response("Too many requests. You have been added to the blacklist for 1 hour.", 429)
                # 计算剩余的封禁时间（以秒为单位），并添加到'Retry-After'头部
                retry_after = int((blacklist[ip] - datetime.now()).total_seconds())
                response.headers['Retry-After'] = str(retry_after)
                return response
            else:
                # 如果限制已经解除，那么从黑名单中移除这个IP
                del blacklist[ip]
        # 如果你需要将HTTP请求重定向到HTTPS，请取消下方代码的注释
        # if not request.is_secure:
        #     # noinspection HttpUrlsUsage
        #     url = request.url.replace('http://', 'https://', 1)
        #     code = 301
        #     return redirect(url, code=code)


@app.errorhandler(429)
def ratelimit_handler(_e):
    # 将触发限制的IP添加到黑名单中，限制解除时间为1小时后
    blacklist[get_remote_address()] = datetime.now() + timedelta(hours=1)
    response = make_response("Too many requests. You have been added to the blacklist for 1 hour.", 429)
    response.headers['Retry-After'] = str(3600)  # 1小时的秒数
    return response


# 定义爬虫类
class Spider:
    def __init__(self):
        # 初始化URL队列
        self.url_queue = queue.Queue()
        # 设置运行状态为True
        self.is_running = True
        # 初始化任务状态字典
        self.task_status = {}

    @staticmethod
    def crawl(url):
        try:
            print(f"Crawling for URL: {url}")
            with Manager() as manager:
                return_dict = manager.dict()
                # 创建一个新的进程来运行爬虫函数
                p = Process(target=fa.qimao_l, args=(url, 'utf-8', return_dict))
                p.start()
                p.join()  # 等待进程结束
                if 'error' in return_dict:
                    print(f"Error: {return_dict['error']}")
                    return False
                else:
                    return True
        except Exception as e:
            print(f"Error: {e}")
            return False

    def worker(self):
        # 当运行状态为True时，持续工作
        while self.is_running:
            try:
                # 从URL队列中获取URL
                url = self.url_queue.get(timeout=1)
                self.task_status[url] = "进行中"
                # 调用爬虫函数爬取URL，如果出错则标记为失败并跳过这个任务进行下一个
                if Spider.crawl(url):
                    self.task_status[url] = "已完成"
                else:
                    self.task_status[url] = "失败"
                # 完成任务后，标记任务为完成状态
                self.url_queue.task_done()
            except queue.Empty:
                time.sleep(5)
                continue

    def start(self):
        # 启动工作线程
        threading.Thread(target=self.worker, daemon=True).start()

    def add_url(self, url):
        # 检查URL格式是否正确，如果不正确则返回错误信息，否则将URL添加到队列中并返回成功信息
        if "/shuku/" not in url:
            print(f"{url} URL格式不正确，内部错误")
            return "URL格式不正确，内部错误", 500
        else:
            if url not in self.task_status or self.task_status[url] == "失败":
                self.url_queue.put(url)
                self.task_status[url] = "等待中"
                return "此书籍已添加到下载队列"
            else:
                return "此书籍已存在"

    def stop(self):
        # 设置运行状态为False以停止工作线程
        self.is_running = False


# 创建爬虫实例并启动
spider = Spider()
spider.start()


@app.route('/api', methods=['POST'])
@limiter.limit("15/minute;200/hour;300/day")  # 限制请求
# 如果需要限制访问的时间段，请取消下一行的注释，并将时间段替换为你的时间段
# 注意！该装饰器将使用服务器的本地时区时间，而不是你所在的时区的时间！
# @only_on_time_range(8, 22)
def api():
    # 获取请求数据
    data = request.get_json()
    # 检查请求数据是否包含'action'和'id'字段，如果没有则返回418错误
    if 'action' not in data or 'id' not in data:
        return "Bad Request.The request is missing necessary json data.", 400
    if data['id'].isdigit():
        pass
    else:
        if '_0' in data['id']:
            return "暂不支持此书籍（书籍ID中含有“_0”），请等待该书籍后续更新。"
        if 'www.qimao.com/shuku' in data['id']:
            # noinspection PyBroadException
            try:
                data['id'] = re.search(r"shuku/(\d+)", data['id']).group(1)
            except Exception:
                return "你输入的不是书籍ID或正确的链接。", 400
        elif 'app-share.wtzw.com' in data['id']:
            # noinspection PyBroadException
            try:
                data['id'] = re.search(r"article-detail/(\d+)", data['id']).group(1)
            except Exception:
                return "你输入的不是书籍ID或正确的链接。", 400
        else:
            return "你输入的不是书籍ID或正确的链接。", 400

    # 如果'action'字段的值为'add'，则尝试将URL添加到队列中，并返回相应的信息和位置
    if data['action'] == 'add':
        url = 'https://www.qimao.com/shuku/' + data['id'] + '/'
        message = spider.add_url(url)
        position = list(spider.url_queue.queue).index(url) + 1 if url in list(spider.url_queue.queue) else None
        status = spider.task_status.get(url, None)
        return jsonify({'message': message, 'position': position, 'status': status})

    # 如果'action'字段的值为'query'，则检查URL是否在队列中，并返回相应的信息和位置或不存在的信息
    elif data['action'] == 'query':
        url = 'https://www.qimao.com/shuku/' + data['id'] + '/'
        position = list(spider.url_queue.queue).index(url) + 1 if url in list(spider.url_queue.queue) else None
        status = spider.task_status.get(url, None)
        return jsonify({'exists': status is not None, 'position': position, 'status': status})

    else:
        return "Bad Request.The value of ‘action’ can only be ‘add’ or ‘query’.", 400


@app.route('/list')
@limiter.limit("20/minute;200/hour;500/day")
def file_list():
    folder_path = 'qimao_output'  # 替换为你的文件夹路径
    files = os.listdir(folder_path)
    # 按最后修改时间排序
    files.sort(key=lambda x: os.path.getmtime(os.path.join(folder_path, x)), reverse=True)
    file_links = ['<a href="/download/{}">{}</a>'.format(f, f) for f in files]
    return '<html><body>{}</body></html>'.format('<br>'.join(file_links))


@app.route('/download/<path:filename>')
@limiter.limit("10/minute;100/hour;300/day")
def download_file(filename):
    directory = os.path.abspath('qimao_output')
    return send_from_directory(directory, filename, as_attachment=True)  # 替换为你的文件夹路径


# 检测是否支持IPv6
def is_ipv6_supported():
    # noinspection PyBroadException
    try:
        socket.socket(socket.AF_INET6)
        return True
    except Exception:
        return False


if __name__ == "__main__":
    multiprocessing.freeze_support()
    # 如果支持IPv6，则同时监听IPv4和IPv6
    if is_ipv6_supported():
        print("Your system supports IPv6, so both IPv4 and IPv6 are listened.")
        app.run(host='::', port=5001, threaded=True)
        # 如果需要启用HTTPS，请取消下一行的注释，并将证书和密钥的路径替换为你的证书和密钥的路径
        # app.run(host='::', port=5001, threaded=True, ssl_context=('path/xxxx.pem', 'path/xxxx.key'))
    else:
        print("Your system does not support IPv6, so only IPv4 is listened.")
        # 否则只监听IPv4
        app.run(host='0.0.0.0', port=5001)
        # 如果需要启用HTTPS，请取消下一行的注释，并将证书和密钥的路径替换为你的证书和密钥的路径
        # app.run(host='0.0.0.0', port=5001, ssl_context=('path/xxxx.pem', 'path/xxxx.key'))
