import pytest
from playwright.sync_api import Page, expect
import re


class TestUserManagement:
    """
    若依管理系统-用户管理功能测试
    
    本测试仅包含经过验证可复现的测试用例
    """
    
    base_url = "http://192.168.142.146"
    
    def clear_form_data(self, page: Page):
        """清除表单自动填充数据"""
        page.evaluate("""
            () => {
                document.querySelectorAll('input').forEach(input => {
                    input.value = '';
                });
            }
        """)
    
    def login(self, page: Page):
        """登录系统"""
        page.goto(f"{self.base_url}/login?", wait_until="networkidle", timeout=30000)
        self.clear_form_data(page)
        page.wait_for_timeout(500)
        
        page.get_by_placeholder("账号").fill("admin")
        page.get_by_placeholder("密码").fill("admin123")
        page.get_by_role("button", name="登 录").click()
        page.wait_for_load_state("networkidle", timeout=30000)
        page.wait_for_timeout(3000)
        
        expect(page).to_have_url(re.compile(r".*\/index.*"))
    
    def navigate_to_user_management(self, page: Page):
        """导航到用户管理页面"""
        page.goto(f"{self.base_url}/system/user", wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(2000)
        expect(page).to_have_url(re.compile(r".*system\/user.*"))
    
    def test_user_delete_functionality(self, page: Page):
        """
        TC001: 用户删除功能测试
        
        测试目标：验证用户管理页面的删除功能是否可访问
        
        测试步骤：
        1. 登录系统
        2. 导航到用户管理页面
        3. 查找并点击删除按钮
        4. 验证删除确认对话框
        5. 关闭对话框（不实际删除）
        
        预期结果：能够成功打开删除确认对话框
        """
        # 登录
        self.login(page)
        print("✅ 登录成功")
        
        # 导航到用户管理
        self.navigate_to_user_management(page)
        print("✅ 导航到用户管理页面")
        
        # 验证URL正确
        expect(page).to_have_url("http://192.168.142.146/system/user")
        print("✅ URL验证正确")
        
        # 等待页面完全加载
        page.wait_for_timeout(3000)
        
        # 查找删除按钮
        delete_buttons = page.locator("button:has-text('删除')")
        button_count = delete_buttons.count()
        print(f"✅ 找到 {button_count} 个删除按钮")
        
        # 至少需要2个用户（admin + 其他用户）才能安全测试删除功能
        if button_count > 1:
            # 点击第二个删除按钮（确保不删除admin用户）
            print("📍 点击第二个删除按钮（非admin用户）")
            delete_buttons.nth(1).click()
            page.wait_for_timeout(2000)
            
            # 验证删除确认对话框出现
            # 直接检查对话框文本是否包含"是否确认删除"
            try:
                delete_confirm_text = page.get_by_text("是否确认删除用户")
                expect(delete_confirm_text).to_be_visible()
                print("✅ 删除确认对话框已打开")
                
                # 查找并点击取消按钮
                cancel_button = page.locator(".el-message-box__btns").get_by_text("取消")
                if cancel_button.count() > 0:
                    cancel_button.click()
                    page.wait_for_timeout(1000)
                    print("✅ 已取消删除操作")
                else:
                    page.keyboard.press("Escape")
                    page.wait_for_timeout(1000)
                    print("✅ 已通过ESC取消删除操作")
                
                print("✅ TC001 测试通过：删除功能可访问且对话框正常")
                
            except Exception as e:
                print(f"⚠️ 删除对话框验证异常: {str(e)}")
                # 截图用于调试
                page.screenshot(path="工作区/tc001_delete_debug_final.png")
                raise
        else:
            print("⚠️ 用户数量不足，无法安全测试删除功能")
            print("   需要至少2个用户（admin + 其他用户）")
            pytest.skip("用户数量不足")