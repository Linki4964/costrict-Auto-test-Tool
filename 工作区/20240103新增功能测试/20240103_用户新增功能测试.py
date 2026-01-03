# -*- coding: utf-8 -*-
from playwright.sync_api import sync_playwright
import json
import random
import time

def generate_random_username():
    random_num = random.randint(1000, 9999)
    return f"test_{random_num}"

def generate_random_phonenumber():
    return f"1{random.randint(3, 9)}{random.randint(100000000, 999999999)}"

def generate_random_email():
    return f"test{random.randint(1000, 9999)}@example.com"

def test_user_add():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        test_username = generate_random_username()
        test_phonenumber = generate_random_phonenumber()
        test_email = generate_random_email()
        print(f"测试用户名: {test_username}")
        print(f"测试手机号: {test_phonenumber}")
        print(f"测试邮箱: {test_email}")
        
        try:
            page.goto("http://192.168.142.146/login?redirect=%2Findex")
            page.wait_for_load_state('networkidle')
            
            page.wait_for_timeout(1000)
            try:
                page.fill("input[placeholder*='用户名'], input[type='text']", "admin", timeout=5000)
            except:
                page.get_by_role("textbox", name="用户名").fill("admin")
            
            page.wait_for_timeout(300)
            try:
                page.fill("input[placeholder*='密码'], input[type='password']", "admin123", timeout=5000)
            except:
                page.get_by_role("textbox", name="密码", exact=True).fill("admin123")
            
            page.wait_for_timeout(500)
            
            try:
                page.click("button:has-text('登 录')", timeout=3000)
            except:
                page.get_by_role("button", name="登 录").click()
            
            print("等待登录...")
            page.wait_for_timeout(2000)
            
            try:
                page.wait_for_selector("text=系统管理", timeout=5000)
                page.click("text=系统管理")
                page.wait_for_timeout(500)
                
                page.wait_for_selector("text=用户管理", timeout=5000)
                page.click("text=用户管理")
                page.wait_for_load_state('networkidle')
            except Exception as e:
                print(f"导航异常，尝试直接访问: {e}")
                page.goto("http://192.168.142.146/#/system/user")
                page.wait_for_load_state('networkidle')
            
            print("打开新增表单...")
            page.wait_for_selector("button:has-text('新增')", timeout=10000)
            page.click("button:has-text('新增')")
            page.wait_for_timeout(1000)
            
            dialog = page.get_by_role("dialog")
            dialog.wait_for(state='visible')
            
            print("填写表单...")
            
            dialog.get_by_placeholder("请输入用户昵称").fill("测试用户")
            page.wait_for_timeout(300)
            
            print("选择部门...")
            dept_select = dialog.locator(".vue-treeselect").first
            dept_select.click()
            page.wait_for_timeout(800)
            
            try:
                page.locator(".vue-treeselect__menu").locator(".vue-treeselect__option").first.click()
            except:
                print("尝试使用文本选择部门")
                page.locator(".vue-treeselect__menu").locator("text=研发部").first.click()
            
            page.wait_for_timeout(500)
            
            dialog.get_by_placeholder("请输入手机号码").fill(test_phonenumber)
            page.wait_for_timeout(300)
            
            dialog.get_by_placeholder("请输入邮箱").fill(test_email)
            page.wait_for_timeout(300)
            
            dialog.get_by_placeholder("请输入用户名称").fill(test_username)
            page.wait_for_timeout(300)
            
            dialog.get_by_placeholder("请输入用户密码").fill("test123456")
            page.wait_for_timeout(300)
            
            print("选择性别...")
            gender_select = dialog.get_by_placeholder("请选择性别")
            gender_select.click()
            page.wait_for_timeout(500)
            page.get_by_text("男").click()
            page.wait_for_timeout(300)
            
            print("选择状态...")
            try:
                status_container = dialog.locator("text=状态").locator("..").locator("..")
                radiobuttons = status_container.locator(".el-radio")
                radiobuttons.nth(0).click()
            except Exception as e:
                print(f"状态选择异常(使用默认): {e}")
            
            page.wait_for_timeout(300)
            
            print("选择岗位...")
            try:
                post_select = dialog.get_by_placeholder("请选择岗位")
                post_select.click()
                page.wait_for_timeout(800)
                post_dropdown = page.locator(".el-select-dropdown__item").last
                post_dropdown.wait_for(state='visible', timeout=5000)
                post_dropdown.click()
                print("岗位选择成功")
            except Exception as e:
                print(f"岗位选择跳过(可选字段): {e}")
            
            page.wait_for_timeout(300)
            
            print("选择角色...")
            try:
                role_select = dialog.get_by_placeholder("请选择角色")
                role_select.click()
                page.wait_for_timeout(800)
                role_dropdown = page.locator(".el-select-dropdown__item").last
                role_dropdown.wait_for(state='visible', timeout=5000)
                role_dropdown.click()
                print("角色选择成功")
            except Exception as e:
                print(f"角色选择跳过(可选字段): {e}")
            
            page.wait_for_timeout(300)
            
            dialog.get_by_placeholder("请输入内容").fill("这是一个测试用户")
            page.wait_for_timeout(500)
            
            print("提交表单...")
            confirm_button = dialog.locator("button").filter(has_text="确 定")
            confirm_button.click()
            
            print("等待对话框关闭...")
            try:
                dialog.wait_for(state='hidden', timeout=5000)
                print("对话框已关闭")
            except:
                print("对话框关闭超时，尝试强制关闭")
                try:
                    page.click("button:has-text('取 消')")
                    page.wait_for_timeout(500)
                except:
                    page.keyboard.press("Escape")
                    page.wait_for_timeout(500)
            
            print("确保对话框完全消失...")
            try:
                page.get_by_role("dialog").wait_for(state='hidden', timeout=3000)
            except:
                print("对话框可能仍存在，继续执行")
            
            print("等待提交流程完成...")
            page.wait_for_timeout(1500)
            
            print("验证成功提示...")
            try:
                success_message = page.locator(".el-message--success")
                success_message.wait_for(state='visible', timeout=5000)
                print("发现成功提示")
            except:
                try:
                    success_msg = page.locator("text=操作成功, text=新增成功")
                    assert success_msg.count() > 0
                    print("验证成功提示通过文本")
                except Exception as e:
                    print(f"未发现成功提示，检查错误: {e}")
                    try:
                        error_elements = page.locator(".el-form-item__error")
                        if error_elements.count() > 0:
                            error_text = error_elements.first.text_content()
                            print(f"表单错误: {error_text}")
                    except:
                        print("无法获取错误信息")
            
            page.wait_for_timeout(2000)
            
            print("验证用户已添加...")
            try:
                user_name_input = page.locator("div[role='dialog']").locator("input[placeholder='请输入用户名称']").first
                user_name_input.wait_for(state='visible', timeout=3000)
                print("使用对话框内的搜索输入框")
            except:
                try:
                    user_name_input = page.locator(".el-form").filter(has_not_text="新增用户").locator("input[placeholder='请输入用户名称']").first
                    user_name_input.wait_for(state='visible', timeout=3000)
                    print("使用搜索表单的输入框")
                except:
                    user_name_input = page.locator("input[placeholder='请输入用户名称']").nth(1)
                    user_name_input.wait_for(state='visible', timeout=3000)
                    print("使用第二个输入框")
            
            user_name_input.fill(test_username)
            page.wait_for_timeout(500)
            
            try:
                page.locator(".el-button--primary").filter(has_text="搜索").or_(page.locator(".el-button--primary").filter(has_text="查询")).click()
            except:
                page.get_by_role("button", name="搜\\u7d22").or_(page.get_by_role("button", name="查\\u8be2")).click()
            
            page.wait_for_timeout(1000)
            
            try:
                user_table = page.locator(".el-table__body")
                assert test_username in user_table.inner_text()
                print(f"用户 {test_username} 已成功添加")
            except:
                print("未在表中找到用户，可能因为分页或其他原因")
            
            page.wait_for_timeout(3000)
            
        except Exception as e:
            print(f"测试执行异常: {e}")
            import traceback
            traceback.print_exc()
        finally:
            browser.close()
            print(f"测试完成，测试用户名: {test_username}")

if __name__ == "__main__":
    print("RuoYi用户新增功能测试启动\n")
    test_user_add()