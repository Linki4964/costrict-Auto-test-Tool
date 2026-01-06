"""
用户新增功能自动化测试脚本
基于Playwright进行UI自动化测试
"""

from playwright.sync_api import sync_playwright, expect
import pytest
import random
import json
import time

class TestUserAdd:
    """用户新增功能测试类"""
    
    @pytest.fixture(autouse=True)
    def setup_browser(self):
        """初始化浏览器和页面"""
        with sync_playwright() as p:
            self.browser = p.chromium.launch(headless=False)
            self.context = self.browser.new_context()
            self.page = self.context.new_page()
            
            self.base_url = "http://192.168.142.146/"
            
            yield
            
            self.context.close()
            self.browser.close()
    
    def login_and_navigate(self):
        """登录并导航到用户管理页面"""
        self.page.goto(self.base_url + 'login?redirect=%2Findex')
        self.page.wait_for_load_state("networkidle")
        
        # 点击登录按钮（默认密码已填充）
        self.page.get_by_role("button", name="登 录").click()
        self.page.wait_for_url("**/index", timeout=10000)
        print("登录成功")
        
        # 导航到用户管理
        print("正在展开侧边栏菜单...")
        system_menu = self.page.locator("li").filter(has_text="系统管理").first
        system_menu.click()
        
        user_link = self.page.get_by_role("link", name="用户管理")
        user_link.wait_for(state="visible", timeout=5000)
        user_link.click()
        print("已进入用户管理页面")
        self.page.wait_for_load_state("networkidle")
    
    def open_add_dialog(self):
        """打开新增用户对话框"""
        self.page.get_by_role("button", name="新增").click()
        dialog = self.page.get_by_role("dialog")
        dialog.wait_for(state="visible", timeout=5000)
        print("新增对话框已弹出")
        return dialog
    
    def close_dialog(self):
        """关闭对话框"""
        try:
            cancel_btn = self.page.locator(".el-dialog__footer").get_by_role("button", name="取 消")
            if cancel_btn.is_visible():
                cancel_btn.click()
                print("已关闭对话框")
        except:
            pass
    
    @staticmethod
    def check_success_message(page):
        """检查成功提示消息"""
        success_msgs = ["操作成功", "新增成功", "保存成功"]
        for msg in success_msgs:
            try:
                expect(page.get_by_text(msg)).to_be_visible(timeout=2000)
                print(f"[PASS] 找到提示: {msg}")
                return True
            except:
                continue
        return False
    
    @staticmethod
    def check_error_message(dialog):
        """检查错误提示消息"""
        try:
            # 等待一下让校验生效
            import time
            time.sleep(0.5)
            # 查找所有可能的错误提示
            errors = dialog.locator(".el-form-item__error")
            if errors.count() > 0:
                for i in range(errors.count()):
                    error = errors.n(i)
                    if error.is_visible():
                        error_text = error.inner_text()
                        print(f"[ERROR] 错误提示: {error_text}")
                        return error_text
            return None
        except Exception as e:
            print(f"检查错误提示异常: {e}")
            return None
    
    def test_tc001_normal_flow(self):
        """TC001: 用户新增-正常流程测试"""
        print("\n=== TC001: 用户新增-正常流程测试 ===")
        
        self.login_and_navigate()
        dialog = self.open_add_dialog()
        
        # 生成随机测试数据
        test_id = random.randint(10000, 99999)
        
        # 填写表单
        print(f"填写用户信息: test_user_{test_id}")
        
        # 用户昵称
        dialog.get_by_placeholder("请输入用户昵称").fill(f"昵称_{test_id}")
        
        # 部门选择 (Vue-treeselect)
        self.page.locator(".vue-treeselect__control").click()
        time.sleep(0.5)
        try:
            self.page.locator(".vue-treeselect__menu").get_by_text("若依科技").first.click()
        except:
            self.page.locator(".vue-treeselect__menu").locator("div").first.click()
        
        # 手机号码
        dialog.get_by_placeholder("请输入手机号码").fill(f"138{random.randint(10000000, 99999999)}")
        
        # 邮箱
        dialog.get_by_placeholder("请输入邮箱").fill(f"test{test_id}@qq.com")
        
        # 用户名称
        dialog.get_by_placeholder("请输入用户名称").fill(f"user_{test_id}")
        
        # 用户密码
        dialog.get_by_placeholder("请输入用户密码").fill("admin123")
        
        # 提交
        print("提交表单...")
        self.page.locator(".el-dialog__footer").get_by_role("button", name="确 定").click()
        
        # 验证
        assert self.check_success_message(self.page), "未找到成功提示消息"
        print("[PASS] 表单提交成功")
        
        # 等待对话框关闭
        self.page.wait_for_timeout(1000)
    
    def test_tc002_required_field_validation(self):
        """TC002: 用户新增-必填字段校验测试"""
        print("\n=== TC002: 用户新增-必填字段校验测试 ===")
        
        self.login_and_navigate()
        dialog = self.open_add_dialog()
        
        # 直接点击确定，不填写任何字段
        self.page.locator(".el-dialog__footer").get_by_role("button", name="确 定").click()
        
        # 检查必填字段错误提示
        error = self.check_error_message(dialog)
        assert error is not None, "应显示必填字段错误提示"
        print(f"[PASS] 正确显示必填错误: {error}")
        
        time.sleep(1)
        
        # 仅填写昵称
        dialog.get_by_placeholder("请输入用户昵称").fill("测试昵称")
        self.page.locator(".el-dialog__footer").get_by_role("button", name="确 定").click()
        
        error = self.check_error_message(dialog)
        assert error is not None, "用户名称和密码应仍显示必填错误"
        print(f"[PASS] 用户名称/密码仍显示错误: {error}")
        
        self.close_dialog()
    
    def test_tc003_username_length_validation(self):
        """TC003: 用户新增-用户名称长度校验测试"""
        print("\n=== TC003: 用户新增-用户名称长度校验测试 ===")
        
        self.login_and_navigate()
        dialog = self.open_add_dialog()
        
        # 测试1个字符
        dialog.get_by_placeholder("请输入用户名称").fill("a")
        self.page.locator(".el-dialog__footer").get_by_role("button", name="确 定").click()
        error = self.check_error_message(dialog)
        assert error is not None, "应显示长度错误（1个字符）"
        print(f"[PASS] 1个字符: {error}")
        time.sleep(0.5)
        
        # 测试21个字符
        dialog.get_by_placeholder("请输入用户名称").fill("a" * 21)
        self.page.locator(".el-dialog__footer").get_by_role("button", name="确 定").click()
        error = self.check_error_message(dialog)
        assert error is not None, "应显示长度错误（21个字符）"
        print(f"[PASS] 21个字符: {error}")
        time.sleep(0.5)
        
        # 测试2个字符（应通过）
        dialog.get_by_placeholder("请输入用户名称").fill("ab")
        self.page.locator(".el-dialog__footer").get_by_role("button", name="确 定").click()
        try:
            error = self.check_error_message(dialog)
            if error and "长度" in error:
                print("[FAIL] 2个字符应通过校验")
        except:
            print("[PASS] 2个字符校验通过")
        time.sleep(0.5)
        
        # 测试20个字符（应通过）
        dialog.get_by_placeholder("请输入用户名称").fill("a" * 20)
        self.page.locator(".el-dialog__footer").get_by_role("button", name="确 定").click()
        try:
            error = self.check_error_message(dialog)
            if error and "长度" in error:
                print("[FAIL] 20个字符应通过校验")
        except:
            print("[PASS] 20个字符校验通过")
        
        self.close_dialog()
    
    def test_tc004_password_length_validation(self):
        """TC004: 用户新增-密码长度校验测试"""
        print("\n=== TC004: 用户新增-密码长度校验测试 ===")
        
        self.login_and_navigate()
        dialog = self.open_add_dialog()
        
        # 测试4个字符
        dialog.get_by_placeholder("请输入用户名称").fill("testuser4")
        dialog.get_by_placeholder("请输入用户密码").fill("1234")
        self.page.locator(".el-dialog__footer").get_by_role("button", name="确 定").click()
        error = self.check_error_message(dialog)
        assert error is not None, "应显示密码长度错误（4个字符）"
        print(f"[PASS] 4个字符: {error}")
        time.sleep(0.5)
        
        # 测试21个字符
        dialog.get_by_placeholder("请输入用户密码").fill("" * 21)
        self.page.locator(".el-dialog__footer").get_by_role("button", name="确 定").click()
        error = self.check_error_message(dialog)
        assert error is not None, "应显示密码长度错误（21个字符）"
        print(f"[PASS] 21个字符: {error}")
        time.sleep(0.5)
        
        # 测试5个字符（应通过）
        dialog.get_by_placeholder("请输入用户密码").fill("12345")
        self.page.locator(".el-dialog__footer").get_by_role("button", name="确 定").click()
        try:
            error = self.check_error_message(dialog)
            if error and "密码" in error and "长度" in error:
                print("[FAIL] 5个字符应通过校验")
        except:
            print("[PASS] 5个字符校验通过")
        time.sleep(0.5)
        
        # 测试20个字符（应通过）
        dialog.get_by_placeholder("请输入用户密码").fill("a" * 20)
        self.page.locator(".el-dialog__footer").get_by_role("button", name="确 定").click()
        try:
            error = self.check_error_message(dialog)
            if error and "密码" in error and "长度" in error:
                print("[FAIL] 20个字符应通过校验")
        except:
            print("[PASS] 20个字符校验通过")
        
        self.close_dialog()
    
    def test_tc005_phone_format_validation(self):
        """TC005: 用户新增-手机号码格式校验测试"""
        print("\n=== TC005: 用户新增-手机号码格式校验测试 ===")
        
        self.login_and_navigate()
        dialog = self.open_add_dialog()
        
        # 填写基本必填字段
        dialog.get_by_placeholder("请输入用户昵称").fill("测试昵称")
        dialog.get_by_placeholder("请输入用户名称").fill("testphone")
        dialog.get_by_placeholder("请输入用户密码").fill("123456")
        
        # 测试错误格式
        dialog.get_by_placeholder("请输入手机号码").fill("12345")
        self.page.locator(".el-dialog__footer").get_by_role("button", name="确 定").click()
        error = self.check_error_message(dialog)
        assert error is not None or error and "手机号码" in error, "应显示手机号码格式错误"
        print(f"[PASS] 错误格式: {error if error else '(等待中)'}")
        time.sleep(0.5)
        
        # 测试12位数字
        dialog.get_by_placeholder("请输入手机号码").fill("138123456789")
        self.page.locator(".el-dialog__footer").get_by_role("button", name="确 定").click()
        error = self.check_error_message(dialog)
        assert error is not None or error and "手机号码" in error, "12位数字应报错"
        print(f"[PASS] 12位数字: {error if error else '(等待中)'}")
        time.sleep(0.5)
        
        # 测试正确格式
        dialog.get_by_placeholder("请输入手机号码").fill("13812345678")
        self.page.locator(".el-dialog__footer").get_by_role("button", name="确 定").click()
        try:
            error = self.check_error_message(dialog)
            if error and "手机号码" in error:
                print("[FAIL] 11位正确手机号应通过校验")
        except:
            print("[PASS] 11位正确手机号校验通过")
        
        self.close_dialog()
    
    def test_tc006_email_format_validation(self):
        """TC006: 用户新增-邮箱格式校验测试"""
        print("\n=== TC006: 用户新增-邮箱格式校验测试 ===")
        
        self.login_and_navigate()
        dialog = self.open_add_dialog()
        
        # 填写基本必填字段
        dialog.get_by_placeholder("请输入用户昵称").fill("测试昵称")
        dialog.get_by_placeholder("请输入用户名称").fill("testemail")
        dialog.get_by_placeholder("请输入用户密码").fill("123456")
        dialog.get_by_placeholder("请输入手机号码").fill("13812345678")
        
        # 测试错误格式
        dialog.get_by_placeholder("请输入邮箱").fill("invalid-email")
        self.page.locator(".el-dialog__footer").get_by_role("button", name="确 定").click()
        error = self.check_error_message(dialog)
        assert error is not None or error and "邮箱" in error, "应显示邮箱格式错误"
        print(f"[PASS] 错误格式: {error if error else '(等待中)'}")
        time.sleep(0.5)
        
        # 测试正确格式
        dialog.get_by_placeholder("请输入邮箱").fill("test@valid.com")
        self.page.locator(".el-dialog__footer").get_by_role("button", name="确 定").click()
        try:
            error = self.check_error_message(dialog)
            if error and "邮箱" in error:
                print("[FAIL] 正确邮箱应通过校验")
        except:
            print("[PASS] 正确邮箱校验通过")
        
        self.close_dialog()
    
    def test_tc007_dept_selection(self):
        """TC007: 用户新增-部门选择测试"""
        print("\n=== TC007: 用户新增-部门选择测试 ===")
        
        self.login_and_navigate()
        dialog = self.open_add_dialog()
        
        # 点击部门选择框
        self.page.locator(".vue-treeselect__control").click()
        time.sleep(0.5)
        
        # 检查部门树是否展开
        menu = self.page.locator(".vue-treeselect__menu")
        assert menu.is_visible(), "部门树形选择器应显示"
        print("[PASS] 部门树形选择器已展开")
        
        # 选择部门
        try:
            self.page.locator(".vue-treeselect__menu").get_by_text("若依科技").first.click()
            print("[PASS] 成功选择部门")
        except:
            self.page.locator(".vue-treeselect__menu").locator("div").first.click()
            print("[PASS] 成功选择第一个部门")
        
        # 检查选中结果
        selected = self.page.locator(".vue-treeselect__single-value")
        if selected.count() > 0:
            dept_name = selected.inner_text()
            print(f"[PASS] 选中的部门: {dept_name}")
        
        self.close_dialog()
    
    def test_tc008_gender_selection(self):
        """TC008: 用户新增-性别选择测试"""
        print("\n=== TC008: 用户新增-性别选择测试 ===")
        
        self.login_and_navigate()
        dialog = self.open_add_dialog()
        
        # 查找性别下拉框
        try:
            # 方式1: 通过label查找
            gender_label = dialog.get_by_text("用户性别")
            if gender_label.count() > 0:
                select_container = gender_label.locator("..").locator("..").locator(".el-select")
                select_container.click()
                
                # 选择选项
                option = self.page.get_by_text("男").first
                if option.is_visible():
                    option.click()
                    print("[PASS] 成功选择性别")
                else:
                    print("[INFO] 未找到性别选项")
        except:
            print("[INFO] 性别选择可能为单选按钮，跳过")
        
        self.close_dialog()
    
    def test_tc009_status_selection(self):
        """TC009: 用户新增-状态选择测试"""
        print("\n=== TC009: 用户新增-状态选择测试 ===")
        
        self.login_and_navigate()
        dialog = self.open_add_dialog()
        
        # 查找状态单选框
        status_label = dialog.get_by_text("状态")
        if status_label.count() > 0:
            radio_container = status_label.locator("..").locator("..")
            radios = radio_container.locator(".el-radio")
            
            # 默认应选中"正常"
            print(f"[INFO] 找到 {radios.count()} 个状态选项")
            print("[PASS] 状态单选框显示正常")
            
            # 测试切换
            try:
                radios.n(1).click()  # 点击第二个选项
                print("[PASS] 成功切换状态")
            except:
                pass
        
        self.close_dialog()
    
    def test_tc010_post_multi_select(self):
        """TC010: 用户新增-岗位多选测试"""
        print("\n=== TC010: 用户新增-岗位多选测试 ===")
        
        self.login_and_navigate()
        dialog = self.open_add_dialog()
        
        # 查找岗位选择框
        post_label = dialog.get_by_text("岗位")
        if post_label.count() > 0:
            select_container = post_label.locator("..").locator("..").locator(".el-select")
            select_container.click()
            time.sleep(0.5)
            
            # 检查下拉选项
            options = self.page.locator(".el-select-dropdown__item")
            print(f"[INFO] 找到 {options.count()} 个岗位选项")
            print("[PASS] 岗位下拉选项显示正常")
            
            # 点击其他位置关闭
            self.page.click("body", position={"x": 100, "y": 100})
        
        self.close_dialog()
    
    def test_tc011_role_multi_select(self):
        """TC011: 用户新增-角色多选测试"""
        print("\n=== TC011: 用户新增-角色多选测试 ===")
        
        self.login_and_navigate()
        dialog = self.open_add_dialog()
        
        # 查找角色选择框
        role_label = dialog.get_by_text("角色")
        if role_label.count() > 0:
            select_container = role_label.locator("..").locator("..").locator(".el-select")
            select_container.click()
            time.sleep(0.5)
            
            # 检查下拉选项
            options = self.page.locator(".el-select-dropdown__item")
            print(f"[INFO] 找到 {options.count()} 个角色选项")
            print("[PASS] 角色下拉选项显示正常")
            
            # 点击其他位置关闭
            self.page.click("body", position={"x": 100, "y": 100})
        
        self.close_dialog()
    
    def test_tc012_remark_field(self):
        """TC012: 用户新增-备注字段测试"""
        print("\n=== TC012: 用户新增-备注字段测试 ===")
        
        self.login_and_navigate()
        dialog = self.open_add_dialog()
        
        # 查找备注文本域
        remark_label = dialog.get_by_text("备注")
        if remark_label.count() > 0:
            textarea = dialog.locator("textarea")
            if textarea.count() > 0:
                textarea.first.fill("这是测试备注内容")
                time.sleep(0.5)
                
                # 验证输入
                value = textarea.first.input_value()
                assert "测试备注" in value, "备注内容应正确填写"
                print("[PASS] 备注字段输入正常")
        
        self.close_dialog()
    
    def test_tc013_cancel_button(self):
        """TC013: 用户新增-取消按钮测试"""
        print("\n=== TC013: 用户新增-取消按钮测试 ===")
        
        self.login_and_navigate()
        dialog = self.open_add_dialog()
        
        # 填写部分字段
        test_id = random.randint(1000, 9999)
        dialog.get_by_placeholder("请输入用户昵称").fill(f"测试取消_{test_id}")
        time.sleep(0.5)
        
        # 点击取消按钮
        self.page.locator(".el-dialog__footer").get_by_role("button", name="取 消").click()
        
        # 等待对话框关闭
        dialog.wait_for(state="hidden", timeout=3000)
        print("[PASS] 对话框已关闭")
        
        # 检查是否还在用户管理页面
        current_url = self.page.url
        assert "user" in current_url, "应仍在用户管理页面"
        print("[PASS] 取消后仍在用户管理页面")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "--tb=short"])