from playwright.sync_api import sync_playwright, Page, expect
import pytest
import time
import re

class TestUserUpdate:
    """用户管理-修改功能测试类"""
    
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
        
        # 点击登录按钮 - 使用纯CSS选择器避免编码问题
        self.page.locator(".login-form .el-button--primary").click()
        
        # 等待登录成功 - 检查URL变化或导航栏出现
        self.page.wait_for_load_state("networkidle")
        time.sleep(1)
    
    def navigate_to_user_management(self):
        """导航到用户管理页面"""
        # 直接访问用户管理页面URL
        self.page.goto(f"{self.BASE_URL}/system/user", wait_until="networkidle")
        
        # 验证页面加载完成 - 检查面包屑
        expect(self.page.locator(".el-breadcrumb__inner").filter(has_text="用户管理")).to_be_visible()
    
    def open_update_dialog(self, row_index=1):
        """打开修改用户对话框"""
        # 使用文本点击第一个修改按钮
        self.page.get_by_text("修改").first.click()
        
        # 等待对话框出现
        self.page.wait_for_timeout(1500)
        
        # 直接返回找到的对话框
        dialog = self.page.locator(".el-dialog").nth(2)
        return dialog
    
    def verify_success_toast(self, expected_text="修改成功"):
        """验证成功提示消息"""
        toast = self.page.locator(".el-message")
        expect(toast).to_be_visible()
        expect(toast).to_contain_text(expected_text)
    
    def verify_network_request(self, url_pattern, expected_status=200):
        """验证网络请求"""
        pass
    
    def test_update_001(self):
        """TC_UPDATE_001: 正常修改用户-修改用户昵称"""
        print("\n" + "=" * 60)
        print("执行测试用例: TC_UPDATE_001 - 正常修改用户-修改用户昵称")
        print("=" * 60)
        
        # 导航到用户管理页面
        self.navigate_to_user_management()
        
        # 打开修改对话框 - 修改第一行数据
        dialog = self.open_update_dialog(row_index=0)
        
        # 修改用户昵称 - 使用CSS选择器定位
        dialog.locator("input[placeholder*='昵称']").fill("修改后昵称")
        
        # 点击确定按钮
        with self.page.expect_response(re.compile(r"/system/user", re.IGNORECASE)) as response_info:
            dialog.locator(".dialog-footer .el-button--primary").click()
        
        # 验证响应
        response = response_info.value
        assert response.status == 200, f"期望状态码200，实际{response.status}"
        response_data = response.json()
        assert response_data.get("code") == 200, f"期望业务码200，实际{response_data.get('code')}"
        
        # UI层验证
        self.verify_success_toast("修改成功")
        expect(dialog).not_to_be_visible()
        
        # UX层验证 - 列表中显示修改后的昵称
        table = self.page.locator(".el-table")
        expect(table).to_contain_text("修改后昵称")
        
        print("✓ 测试用例 TC_UPDATE_001 通过")
    
    def test_update_002(self):
        """TC_UPDATE_002: 正常修改用户-修改手机号和邮箱"""
        print("\n" + "=" * 60)
        print("执行测试用例: TC_UPDATE_002 - 正常修改用户-修改手机号和邮箱")
        print("=" * 60)
        
        self.navigate_to_user_management()
        dialog = self.open_update_dialog(row_index=0)
        
        # 修改手机号和邮箱
        dialog.locator("input[placeholder*='手机']").fill("13900139000")
        dialog.locator("input[placeholder*='邮箱']").fill("updated@example.com")
        
        # 提交
        dialog.locator(".dialog-footer .el-button--primary").click()
        time.sleep(1)
        
        # 验证
        self.verify_success_toast("修改成功")
        expect(dialog).not_to_be_visible()
        
        print("✓ 测试用例 TC_UPDATE_002 通过")
    
    def test_update_003(self):
        """TC_UPDATE_003: 正常修改用户-修改岗位和角色"""
        print("\n" + "=" * 60)
        print("执行测试用例: TC_UPDATE_003 - 正常修改用户-修改岗位和角色")
        print("=" * 60)
        
        self.navigate_to_user_management()
        dialog = self.open_update_dialog(row_index=0)
        
        # 修改岗位和角色
        dialog.locator("input[placeholder*='岗位']").click()
        dialog.locator(".el-select-dropdown li").nth(1).click()
        
        dialog.locator("input[placeholder*='角色']").click()
        dialog.locator(".el-select-dropdown li").nth(1).click()
        
        # 提交
        dialog.locator(".dialog-footer .el-button--primary").click()
        time.sleep(1)
        
        # 验证
        self.verify_success_toast("修改成功")
        
        print("✓ 测试用例 TC_UPDATE_003 通过")
    
    def test_update_004(self):
        """TC_UPDATE_004: 异常测试-用户昵称为空"""
        print("\n" + "=" * 60)
        print("执行测试用例: TC_UPDATE_004 - 异常测试-用户昵称为空")
        print("=" * 60)
        
        self.navigate_to_user_management()
        dialog = self.open_update_dialog(row_index=0)
        
        # 清空用户昵称
        dialog.locator("input[placeholder*='昵称']").fill("")
        
        # 尝试提交
        dialog.locator(".dialog-footer .el-button--primary").click()
        time.sleep(0.5)
        
        # 验证错误提示
        error_msg = dialog.locator(".el-form-item__error")
        expect(error_msg).to_be_visible()
        expect(error_msg).to_contain_text("用户昵称不能为空")
        
        # 验证对话框未关闭
        expect(dialog).to_be_visible()
        
        print("✓ 测试用例 TC_UPDATE_004 通过")
    
    def test_update_005(self):
        """TC_UPDATE_005: 异常测试-手机号码格式错误"""
        print("\n" + "=" * 60)
        print("执行测试用例: TC_UPDATE_005 - 异常测试-手机号码格式错误")
        print("=" * 60)
        
        self.navigate_to_user_management()
        dialog = self.open_update_dialog(row_index=0)
        
        # 修改手机号为错误格式
        dialog.locator("input[placeholder*='手机']").fill("12345")
        
        dialog.locator(".dialog-footer .el-button--primary").click()
        time.sleep(0.5)
        
        # 验证错误提示
        error_msg = dialog.locator(".el-form-item__error")
        expect(error_msg).to_be_visible()
        expect(error_msg).to_contain_text("请输入正确的手机号码")
        
        print("✓ 测试用例 TC_UPDATE_005 通过")
    
    def test_update_006(self):
        """TC_UPDATE_006: 异常测试-邮箱格式错误"""
        print("\n" + "=" * 60)
        print("执行测试用例: TC_UPDATE_006 - 异常测试-邮箱格式错误")
        print("=" * 60)
        
        self.navigate_to_user_management()
        dialog = self.open_update_dialog(row_index=0)
        
        # 修改邮箱为错误格式
        dialog.locator("input[placeholder*='邮箱']").fill("invalid-email")
        
        dialog.locator(".dialog-footer .el-button--primary").click()
        time.sleep(0.5)
        
        # 验证错误提示
        error_msg = dialog.locator(".el-form-item__error")
        expect(error_msg).to_be_visible()
        expect(error_msg).to_contain_text("请输入正确的邮箱地址")
        
        print("✓ 测试用例 TC_UPDATE_006 通过")
    
    def test_update_007(self):
        """TC_UPDATE_007: 正常用户-取消按钮功能"""
        print("\n" + "=" * 60)
        print("执行测试用例: TC_UPDATE_007 - 正常用户-取消按钮功能")
        print("=" * 60)
        
        self.navigate_to_user_management()
        dialog = self.open_update_dialog(row_index=0)
        
        # 修改部分数据
        dialog.locator("input[placeholder*='昵称']").fill("修改测试")
        
        # 记录填写数据
        initial_text = dialog.locator("input[placeholder*='昵称']").input_value()
        assert initial_text == "修改测试", "数据应该已填写"
        
        # 点击取消按钮
        dialog.locator(".dialog-footer .el-button--default").click()
        time.sleep(0.5)
        
        # 验证对话框关闭
        expect(dialog).not_to_be_visible()
        
        print("✓ 测试用例 TC_UPDATE_007 通过")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])