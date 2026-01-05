import re
import random
import string
from playwright.sync_api import Playwright, sync_playwright

def generate_random_phone():
    """生成随机的中国大陆手机号"""
    prefixes = ["134", "135", "136", "137", "138", "139", "150", "151", "152", "182", "187", "188"]
    return random.choice(prefixes) + "".join(random.choices(string.digits, k=8))

def generate_random_name(prefix="User_"):
    """生成带前缀的随机昵称"""
    suffix = "".join(random.choices(string.ascii_letters + string.digits, k=4))
    return f"{prefix}{suffix}"

def run(playwright: Playwright) -> None:
    # 启动浏览器
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    # 1. 登录流程
    page.goto("http://192.168.142.146/login?redirect=%2Findex")
    # 填入你的登录凭据

    page.get_by_role("button", name="登 录").click()
    
    # 确保进入首页后再操作
    page.wait_for_url("**/index")

    # 2. 导航至用户管理
    page.locator("div").filter(has_text=re.compile(r"^系统管理$")).click()
    page.get_by_role("link", name="用户管理").click()

    # 3. 选择并点击修改
    # 选中第二行数据
    page.locator("tr:nth-child(2) > .el-table_1_column_1 > .cell > .el-checkbox > .el-checkbox__input > .el-checkbox__inner").click()
    page.get_by_role("button", name=" 修改").nth(1).click()

    # --- 随机化修改部分 ---
    new_nickname = generate_random_name("测试员")
    new_phone = generate_random_phone()
    
    print(f"正在修改用户信息：昵称 -> {new_nickname}, 手机号 -> {new_phone}")

    # 输入随机生成的昵称
    nickname_field = page.get_by_role("textbox", name="请输入用户昵称")
    nickname_field.click()
    nickname_field.fill(new_nickname)

    # 输入随机生成的手机号
    phone_field = page.get_by_role("dialog", name="修改用户").get_by_placeholder("请输入手机号码")
    phone_field.click()
    phone_field.fill(new_phone)
    # -----------------------

    # 选择岗位和角色（如果需要随机选，也可以通过 listitem 随机抽取）
    page.get_by_role("textbox", name="请选择岗位").click()
    page.get_by_role("listitem").filter(has_text="普通员工").click()

    page.get_by_role("textbox", name="请选择角色").click()
    page.get_by_text("普通角色").click()

    # 4. 提交
    page.get_by_role("button", name="确 定").click()

    # 等待成功提示（如果有的话）或停留观察
    page.wait_for_timeout(2000)
    
    context.close()
    browser.close()

if __name__ == "__main__":
    with sync_playwright() as playwright:
        run(playwright)