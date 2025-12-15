import re
from playwright.sync_api import Playwright, sync_playwright, expect,Page
import json

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    #登录功能检测
    page.goto("http://192.168.142.146/login?redirect=%2Findex")
# ## --- 测试步骤一：输入错误密码 (预期失败) ---
    print("\n--- 正在执行：错误密码登录测试 ---")
    print("--- 正在执行：第一次尝试（错误密码） ---")
    page.get_by_role("textbox", name="账号").fill("admin2")
    page.get_by_role("textbox", name="密码").fill("admin12322")
    
    print(">>> 程序已暂停，请在浏览器中手动输入验证码，然后点击 Inspector 窗口的 Resume 按钮。")
    page.pause() # <-- 程序暂停点
    page.get_by_role("textbox", name="验证码").press("Enter")
    error_message_locator = page.get_by_text("用户不存在/密码错误", exact=False)
    expect(error_message_locator).to_be_visible()
    print("✅ 错误密码提示已成功显示。")
    #正确密码
    page.reload() 
    print("\n--- 正在执行：第二次尝试（正确密码） ---")
    page.get_by_role("textbox", name="账号").fill("admin")
    page.get_by_role("textbox", name="密码").fill("admin123")

    print(">>> 程序已再次暂停，请手动输入本次的验证码，然后点击 Inspector 窗口的 Resume 按钮。")
    page.pause() # <-- 程序暂停点
    page.get_by_role("button", name="登 录").click()
    expect(page.get_by_role("menubar").get_by_role("link", name="首页")).to_be_visible()
    print("✅ 登录成功，已进入首页。")


    # 存储捕获到的数据包
captured_payload = {}
# 表单提交的目标 API 地址，请替换为您的实际地址
SUBMIT_API = "**/system/user" 

def handle_user_submit_request(route):
    """拦截并捕获表单提交的请求体"""
    global captured_payload
    try:
        # 获取请求体 (bytes)
        post_data_bytes = route.request.post_data_bytes
        if post_data_bytes:
            # 解析 JSON 数据
            captured_payload = json.loads(post_data_bytes.decode('utf-8'))
    except Exception as e:
        print(f"Error handling request: {e}")
        
    # 允许请求继续发送到后端
    route.continue_()


def test_add_user_form_validation(page: Page):

    page.route(SUBMIT_API, handle_user_submit_request)
    
    # --- 1. 定义期望值 (Expected Data) ---
    expected_nickname = "测试用户_001"
    expected_phone = "13420002424"
    expected_email = "496478705@qq.com"
    expected_username = "user_test" # 对应用户名称
    expected_remark = "这是一条备注"
        
    page.locator("div").filter(has_text=re.compile(r"^系统管理$")).click()
    page.get_by_role("link", name="用户管理").click()
    # 断言：确认进入用户管理页面
    expect(page.get_by_role("heading", name="用户管理")).to_be_visible()
    
    page.get_by_role("button", name="新增").click()

    add_user_dialog = page.get_by_role("dialog", name="添加用户")
    expect(add_user_dialog).to_be_visible()

    add_user_dialog.get_by_role("textbox", name="请输入用户昵称").fill(expected_nickname)
    add_user_dialog.locator(".vue-treeselect__input").click()
    page.get_by_text("若依科技(2)").click() 
    add_user_dialog.get_by_placeholder("请输入手机号码").fill(expected_phone)
    add_user_dialog.get_by_role("textbox", name="请输入邮箱").fill(expected_email)
    add_user_dialog.get_by_placeholder("请输入用户名称").fill(expected_username) 

    page.get_by_role("textbox", name="请选择性别").click()
    page.get_by_role("listitem").filter(has_text="未知").click()
    add_user_dialog.get_by_role("textbox", name="请输入内容").fill(expected_remark)
    page.get_by_role("button", name="确 定").click()
    
    print("\n--- 正在执行：后端数据包验证 ---")
    expect(captured_payload).not_to_be_empty()
    assert captured_payload.get("nickName") == expected_nickname, "昵称字段不匹配"
    assert captured_payload.get("phonenumber") == expected_phone, "手机号字段不匹配"
    assert captured_payload.get("email") == expected_email, "邮箱字段不匹配"
    assert captured_payload.get("userName") == expected_username, "用户名称字段不匹配"
    assert captured_payload.get("remark") == expected_remark, "备注字段不匹配"
    print("✅ 后端数据包比对成功！所有核心字段均匹配期望值。")

    expect(page.get_by_text("新增用户成功")).to_be_visible()
    expect(add_user_dialog).to_be_hidden()
    print("\n--- 正在执行：前端回显验证 ---")
    
    user_row = page.get_by_role("row", has_text=expected_nickname)
    expect(user_row).to_be_visible()

    expect(user_row.get_by_text(expected_phone)).to_be_visible()
    print("✅ 前端列表回显验证成功！新增用户记录正确显示。")


    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
