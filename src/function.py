import qimao_normal as qn
import qimao_batch as qb
import qimao_chapter as qc
import qimao_update as qu
import qimao_epub as qe
import public as p
import os
import re
import time
import requests
from requests.exceptions import Timeout
import platform
from sys import exit
from packaging import version
from colorama import Fore, Style, init

init(autoreset=True)

# 定义全局变量
mode = None
page_url = None
txt_encoding = None
type_path_num = None
return_info = None
user_folder = os.path.expanduser("~")
data_path = os.path.join(user_folder, "qimao_data")
eula_path = os.path.join(data_path, "eula.txt")
config_path = os.path.join(data_path, "config.json")
eula_url = "https://gitee.com/xingyv1024/7mao-novel-downloader/raw/main/EULA.md"
license_url = "https://gitee.com/xingyv1024/7mao-novel-downloader/raw/main/LICENSE.md"
license_url_zh = "https://gitee.com/xingyv1024/7mao-novel-downloader/raw/main/LICENSE-ZH.md"
os.makedirs(data_path, exist_ok=True)
book_id = None
start_chapter_id = "0"


# 用户须知
def print_usage():
    print("欢迎使用", end=" ")
    print(Fore.YELLOW + Style.BRIGHT + "七猫小说下载工具")
    print("""用户须知：
此程序开源免费，如果您付费获取，请您立即举报商家。
本程序灵感及api来自于ibxff所作用户脚本，详情请到更多中查看；；
此程序使用GPLv3开源许可证发布。

使用本程序代表您已阅读并同意本程序最终用户许可协议(EULA)（初次启动时已展示，可在更多中再次阅读）。
（包括不得销售此程序副本，提供代下载服务需明确告知用户开源地址等）

QQ： 外1群：149050832  外2群：667146297
如果想要指定开始下载的章节，请在输入目录页链接时按Ctrl+C。

免责声明：
该程序仅用于学习和研究Python网络爬虫和网页处理技术，不得用于任何非法活动或侵犯他人权益的行为。
使用本程序所产生的一切法律责任和风险，均由用户自行承担，与作者和项目协作者、贡献者无关。
作者不对因使用该程序而导致的任何损失或损害承担任何责任。
""")


# 请用户同意协议并选择模式
def start():
    global mode  # 声明mode为全局变量
    global return_info

    while True:
        # 定义变量flag控制是否退出程序
        flag = True
        flag2 = True
        print_usage()
        print("请选择以下操作：")
        print("1. 进入正常模式")
        print("2. 进入自动批量模式")
        print("3. 进入分章保存模式")
        print("5. 进入Epub电子书模式")
        print("6. 查看更多")
        print("7. 更新已下载的小说(已支持epub)")
        print("8. 查看贡献（赞助）者名单")
        print("9. 退出程序")
        print("10. 撤回同意/重置默认路径")
        choice = input("请输入您的选择（1~10）:（默认“1”）\n")

        # 通过用户选择，决定模式，给mode赋值
        if not choice:
            choice = '1'

        if choice == '1':
            mode = 0
            clear_screen()
            print("您已进入正常下载模式：")
            break
        elif choice == '2':
            mode = 2
            clear_screen()
            print("您已进入自动批量下载模式:")
            break
        elif choice == '3':
            mode = 3
            clear_screen()
            print("您已进入分章保存模式:")
            break
        elif choice == '5':
            mode = 4
            clear_screen()
            print("您已进入EPUB模式，将输出epub电子书文件。\n")
            # print("EPUB模式正在开发中，敬请期待\n")
            break
        elif choice == '6':
            clear_screen()
            print("""作者：星隅（xing-yv）
版权所有（C）2023 星隅（xing-yv）

本软件根据GNU通用公共许可证第三版（GPLv3）发布；
你可以在以下位置找到该许可证的副本：
https://www.gnu.org/licenses/gpl-3.0.html

根据GPLv3的规定，您有权在遵循许可证的前提下自由使用、修改和分发本软件。
请注意，根据许可证的要求，任何对本软件的修改和分发都必须包括原始的版权声明和GPLv3的完整文本。

本软件提供的是按"原样"提供的，没有任何明示或暗示的保证，包括但不限于适销性和特定用途的适用性。作者不对任何直接或间接损害或其他责任承担任何责任。在适用法律允许的最大范围内，作者明确放弃了所有明示或暗示的担保和条件。

免责声明：
该程序仅用于学习和研究Python网络爬虫和网页处理技术，不得用于任何非法活动或侵犯他人权益的行为。使用本程序所产生的一切法律责任和风险，均由用户自行承担，与作者和项目贡献者无关。作者不对因使用该程序而导致的任何损失或损害承担任何责任。

请在使用本程序之前确保遵守相关法律法规和网站的使用政策，如有疑问，请咨询法律顾问。

ibxff所作用户脚本:https://greasyfork.org/zh-CN/scripts/479460
开源仓库地址:https://github.com/xing-yv/7mao-novel-downloader
gitee地址:https://gitee.com/xingyv1024/7mao-novel-downloader
作者B站主页:https://space.bilibili.com/1920711824
提出反馈:https://github.com/xing-yv/7mao-novel-downloader/issues/new
(请在右侧Label处选择issue类型以得到更快回复)

最终用户许可协议(EULA)：https://gitee.com/xingyv1024/fanqie-novel-download/blob/main/EULA.md
""")
            input("按Enter键返回...")
            clear_screen()
        elif choice == '7':
            clear_screen()
            print("您已进入更新模式")
            # 调用7猫更新函数
            return_info = qu.qimao_update(data_path)
            return
        elif choice == '8':
            clear_screen()
            contributors_url = 'https://gitee.com/xingyv1024/7mao-novel-downloader/raw/main/CONTRIBUTORS.md'
            try:
                contributors = requests.get(contributors_url, timeout=5, proxies=p.proxies)

                # 检查响应状态码
                if contributors.status_code == 200:
                    contributor_md_content = contributors.text
                    print(contributor_md_content)
                else:
                    print(f"获取贡献名单失败，HTTP响应代码: {contributors.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"发生错误: {e}")
            input("按Enter键返回...")
            clear_screen()
        elif choice == '9':
            clear_screen()
            # 确认退出
            while True:
                sure = input("您确定要退出程序吗(yes/no)(默认:no): ")
                if not sure:
                    sure = "no"
                if sure.lower() == "yes":
                    input("按Enter退出程序...")
                    break
                elif sure.lower() == "no":
                    flag = False
                    break
                else:
                    print("输入无效，请重新输入。")
            if flag is True:
                exit(0)
            else:
                clear_screen()
                continue
        elif choice == '10':
            clear_screen()
            cho = input("1-> 撤回同意  2-> 重置默认路径\n")
            if cho == '1':
                while True:
                    sure = input("您确定要撤回同意吗(yes/no)(默认:no): ")
                    if not sure:
                        sure = "no"
                    if sure.lower() == "yes":
                        break
                    elif sure.lower() == "no":
                        flag2 = False
                        break
                    else:
                        print("输入无效，请重新输入。")
                if flag2 is False:
                    clear_screen()
                    continue
                else:
                    with open(eula_path, "w", encoding="utf-8") as f:
                        eula_txt = f"""eula_url: {eula_url}
license_url: {license_url}
agreed: 
no
eula_date: 
None

"""
                        f.write(eula_txt)
                    print("您已撤回同意")
                    input("按Enter键退出程序...")
                    exit(0)
            elif cho == '2':
                os.remove(config_path)
                print("已重置默认路径")
                input("按Enter键退出程序...")
                exit(0)
            else:
                print("输入无效")
                input("按Enter键退出程序...")
                exit(0)
        else:
            print("无效的选择，请重新输入。")
    get_parameter(retry=False)


def get_parameter(retry):
    global page_url
    global txt_encoding
    global type_path_num
    global book_id
    global start_chapter_id
    global mode

    page_url = None
    # 判断是否是批量下载模式
    if mode == 2:
        if not os.path.exists('urls.txt'):
            with open('urls.txt', 'x') as _:
                pass
        if retry is True:
            print("您在urls.txt中输入的内容有误，请重新输入")
            print("请重新在程序同文件夹(或执行目录)下的urls.txt中，以每行一个的形式写入链接/ID")
        elif retry is False:
            print("请在程序同文件夹(或执行目录)下的urls.txt中，以每行一个的形式写入链接/ID")
            try:
                os.startfile('urls.txt')
                print("您正在使用Windows，文件应该已自动弹出窗口")
            except AttributeError:
                print("您正在使用非Windows系统，请手动打开文件")
        input("完成后请按Enter键继续:")
    else:
        # 不是则让用户输入小说目录页的链接
        while True:
            try:
                page_url = input("请输入链接/ID，或输入s以进入搜索模式：\n")

                # 检查 url 类型
                if page_url.isdigit():
                    book_id = page_url
                    page_url = "https://www.qimao.com/shuku/" + book_id + "/"
                    break

                elif "www.qimao.com/shuku/" in page_url:
                    book_id = re.search(r"www.qimao.com/shuku/(\d+)", page_url).group(1)
                    page_url = "https://www.qimao.com/shuku/" + book_id + "/"
                    break  # 如果是正确的链接，则退出循环

                elif "app-share.wtzw.com" in page_url:
                    book_id = re.search(r"article-detail/(\d+)", page_url).group(1)
                    page_url = "https://www.qimao.com/shuku/" + book_id + "/"
                    break
                elif page_url.lower() == 's':
                    print("正在进入搜索模式...")
                    book_id = search()
                    if book_id is None:
                        print(Fore.YELLOW + Style.BRIGHT + "\n您取消了搜索，请重新输入。")
                        continue
                    page_url = "https://www.qimao.com/shuku/" + book_id + "/"
                    break
                else:
                    print(Fore.YELLOW + Style.BRIGHT + "无法识别的内容，请重新输入。")
            except AttributeError:
                print(Fore.YELLOW + Style.BRIGHT + "链接无法识别，请检查并重新输入。")
                continue
            # 当用户按下Ctrl+C是，可以自定义起始章节id
            except KeyboardInterrupt:
                while True:
                    if mode == 4:
                        input("epub模式不支持指定开始章节id，请按Enter继续，或按Ctrl+C退出程序...")
                        break
                    start_chapter_id = input("您已按下Ctrl+C，请输入起始章节的id(输入help以查看帮助):\n")
                    if start_chapter_id == 'help':
                        print(
                            "\n打开小说章节阅读界面，上方链接中第二串的数字即为章节id\n请输入您想要开始下载的章节的id\n")
                        continue
                    elif start_chapter_id.isdigit():
                        break
                    else:
                        print("无效的输入，请重新输入")

    # 让用户选择保存文件的编码
    while True:
        if mode == 4:
            break
        txt_encoding_num = input("请输入保存文件所使用的编码(默认:1)：1 -> utf-8 | 2 -> gb2312 | 3-> 搜索编码\n")

        if not txt_encoding_num:
            txt_encoding_num = '1'

        # 检查用户选择文件编码是否正确
        if txt_encoding_num == '1':
            txt_encoding = 'utf-8'
            break
        elif txt_encoding_num == '2':
            txt_encoding = 'gb2312'
            break
        elif txt_encoding_num == '3':
            txt_encoding = get_more_encoding()
            break
        else:
            print("输入无效，请重新输入。")

    if mode != 4:
        print(f"你选择的保存编码是：{txt_encoding}")

    type_path_num = None

    # 询问用户是否自定义保存路径
    while True:

        type_path = input("是否自行选择保存路径(yes/no)(默认:no):")

        if not type_path:
            type_path = "no"

        if type_path.lower() == "yes":
            type_path_num = 1
            if mode == 2:
                print("您选择了自定义保存文件夹，请在文件检查后选择保存文件夹。")
            else:
                print("您选择了自定义保存路径，请在获取完成后选择保存路径。")
            break

        elif type_path.lower() == "no":
            type_path_num = 0
            if mode == 2 or mode == 3:
                print("您未选择自定义保存路径，请在获取完成后到默认路径下output文件夹寻找文件。")
                print("(初始默认路径为程序所在文件夹，命令行为执行目录)")
            else:
                print("您未选择自定义保存路径，请在获取完成后到默认路径下寻找文件。")
                print("(初始默认路径为程序所在文件夹，命令行为执行目录)")
            break

        else:
            print("输入无效，请重新输入。")
            continue
    perform_user_mode_action()


def get_more_encoding():
    encodings = [
        "utf-8", "ascii", "latin-1", "iso-8859-1", "utf-16",
        "utf-16-le", "utf-16-be", "utf-32", "utf-32-le", "utf-32-be",
        "cp1252", "cp437", "cp850", "cp866", "cp932",
        "cp949", "cp950", "koi8-r", "koi8-u", "macroman",
        "macintosh", "gb2312", "gbk", "gb18030", "big5",
        "big5hkscs", "shift_jis", "euc_jp", "euc_kr", "iso2022_jp",
        "iso2022_jp_1", "iso2022_jp_2", "iso2022_jp_2004", "iso2022_jp_3", "iso2022_jp_ext",
        "shift_jis_2004", "shift_jisx0213", "euc_jis_2004", "euc_jisx0213", "latin_1",
        "iso8859_2", "iso8859_3", "iso8859_4", "iso8859_5", "iso8859_6",
        "iso8859_7", "iso8859_8", "iso8859_9", "iso8859_10", "iso8859_13",
        "iso8859_14", "iso8859_15", "iso8859_16", "cp500", "cp720",
        "cp737", "cp775", "cp852", "cp855", "cp857",
        "cp858", "cp860", "cp861", "cp862", "cp863",
        "cp864", "cp865", "cp869", "cp874", "cp875",
        "cp1006", "cp1026", "cp1140", "cp1250", "cp1251",
        "cp1253", "cp1254", "cp1255", "cp1256", "cp1257",
        "cp1258", "cp65001", "hz", "iso2022_jp_2004", "iso2022_kr",
        "iso8859_11", "iso8859_16", "johab", "ptcp154", "utf_7",
        "utf_8_sig"
    ]

    while True:
        query = input("请输入你想要搜索的编码：")
        query = query.lower()
        import difflib
        # 使用difflib库的get_close_matches方法找到相似的编码
        similar_encodings = difflib.get_close_matches(query, encodings)

        print("以下是与你的搜索内容相似的编码：")
        for i, encoding in enumerate(similar_encodings):
            print(f"{i + 1}. {encoding}")

        while True:
            choice_ = input("请选择一个编码, 输入r以重新搜索：")
            if choice_ == "r":
                clear_screen()
                break
            elif choice_.isdigit():
                choice = int(choice_)
                if choice > len(similar_encodings):
                    print("输入无效，请重新输入。")
                    continue
                chosen_encoding = similar_encodings[choice - 1]
                print(f"你选择的编码是：{chosen_encoding}")
                return chosen_encoding
            else:
                print("输入无效，请重新输入。")
                continue


def perform_user_mode_action():
    global return_info
    # 判断用户处于什么模式
    if mode == 0:
        # 调用7猫正常模式函数
        return_info = qn.qimao_n(page_url, txt_encoding, type_path_num, data_path, start_chapter_id,
                                 config_path)
    elif mode == 2:
        # 调用7猫批量模式函数
        return_info = qb.qimao_b(txt_encoding, type_path_num, data_path,
                                 config_path)
    elif mode == 3:
        # 调用7猫分章模式函数
        return_info = qc.qimao_c(page_url, txt_encoding, type_path_num, start_chapter_id,
                                 config_path)
    elif mode == 4:
        # 调用7猫epub电子书模式函数
        return_info = qe.qimao_epub(page_url, type_path_num,
                                    config_path)


# 检查更新
def check_update(now_version):
    owner = "xingyv1024"
    repo = "7mao-novel-downloader"
    api_url = f"https://gitee.com/api/v5/repos/{owner}/{repo}/releases/latest"

    print("正在检查更新...")
    print(f"当前版本: {now_version}")

    if 'dev' in now_version or 'alpha' in now_version or 'beta' in now_version:
        print(Fore.YELLOW + Style.BRIGHT + '测试版本，检查更新已关闭！')
        print(Fore.YELLOW + Style.BRIGHT + '注意！您正在使用测试/预览版本！\n该版本可能极不稳定，不建议在生产环境中使用！')
        input('按Enter键继续...')
        return

    # noinspection PyBroadException
    try:
        # 发送GET请求以获取最新的发行版信息
        response = requests.get(api_url, timeout=5, proxies=p.proxies)

        if response.status_code != 200:
            print(f"请求失败，状态码：{response.status_code}")
            input("按Enter键继续...\n")
            return 0
        release_info = response.json()
        if "tag_name" in release_info:
            latest_version = release_info["tag_name"]
            release_describe = release_info["body"]
            print(f"最新的发行版是：{latest_version}")
            result = compare_versions(now_version, latest_version)
            if result == -1:
                # 检测是否是重要更新
                if "!important!" in release_describe:
                    # 如果是，则弹窗提示
                    import tkinter as tk
                    from tkinter import messagebox
                    root = tk.Tk()

                    # 点击确认跳转到下载页面
                    def open_url():
                        import webbrowser
                        webbrowser.open("https://gitee.com/xingyv1024/7mao-novel-downloader/releases/latest")
                        exit(0)

                    root.withdraw()
                    result = messagebox.askokcancel("重要更新",
                                                    f"检测到重要更新！\n更新内容:\n{release_describe}\n点击确定前往下载",
                                                    icon="warning")
                    if result:
                        open_url()
                    root.destroy()
                    return
                elif "!very important!" in release_describe:
                    # 如果是，则弹窗提示
                    import tkinter as tk
                    from tkinter import messagebox
                    root = tk.Tk()

                    # 点击确认跳转到下载页面
                    def open_url():
                        import webbrowser
                        webbrowser.open("https://gitee.com/xingyv1024/7mao-novel-downloader/releases/latest")
                        exit(0)

                    root.withdraw()
                    # 此更新不可取消
                    messagebox.showinfo("非常重要更新",
                                        f"检测到非常重要更新！\n更新内容:\n{release_describe}\n点击确定前往下载")
                    open_url()
                    root.destroy()
                    exit(0)
                elif "|notification|" in release_describe:
                    print(f"检测到通知：\n{release_describe}")
                    input("按Enter键继续...\n")
                    return
                print(
                    "检测到新版本\n更新可用！请到 https://gitee.com/xingyv1024/7mao-novel-downloader/releases/latest 下载最新版")
                print(f"更新内容:\n{release_describe}")
                input("按Enter键继续...\n")
            else:
                print("您正在使用最新版")

        else:
            print("未获取到发行版信息。")
            input("按Enter键继续...\n")

    except BaseException:
        print(":(  检查更新失败...")
        input("按Enter键继续...\n")


def compare_versions(version1, version2):
    # 使用packaging模块进行版本比较
    v1 = version.parse(version1)
    v2 = version.parse(version2)

    if v1 < v2:
        return -1
    elif v1 > v2:
        return 1
    else:
        return 0


def clear_screen():
    # 根据系统类型执行不同的清屏指令
    os.system('cls') if platform.system() == 'Windows' else os.system('clear')


def check_eula():
    if os.path.exists(eula_path):
        with open(eula_path, "r", encoding="utf-8") as f:
            eula_txt = f.read()
        agreed = eula_txt.splitlines()[3]
        if agreed != "yes":
            agree_eula()
            return True
        eula_date_old = eula_txt.splitlines()[5]
        # noinspection PyBroadException
        try:
            eula_text = requests.get(eula_url, timeout=10, proxies=p.proxies).text
        except Exception:
            print("获取最终用户许可协议失败，请检查网络连接")
            input("按Enter键继续...\n")
            exit(0)
        eula_date_new = eula_text.splitlines()[3]
        if eula_date_old != eula_date_new:
            while True:
                print(Fore.YELLOW + Style.BRIGHT + "最终用户许可协议（EULA）已更新")
                print(Fore.YELLOW + Style.BRIGHT + "在继续使用之前，请阅读并同意以下协议：")
                print("1. 最终用户许可协议（EULA）")
                print("输入序号以查看对应协议，输入yes表示同意，输入no以退出程序。")
                print("您可以随时在程序内撤回同意")
                input_num = input("请输入：")
                if input_num == "1":
                    clear_screen()
                    print(eula_text)
                    input("按Enter键继续...")
                    clear_screen()
                elif input_num == "yes":
                    with open(eula_path, "w", encoding="utf-8") as f:
                        eula_txt = f"""eula_url: {eula_url}
license_url: {license_url}
agreed: 
yes
eula_date: 
{eula_date_new}

"""
                        f.write(eula_txt)
                    break
                elif input_num == "no":
                    print("感谢您的使用！")
                    exit(0)
                else:
                    clear_screen()
                    print("输入无效，请重新输入。")
    else:
        agree_eula()
        return True
    return True


def agree_eula():
    # noinspection PyBroadException
    try:
        eula_text = requests.get(eula_url, timeout=10, proxies=p.proxies).text
        license_text = requests.get(license_url, timeout=10, proxies=p.proxies).text
        license_text_zh = requests.get(license_url_zh, timeout=10, proxies=p.proxies).text
    except Exception:
        print("获取最终用户许可协议失败，请检查网络连接")
        input("按Enter键继续...\n")
        exit(0)
    eula_date = eula_text.splitlines()[3]
    while True:
        print(Fore.YELLOW + Style.BRIGHT + "在继续使用之前，请阅读并同意以下协议：")
        print("1. 最终用户许可协议（EULA）")
        print("2. GPLv3开源许可证 (3. 中文译本（无法律效力）)")
        print("输入序号以查看对应协议，输入yes表示同意，输入no以退出程序。")
        print("您可以随时在程序内撤回同意")
        input_num = input("请输入：")
        if input_num == "1":
            clear_screen()
            print(eula_text)
            input("按Enter键继续...")
            clear_screen()
        elif input_num == "2":
            clear_screen()
            print(license_text)
            input("按Enter键继续...")
            clear_screen()
        elif input_num == "3":
            clear_screen()
            print(license_text_zh)
            input("按Enter键继续...")
            clear_screen()
        elif input_num == "yes":
            with open(eula_path, "w", encoding="utf-8") as f:
                eula_txt = f"""eula_url: {eula_url}
license_url: {license_url}
agreed: 
yes
eula_date: 
{eula_date}

"""
                f.write(eula_txt)
            break
        elif input_num == "no":
            print("感谢您的使用！")
            exit(0)
        else:
            clear_screen()
            print("输入无效，请重新输入。")


def search():
    try:

        while True:

            key = input("请输入搜索关键词（按下Ctrl+C返回）：")

            # 获取搜索结果列表
            params_ = {
                'extend': '',
                'tab': '0',
                'gender': '0',
                'refresh_state': '8',
                'page': '1',
                'wd': f'{key}',
                'is_short_story_user': '0'
            }
            response = requests.get("https://api-bc.wtzw.com/search/v1/words", params=p.sign_url_params(params_),
                                    headers=p.get_headers("00000000"), timeout=10).json()
            books = response['data']['books']

            for i, book in enumerate(books):
                try:
                    print(f"{i + 1}. 名称：{book['original_title']} 作者：{book['original_author']} "
                          f"ID：{book['id']} 字数：{book['words_num']}")
                except KeyError:
                    break

            while True:
                choice_ = input("请选择一个结果, 输入r以重新搜索：")
                if choice_ == "r":
                    clear_screen()
                    break
                elif choice_.isdigit():
                    choice = int(choice_)
                    if choice > len(books):
                        print("输入无效，请重新输入。")
                        continue
                    chosen_book = books[choice - 1]
                    return chosen_book['id']
                else:
                    print("输入无效，请重新输入。")
                    continue
    except KeyboardInterrupt:
        return
    except Timeout:
        print("请求超时，请检查网络连接")
        return
    # except Exception as e:
    #     print(f"发生错误: {e}")
    #     return


def clear_stdin():
    try:
        import msvcrt
        while msvcrt.kbhit():
            msvcrt.getch()
    except ImportError:
        import sys
        import termios
        termios.tcflush(sys.stdin, termios.TCIOFLUSH)


sock = None


def check_instance():
    global sock
    # 通过端口检查是否有其他实例正在运行
    import socket

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(('localhost', 52511))
    except socket.error:
        print("另一个程序进程已经在运行中，请勿重复运行")
        print("将在5秒后退出程序")
        for i in range(5, 0, -1):
            print(f"{i}")
            time.sleep(1)
        exit(1)


def clear_old():
    # 清除旧版本pyppeteer残留
    if platform.system() == "Windows":
        if os.path.exists(os.path.join(user_folder, "AppData", "Local", "pyppeteer")):
            import shutil
            shutil.rmtree(os.path.join(user_folder, "AppData", "Local", "pyppeteer"))
            print("已自动为您清除旧版本pyppeteer残留")
    else:
        if os.path.exists(os.path.join(user_folder, ".pyppeteer")):
            import shutil
            shutil.rmtree(os.path.join(user_folder, ".pyppeteer"))
            print("已自动为您清除旧版本pyppeteer残留")
