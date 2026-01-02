from playwright.sync_api import sync_playwright, Page, expect
import pytest
import time
import re

class TestUserAdd:
    """用户管理-新增功能测试类"""
    
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
        
        # 点击登录按钮 - 使用CSS选择器避免编码问题
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
    
    def open_add_dialog(self):
        """打开新增用户对话框"""
        # 点击新增按钮
        self.page.get_by_text("新增").click()
        
        # 等待对话框出现
        self.page.wait_for_timeout(1500)
        
        # 直接返回找到的对话框
        dialog = self.page.locator(".el-dialog").nth(2)
        return dialog
        
        return dialog
    
    def verify_success_toast(self, expected_text="新增成功"):
        """验证成功提示消息"""
        toast = self.page.locator(".el-message")
        expect(toast).to_be_visible()
        expect(toast).to_contain_text(expected_text)
    
    def verify_network_request(self, url_pattern, expected_status=200):
        """验证网络请求（需要启用CDP）"""
        # 简化的网络验证逻辑
        # 在完整实现中，可以通过CDP或Response API验证
        pass
    
    def test_add_001(self):
        """TC_ADD_001: 正常新增用户-填写所有必填字段"""
        print("\n" + "=" * 60)
        print("执行测试用例: TC_ADD_001 - 正常新增用户-填写所有必填字段")
        print("=" * 60)
        
        # 导航到用户管理页面
        self.navigate_to_user_management()
        
        # 打开新增对话框
        dialog = self.open_add_dialog()
        
        # 填写必填字段 - 使用纯CSS选择器
        dialog.locator("input[placeholder*='昵称']").fill("测试用户001")
        
        # 选择部门 - 点击树形选择器
        dialog.locator(".vue-treeselect__control").click()
        dialog.locator(".vue-treeselect__option").nth(1).click()
        
        dialog.locator("input[placeholder*='用户名']").fill("testuser001")
        dialog.locator("input[type='password']").fill("Test@12345")
        
        # 点击确定按钮
        with self.page.expect_response(re.compile(r"/system/user", re.IGNORECASE)) as response_info:
            dialog.locator(".dialog-footer .el-button--primary").click()
        
        # 验证响应
        response = response_info.value
        assert response.status == 200, f"期望状态码200，实际{response.status}"
        response_data = response.json()
        assert response_data.get("code") == 200, f"期望业务码200，实际{response_data.get('code')}"
        
        # UI层验证
        self.verify_success_toast("新增成功")
        expect(dialog).not_to_be_visible()
        
        # UX层验证 - 列表中显示新用户
        table = self.page.locator(".el-table")
        expect(table).to_contain_text("测试用户001")
        
        print("✓ 测试用例 TC_ADD_001 通过")
    
    def test_add_002(self):
        """TC_ADD_002: 正常新增用户-填写所有字段"""
        print("\n" + "=" * 60)
        print("执行测试用例: TC_ADD_002 - 正常新增用户-填写所有字段")
        print("=" * 60)
        
        self.navigate_to_user_management()
        dialog = self.open_add_dialog()
        
        # 填写所有字段
        dialog.locator("[prop='nickName'] input").fill("测试用户002")
        
        # 选择部门
        dialog.locator("[prop='deptId'] .vue-treeselect__control").click()
        dialog.locator(".vue-treeselect__menu .vue-treeselect__option").first.click()
        
        dialog.locator("[prop='phonenumber'] input").fill("13800138000")
        dialog.locator("[prop='email'] input").fill("test002@example.com")
        dialog.locator("[prop='userName'] input").fill("testuser002")
        dialog.locator("[prop='password'] input").fill("Test@12345")
        
        # 选择性别
        dialog.locator("[prop='sex'] .el-input__inner").click()
        dialog.get_by_text("男").click()
        
        # 选择状态（默认已选中"正常"）
        
        # 选择岗位
        dialog.locator("[prop='postIds'] .el-input__inner").click()
        dialog.locator("[prop='postIds'] .el-select-dropdown").locator("li").first.click()
        
        # 选择角色
        dialog.locator("[prop='roleIds'] .el-input__inner").click()
        dialog.locator("[prop='roleIds'] .el-select-dropdown").locator("li").first.click()
        
        # 备注信息
        dialog.locator("[prop='remark'] textarea").fill("自动化测试创建的用户")
        
        # 提交
        dialog.locator(".dialog-footer .el-button--primary").click()
        
        # 验证
        self.verify_success_toast("新增成功")
        expect(dialog).not_to_be_visible()
        
        print("✓ 测试用例 TC_ADD_002 通过")
    
    def test_add_003(self):
        """TC_ADD_003: 异常测试-用户昵称为空"""
        print("\n" + "=" * 60)
        print("执行测试用例: TC_ADD_003 - 异常测试-用户昵称为空")
        print("=" * 60)
        
        self.navigate_to_user_management()
        dialog = self.open_add_dialog()
        
        # 不填写用户昵称，填写其他必填字段
        dialog.locator("[prop='deptId'] .vue-treeselect__control").click()
        dialog.locator(".vue-treeselect__menu .vue-treeselect__option").first.click()
        
        dialog.locator("[prop='userName'] input").fill("testuser003")
        dialog.locator("[prop='password'] input").fill("Test@12345")
        
        # 尝试提交
        dialog.locator(".dialog-footer .el-button--primary").click()
        
        # 验证错误提示
        error_msg = dialog.locator(".el-form-item__error")
        expect(error_msg).to_be_visible()
        expect(error_msg).to_contain_text("用户昵称不能为空")
        
        # 验证对话框未关闭
        expect(dialog).to_be_visible()
        
        print("✓ 测试用例 TC_ADD_003 通过")
    
    def test_add_004(self):
        """TC_ADD_004: 异常测试-用户名称为空"""
        print("\n" + "=" * 60)
        print("执行测试用例: TC_ADD_004 - 异常测试-用户名称为空")
        print("=" * 60)
        
        self.navigate_to_user_management()
        dialog = self.open_add_dialog()
        
        dialog.locator("[prop='nickName'] input").fill("测试用户004")
        
        dialog.locator("[prop='deptId'] .vue-treeselect__control").click()
        dialog.locator(".vue-treeselect__menu .vue-treeselect__option").first.click()
        
        # 不填写用户名称
        dialog.locator("[prop='password'] input").fill("Test@12345")
        
        dialog.locator(".dialog-footer .el-button--primary").click()
        
        error_msg = dialog.locator(".el-form-item__error")
        expect(error_msg).to_be_visible()
        expect(error_msg).to_contain_text("用户名称不能为空")
        
        expect(dialog).to_be_visible()
        
        print("✓ 测试用例 TC_ADD_004 通过")
    
    def test_add_005(self):
        """TC_ADD_005: 异常测试-用户密码为空"""
        print("\n" + "=" * 60)
        print("执行测试用例: TC_ADD_005 - 异常测试-用户密码为空")
        print("=" * 60)
        
        self.navigate_to_user_management()
        dialog = self.open_add_dialog()
        
        dialog.locator("[prop='nickName'] input").fill("测试用户005")
        
        dialog.locator("[prop='deptId'] .vue-treeselect__control").click()
        dialog.locator(".vue-treeselect__menu .vue-treeselect__option").first.click()
        
        dialog.locator("[prop='userName'] input").fill("testuser005")
        
        # 不填写密码
        dialog.locator(".dialog-footer .el-button--primary").click()
        
        error_msg = dialog.locator(".el-form-item__error")
        expect(error_msg).to_be_visible()
        expect(error_msg).to_contain_text("用户密码不能为空")
        
        expect(dialog).to_be_visible()
        
        print("✓ 测试用例 TC_ADD_005 通过")
    
    def test_add_006(self):
        """TC_ADD_006: 边界测试-用户名称少于2字符"""
        print("\n" + "=" * 60)
        print("执行测试用例: TC_ADD_006 - 边界测试-用户名称少于2字符")
        print("=" * 60)
        
        self.navigate_to_user_management()
        dialog = self.open_add_dialog()
        
        dialog.locator("[prop='nickName'] input").fill("测试用户006")
        
        dialog.locator("[prop='deptId'] .vue-treeselect__control").click()
        dialog.locator(".vue-treeselect__menu .vue-treeselect__option").first.click()
        
        dialog.locator("[prop='userName'] input").fill("t")  # 1个字符
        dialog.locator("[prop='password'] input").fill("Test@12345")
        
        dialog.locator(".dialog-footer .el-button--primary").click()
        
        error_msg = dialog.locator(".el-form-item__error")
        expect(error_msg).to_be_visible()
        expect(error_msg).to_contain_text("用户名称长度必须介于 2 和 20 之间")
        
        expect(dialog).to_be_visible()
        
        print("✓ 测试用例 TC_ADD_006 通过")
    
    def test_add_007(self):
        """TC_ADD_007: 边界测试-用户名称超过20字符"""
        print("\n" + "=" * 60)
        print("执行测试用例: TC_ADD_007 - 边界测试-用户名称超过20字符")
        print("=" * 60)
        
        self.navigate_to_user_management()
        dialog = self.open_add_dialog()
        
        dialog.locator("[prop='nickName'] input").fill("测试用户007")
        
        dialog.locator("[prop='deptId'] .vue-treeselect__control").click()
        dialog.locator(".vue-treeselect__menu .vue-treeselect__option").first.click()
        
        dialog.locator("[prop='userName'] input").fill("testusernameexceedslength")  # 21个字符
        dialog.locator("[prop='password'] input").fill("Test@12345")
        
        dialog.locator(".dialog-footer .el-button--primary").click()
        
        error_msg = dialog.locator(".el-form-item__error")
        expect(error_msg).to_be_visible()
        expect(error_msg).to_contain_text("用户名称长度必须介于 2 和 20 之间")
        
        expect(dialog).to_be_visible()
        
        print("✓ 测试用例 TC_ADD_007 通过")
    
    def test_add_008(self):
        """TC_ADD_008: 边界测试-用户密码少于5字符"""
        print("\n" + "=" * 60)
        print("执行测试用例: TC_ADD_008 - 边界测试-用户密码少于5字符")
        print("=" * 60)
        
        self.navigate_to_user_management()
        dialog = self.open_add_dialog()
        
        dialog.locator("[prop='nickName'] input").fill("测试用户008")
        
        dialog.locator("[prop='deptId'] .vue-treeselect__control").click()
        dialog.locator(".vue-treeselect__menu .vue-treeselect__option").first.click()
        
        dialog.locator("[prop='userName'] input").fill("testuser008")
        dialog.locator("[prop='password'] input").fill("Test")  # 4个字符
        
        dialog.locator(".dialog-footer .el-button--primary").click()
        
        error_msg = dialog.locator(".el-form-item__error")
        expect(error_msg).to_be_visible()
        expect(error_msg).to_contain_text("用户密码长度必须介于 5 和 20 之间")
        
        expect(dialog).to_be_visible()
        
        print("✓ 测试用例 TC_ADD_008 通过")
    
    def test_add_009(self):
        """TC_ADD_009: 异常测试-用户密码包含非法字符"""
        print("\n" + "=" * 60)
        print("执行测试用例: TC_ADD_009 - 异常测试-用户密码包含非法字符")
        print("=" * 60)
        
        self.navigate_to_user_management()
        dialog = self.open_add_dialog()
        
        dialog.locator("[prop='nickName'] input").fill("测试用户009")
        
        dialog.locator("[prop='deptId'] .vue-treeselect__control").click()
        dialog.locator(".vue-treeselect__menu .vue-treeselect__option").first.click()
        
        dialog.locator("[prop='userName'] input").fill("testuser009")
        dialog.locator("[prop='password'] input").fill("Test<12345")  # 包含非法字符
        
        dialog.locator(".dialog-footer .el-button--primary").click()
        
        error_msg = dialog.locator(".el-form-item__error")
        expect(error_msg).to_be_visible()
        expect(error_msg).to_contain_text("不能包含非法字符")
        
        expect(dialog).to_be_visible()
        
        print("✓ 测试用例 TC_ADD_009 通过")
    
    def test_add_010(self):
        """TC_ADD_010: 异常测试-手机号码格式错误"""
        print("\n" + "=" * 60)
        print("执行测试用例: TC_ADD_010 - 异常测试-手机号码格式错误")
        print("=" * 60)
        
        self.navigate_to_user_management()
        dialog = self.open_add_dialog()
        
        dialog.locator("[prop='nickName'] input").fill("测试用户010")
        
        dialog.locator("[prop='deptId'] .vue-treeselect__control").click()
        dialog.locator(".vue-treeselect__menu .vue-treeselect__option").first.click()
        
        dialog.locator("[prop='userName'] input").fill("testuser010")
        dialog.locator("[prop='password'] input").fill("Test@12345")
        dialog.locator("[prop='phonenumber'] input").fill("12345")  # 格式错误
        
        dialog.locator(".dialog-footer .el-button--primary").click()
        
        error_msg = dialog.locator(".el-form-item__error")
        expect(error_msg).to_be_visible()
        expect(error_msg).to_contain_text("请输入正确的手机号码")
        
        print("✓ 测试用例 TC_ADD_010 通过")
    
    def test_add_011(self):
        """TC_ADD_011: 异常测试-邮箱格式错误"""
        print("\n" + "=" * 60)
        print("执行测试用例: TC_ADD_011 - 异常测试-邮箱格式错误")
        print("=" * 60)
        
        self.navigate_to_user_management()
        dialog = self.open_add_dialog()
        
        dialog.locator("[prop='nickName'] input").fill("测试用户011")
        
        dialog.locator("[prop='deptId'] .vue-treeselect__control").click()
        time.sleep(1)
        dialog.locator(".vue-treeselect__menu .vue-treeselect__option").first.click()
        time.sleep(1)
        
        dialog.locator("[prop='userName'] input").fill("testuser011")
        dialog.locator("[prop='password'] input").fill("Test@12345")
        dialog.locator("[prop='email'] input").fill("invalid-email")  # 格式错误
        
        dialog.locator(".dialog-footer .el-button--primary").click()
        time.sleep(0.5)
        
        error_msg = dialog.locator(".el-form-item__error")
        expect(error_msg).to_be_visible()
        expect(error_msg).to_contain_text("请输入正确的邮箱地址")
        
        print("✓ 测试用例 TC_ADD_011 通过")
    
    def test_add_012(self):
        """TC_ADD_012: 正常用户-取消按钮功能"""
        print("\n" + "=" * 60)
        print("执行测试用例: TC_ADD_012 - 正常用户-取消按钮功能")
        print("=" * 60)
        
        self.navigate_to_user_management()
        dialog = self.open_add_dialog()
        
        # 填写部分数据
        dialog.locator("[prop='nickName'] input").fill("测试用户012")
        
        # 记录填写数据
        initial_text = dialog.locator("[prop='nickName'] input").input_value()
        assert initial_text == "测试用户012", "数据应该已填写"
        
        # 点击取消按钮
        dialog.locator(".dialog-footer .el-button--default").click()
        
        # 验证对话框关闭
        expect(dialog).not_to_be_visible()
        
        print("✓ 测试用例 TC_ADD_012 通过")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])