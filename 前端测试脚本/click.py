import re
from playwright.sync_api import sync_playwright, expect

LOGIN_URL = "http://192.168.142.146/login?redirect=%2Findex"

def test_login():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        # 进入登录页
        page.goto(LOGIN_URL)

        # ===== 场景一：账号错误 =====
        page.get_by_role("textbox", name="账号").fill("admin11")
        page.get_by_role("textbox", name="密码").fill("admin123")
        page.get_by_role("button", name="登 录").click()

        # 断言：仍在 login 页面
        expect(page).to_have_url(re.compile("login"))

        # ===== 场景二：账号正确 =====
        page.get_by_role("textbox", name="账号").fill("admin")
        page.get_by_role("textbox", name="密码").fill("admin123")
        page.get_by_role("button", name="登 录").click()

        # 断言：进入 index
        expect(page).to_have_url(re.compile("index"))

        browser.close()

if __name__ == "__main__":
    test_login()
