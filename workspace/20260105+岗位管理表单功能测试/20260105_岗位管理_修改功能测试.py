# -*- coding: utf-8 -*-
import pytest
from playwright.sync_api import sync_playwright, expect
import random

def generate_random_id():
    """生成随机ID"""
    return str(random.randint(1000, 9999))

class TestPostUpdate:
    """岗位管理修改功能测试"""
    
    @pytest.fixture(scope="function")
    def browser_context(self):
        """初始化浏览器上下文"""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()
            yield page
            context.close()
            browser.close()
    
    def login_and_navigate(self, page):
        """登录并导航到岗位管理页面"""
        page.goto("http://192.168.142.146/login?redirect=%2Findex")
        page.wait_for_load_state("networkidle")
        
        # 点击登录按钮
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
    def test_update_post_normal(self, browser_context):
        """TC001: 正常修改岗位信息"""
        page = browser_context
        self.login_and_navigate(page)
        
        # 等待表格加载
        page.wait_for_timeout(1000)
        
        # 选中第一条记录
        page.locator("tr").nth(1).locator(".el-checkbox").click()
        
        # 点击修改按钮（工具栏第二个按钮）
        update_buttons = page.get_by_role("button", name="修改").all()
        if len(update_buttons) >= 2:
            update_buttons[1].click()
        else:
            raise Exception("未找到修改按钮")
        
        # 等待对话框出现
        dialog = page.get_by_role("dialog")
        dialog.wait_for(state="visible", timeout=5000)
        
        # 生成随机数据
        test_id = generate_random_id()
        
        print(f"修改岗位信息: 修改后岗位_{test_id}")
        
        # 修改岗位名称
        name_input = dialog.get_by_placeholder("请输入岗位名称")
        name_input.fill(f"修改后岗位_{test_id}")
        
        # 修改岗位状态为停用
        disabled_radio_label = dialog.locator("label").filter(has_text="停用")
        disabled_radio_label.click()
        
        # 修改备注
        remark_input = dialog.get_by_placeholder("请输入内容")
        remark_input.fill("修改后的备注信息")
        
        # 提交表单
        print("提交修改...")
        page.locator(".dialog-footer").get_by_role("button", name="确 定").click()
        
        # 验证修改成功提示
        success_msgs = ["操作成功", "修改成功", "保存成功"]
        success_found = False
        for msg in success_msgs:
            try:
                expect(page.get_by_text(msg)).to_be_visible(timeout=2000)
                success_found = True
                print(f"[PASS] 找到提示: {msg}")
                break
            except:
                continue
        
        assert success_found, "未找到修改成功的提示"
        
        # 验证对话框关闭
        dialog.wait_for(state="hidden", timeout=3000)
        print("对话框已关闭，测试通过")
    
    @pytest.mark.validation
    def test_update_post_without_name(self, browser_context):
        """TC002: 修改岗位-清空必填项校验"""
        page = browser_context
        self.login_and_navigate(page)
        
        # 等待表格加载
        page.wait_for_timeout(1000)
        
        # 选中一条包含"修改后"的记录
        table_rows = page.locator("table tbody tr").all()
        if len(table_rows) > 0:
            page.locator("tr").nth(1).locator(".el-checkbox").click()
        else:
            raise Exception("表格中没有数据")
        
        # 点击修改按钮
        update_buttons = page.get_by_role("button", name="修改").all()
        if len(update_buttons) >= 2:
            update_buttons[1].click()
        else:
            raise Exception("未找到修改按钮")
        
        # 等待对话框出现
        dialog = page.get_by_role("dialog")
        dialog.wait_for(state="visible", timeout=5000)
        
        # 清空岗位名称
        name_input = dialog.get_by_placeholder("请输入岗位名称")
        name_input.fill("")
        
        # 点击确定按钮
        page.locator(".dialog-footer").get_by_role("button", name="确 定").click()
        
        # 验证岗位名称必填提示
        expect(page.get_by_text("岗位名称不能为空")).to_be_visible(timeout=2000)
        print("[PASS] 岗位名称必填校验通过")
    
    @pytest.mark.happy
    def test_update_post_only_remark(self, browser_context):
        """TC003: 修改岗位-仅修改备注"""
        page = browser_context
        self.login_and_navigate(page)
        
        # 等待表格加载
        page.wait_for_timeout(1000)
        
        # 选中一条记录
        page.locator("tr").nth(1).locator(".el-checkbox").click()
        
        # 点击修改按钮
        update_buttons = page.get_by_role("button", name="修改").all()
        if len(update_buttons) >= 2:
            update_buttons[1].click()
        else:
            raise Exception("未找到修改按钮")
        
        # 等待对话框出现
        dialog = page.get_by_role("dialog")
        dialog.wait_for(state="visible", timeout=5000)
        
        # 仅修改备注
        test_id = generate_random_id()
        remark_input = dialog.get_by_placeholder("请输入内容")
        remark_input.fill(f"仅修改备注_{test_id}")
        
        # 提交表单
        print("提交修改...")
        page.locator(".dialog-footer").get_by_role("button", name="确 定").click()
        
        # 验证修改成功提示
        success_msgs = ["操作成功", "修改成功", "保存成功"]
        success_found = False
        for msg in success_msgs:
            try:
                expect(page.get_by_text(msg)).to_be_visible(timeout=2000)
                success_found = True
                print(f"[PASS] 找到提示: {msg}")
                break
            except:
                continue
        
        assert success_found, "未找到修改成功的提示"
        print("[PASS] 仅修改备注测试通过")
    
    @pytest.mark.happy
    def test_update_post_switch_status(self, browser_context):
        """TC004: 修改岗位-切换状态"""
        page = browser_context
        self.login_and_navigate(page)
        
        # 等待表格加载
        page.wait_for_timeout(1000)
        
        # 选中一条记录
        page.locator("tr").nth(1).locator(".el-checkbox").click()
        
        # 点击修改按钮
        update_buttons = page.get_by_role("button", name="修改").all()
        if len(update_buttons) >= 2:
            update_buttons[1].click()
        else:
            raise Exception("未找到修改按钮")
        
        # 等待对话框出现
        dialog = page.get_by_role("dialog")
        dialog.wait_for(state="visible", timeout=5000)
        
        # 切换岗位状态为正常
        normal_radio_label = dialog.locator("label").filter(has_text="正常")
        normal_radio_label.click()
        
        # 提交表单
        print("提交修改...")
        page.locator(".dialog-footer").get_by_role("button", name="确 定").click()
        
        # 验证修改成功提示
        success_msgs = ["操作成功", "修改成功", "保存成功"]
        success_found = False
        for msg in success_msgs:
            try:
                expect(page.get_by_text(msg)).to_be_visible(timeout=2000)
                success_found = True
                print(f"[PASS] 找到提示: {msg}")
                break
            except:
                continue
        
        assert success_found, "未找到修改成功的提示"
        print("[PASS] 状态切换测试通过")

if __name__ == "__main__":
    pytest.main([
        __file__,
        "-v",
        "-s",
        "--tb=short"
    ])