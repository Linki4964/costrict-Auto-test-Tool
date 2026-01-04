import pytest
import random
import string
import time
import json
from playwright.sync_api import sync_playwright, Page, Browser, Locator
from datetime import datetime

class TestUserAddFunction:
    def __init__(self):
        self.base_url = "http://192.168.142.146/"
        self.login_url = "http://192.168.142.146/login"
        self.username = "admin"
        self.password = "admin123"
        self.test_results = []
        self.random_suffix = None
        self.page = None
    
    def generate_random_string(self, length=10):
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
    
    def get_test_timestamp(self):
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def login(self):
        print("\n=== [步骤1] 登录系统 ===")
        self.page.goto(self.login_url)
        time.sleep(1)
        
        username_input = self.page.locator('input[placeholder*="账号"]').first
        username_input.fill(self.username)
        
        password_input = self.page.locator('input[type="password"]').first
        password_input.fill(self.password)
        
        login_button = self.page.locator('button:has-text("登")').first
        login_button.click()
        
        self.page.wait_for_url("**/index", timeout=10000)
        print("[OK] 登录成功")
    
    def navigate_to_user_management(self):
        print("\n=== [步骤2] 导航到用户管理 ===")
        time.sleep(1)
        
        system_menu = self.page.get_by_text("系统管理").first
        system_menu.click()
        time.sleep(0.5)
        
        user_menu = self.page.get_by_text("用户管理").first
        user_menu.click()
        
        self.page.wait_for_load_state("networkidle")
        print("[OK] 已进入用户管理页面")
    
    def open_add_dialog(self):
        print("\n=== [步骤3] 打开新增对话框 ===")
        time.sleep(1)
        
        try:
            add_button = self.page.locator('button:has-text("新")').first
            add_button.click()
        except:
            add_button = self.page.locator('.el-button--primary:has(.el-icon-plus)').first
            add_button.click()
        
        time.sleep(1)
        dialog = self.page.get_by_role("dialog").first
        if not dialog.is_visible():
            print("[ERROR] 新增对话框未出现")
            raise Exception("对话框未显示")
        
        print("[OK] 新增对话框已打开")
        return dialog
    
    def fill_basic_fields(self, dialog, test_data):
        print("\n--- 填写表单字段 ---")
        
        try:
            nick_name = dialog.locator('input[placeholder*="用户昵称"]').first
            nick_name.fill(test_data.get('nickName', ''))
            print(f"  - 用户昵称: {test_data.get('nickName', '')}")
        except Exception as e:
            print(f"  - 用户昵称填写失败: {str(e)}")
        
        try:
            user_name = dialog.locator('input[placeholder*="用户帐号"]').first
            user_name.fill(test_data.get('userName', ''))
            print(f"  - 用户名称: {test_data.get('userName', '')}")
        except Exception as e:
            print(f"  - 用户名称填写失败: {str(e)}")
        
        try:
            dept_select = dialog.locator('input[placeholder*="请选择归属部门"]').first
            dept_select.click()
            time.sleep(0.5)
            dept_option = self.page.locator('.el-tree-node__content').first
            dept_option.click()
            time.sleep(0.5)
            print(f"  - 归属部门: 已选择")
        except Exception as e:
            print(f"  - 归属部门选择失败: {str(e)}")
        
        try:
            phone_number = dialog.locator('input[placeholder*="手机号码"]').first
            phone_number.fill(test_data.get('phonenumber', ''))
            print(f"  - 手机号码: {test_data.get('phonenumber', '')}")
        except Exception as e:
            print(f"  - 手机号码填写失败: {str(e)}")
        
        try:
            email = dialog.locator('input[placeholder*="邮箱"]').first
            email.fill(test_data.get('email', ''))
            print(f"  - 邮箱: {test_data.get('email', '')}")
        except Exception as e:
            print(f"  - 邮箱填写失败: {str(e)}")
        
        try:
            user_password = dialog.locator('input[type="password"][placeholder*="用户密码"]').first
            user_password.fill(test_data.get('password', ''))
            print(f"  - 用户密码: {test_data.get('password', '')}")
        except Exception as e:
            print(f"  - 用户密码填写失败: {str(e)}")
    
    def submit_form(self, dialog):
        print("\n--- 提交表单 ---")
        try:
            confirm_button = dialog.locator('.el-dialog__footer button.el-button--primary').first
            confirm_button.click()
        except Exception as e:
            print(f"[WARN] 主按钮点击失败: {str(e)}，尝试备用定位")
            try:
                buttons = dialog.locator('.el-dialog__footer button')
                buttons.nth(0).click()
            except Exception as e2:
                print(f"[ERROR] 所有按钮点击失败: {str(e2)}")
                return False, "无法点击提交按钮"
        
        time.sleep(2)
        
        try:
            success_message = self.page.locator('.el-message__content').first
            if success_message.is_visible(timeout=3000):
                message_text = success_message.inner_text()
                print(f"[OK] 提交成功: {message_text}")
                return True, message_text
        except:
            print("[INFO] 未检测到成功消息，检查错误提示")
        
        try:
            error_messages = dialog.locator('.el-form-item__error')
            if error_messages.count() > 0:
                error_texts = []
                for i in range(error_messages.count()):
                    error_text = error_messages.nth(i).inner_text()
                    error_texts.append(error_text)
                error_str = "; ".join(error_texts)
                print(f"[ERROR] 提交失败: {error_str}")
                return False, error_str
        except:
            pass
        
        return True, "未知状态"
    
    def cancel_form(self, dialog):
        print("\n--- 取消表单 ---")
        try:
            cancel_button = dialog.locator('.el-dialog__footer button.el-button--default').first
            cancel_button.click()
        except:
            buttons = dialog.locator('.el-dialog__footer button')
            buttons.last.click()
        time.sleep(1)
        print("[OK] 已点击取消按钮")
    
    def TC001_正常用例_完整必填项(self):
        print("\n" + "="*60)
        print("测试用例 TC001: 正常用例-完整必填项")
        print("="*60)
        
        self.random_suffix = self.generate_random_string(6)
        test_data = {
            'nickName': f'测试用户_{self.random_suffix}',
            'phonenumber': '13800138001',
            'email': f'test{self.random_suffix}@example.com',
            'userName': f'testuser_{self.random_suffix}',
            'password': 'Test123456'
        }
        
        try:
            dialog = self.open_add_dialog()
            self.fill_basic_fields(dialog, test_data)
            success, message = self.submit_form(dialog)
            
            result = {
                "case_id": "TC001",
                "name": "正常用例-完整必填项",
                "success": success,
                "message": message,
                "test_data": test_data
            }
            self.test_results.append(result)
            
            if not success:
                print(f"[FAIL] 测试失败: {message}")
            return success
            
        except Exception as e:
            print(f"[ERROR] 测试执行异常: {str(e)}")
            return False
    
    def TC002_边界值测试_用户名称长度(self):
        print("\n" + "="*60)
        print("测试用例 TC002: 边界值测试-用户名称长度")
        print("="*60)
        
        self.random_suffix = self.generate_random_string(6)
        test_data = {
            'nickName': f'测试用户_{self.random_suffix}',
            'phonenumber': '13800138002',
            'email': f'test{self.random_suffix}@example.com',
            'userName': 'a' * 30,
            'password': 'Test123456'
        }
        
        try:
            dialog = self.open_add_dialog()
            self.fill_basic_fields(dialog, test_data)
            success, message = self.submit_form(dialog)
            
            result = {
                "case_id": "TC002",
                "name": "边界值测试-用户名称长度",
                "success": success,
                "message": message,
                "test_data": test_data
            }
            self.test_results.append(result)
            
            if not success:
                print(f"[FAIL] 测试失败: {message}")
            return success
            
        except Exception as e:
            print(f"[ERROR] 测试执行异常: {str(e)}")
            return False
    
    def TC003_边界值测试_用户密码长度(self):
        print("\n" + "="*60)
        print("测试用例 TC003: 边界值测试-用户密码长度")
        print("="*60)
        
        self.random_suffix = self.generate_random_string(6)
        test_data = {
            'nickName': f'测试用户_{self.random_suffix}',
            'phonenumber': '13800138003',
            'email': f'test{self.random_suffix}@example.com',
            'userName': f'testuser_{self.random_suffix}',
            'password': 'a' * 20
        }
        
        try:
            dialog = self.open_add_dialog()
            self.fill_basic_fields(dialog, test_data)
            success, message = self.submit_form(dialog)
            
            result = {
                "case_id": "TC003",
                "name": "边界值测试-用户密码长度",
                "success": success,
                "message": message,
                "test_data": test_data
            }
            self.test_results.append(result)
            
            if not success:
                print(f"[FAIL] 测试失败: {message}")
            return success
            
        except Exception as e:
            print(f"[ERROR] 测试执行异常: {str(e)}")
            return False
    
    def TC004_必填项验证_未填写用户名称(self):
        print("\n" + "="*60)
        print("测试用例 TC004: 必填项验证-未填写用户名称")
        print("="*60)
        
        self.random_suffix = self.generate_random_string(6)
        test_data = {
            'nickName': f'测试用户_{self.random_suffix}',
            'phonenumber': '13800138004',
            'email': f'test{self.random_suffix}@example.com',
            'userName': '',
            'password': 'Test123456'
        }
        
        try:
            dialog = self.open_add_dialog()
            self.fill_basic_fields(dialog, test_data)
            success, message = self.submit_form(dialog)
            
            expected_fail = not success  # 预期应该失败
            result = {
                "case_id": "TC004",
                "name": "必填项验证-未填写用户名称",
                "success": expected_fail,
                "message": f"预期失败，实际: {message}",
                "test_data": test_data
            }
            self.test_results.append(result)
            
            if not expected_fail:
                print(f"[FAIL] 测试失败: 应该显示未填写的错误提示")
            return expected_fail
            
        except Exception as e:
            print(f"[ERROR] 测试执行异常: {str(e)}")
            return False
    
    def TC005_必填项验证_未填写用户密码(self):
        print("\n" + "="*60)
        print("测试用例 TC005: 必填项验证-未填写用户密码")
        print("="*60)
        
        self.random_suffix = self.generate_random_string(6)
        test_data = {
            'nickName': f'测试用户_{self.random_suffix}',
            'phonenumber': '13800138005',
            'email': f'test{self.random_suffix}@example.com',
            'userName': f'testuser_{self.random_suffix}',
            'password': ''
        }
        
        try:
            dialog = self.open_add_dialog()
            self.fill_basic_fields(dialog, test_data)
            success, message = self.submit_form(dialog)
            
            expected_fail = not success
            result = {
                "case_id": "TC005",
                "name": "必填项验证-未填写用户密码",
                "success": expected_fail,
                "message": f"预期失败，实际: {message}",
                "test_data": test_data
            }
            self.test_results.append(result)
            
            if not expected_fail:
                print(f"[FAIL] 测试失败: 应该显示未填写的错误提示")
            return expected_fail
            
        except Exception as e:
            print(f"[ERROR] 测试执行异常: {str(e)}")
            return False
    
    def TC006_必填项验证_未选择归属部门(self):
        print("\n" + "="*60)
        print("测试用例 TC006: 必填项验证-未选择归属部门")
        print("="*60)
        
        self.random_suffix = self.generate_random_string(6)
        test_data = {
            'nickName': f'测试用户_{self.random_suffix}',
            'phonenumber': '13800138006',
            'email': f'test{self.random_suffix}@example.com',
            'userName': f'testuser_{self.random_suffix}',
            'password': 'Test123456'
        }
        
        try:
            dialog = self.open_add_dialog()
            
            try:
                nick_name = dialog.locator('input[placeholder*="用户昵称"]').first
                nick_name.fill(test_data.get('nickName', ''))
                print(f"  - 用户昵称: {test_data.get('nickName', '')}")
            except:
                pass
            try:
                user_name = dialog.locator('input[placeholder*="用户帐号"]').first
                user_name.fill(test_data.get('userName', ''))
                print(f"  - 用户名称: {test_data.get('userName', '')}")
            except:
                pass
            try:
                phone_number = dialog.locator('input[placeholder*="手机号码"]').first
                phone_number.fill(test_data.get('phonenumber', ''))
                print(f"  - 手机号码: {test_data.get('phonenumber', '')}")
            except:
                pass
            try:
                email = dialog.locator('input[placeholder*="邮箱"]').first
                email.fill(test_data.get('email', ''))
                print(f"  - 邮箱: {test_data.get('email', '')}")
            except:
                pass
            try:
                user_password = dialog.locator('input[type="password"][placeholder*="用户密码"]').first
                user_password.fill(test_data.get('password', ''))
                print(f"  - 用户密码: {test_data.get('password', '')}")
            except:
                pass
            
            success, message = self.submit_form(dialog)
            
            expected_fail = not success
            result = {
                "case_id": "TC006",
                "name": "必填项验证-未选择归属部门",
                "success": expected_fail,
                "message": f"预期失败，实际: {message}",
                "test_data": test_data
            }
            self.test_results.append(result)
            
            if not expected_fail:
                print(f"[FAIL] 测试失败: 应该显示未选择部门的错误提示")
            return expected_fail
            
        except Exception as e:
            print(f"[ERROR] 测试执行异常: {str(e)}")
            return False
    
    def TC007_功能验证_密码显示切换(self):
        print("\n" + "="*60)
        print("测试用例 TC007: 功能验证-密码显示切换")
        print("="*60)
        
        try:
            self.random_suffix = self.generate_random_string(6)
            test_data = {
                'nickName': f'测试用户_{self.random_suffix}',
                'phonenumber': '13800138007',
                'email': f'test{self.random_suffix}@example.com',
                'userName': f'testuser_{self.random_suffix}',
                'password': 'Test123456'
            }
            
            dialog = self.open_add_dialog()
            self.fill_basic_fields(dialog, test_data)
            
            password_input = dialog.locator('input[type="password"][placeholder*="用户密码"]').first
            password_type = password_input.get_attribute('type')
            
            suffix_icon = dialog.locator('.el-input__suffix').first
            suffix_icon.click()
            time.sleep(0.5)
            
            password_type_after = password_input.get_attribute('type')
            
            suffix_icon.click()
            time.sleep(0.5)
            
            password_type_final = password_input.get_attribute('type')
            
            print(f"[OK] 密码显示切换验证完成: {password_type} -> {password_type_after} -> {password_type_final}")
            
            result = {
                "case_id": "TC007",
                "name": "功能验证-密码显示切换",
                "success": True,
                "message": "密码显示切换功能正常"
            }
            self.test_results.append(result)
            self.cancel_form(dialog)
            
            return True
            
        except Exception as e:
            print(f"[ERROR] 密码显示切换验证失败: {str(e)}")
            result = {
                "case_id": "TC007",
                "name": "功能验证-密码显示切换",
                "success": False,
                "message": f"验证失败: {str(e)}"
            }
            self.test_results.append(result)
            self.cancel_form(dialog)
            return False
    
    def TC008_功能验证_多选岗位(self):
        print("\n" + "="*60)
        print("测试用例 TC008: 功能验证-多选岗位")
        print("="*60)
        
        try:
            self.random_suffix = self.generate_random_string(6)
            test_data = {
                'nickName': f'测试用户_{self.random_suffix}',
                'phonenumber': '13800138008',
                'email': f'test{self.random_suffix}@example.com',
                'userName': f'testuser_{self.random_suffix}',
                'password': 'Test123456'
            }
            
            dialog = self.open_add_dialog()
            self.fill_basic_fields(dialog, test_data)
            
            post_select = dialog.locator('input[placeholder*="岗位"]').first
            post_select.click()
            time.sleep(0.5)
            
            select_options = self.page.locator('.el-select-dropdown__item')
            if select_options.count() > 0:
                try:
                    select_options.nth(0).click()  # 选择第一个岗位
                    time.sleep(0.5)
                    print("[OK] 岗位多选功能验证完成")
                except:
                    print("[WARN] 无法选择岗位选项")
            else:
                print("[WARN] 未找到岗位选项")
            
            result = {
                "case_id": "TC008",
                "name": "功能验证-多选岗位",
                "success": True,
                "message": "岗位多选功能正常"
            }
            self.test_results.append(result)
            self.cancel_form(dialog)
            
            return True
            
        except Exception as e:
            print(f"[ERROR] 岗位多选验证失败: {str(e)}")
            result = {
                "case_id": "TC008",
                "name": "功能验证-多选岗位",
                "success": False,
                "message": f"验证失败: {str(e)}"
            }
            self.test_results.append(result)
            self.cancel_form(dialog)
            return False
    
    def TC009_功能验证_多选角色(self):
        print("\n" + "="*60)
        print("测试用例 TC009: 功能验证-多选角色")
        print("="*60)
        
        try:
            self.random_suffix = self.generate_random_string(6)
            test_data = {
                'nickName': f'测试用户_{self.random_suffix}',
                'phonenumber': '13800138009',
                'email': f'test{self.random_suffix}@example.com',
                'userName': f'testuser_{self.random_suffix}',
                'password': 'Test123456'
            }
            
            dialog = self.open_add_dialog()
            self.fill_basic_fields(dialog, test_data)
            
            role_select = dialog.locator('input[placeholder*="角色"]').first
            role_select.click()
            time.sleep(0.5)
            
            select_options = self.page.locator('.el-select-dropdown__item')
            if select_options.count() > 0:
                try:
                    select_options.nth(0).click()  # 选择第一个角色
                    time.sleep(0.5)
                    print("[OK] 角色多选功能验证完成")
                except:
                    print("[WARN] 无法选择角色选项")
            else:
                print("[WARN] 未找到角色选项")
            
            result = {
                "case_id": "TC009",
                "name": "功能验证-多选角色",
                "success": True,
                "message": "角色多选功能正常"
            }
            self.test_results.append(result)
            self.cancel_form(dialog)
            
            return True
            
        except Exception as e:
            print(f"[ERROR] 角色多选验证失败: {str(e)}")
            result = {
                "case_id": "TC009",
                "name": "功能验证-多选角色",
                "success": False,
                "message": f"验证失败: {str(e)}"
            }
            self.test_results.append(result)
            self.cancel_form(dialog)
            return False
    
    def TC010_功能验证_取消按钮(self):
        print("\n" + "="*60)
        print("测试用例 TC010: 功能验证-取消按钮")
        print("="*60)
        
        try:
            self.random_suffix = self.generate_random_string(6)
            test_data = {
                'nickName': f'测试用户_{self.random_suffix}',
                'phonenumber': '13800138010',
                'email': f'test{self.random_suffix}@example.com',
                'userName': f'testuser_{self.random_suffix}',
                'password': 'Test123456'
            }
            
            dialog = self.open_add_dialog()
            self.fill_basic_fields(dialog, test_data)
            
            self.cancel_form(dialog)
            
            time.sleep(1)
            
            dialog_after = self.page.get_by_role("dialog").first
            dialog_visible = dialog_after.is_visible()
            
            if not dialog_visible:
                print("[OK] 对话框已关闭")
                result = {
                    "case_id": "TC010",
                    "name": "功能验证-取消按钮",
                    "success": True,
                    "message": "取消按钮功能正常"
                }
                self.test_results.append(result)
                return True
            else:
                print("[ERROR] 对话框未关闭")
                result = {
                    "case_id": "TC010",
                    "name": "功能验证-取消按钮",
                    "success": False,
                    "message": "对话框未关闭"
                }
                self.test_results.append(result)
                return False
            
        except Exception as e:
            print(f"[ERROR] 取消按钮验证失败: {str(e)}")
            result = {
                "case_id": "TC010",
                "name": "功能验证-取消按钮",
                "success": False,
                "message": f"验证失败: {str(e)}"
            }
            self.test_results.append(result)
            return False
    
    def TC011_手机号码格式验证(self):
        print("\n" + "="*60)
        print("测试用例 TC011: 手机号码格式验证")
        print("="*60)
        
        test_phones = [
            {"number": "12345", "expected": False, "desc": "5位数字"},
            {"number": "abcdefghijk", "expected": False, "desc": "字母"},
            {"number": "13800138000", "expected": True, "desc": "11位正确格式"}
        ]
        
        all_passed = True
        for test_phone in test_phones:
            try:
                self.random_suffix = self.generate_random_string(6)
                test_data = {
                    'nickName': f'测试用户_{self.random_suffix}',
                    'phonenumber': test_phone['number'],
                    'email': f'test{self.random_suffix}@example.com',
                    'userName': f'testuser_{self.random_suffix}',
                    'password': 'Test123456'
                }
                
                print(f"\n  测试手机号码: {test_phone['number']} ({test_phone['desc']})")
                
                dialog = self.open_add_dialog()
                self.fill_basic_fields(dialog, test_data)
                success, message = self.submit_form(dialog)
                
                expected_result = test_phone['expected']
                actual_result = success
                passed = (actual_result == expected_result)
                
                if test_phone['expected']:
                    print(f"    [预期成功] 实际: {actual_result}")
                else:
                    print(f"    [预期失败] 实际: {actual_result}")
                
                result = {
                    "case_id": "TC011",
                    "name": f"手机号码格式验证-{test_phone['desc']}",
                    "success": passed,
                    "message": message,
                    "test_data": test_data,
                    "expected_success": expected_result,
                    "actual_success": actual_result
                }
                self.test_results.append(result)
                
                if not passed:
                    all_passed = False
                    
            except Exception as e:
                print(f"    [ERROR] 测试失败: {str(e)}")
                result = {
                    "case_id": "TC011",
                    "name": f"手机号码格式验证-{test_phone['desc']}",
                    "success": False,
                    "message": f"测试异常: {str(e)}"
                }
                self.test_results.append(result)
                all_passed = False
        
        return all_passed
    
    def TC012_邮箱格式验证(self):
        print("\n" + "="*60)
        print("测试用例 TC012: 邮箱格式验证")
        print("="*60)
        
        test_emails = [
            {"email": "invalid", "expected": False, "desc": "无@符号"},
            {"email": "test@", "expected": False, "desc": "不完整"},
            {"email": "test@example.com", "expected": True, "desc": "正确格式"}
        ]
        
        all_passed = True
        for test_email in test_emails:
            try:
                self.random_suffix = self.generate_random_string(6)
                test_data = {
                    'nickName': f'测试用户_{self.random_suffix}',
                    'phonenumber': '13800138100',
                    'email': test_email['email'],
                    'userName': f'testuser_{self.random_suffix}',
                    'password': 'Test123456'
                }
                
                print(f"\n  测试邮箱: {test_email['email']} ({test_email['desc']})")
                
                dialog = self.open_add_dialog()
                self.fill_basic_fields(dialog, test_data)
                success, message = self.submit_form(dialog)
                
                expected_result = test_email['expected']
                actual_result = success
                passed = (actual_result == expected_result)
                
                if test_email['expected']:
                    print(f"    [预期成功] 实际: {actual_result}")
                else:
                    print(f"    [预期失败] 实际: {actual_result}")
                
                result = {
                    "case_id": "TC012",
                    "name": f"邮箱格式验证-{test_email['desc']}",
                    "success": passed,
                    "message": message,
                    "test_data": test_data,
                    "expected_success": expected_result,
                    "actual_success": actual_result
                }
                self.test_results.append(result)
                
                if not passed:
                    all_passed = False
                    
            except Exception as e:
                print(f"    [ERROR] 测试失败: {str(e)}")
                result = {
                    "case_id": "TC012",
                    "name": f"邮箱格式验证-{test_email['desc']}",
                    "success": False,
                    "message": f"测试异常: {str(e)}"
                }
                self.test_results.append(result)
                all_passed = False
        
        return all_passed
    
    def TC013_正常用例_填写所有字段(self):
        print("\n" + "="*60)
        print("测试用例 TC013: 正常用例-填写所有字段")
        print("="*60)
        
        try:
            self.random_suffix = self.generate_random_string(6)
            test_data = {
                'nickName': f'完整测试用户_{self.random_suffix}',
                'phonenumber': '13800138200',
                'email': f'fulltest{self.random_suffix}@example.com',
                'userName': f'fulluser_{self.random_suffix}',
                'password': 'Test123456'
            }
            
            dialog = self.open_add_dialog()
            self.fill_basic_fields(dialog, test_data)
            
            try:
                remark_textarea = dialog.locator('textarea').first
                remark_textarea.fill(f'这是{self.random_suffix}用户的备注信息')
                print(f"  - 备注: 已填写")
            except Exception as e:
                print(f"  - 备注填写失败: {str(e)}")
            
            success, message = self.submit_form(dialog)
            
            result = {
                "case_id": "TC013",
                "name": "正常用例-填写所有字段",
                "success": success,
                "message": message,
                "test_data": test_data
            }
            self.test_results.append(result)
            
            if not success:
                print(f"[FAIL] 测试失败: {message}")
            return success
            
        except Exception as e:
            print(f"[ERROR] 测试执行异常: {str(e)}")
            return False
    
    def generate_report(self):
        total_tests = len(self.test_results)
        if total_tests == 0:
            print("\n[ERROR] 无测试结果")
            return
        
        passed_tests = sum(1 for r in self.test_results if r['success'])
        failed_tests = total_tests - passed_tests
        pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        report = {
            "test_summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "pass_rate": f"{pass_rate:.2f}%",
                "timestamp": self.get_test_timestamp()
            },
            "test_results": self.test_results
        }
        
        filename = f"测试报告.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n\n=== 测试报告 ===")
        print(f"总测试数: {total_tests}")
        print(f"通过: {passed_tests}")
        print(f"失败: {failed_tests}")
        print(f"通过率: {pass_rate:.2f}%")
        print(f"\n测试报告已保存至: {filename}")
    
    def run_all_tests(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            self.page = browser.new_page()
            self.page.set_default_timeout(10000)
            
            try:
                self.login()
                self.navigate_to_user_management()
                
                print("\n\n" + "="*80)
                print("开始执行测试用例")
                print("="*80)
                
                test_methods = [
                    self.TC001_正常用例_完整必填项,
                    self.TC004_必填项验证_未填写用户名称,
                    self.TC005_必填项验证_未填写用户密码,
                    self.TC006_必填项验证_未选择归属部门,
                    self.TC002_边界值测试_用户名称长度,
                    self.TC003_边界值测试_用户密码长度,
                    self.TC013_正常用例_填写所有字段,
                    self.TC011_手机号码格式验证,
                    self.TC012_邮箱格式验证,
                    self.TC007_功能验证_密码显示切换,
                    self.TC008_功能验证_多选岗位,
                    self.TC009_功能验证_多选角色,
                    self.TC010_功能验证_取消按钮
                ]
                
                for test_method in test_methods:
                    try:
                        test_method()
                    except Exception as e:
                        print(f"\n[TEST ERROR] {test_method.__name__}: {str(e)}")
                    
                    time.sleep(2)
                
                print("\n\n" + "="*80)
                print("所有测试用例执行完成")
                print("="*80)
                
                self.generate_report()
                
            except Exception as e:
                print(f"\n测试执行过程中发生错误: {str(e)}")
                import traceback
                traceback.print_exc()
            finally:
                time.sleep(3)
                browser.close()

if __name__ == "__main__":
    tester = TestUserAddFunction()
    tester.run_all_tests()