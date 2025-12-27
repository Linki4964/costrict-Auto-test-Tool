# -*- coding: utf-8 -*-
import pytest
import json
from playwright.sync_api import Page, Expect, expect
import time

class TestUserAddForm:
    """
    用户管理表单新增功能测试
    测试范围：用户管理界面的表单新增界面
    """
    
    def setup_method(self):
        """测试前准备"""
        self.base_url = "http://192.168.142.146"
        self.username = "admin"
        self.password = "admin123"
        
    def get_perception_script(self, scope):
        """
        增强型感知脚本 - 探测表单元素
        """
        return f"""
        (() => {{
            const container = document.querySelector('{scope}') || document.body;
            const items = container.querySelectorAll('.el-form-item');
            return Array.from(items).map(item => {{
                const labelEl = item.querySelector('.el-form-item__label');
                const input = item.querySelector('input, textarea, .vue-treeselect, .el-cascader');
                if (!input) return null;
                
                return {{
                    label: labelEl?.innerText.trim().replace(/[:：*]/g, ''),
                    placeholder: input.placeholder || input.getAttribute('placeholder') || '',
                    type: input.className.includes('treeselect') ? 'treeselect' : 
                          item.querySelector('.el-select') ? 'select' : 
                          item.querySelector('.el-cascader') ? 'cascader' : 'input',
                    required: item.classList.contains('is-required')
                }};
            }}).filter(i => i !== null);
        }})()
        """

    def test_login(self, page: Page):
        """
        步骤1-4: 登录系统
        """
        # 打开浏览器，访问登录页面
        page.goto(self.base_url)
        
        # 输入用户名
        page.get_by_label("用户名").fill(self.username)
        
        # 输入密码
        page.get_by_label("密码").fill(self.password)
        
        # 点击登录按钮
        page.get_by_role("button", name="登录").click()
        
        # 等待页面加载完成
        page.wait_for_load_state("networkidle")
        
        # 验证登录成功
        expect(page).to_have_url(f"{self.base_url}/index")

    def test_navigate_to_user_management(self, page: Page):
        """
        步骤5-8: 导航到用户管理页面
        """
        # 先确保已登录
        self.test_login(page)
        
        # 点击系统管理菜单
        page.get_by_text("系统管理").click()
        
        # 等待菜单展开
        time.sleep(0.5)
        
        # 点击用户管理子菜单
        page.get_by_text("用户管理").click()
        
        # 等待用户管理页面加载
        page.wait_for_load_state("networkidle")
        
        # 验证页面URL
        expect(page).to_have_url(f"{self.base_url}/system/user")
        
        # 截图保存
        page.screenshot(path="工作区/工作区/user_management_page.png")

    def test_detect_form_elements(self, page: Page):
        """
        测试表单元素探测器
        """
        # 导航到用户管理页面
        self.test_navigate_to_user_management(page)
        
        # 点击新增按钮
        page.get_by_role("button", name="新增").click()
        
        # 等待弹窗出现
        page.wait_for_timeout(1000)
        
        # 使用探测器脚本探测表单元素
        scope = ".el-dialog.el-dialog--center"
        perception_result = page.evaluate(self.get_perception_script(scope))
        
        # 保存探测结果
        with open("工作区/工作区/form_elements_detection.json", "w", encoding="utf-8") as f:
            json.dump(perception_result, f, ensure_ascii=False, indent=2)
        
        # 打印探测结果
        print("\n=== 表单元素探测结果 ===")
        print(json.dumps(perception_result, ensure_ascii=False, indent=2))
        
        # 验证关键元素存在
        assert len(perception_result) > 0, "未检测到表单元素"
        
        # 截图保存
        page.screenshot(path="工作区/工作区/user_add_dialog.png")
        
        return perception_result

    def test_tc001_normal_user_add(self, page: Page):
        """
        TC001: 正常用户新增
        """
        # 导航到用户管理页面
        self.test_navigate_to_user_management(page)
        
        # 点击新增按钮
        page.get_by_role("button", name="新增").click()
        
        # 等待弹窗出现
        page.wait_for_timeout(1000)
        
        # 填写用户昵称
        page.get_by_placeholder("请输入用户昵称").fill("自动化测试用户001")
        
        # 选择归属部门（树形选择器）
        page.get_by_placeholder("请选择归属部门").click()
        page.wait_for_timeout(500)
        # 点击第一个可见的部门选项
        page.locator(".vue-treeselect__menu .vue-treeselect__label").first.click()
        
        # 填写手机号码
        page.get_by_placeholder("请输入手机号码").fill("13800138001")
        
        # 填写用户名称
        page.get_by_placeholder("请输入用户名称").fill("autotest001")
        
        # 填写用户密码
        page.get_by_placeholder("请输入用户密码").fill("test123456")
        
        # 点击确定按钮，同时监听API响应
        with page.expect_response("**/system/user") as response_info:
            page.get_by_role("button", name="确定").click()
        
        # 验证API响应
        response = response_info.value
        assert response.status == 200 or response.status == 201, f"API请求失败: {response.status}"
        
        # 等待成功提示
        page.wait_for_timeout(1000)
        
        # 验证弹窗关闭
        expect(page.locator(".el-dialog")).to_be_hidden()
        
        # 验证成功提示消息
        success_message = page.locator(".el-message").inner_text()
        assert "新增成功" in success_message, f"未显示成功提示: {success_message}"
        
        print("✓ TC001: 正常用户新增-测试通过")

    def test_tc002_nick_name_required(self, page: Page):
        """
        TC002: 必填字段验证-用户昵称为空
        """
        # 导航到用户管理页面
        self.test_navigate_to_user_management(page)
        
        # 点击新增按钮
        page.get_by_role("button", name="新增").click()
        page.wait_for_timeout(1000)
        
        # 选择归属部门
        page.get_by_placeholder("请选择归属部门").click()
        page.wait_for_timeout(500)
        page.locator(".vue-treeselect__menu .vue-treeselect__label").first.click()
        
        # 填写手机号码
        page.get_by_placeholder("请输入手机号码").fill("13800138001")
        
        # 用户昵称留空
        
        # 填写用户名称
        page.get_by_placeholder("请输入用户名称").fill("testuser002")
        
        # 填写用户密码
        page.get_by_placeholder("请输入用户密码").fill("test123456")
        
        # 点击确定按钮
        page.get_by_role("button", name="确定").click()
        page.wait_for_timeout(500)
        
        # 验证错误提示
        error_message = page.locator(".el-form-item__error").filter(has_text="用户昵称不能为空")
        expect(error_message).to_be_visible()
        
        print("✓ TC002: 必填字段验证-用户昵称为空-测试通过")

    def test_tc003_user_name_required(self, page: Page):
        """
        TC003: 必填字段验证-用户名称为空
        """
        # 导航到用户管理页面
        self.test_navigate_to_user_management(page)
        
        # 点击新增按钮
        page.get_by_role("button", name="新增").click()
        page.wait_for_timeout(1000)
        
        # 填写用户昵称
        page.get_by_placeholder("请输入用户昵称").fill("测试用户002")
        
        # 选择归属部门
        page.get_by_placeholder("请选择归属部门").click()
        page.wait_for_timeout(500)
        page.locator(".vue-treeselect__menu .vue-treeselect__label").first.click()
        
        # 填写手机号码
        page.get_by_placeholder("请输入手机号码").fill("13800138002")
        
        # 填写用户密码
        page.get_by_placeholder("请输入用户密码").fill("test123456")
        
        # 用户名称留空
        
        # 点击确定按钮
        page.get_by_role("button", name="确定").click()
        page.wait_for_timeout(500)
        
        # 验证错误提示
        error_message = page.locator(".el-form-item__error").filter(has_text="用户名称不能为空")
        expect(error_message).to_be_visible()
        
        print("✓ TC003: 必填字段验证-用户名称为空-测试通过")

    def test_tc004_password_required(self, page: Page):
        """
        TC004: 必填字段验证-密码为空
        """
        # 导航到用户管理页面
        self.test_navigate_to_user_management(page)
        
        # 点击新增按钮
        page.get_by_role("button", name="新增").click()
        page.wait_for_timeout(1000)
        
        # 填写用户昵称
        page.get_by_placeholder("请输入用户昵称").fill("测试用户003")
        
        # 选择归属部门
        page.get_by_placeholder("请选择归属部门").click()
        page.wait_for_timeout(500)
        page.locator(".vue-treeselect__menu .vue-treeselect__label").first.click()
        
        # 填写手机号码
        page.get_by_placeholder("请输入手机号码").fill("13800138003")
        
        # 填写用户名称
        page.get_by_placeholder("请输入用户名称").fill("testuser003")
        
        # 密码留空
        
        # 点击确定按钮
        page.get_by_role("button", name="确定").click()
        page.wait_for_timeout(500)
        
        # 验证错误提示
        error_message = page.locator(".el-form-item__error").filter(has_text="用户密码不能为空")
        expect(error_message).to_be_visible()
        
        print("✓ TC004: 必填字段验证-密码为空-测试通过")

    def test_tc005_phone_required(self, page: Page):
        """
        TC005: 必填字段验证-手机号码为空
        """
        # 导航到用户管理页面
        self.test_navigate_to_user_management(page)
        
        # 点击新增按钮
        page.get_by_role("button", name="新增").click()
        page.wait_for_timeout(1000)
        
        # 填写用户昵称
        page.get_by_placeholder("请输入用户昵称").fill("测试用户004")
        
        # 选择归属部门
        page.get_by_placeholder("请选择归属部门").click()
        page.wait_for_timeout(500)
        page.locator(".vue-treeselect__menu .vue-treeselect__label").first.click()
        
        # 手机号码留空
        
        # 填写用户名称
        page.get_by_placeholder("请输入用户名称").fill("testuser004")
        
        # 填写用户密码
        page.get_by_placeholder("请输入用户密码").fill("test123456")
        
        # 点击确定按钮
        page.get_by_role("button", name="确定").click()
        page.wait_for_timeout(500)
        
        # 验证错误提示
        error_message = page.locator(".el-form-item__error").filter(has_text="请输入正确的手机号码")
        expect(error_message).to_be_visible()
        
        print("✓ TC005: 必填字段验证-手机号码为空-测试通过")

    def test_tc006_dept_required(self, page: Page):
        """
        TC006: 必填字段验证-归属部门为空
        """
        # 导航到用户管理页面
        self.test_navigate_to_user_management(page)
        
        # 点击新增按钮
        page.get_by_role("button", name="新增").click()
        page.wait_for_timeout(1000)
        
        # 填写用户昵称
        page.get_by_placeholder("请输入用户昵称").fill("测试用户005")
        
        # 归属部门不选择
        
        # 填写手机号码
        page.get_by_placeholder("请输入手机号码").fill("13800138005")
        
        # 填写用户名称
        page.get_by_placeholder("请输入用户名称").fill("testuser005")
        
        # 填写用户密码
        page.get_by_placeholder("请输入用户密码").fill("test123456")
        
        # 点击确定按钮
        page.get_by_role("button", name="确定").click()
        page.wait_for_timeout(500)
        
        # 验证错误提示
        error_message = page.locator(".el-form-item__error").filter(has_text="请选择归属部门")
        expect(error_message).to_be_visible()
        
        print("✓ TC006: 必填字段验证-归属部门为空-测试通过")

    def test_tc007_user_name_too_short(self, page: Page):
        """
        TC007: 字段长度验证-用户名称过短
        """
        # 导航到用户管理页面
        self.test_navigate_to_user_management(page)
        
        # 点击新增按钮
        page.get_by_role("button", name="新增").click()
        page.wait_for_timeout(1000)
        
        # 填写用户昵称
        page.get_by_placeholder("请输入用户昵称").fill("测试用户006")
        
        # 选择归属部门
        page.get_by_placeholder("请选择归属部门").click()
        page.wait_for_timeout(500)
        page.locator(".vue-treeselect__menu .vue-treeselect__label").first.click()
        
        # 填写手机号码
        page.get_by_placeholder("请输入手机号码").fill("13800138006")
        
        # 用户名称输入1个字符
        page.get_by_placeholder("请输入用户名称").fill("a")
        
        # 填写用户密码
        page.get_by_placeholder("请输入用户密码").fill("test123456")
        
        # 点击确定按钮
        page.get_by_role("button", name="确定").click()
        page.wait_for_timeout(500)
        
        # 验证错误提示
        error_message = page.locator(".el-form-item__error").filter(has_text="用户名称长度必须介于 2 和 20 之间")
        expect(error_message).to_be_visible()
        
        print("✓ TC007: 字段长度验证-用户名称过短-测试通过")

    def test_tc008_password_too_short(self, page: Page):
        """
        TC008: 字段长度验证-密码过短
        """
        # 导航到用户管理页面
        self.test_navigate_to_user_management(page)
        
        # 点击新增按钮
        page.get_by_role("button", name="新增").click()
        page.wait_for_timeout(1000)
        
        # 填写用户昵称
        page.get_by_placeholder("请输入用户昵称").fill("测试用户007")
        
        # 选择归属部门
        page.get_by_placeholder("请选择归属部门").click()
        page.wait_for_timeout(500)
        page.locator(".vue-treeselect__menu .vue-treeselect__label").first.click()
        
        # 填写手机号码
        page.get_by_placeholder("请输入手机号码").fill("13800138007")
        
        # 填写用户名称
        page.get_by_placeholder("请输入用户名称").fill("testuser007")
        
        # 密码输入4个字符
        page.get_by_placeholder("请输入用户密码").fill("test")
        
        # 点击确定按钮
        page.get_by_role("button", name="确定").click()
        page.wait_for_timeout(500)
        
        # 验证错误提示
        error_message = page.locator(".el-form-item__error").filter(has_text="用户密码长度必须介于 5 和 20 之间")
        expect(error_message).to_be_visible()
        
        print("✓ TC008: 字段长度验证-密码过短-测试通过")

    def test_tc009_phone_format_error(self, page: Page):
        """
        TC009: 字段格式验证-手机号码格式错误
        """
        # 导航到用户管理页面
        self.test_navigate_to_user_management(page)
        
        # 点击新增按钮
        page.get_by_role("button", name="新增").click()
        page.wait_for_timeout(1000)
        
        # 填写用户昵称
        page.get_by_placeholder("请输入用户昵称").fill("测试用户008")
        
        # 选择归属部门
        page.get_by_placeholder("请选择归属部门").click()
        page.wait_for_timeout(500)
        page.locator(".vue-treeselect__menu .vue-treeselect__label").first.click()
        
        # 手机号码输入123
        page.get_by_placeholder("请输入手机号码").fill("123")
        
        # 填写用户名称
        page.get_by_placeholder("请输入用户名称").fill("testuser008")
        
        # 填写用户密码
        page.get_by_placeholder("请输入用户密码").fill("test123456")
        
        # 点击确定按钮
        page.get_by_role("button", name="确定").click()
        page.wait_for_timeout(500)
        
        # 验证错误提示
        error_message = page.locator(".el-form-item__error").filter(has_text="请输入正确的手机号码")
        expect(error_message).to_be_visible()
        
        print("✓ TC009: 字段格式验证-手机号码格式错误-测试通过")

    def test_tc010_email_format_error(self, page: Page):
        """
        TC010: 字段格式验证-邮箱格式错误
        """
        # 导航到用户管理页面
        self.test_navigate_to_user_management(page)
        
        # 点击新增按钮
        page.get_by_role("button", name="新增").click()
        page.wait_for_timeout(1000)
        
        # 填写用户昵称
        page.get_by_placeholder("请输入用户昵称").fill("测试用户009")
        
        # 选择归属部门
        page.get_by_placeholder("请选择归属部门").click()
        page.wait_for_timeout(500)
        page.locator(".vue-treeselect__menu .vue-treeselect__label").first.click()
        
        # 填写手机号码
        page.get_by_placeholder("请输入手机号码").fill("13800138009")
        
        # 邮箱输入invalid-email
        page.get_by_placeholder("请输入邮箱").fill("invalid-email")
        
        # 填写用户名称
        page.get_by_placeholder("请输入用户名称").fill("testuser009")
        
        # 填写用户密码
        page.get_by_placeholder("请输入用户密码").fill("test123456")
        
        # 点击确定按钮
        page.get_by_role("button", name="确定").click()
        page.wait_for_timeout(500)
        
        # 验证错误提示
        error_message = page.locator(".el-form-item__error").filter(has_text="请输入正确的邮箱地址")
        expect(error_message).to_be_visible()
        
        print("✓ TC010: 字段格式验证-邮箱格式错误-测试通过")

    def test_tc011_password_invalid_chars(self, page: Page):
        """
        TC011: 非法字符验证-密码包含特殊字符
        """
        # 导航到用户管理页面
        self.test_navigate_to_user_management(page)
        
        # 点击新增按钮
        page.get_by_role("button", name="新增").click()
        page.wait_for_timeout(1000)
        
        # 填写用户昵称
        page.get_by_placeholder("请输入用户昵称").fill("测试用户010")
        
        # 选择归属部门
        page.get_by_placeholder("请选择归属部门").click()
        page.wait_for_timeout(500)
        page.locator(".vue-treeselect__menu .vue-treeselect__label").first.click()
        
        # 填写手机号码
        page.get_by_placeholder("请输入手机号码").fill("13800138010")
        
        # 填写用户名称
        page.get_by_placeholder("请输入用户名称").fill("testuser010")
        
        # 密码输入test<123
        page.get_by_placeholder("请输入用户密码").fill("test<123")
        
        # 点击确定按钮
        page.get_by_role("button", name="确定").click()
        page.wait_for_timeout(500)
        
        # 验证错误提示
        error_message = page.locator(".el-form-item__error").filter(has_text="不能包含非法字符")
        expect(error_message).to_be_visible()
        
        print("✓ TC011: 非法字符验证-密码包含特殊字符-测试通过")

    def test_tc012_full_form_fields(self, page: Page):
        """
        TC012: 完整表单填写-包含可选字段
        """
        # 导航到用户管理页面
        self.test_navigate_to_user_management(page)
        
        # 点击新增按钮
        page.get_by_role("button", name="新增").click()
        page.wait_for_timeout(1000)
        
        # 填写用户昵称
        page.get_by_placeholder("请输入用户昵称").fill("自动化测试用户002")
        
        # 选择归属部门
        page.get_by_placeholder("请选择归属部门").click()
        page.wait_for_timeout(500)
        page.locator(".vue-treeselect__menu .vue-treeselect__label").first.click()
        
        # 填写手机号码
        page.get_by_placeholder("请输入手机号码").fill("13800138002")
        
        # 填写邮箱
        page.get_by_placeholder("请输入邮箱").fill("autotest002@example.com")
        
        # 填写用户名称
        page.get_by_placeholder("请输入用户名称").fill("autotest002")
        
        # 填写用户密码
        page.get_by_placeholder("请输入用户密码").fill("test123456")
        
        # 选择用户性别
        page.get_by_placeholder("请选择性别").click()
        page.wait_for_timeout(300)
        page.get_by_role("option", name="女").click()
        
        # 状态保持默认（启用）
        
        # 选择岗位（多选）
        page.get_by_placeholder("请选择岗位").click()
        page.wait_for_timeout(300)
        page.get_by_role("option").first.click()
        
        # 选择角色（多选）
        page.get_by_placeholder("请选择角色").click()
        page.wait_for_timeout(300)
        page.get_by_role("option").first.click()
        
        # 填写备注
        page.get_by_placeholder("请输入内容").fill("这是通过自动化测试创建的完整字段用户")
        
        # 点击确定按钮，同时监听API响应
        with page.expect_response("**/system/user") as response_info:
            page.get_by_role("button", name="确定").click()
        
        # 验证API响应
        response = response_info.value
        assert response.status == 200 or response.status == 201, f"API请求失败: {response.status}"
        
        # 等待成功提示
        page.wait_for_timeout(1000)
        
        # 验证弹窗关闭
        expect(page.locator(".el-dialog")).to_be_hidden()
        
        # 验证成功提示消息
        success_message = page.locator(".el-message").inner_text()
        assert "新增成功" in success_message, f"未显示成功提示: {success_message}"
        
        print("✓ TC012: 完整表单填写-包含可选字段-测试通过")

    def test_tc013_cancel_add(self, page: Page):
        """
        TC013: 取消新增操作
        """
        # 导航到用户管理页面
        self.test_navigate_to_user_management(page)
        
        # 点击新增按钮
        page.get_by_role("button", name="新增").click()
        page.wait_for_timeout(1000)
        
        # 填写部分字段
        page.get_by_placeholder("请输入用户昵称").fill("测试用户011")
        
        # 点击取消按钮
        page.get_by_role("button", name="取消").click()
        
        # 验证弹窗关闭
        page.wait_for_timeout(500)
        expect(page.locator(".el-dialog")).to_be_hidden()
        
        print("✓ TC013: 取消新增操作-测试通过")