# -*- coding: utf-8 -*-
import pytest
from playwright.sync_api import Page, Expect, expect
import time
import random

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
        
    def generate_unique_user_name(self):
        """生成唯一的用户名，长度控制在2-20字符之间"""
        timestamp = str(int(time.time()))[-6:]  # 取后6位
        random_num = str(random.randint(10, 99))  # 2位随机数
        return f"aut{timestamp}{random_num}"  # 总长度: 3 + 6 + 2 = 11字符
        
    def test_login(self, page: Page):
        """
        步骤1-4: 登录系统
        """
        page.goto(self.base_url)
        page.get_by_placeholder("账号").fill(self.username)
        page.get_by_placeholder("密码").fill(self.password)
        page.get_by_role("button", name="登 录").click()
        page.wait_for_load_state("networkidle")
        expect(page).to_have_url(f"{self.base_url}/index")

    def test_navigate_to_user_management(self, page: Page):
        """
        步骤5-8: 导航到用户管理页面
        """
        self.test_login(page)
        page.get_by_text("系统管理").click()
        time.sleep(0.5)
        page.get_by_role("link", name="用户管理").first.click()
        page.wait_for_load_state("networkidle")
        expect(page).to_have_url(f"{self.base_url}/system/user")

    def test_tc001_normal_user_add(self, page: Page):
        """
        TC001: 正常用户新增
        """
        self.test_navigate_to_user_management(page)
        
        # 生成唯一的用户名（长度控制在2-20字符）
        unique_username = self.generate_unique_user_name()
        
        # 点击新增按钮
        page.get_by_role("button", name="新增").click()
        page.wait_for_timeout(1000)
        
        # 获取对话框定位器，后续所有操作都在对话框中进行
        dialog = page.get_by_role("dialog", name="添加用户")
        
        # 填写用户昵称（在对话框中查找）
        dialog.get_by_placeholder("请输入用户昵称").fill(f"自动化测试用户{unique_username}")
        
        # 选择归属部门（使用XPath定位）
        dialog.locator("xpath=//label[contains(text(),'归属部门')]/following-sibling::div//div[contains(@class,'vue-treeselect')]").first.click()
        page.wait_for_timeout(500)
        
        # 尝试点击第一个树形选项
        try:
            page.locator("xpath=//div[contains(@class,'vue-treeselect__label')]")[0].click()
        except:
            pass
        
        # 填写手机号码（在对话框中查找）
        random_phone = f"13800{random.randint(100000, 999999)}"
        dialog.get_by_placeholder("请输入手机号码").fill(random_phone)
        
        # 填写用户名称（在对话框中查找）
        dialog.get_by_placeholder("请输入用户名称").fill(unique_username)
        
        # 填写用户密码（在对话框中查找）
        dialog.get_by_placeholder("请输入用户密码").fill("test123456")
        
        # 点击确定按钮（在对话框中查找）
        dialog.get_by_role("button", name="确 定").click()
        
        # 等待操作完成
        page.wait_for_timeout(2000)
        
        # 验证对话框关闭
        try:
            expect(dialog).to_be_hidden()
        except AssertionError:
            # 如果对话框未关闭，可能是验证错误，检查是否有错误消息
            try:
                error_message = dialog.locator(".el-form-item__error").inner_text()
                print(f"表单验证错误: {error_message}")
            except:
                print("对话框未关闭，可能是其他原因")
            raise
        
        # 验证成功提示消息
        success_message = page.locator(".el-message").inner_text()
        assert "新增成功" in success_message, f"未显示成功提示: {success_message}"
        
        print(f"TC001: 正常用户新增-测试通过 (用户名: {unique_username})")

    def test_tc013_cancel_add(self, page: Page):
        """
        TC013: 取消新增操作
        """
        self.test_navigate_to_user_management(page)
        page.get_by_role("button", name="新增").click()
        page.wait_for_timeout(1000)
        
        dialog = page.get_by_role("dialog", name="添加用户")
        dialog.get_by_placeholder("请输入用户昵称").fill("测试用户011")
        dialog.get_by_role("button", name="取 消").click()
        page.wait_for_timeout(500)
        expect(dialog).to_be_hidden()
        print("TC013: 取消新增操作-测试通过")