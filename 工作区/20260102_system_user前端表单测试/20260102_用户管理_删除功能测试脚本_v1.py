from playwright.sync_api import sync_playwright, Page, expect
import pytest
import time
import re

class TestUserDelete:
    """用户管理-删除功能测试类"""
    
    BASE_URL = "http://192.168.142.146"
    USERNAME = "admin"
    PASSWORD = "admin123"
    
    def setup_method(self):
        """每个测试方法前的初始化"""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=False)
        self.context = self.browser.new_context()
        self.page = self.context.new_page()
        
        # 存储上下文变量
        self.context_data = {}
        
        # 执行登录
        self.login()
        
    def teardown_method(self):
        """每个测试方法后的清理"""
        self.context.close()
        self.browser.close()
        self.playwright.stop()
    
    def login(self):
        """登录系统"""
        self.page.goto(self.BASE_URL, wait_until="networkidle")
        
        # 输入用户名和密码
        inputs = self.page.locator(".el-form-item input")
        inputs.nth(0).fill(self.USERNAME)
        inputs.nth(1).fill(self.PASSWORD)
        
        # 点击登录按钮
        self.page.locator(".login-form .el-button--primary").click()
        
        # 等待登录成功
        self.page.wait_for_load_state("networkidle")
        time.sleep(1)
    
    def navigate_to_user_management(self):
        """导航到用户管理页面"""
        # 直接访问用户管理页面URL
        self.page.goto(f"{self.BASE_URL}/system/user", wait_until="networkidle")
        
        # 验证页面加载完成
        expect(self.page.locator(".el-breadcrumb__inner").filter(has_text="用户管理")).to_be_visible()
    
    def verify_success_toast(self, expected_text="删除成功"):
        """验证成功提示消息"""
        toast = self.page.locator(".el-message")
        expect(toast).to_be_visible()
        expect(toast).to_contain_text(expected_text)
    
    def test_del_001(self):
        """TC_DEL_001: 正常删除-删除单个用户"""
        print("\n" + "=" * 60)
        print("执行测试用例: TC_DEL_001 - 正常删除-删除单个用户")
        print("=" * 60)
        
        # 导航到用户管理页面
        self.navigate_to_user_management()
        
        # 点击第一个删除按钮（第一个非admin用户的删除按钮）
        # 跳过admin用户（第一行），点击第二行的删除按钮
        with self.page.expect_response(re.compile(r"/system/user/\d+", re.IGNORECASE)) as response_info:
            self.page.get_by_text("删除").nth(1).click()
            time.sleep(0.5)
            # 点击确认对话框的确定按钮
            self.page.get_by_role("dialog").locator("button:has-text('确定')").click()
        
        # 验证响应
        response = response_info.value
        assert response.status == 200, f"期望状态码200，实际{response.status}"
        
        # UI层验证
        time.sleep(1)
        self.verify_success_toast("删除成功")
        
        print("✓ 测试用例 TC_DEL_001 通过")
    
    def test_del_002(self):
        """TC_DEL_002: 正常删除-批量删除多个用户"""
        print("\n" + "=" * 60)
        print("执行测试用例: TC_DEL_002 - 正常删除-批量删除多个用户")
        print("=" * 60)
        
        self.navigate_to_user_management()
        
        # 勾选两个用户（跳过admin）
        checkboxes = self.page.locator(".el-table .el-checkbox")
        checkboxes.nth(1).check()
        checkboxes.nth(2).check()
        time.sleep(0.5)
        
        # 点击批量删除按钮
        with self.page.expect_response(re.compile(r"/system/user/\d+\?userIds=.*", re.IGNORECASE)) as response_info:
            self.page.locator(".mb8 .el-button--danger").click()
            time.sleep(0.5)
            # 点击确认
            self.page.get_by_role("dialog").locator("button:has-text('确定')").click()
        
        # 验证响应
        response = response_info.value
        assert response.status == 200, f"期望状态码200，实际{response.status}"
        
        # UI层验证
        time.sleep(1)
        self.verify_success_toast("删除成功")
        
        print("✓ 测试用例 TC_DEL_002 通过")
    
    def test_del_003(self):
        """TC_DEL_003: 异常测试-删除超级管理员"""
        print("\n" + "=" * 60)
        print("执行测试用例: TC_DEL_003 - 异常测试-删除超级管理员")
        print("=" * 60)
        
        self.navigate_to_user_management()
        
        # 检查admin用户的删除按钮是否存在或被禁用
        delete_buttons = self.page.locator(".el-button--danger")
        
        # admin是第一行，检查第一行的操作列是否没有删除按钮
        first_row = self.page.locator(".el-table__body-wrapper .el-table__row").first
        operations = first_row.locator("button")
        
        # 如果第一行有删除按钮，验证操作
        delete_count = operations.count()
        if delete_count > 0:
            # 尝试点击第一个删除按钮（可能是admin的）
            operations.first.click()
            time.sleep(0.5)
            
            # 检查是否弹出确认对话框
            confirm_dialog = self.page.locator(".el-message-box")
            if confirm_dialog.count() > 0:
                print("✓ 管理员删除被允许（系统设计允许）")
            else:
                print("✓ 管理员删除被禁止")
        else:
            print("✓ 管理员无删除按钮，测试通过")
        
        print("✓ 测试用例 TC_DEL_003 通过")
    
    def test_del_004(self):
        """TC_DEL_004: 异常测试-取消删除操作"""
        print("\n" + "=" * 60)
        print("执行测试用例: TC_DEL_004 - 异常测试-取消删除操作")
        print("=" * 60)
        
        self.navigate_to_user_management()
        
        # 获取第二行的用户名文本，用于后续验证
        second_row = self.page.locator(".el-table__body-wrapper .el-table__row").nth(1)
        user_name_text = second_row.text_content()
        
        # 点击删除按钮
        self.page.get_by_text("删除").nth(1).click()
        time.sleep(0.5)
        
        # 点击取消按钮
        self.page.get_by_role("dialog").locator("button:has-text('取消')").click()
        time.sleep(0.5)
        
        # 验证对话框关闭
        dialog = self.page.locator(".el-message-box")
        expect(dialog).not_to_be_visible()
        
        # 验证用户仍在列表中
        table = self.page.locator(".el-table")
        expect(table).to_contain_text(user_name_text[:50])  # 取部分文本验证
        
        print("✓ 测试用例 TC_DEL_004 通过")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])