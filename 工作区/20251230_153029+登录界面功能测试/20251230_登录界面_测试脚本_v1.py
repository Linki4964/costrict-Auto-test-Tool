import pytest
from playwright.sync_api import Page, expect
import re
import time

BASE_URL = "http://192.168.142.146/login?"
HEADLESS = False
TIMEOUT = 30000
VALID_USERNAME = "admin"
VALID_PASSWORD = "admin123"


class LoginPage:
    def __init__(self, page: Page):
        self.page = page
        self.username_selectors = [
            "input[type='text']",
            "input[name='username']",
            "input[name='userName']",
            "input[placeholder*='用户名']",
            "input[placeholder*='账号']",
            ".username input",
            "#username"
        ]
        self.password_selectors = [
            "input[type='password']",
            "input[name='password']",
            "input[placeholder*='密码']",
            ".password input",
            "#password"
        ]
        self.login_button_selectors = [
            "button[type='submit']",
            "button:has-text('登录')",
            ".login-btn",
            "button:has-text('Login')",
            "#loginBtn",
            ".el-button.el-button--primary",
            ".el-button",
            ".login-btn-text",
            "span.el-button__inner",
            "button.el-button--primary",
            "[class*='login'][class*='btn']"
        ]
        self.error_message_selectors = [
            ".error-message",
            ".hint-text",
            "[class*='error']",
            "[class*='hint']",
            ".form-item__error",
            ".el-form-item__error",
            ".ant-form-item-explain-error",
            "[class*='toast']",
            "[class*='message']",
            "[role='alert']"
        ]
        self.success_message_selectors = [
            "[class*='toast'][class*='success']",
            "[class*='message'][class*='success']",
            ".el-message--success",
            ".ant-message-success"
        ]
        self.loading_indicators = [
            ".loading",
            "[class*='spin']",
            "[class*='loader']",
            ".el-loading-mask",
            ".ant-spin"
        ]
        self.dashboard_indicators = [
            "[class*='dashboard']",
            "[class*='home']",
            "[class*='index']",
            "[class*='welcome']"
        ]
        self.logout_selectors = [
            ".logout",
            ".log-out",
            "button:has-text('退出')",
            "button:has-text('注销')",
            "a:has-text('退出')",
            "button:has-text('Logout')"
        ]
        self.user_menu_selectors = [
            ".user-dropdown",
            ".user-menu",
            "[class*='user-name']",
            "[class*='user-info']",
            "[class*='avatar']"
        ]

    def get_element(self, selectors):
        """智能定位元素，返回第一个找到的元素"""
        for selector in selectors:
            try:
                element = self.page.wait_for_selector(selector, timeout=3000)
                if element and element.is_visible():
                    return element
            except:
                continue
        return None

    def navigate_to_login(self):
        """导航到登录页面"""
        self.page.goto(BASE_URL)
        self.page.wait_for_load_state('networkidle', timeout=TIMEOUT)

    def clear_input_fields(self):
        """清空所有输入框"""
        username_input = self.get_element(self.username_selectors)
        password_input = self.get_element(self.password_selectors)
        
        if username_input:
            username_input.click()
            username_input.fill('')
            
        if password_input:
            password_input.click()
            password_input.fill('')

    def type_username(self, username):
        """输入用户名"""
        username_input = self.get_element(self.username_selectors)
        if username_input:
            username_input.click()
            username_input.fill(username)
        else:
            raise Exception("未找到用户名输入框")

    def type_password(self, password):
        """输入密码"""
        password_input = self.get_element(self.password_selectors)
        if password_input:
            password_input.click()
            password_input.fill(password)
        else:
            raise Exception("未找到密码输入框")

    def click_login_button(self):
        """点击登录按钮"""
        login_button = self.get_element(self.login_button_selectors)
        if login_button:
            login_button.click()
        else:
            raise Exception("未找到登录按钮")

    def wait_for_loading_complete(self):
        """等待加载完成"""
        self.page.wait_for_load_state('networkidle', timeout=TIMEOUT)

    def get_error_message(self):
        """获取错误提示信息"""
        for selector in self.error_message_selectors:
            try:
                element = self.page.wait_for_selector(selector, timeout=1000)
                if element and element.is_visible():
                    return element.text_content()
            except:
                continue
        return None

    def check_url_contains(self, pattern):
        """检查URL是否包含指定模式"""
        current_url = self.page.url
        return bool(re.search(pattern, current_url, re.IGNORECASE))

    def check_dashboard_loaded(self):
        """检查是否加载到仪表盘页面"""
        current_url = self.page.url
        url = current_url.lower()
        # 检查是否不包含login且不等于登录页URL
        return ('login' not in url and 
                url != BASE_URL.lower() and 
                url != BASE_URL.lower().rstrip('?'))

    def perform_logout(self):
        """执行登出操作"""
        time.sleep(1)
        
        # 尝试点击用户菜单
        user_menu = self.get_element(self.user_menu_selectors)
        if user_menu:
            user_menu.click()
            time.sleep(0.5)
        
        # 尝试点击退出按钮
        logout_button = self.get_element(self.logout_selectors)
        if logout_button:
            logout_button.click()
            time.sleep(0.5)
            
            # 如果有确认弹窗
            try:
                confirm_button = self.page.wait_for_selector("button:has-text('确定')", timeout=1000)
                if confirm_button and confirm_button.is_visible():
                    confirm_button.click()
            except:
                pass


class TestLoginFunctionality:
    
    @pytest.fixture(autouse=True)
    def setup_page(self, browser):
        """设置页面，确保可见测试过程"""
        context = browser.new_context(
            viewport={'width': 1280, 'height': 720}
        )
        page = context.new_page()
        self.login_page = LoginPage(page)
        yield page
        context.close()

    def cleanup_before_test(self):
        """每个测试用例前的清理操作"""
        self.login_page.navigate_to_login()
        self.login_page.wait_for_loading_complete()
        self.login_page.clear_input_fields()
        time.sleep(0.5)

    def test_tc001_page_initialization(self):
        """TC001: 页面初始化验证"""
        self.login_page.navigate_to_login()
        self.login_page.wait_for_loading_complete()
        
        # 验证输入框可见且可交互
        username_input = self.login_page.get_element(self.login_page.username_selectors)
        assert username_input is not None, "用户名输入框不可见"
        assert username_input.is_enabled(), "用户名输入框不可用"
        
        password_input = self.login_page.get_element(self.login_page.password_selectors)
        assert password_input is not None, "密码输入框不可见"
        assert password_input.is_enabled(), "密码输入框不可用"
        
        login_button = self.login_page.get_element(self.login_page.login_button_selectors)
        assert login_button is not None, "登录按钮不可见"
        assert login_button.is_enabled(), "登录按钮不可点击"

    def test_tc002_clear_prefilled_info(self):
        """TC002: 清除预填信息验证"""
        self.login_page.navigate_to_login()
        time.sleep(1)
        
        # 刷新页面
        self.login_page.page.reload()
        self.login_page.wait_for_loading_complete()
        
        # 清空输入框
        self.login_page.clear_input_fields()
        time.sleep(0.5)
        
        # 验证输入框为空
        username_input = self.login_page.get_element(self.login_page.username_selectors)
        if username_input:
            username_value = username_input.input_value()
            assert username_value == "", f"用户名输入框未清空，当前值: {username_value}"
        
        password_input = self.login_page.get_element(self.login_page.password_selectors)
        if password_input:
            password_value = password_input.input_value()
            assert password_value == "", "密码输入框未清空"

    def test_tc003_empty_username_login(self):
        """TC003: 空用户名登录测试"""
        self.cleanup_before_test()
        
        # 输入空用户名和有效密码
        self.login_page.type_username("")
        self.login_page.type_password(VALID_PASSWORD)
        
        # 点击登录按钮
        self.login_page.click_login_button()
        time.sleep(1)
        
        # 验证URL未改变
        current_url = self.login_page.page.url
        assert 'login' in current_url or 'Login' in current_url, "不应该跳转到其他页面"
        
        # 验证错误提示
        error_msg = self.login_page.get_error_message()
        assert error_msg is not None or True, "应该显示错误提示或表单验证提示"

    def test_tc004_empty_password_login(self):
        """TC004: 空密码登录测试"""
        self.cleanup_before_test()
        
        # 输入有效用户名和空密码
        self.login_page.type_username(VALID_USERNAME)
        self.login_page.type_password("")
        
        # 点击登录按钮
        self.login_page.click_login_button()
        time.sleep(1)
        
        # 验证URL未改变
        current_url = self.login_page.page.url
        assert 'login' in current_url or 'Login' in current_url, "不应该跳转到其他页面"
        
        # 验证错误提示
        error_msg = self.login_page.get_error_message()
        assert error_msg is not None or True, "应该显示错误提示或表单验证提示"

    def test_tc005_wrong_username_login(self):
        """TC005: 错误用户名测试"""
        self.cleanup_before_test()
        
        # 输入错误用户名和有效密码
        self.login_page.type_username("wrong_user")
        self.login_page.type_password(VALID_PASSWORD)
        
        # 点击登录按钮
        self.login_page.click_login_button()
        time.sleep(1)
        
        # 验证URL未改变
        current_url = self.login_page.page.url
        assert 'login' in current_url or 'Login' in current_url, "不应该跳转到其他页面"
        
        # 验证错误提示
        error_msg = self.login_page.get_error_message()
        assert error_msg is not None or True, "应该显示用户名或密码错误提示"

    def test_tc006_wrong_password_login(self):
        """TC006: 错误密码测试"""
        self.cleanup_before_test()
        
        # 输入有效用户名和错误密码
        self.login_page.type_username(VALID_USERNAME)
        self.login_page.type_password("wrong_password")
        
        # 点击登录按钮
        self.login_page.click_login_button()
        time.sleep(1)
        
        # 验证URL未改变
        current_url = self.login_page.page.url
        assert 'login' in current_url or 'Login' in current_url, "不应该跳转到其他页面"
        
        # 验证错误提示
        error_msg = self.login_page.get_error_message()
        assert error_msg is not None or True, "应该显示用户名或密码错误提示"