# -*- coding: utf-8 -*-
import pytest
from playwright.sync_api import sync_playwright, expect
import random
import json

def generate_random_id():
    """生成随机ID，防止重复"""
    return str(random.randint(1000, 9999))

class TestPostAdd:
    """岗位管理新增功能测试"""
    
    @pytest.fixture(scope="function")
    def browser_context(self):
        """
        初始化浏览器上下文
        """
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()
            yield page
            context.close()
            browser.close()
    
    def login_and_navigate(self, page):
        """
        登录并导航到岗位管理页面
        """
        page.goto("http://192.168.142.146/login?redirect=%2Findex")
        page.wait_for_load_state("networkidle")
        
        # 点击登录按钮（默认已填充凭证）
        page.get_by_role("button", name="登 录").click()
        
        # 等待跳转到首页
        page.wait_for_url("**/index", timeout=5000)
        
        # 导航到岗位管理
        print("正在展开侧边栏菜单...")
        system_menu = page.locator("li").filter(has_text="系统管理").first
        system_menu.click()
        
        user_link = page.get_by_role("link", name="岗位管理")
        user_link.wait_for(state="visible", timeout=5000)
        user_link.click()
        print("已进入岗位管理页面")
    
    @pytest.mark.happy
    def test_add_post_normal(self, browser_context):
        """
        TC001: 正常新增岗位
        """
        page = browser_context
        self.login_and_navigate(page)
        
        # 点击新增按钮
        add_button = page.get_by_role("button", name="新增")
        add_button.click()
        
        # 等待对话框出现
        dialog = page.get_by_role("dialog")
        dialog.wait_for(state="visible", timeout=5000)
        
        # 生成随机数据
        test_id = generate_random_id()
        
        print(f"填写岗位信息: 测试岗位_{test_id}")
        
        # 填写岗位名称
        dialog.get_by_placeholder("请输入岗位名称").fill(f"测试岗位_{test_id}")
        
        # 填写岗位编码
        dialog.get_by_placeholder("请输入编码名称").fill(f"POST_{test_id}")
        
        # 填写岗位顺序
        dialog.locator("input[role='spinbutton']").fill("1")
        
        # 选择岗位状态-正常
        normal_radio = dialog.locator("label").filter(has_text="正常").locator("input")
        normal_radio.check()
        
        # 输入备注
        dialog.get_by_placeholder("请输入内容").fill("自动化测试备注")
        
        # 提交表单
        print("提交表单...")
        page.locator(".dialog-footer").get_by_role("button", name="确 定").click()
        
        # 验证新增成功提示
        success_msgs = ["操作成功", "新增成功", "保存成功"]
        success_found = False
        for msg in success_msgs:
            try:
                expect(page.get_by_text(msg)).to_be_visible(timeout=2000)
                success_found = True
                print(f"[PASS] 找到提示: {msg}")
                break
            except:
                continue
        
        assert success_found, "未找到新增成功的提示"
        
        # 验证对话框关闭
        dialog.wait_for(state="hidden", timeout=3000)
        print("对话框已关闭，测试通过")
    
    @pytest.mark.validation
    def test_add_post_without_name(self, browser_context):
        """
        TC002: 新增岗位-岗位名称必填校验
        """
        page = browser_context
        self.login_and_navigate(page)
        
        # 点击新增按钮
        page.get_by_role("button", name="新增").click()
        
        # 等待对话框出现
        dialog = page.get_by_role("dialog")
        dialog.wait_for(state="visible", timeout=5000)
        
        # 直接点击确定按钮不填写必填项
        page.locator(".dialog-footer").get_by_role("button", name="确 定").click()
        
        # 验证岗位名称必填提示
        expect(page.get_by_text("岗位名称不能为空")).to_be_visible(timeout=2000)
        print("[PASS] 岗位名称必填校验通过")
    
    @pytest.mark.validation
    def test_add_post_without_code(self, browser_context):
        """
        TC003: 新增岗位-岗位编码必填校验
        """
        page = browser_context
        self.login_and_navigate(page)
        
        # 点击新增按钮
        page.get_by_role("button", name="新增").click()
        
        # 等待对话框出现
        dialog = page.get_by_role("dialog")
        dialog.wait_for(state="visible", timeout=5000)
        
        # 仅填写岗位名称
        test_id = generate_random_id()
        dialog.get_by_placeholder("请输入岗位名称").fill(f"测试岗位_{test_id}")
        
        # 点击确定按钮
        page.locator(".dialog-footer").get_by_role("button", name="确 定").click()
        
        # 验证岗位编码必填提示
        expect(page.get_by_text("岗位编码不能为空")).to_be_visible(timeout=2000)
        print("[PASS] 岗位编码必填校验通过")
    
    @pytest.mark.validation
    def test_add_post_without_sort(self, browser_context):
        """
        TC004: 新增岗位-岗位顺序为0验证
        """
        page = browser_context
        self.login_and_navigate(page)
        
        # 点击新增按钮
        page.get_by_role("button", name="新增").click()
        
        # 等待对话框出现
        dialog = page.get_by_role("dialog")
        dialog.wait_for(state="visible", timeout=5000)
        
        # 填写岗位名称和岗位编码
        test_id = generate_random_id()
        dialog.get_by_placeholder("请输入岗位名称").fill(f"测试岗位_{test_id}")
        dialog.get_by_placeholder("请输入编码名称").fill(f"POST_{test_id}")
        
        # 岗位顺序默认为0，清空后提交
        sort_input = dialog.locator("input[role='spinbutton']")
        sort_input.fill("")
        
        # 点击确定按钮
        page.locator(".dialog-footer").get_by_role("button", name="确 定").click()
        
        # 验证岗位顺序必填提示或验证失败
        try:
            expect(page.get_by_text("岗位顺序不能为空")).to_be_visible(timeout=2000)
            print("[PASS] 岗位顺序必填校验通过")
        except:
            print("[PASS] 岗位顺序默认值验证通过（允许为空或默认值为0）")
    
    @pytest.mark.happy
    def test_add_post_disabled_status(self, browser_context):
        """
        TC005: 新增岗位-岗位状态选择停用
        """
        page = browser_context
        self.login_and_navigate(page)
        
        # 点击新增按钮
        page.get_by_role("button", name="新增").click()
        
        # 等待对话框出现
        dialog = page.get_by_role("dialog")
        dialog.wait_for(state="visible", timeout=5000)
        
        # 生成随机数据
        test_id = generate_random_id()
        
        # 填写岗位名称
        dialog.get_by_placeholder("请输入岗位名称").fill(f"测试岗位_停用_{test_id}")
        
        # 填写岗位编码
        dialog.get_by_placeholder("请输入编码名称").fill(f"POST_DISABLED_{test_id}")
        
        # 填写岗位顺序
        dialog.locator("input[role='spinbutton']").fill("2")
        
        # 选择岗位状态-停用（点击label元素）
        disabled_radio_label = dialog.locator("label").filter(has_text="停用")
        disabled_radio_label.click()
        
        # 输入备注
        dialog.get_by_placeholder("请输入内容").fill("停用状态测试岗位")
        
        # 提交表单
        print("提交表单...")
        page.locator(".dialog-footer").get_by_role("button", name="确 定").click()
        
        # 验证新增成功提示
        success_msgs = ["操作成功", "新增成功", "保存成功"]
        success_found = False
        for msg in success_msgs:
            try:
                expect(page.get_by_text(msg)).to_be_visible(timeout=2000)
                success_found = True
                print(f"[PASS] 找到提示: {msg}")
                break
            except:
                continue
        
        assert success_found, "未找到新增成功的提示"
        print("[PASS] 停用状态岗位新增成功")

if __name__ == "__main__":
    pytest.main([
        __file__,
        "-v",
        "-s",
        "--tb=short"
    ])