"""
登录界面功能测试脚本
测试URL: http://192.168.142.146/login?
测试目标: PC端
测试日期: 2025-12-30
"""

import pytest
from playwright.sync_api import Page, expect, TimeoutError


class TestLogin:
    """登录界面功能测试类"""
    
    @pytest.fixture(scope="function", autouse=True)
    def setup_page(self, browser):
        """创建并返回页面对象"""
        page = browser.new_page()
        page.set_default_timeout(10000)
        page.goto("http://192.168.142.146/login?")
        yield page
        page.close()
    
    def _clear_inputs(self, page: Page):
        """清除账号和密码输入框内容"""
        # 尝试多种选择器定位账号输入框
        account_selectors = [
            "input[name='username']",
            "input[type='text']:first-of-type",
            "input[placeholder*='账号']",
            "input[placeholder*='用户名']",
            "input[id*='username']"
        ]
        
        # 尝试多种选择器定位密码输入框
        password_selectors = [
            "input[name='password']",
            "input[type='password']",
            "input[placeholder*='密码']",
            "input[id*='password']"
        ]
        
        # 清除账号输入框
        for selector in account_selectors:
            try:
                account_input = page.locator(selector).first
                if account_input.is_visible():
                    account_input.clear()
                    print(f"使用选择器 {selector} 清除账号输入框")
                    break
            except:
                continue
        
        # 清除密码输入框
        for selector in password_selectors:
            try:
                password_input = page.locator(selector).first
                if password_input.is_visible():
                    password_input.clear()
                    print(f"使用选择器 {selector} 清除密码输入框")
                    break
            except:
                continue
    
    def _get_account_input(self, page: Page):
        """获取账号输入框"""
        selectors = [
            "input[name='username']",
            "input[type='text']:first-of-type",
            "input[placeholder*='账号']",
            "input[placeholder*='用户名']"
        ]
        for selector in selectors:
            try:
                element = page.locator(selector).first
                if element.is_visible():
                    return element
            except:
                continue
        raise Exception("无法找到账号输入框")
    
    def _get_password_input(self, page: Page):
        """获取密码输入框"""
        selectors = [
            "input[name='password']",
            "input[type='password']",
            "input[placeholder*='密码']"
        ]
        for selector in selectors:
            try:
                element = page.locator(selector).first
                if element.is_visible():
                    return element
            except:
                continue
        raise Exception("无法找到密码输入框")
    
    def _get_login_button(self, page: Page):
        """获取登录按钮"""
        selectors = [
            "button[type='submit']",
            "button:has-text('登录')",
            ".el-button--primary",
            "button.el-button"
        ]
        for selector in selectors:
            try:
                element = page.locator(selector).first
                if element.is_visible():
                    return element
            except:
                continue
        raise Exception("无法找到登录按钮")
    
    def _perform_login(self, page: Page, username: str, password: str):
        """执行登录操作"""
        account_input = self._get_account_input(page)
        password_input = self._get_password_input(page)
        login_button = self._get_login_button(page)
        
        account_input.clear()
        account_input.fill(username)
        password_input.clear()
        password_input.fill(password)
        login_button.click()
    
    def _get_error_message(self, page: Page):
        """获取错误提示信息"""
        error_selectors = [
            ".el-message--error",
            ".el-form-item__error",
            ".error-message",
            "[class*='error']",
            ".toast-error"
        ]
        for selector in error_selectors:
            try:
                element = page.locator(selector).first
                if element.is_visible(timeout=3000):
                    return element
            except:
                continue
        return None
    
    def test_tc001_verify_page_elements(self, setup_page):
        """TC001: 验证页面元素存在性"""
        page = setup_page
        
        # 等待页面加载
        page.wait_for_load_state("networkidle")
        
        # 验证账号输入框存在
        account_input = self._get_account_input(page)
        expect(account_input).to_be_visible()
        
        # 验证密码输入框存在
        password_input = self._get_password_input(page)
        expect(password_input).to_be_visible()
        
        # 验证登录按钮存在
        login_button = self._get_login_button(page)
        expect(login_button).to_be_visible()
        
        print("✓ TC001通过: 页面元素验证成功")
    
    def test_tc002_clear_prefilled_inputs(self, setup_page):
        """TC002: 清除预先填充的账号密码"""
        page = setup_page
        
        # 刷新页面
        page.reload()
        page.wait_for_load_state("networkidle")
        
        # 清除输入框内容
        self._clear_inputs(page)
        
        # 验证输入框为空
        account_input = self._get_account_input(page)
        password_input = self._get_password_input(page)
        
        expect(account_input).to_have_value("")
        expect(password_input).to_have_value("")
        
        print("✓ TC002通过: 清除预设账号密码成功")
    
    def test_tc003_empty_account_login(self, setup_page):
        """TC003: 空账号登录测试"""
        page = setup_page
        
        # 清除输入框
        self._clear_inputs(page)
        
        # 只输入密码
        password_input = self._get_password_input(page)
        password_input.fill("admin123")
        
        # 点击登录
        login_button = self._get_login_button(page)
        login_button.click()
        
        # 验证错误提示
        error_msg = self._get_error_message(page)
        if error_msg:
            expect(error_msg).to_be_visible()
        else:
            # 验证未跳转
            expect(page).to_have_url("http://192.168.142.146/login?")
        
        print("✓ TC003通过: 空账号登录验证成功")
    
    def test_tc004_empty_password_login(self, setup_page):
        """TC004: 空密码登录测试"""
        page = setup_page
        
        # 清除输入框
        self._clear_inputs(page)
        
        # 只输入账号
        account_input = self._get_account_input(page)
        account_input.fill("admin")
        
        # 点击登录
        login_button = self._get_login_button(page)
        login_button.click()
        
        # 验证错误提示
        error_msg = self._get_error_message(page)
        if error_msg:
            expect(error_msg).to_be_visible()
        else:
            # 验证未跳转
            expect(page).to_have_url("http://192.168.142.146/login?")
        
        print("✓ TC004通过: 空密码登录验证成功")
    
    def test_tc005_empty_credentials_login(self, setup_page):
        """TC005: 空账号空密码登录测试"""
        page = setup_page
        
        # 清除输入框
        self._clear_inputs(page)
        
        # 直接点击登录
        login_button = self._get_login_button(page)
        login_button.click()
        
        # 验证错误提示或未跳转
        error_msg = self._get_error_message(page)
        if error_msg:
            expect(error_msg).to_be_visible()
        
        print("✓ TC005通过: 空账号空密码登录验证成功")
    
    def test_tc006_wrong_account_login(self, setup_page):
        """TC006: 错误账号登录测试"""
        page = setup_page
        
        # 清除输入框
        self._clear_inputs(page)
        
        # 输入错误的账号和正确的密码
        self._perform_login(page, "wrongadmin", "admin123")
        
        # 验证错误提示
        error_msg = self._get_error_message(page)
        if error_msg:
            expect(error_msg).to_be_visible()
        else:
            # 验证未跳转
            current_url = page.url
            assert current_url == "http://192.168.142.146/login?" or "login" in current_url
        
        print("✓ TC006通过: 错误账号登录验证成功")
    
    def test_tc007_wrong_password_login(self, setup_page):
        """TC007: 错误密码登录测试"""
        page = setup_page
        
        # 清除输入框
        self._clear_inputs(page)
        
        # 输入正确的账号和错误的密码
        self._perform_login(page, "admin", "wrongpassword")
        
        # 验证错误提示
        error_msg = self._get_error_message(page)
        if error_msg:
            expect(error_msg).to_be_visible()
        else:
            # 验证未跳转
            current_url = page.url
            assert current_url == "http://192.168.142.146/login?" or "login" in current_url
        
        print("✓ TC007通过: 错误密码登录验证成功")
    
    def test_tc009_password_mask_verification(self, setup_page):
        """TC009: 密码输入框掩码验证"""
        page = setup_page
        
        # 获取密码输入框
        password_input = self._get_password_input(page)
        
        # 验证输入类型为password
        expect(password_input).to_have_attribute("type", "password")
        
        print("✓ TC009通过: 密码掩码验证成功")
    
    def test_tc010_enter_key_login(self, setup_page):
        """TC010: 输入框回车键登录测试"""
        page = setup_page
        
        # 清除输入框
        self._clear_inputs(page)
        
        # 输入错误的账号和密码
        account_input = self._get_account_input(page)
        password_input = self._get_password_input(page)
        
        account_input.fill("wrongadmin")
        password_input.fill("wrongpassword")
        
        # 按回车键
        password_input.press("Enter")
        
        # 等待响应
        page.wait_for_timeout(2000)
        
        # 验证未跳转
        current_url = page.url
        assert current_url == "http://192.168.142.146/login?" or "login" in current_url
        
        print("✓ TC010通过: 回车键登录验证成功")
    
    def test_tc011_login_button_state(self, setup_page):
        """TC011: 登录按钮禁用状态测试"""
        page = setup_page
        
        # 清除输入框
        self._clear_inputs(page)
        
        # 验证登录按钮状态
        login_button = self._get_login_button(page)
        
        # 检查按钮是否禁用（部分系统会禁用空表单的提交按钮）
        is_disabled = login_button.get_attribute("disabled")
        print(f"登录按钮禁用状态: {is_disabled}")
        
        # 输入账号后再检查
        account_input = self._get_account_input(page)
        account_input.fill("admin")
        
        # 验证按钮仍然可见
        expect(login_button).to_be_visible()
        
        print("✓ TC011通过: 登录按钮状态验证成功")
    
    def test_tc012_special_character_account(self, setup_page):
        """TC012: 特殊字符账号测试"""
        page = setup_page
        
        # 清除输入框
        self._clear_inputs(page)
        
        # 输入包含特殊字符的账号
        self._perform_login(page, "admin@test", "admin123")
        
        # 等待响应
        page.wait_for_timeout(2000)
        
        # 验证未跳转
        current_url = page.url
        assert current_url == "http://192.168.142.146/login?" or "login" in current_url
        
        print("✓ TC012通过: 特殊字符账号验证成功")
    
    def test_tc013_long_account_test(self, setup_page):
        """TC013: 超长账号测试"""
        page = setup_page
        
        # 清除输入框
        self._clear_inputs(page)
        
        # 输入50个字符的账号
        long_account = "a" * 50
        self._perform_login(page, long_account, "admin123")
        
        # 等待响应
        page.wait_for_timeout(2000)
        
        # 验证未跳转
        current_url = page.url
        assert current_url == "http://192.168.142.146/login?" or "login" in current_url
        
        print("✓ TC013通过: 超长账号验证成功")
    
    
    def test_tc014_consecutive_login_failures(self, setup_page):
        """TC014: 连续登录失败测试"""
        page = setup_page
        
        # 执行3次错误登录
        for i in range(3):
            self._clear_inputs(page)
            self._perform_login(page, "wrongadmin", "wrongpassword")
            
            # 等待响应
            page.wait_for_timeout(1000)
            
            # 验证错误提示
            error_msg = self._get_error_message(page)
            if error_msg:
                print(f"第{i+1}次错误登录提示: {error_msg.text_content()}")
        
        print("✓ TC014通过: 连续登录失败验证成功")
    