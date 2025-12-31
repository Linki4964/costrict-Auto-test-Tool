"""
登录界面功能测试脚本
基于Selenium实现的自动化测试
"""

import sys
import io
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import traceback

# 设置UTF-8编码输出以支持Windows命令行
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


class LoginPage:
    """登录页面元素定位器"""
    
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        
    # 账号输入框
    USERNAME_INPUT = (By.CSS_SELECTOR, "input.el-input__inner[placeholder='账号']")
    USERNAME_INPUT_FALLBACK = (By.CSS_SELECTOR, "input.el-input__inner")
    
    # 密码输入框
    PASSWORD_INPUT = (By.CSS_SELECTOR, "input.el-input__inner[placeholder='密码']")
    PASSWORD_INPUT_FALLBACK = (By.CSS_SELECTOR, "input.el-input__inner[type='password']")
    
    # 登录按钮
    LOGIN_BUTTON = (By.CLASS_NAME, "el-button.el-button--primary.el-button--medium")
    LOGIN_BUTTON_FALLBACK = (By.CSS_SELECTOR, "button.el-button.el-button--primary")
    
    # 记住密码复选框
    REMEMBER_PASSWORD_LABEL = (By.CLASS_NAME, "el-checkbox")
    REMEMBER_PASSWORD_CHECKBOX = (By.CLASS_NAME, "el-checkbox__original")
    
    def get_username_input(self):
        """获取账号输入框元素"""
        try:
            element = self.wait.until(EC.presence_of_element_located(self.USERNAME_INPUT))
            return element
        except:
            elements = self.driver.find_elements(*self.USERNAME_INPUT_FALLBACK)
            if elements:
                return elements[0]
            raise Exception("找不到账号输入框")
            
    def get_password_input(self):
        """获取密码输入框元素"""
        try:
            element = self.wait.until(EC.presence_of_element_located(self.PASSWORD_INPUT))
            return element
        except:
            elements = self.driver.find_elements(*self.PASSWORD_INPUT_FALLBACK)
            if len(elements) > 0:
                return elements[0]
            raise Exception("找不到密码输入框")
            
    def get_login_button(self):
        """获取登录按钮元素"""
        try:
            element = self.wait.until(EC.element_to_be_clickable(self.LOGIN_BUTTON))
            return element
        except:
            try:
                element = self.wait.until(EC.element_to_be_clickable(self.LOGIN_BUTTON_FALLBACK))
                return element
            except Exception as e:
                raise Exception(f"找不到登录按钮: {str(e)}")
                
    def clear_form(self):
        """清空表单"""
        try:
            username_input = self.get_username_input()
            username_input.clear()
            password_input = self.get_password_input()
            password_input.clear()
        except Exception as e:
            print(f"清空表单失败: {str(e)}")
            
    def clear_cookies(self):
        """清除Cookies"""
        self.driver.delete_all_cookies()
        
    def wait_for_page_load(self, timeout=30):
        """等待页面加载完成"""
        time.sleep(1)
        

class LoginTestRunner:
    """登录测试运行器"""
    
    def __init__(self):
        self.driver = None
        self.login_page = None
        self.url = "http://192.168.142.146/login?"
        self.test_results = []
        
    def setup_driver(self):
        """初始化浏览器驱动"""
        chrome_options = Options()
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--ignore-ssl-errors')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        # 使用有头模式以便观察测试执行过程
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.maximize_window()
        self.driver.set_page_load_timeout(30)
        self.login_page = LoginPage(self.driver)
        
    def open_login_page(self):
        """打开登录页面"""
        self.driver.get(self.url)
        time.sleep(2)
        
    def get_element_value(self, element):
        """获取元素的value属性"""
        try:
            return element.get_attribute("value") or ""
        except:
            return ""
            
    def get_input_elements(self):
        """获取所有输入框元素"""
        return self.driver.find_elements(By.CSS_SELECTOR, "input.el-input__inner")
        
    # ==================== 测试用例实现 ====================
    
    def tc_login_001_clear_prefilled_info(self):
        """TC-LOGIN-001: 清除预填信息测试"""
        case_id = "TC-LOGIN-001"
        case_name = "清除预填信息测试"
        print(f"\n{'='*60}")
        print(f"执行测试用例: {case_id} - {case_name}")
        print(f"{'='*60}")
        
        result = {
            "case_id": case_id,
            "case_name": case_name,
            "status": "UNEXECUTED",
            "steps": []
        }
        
        try:
            # 步骤1: 清除Cookies并刷新页面
            print("步骤1: 清除Cookies")
            self.login_page.clear_cookies()
            time.sleep(1)
            self.driver.refresh()
            time.sleep(2)
            result["steps"].append({"step": "清除Cookies", "status": "PASS"})
            
            # 步骤2: 检查账号输入框是否为空
            print("步骤2: 检查账号输入框")
            inputs = self.get_input_elements()
            if len(inputs) >= 2:
                username_value = self.get_element_value(inputs[0])
                print(f"  账号输入框value: '{username_value}'")
                if username_value == "":
                    print("  [PASS] 账号输入框为空")
                    result["steps"].append({"step": "检查账号输入框", "status": "PASS"})
                else:
                    print(f"  [FAIL] 账号输入框不为空: '{username_value}'")
                    result["steps"].append({"step": "检查账号输入框", "status": "FAIL", "detail": f"期望空值，实际值: '{username_value}'"})
            else:
                print("  [FAIL] 找不到账号输入框")
                result["steps"].append({"step": "检查账号输入框", "status": "FAIL", "detail": "找不到输入框"})
                
            # 步骤3: 检查密码输入框是否为空
            print("步骤3: 检查密码输入框")
            if len(inputs) >= 2:
                password_value = self.get_element_value(inputs[1])
                print(f"  密码输入框value: '{password_value}'")
                if password_value == "":
                    print("  [PASS] 密码输入框为空")
                    result["steps"].append({"step": "检查密码输入框", "status": "PASS"})
                else:
                    print(f"  [FAIL] 密码输入框不为空: '{password_value}'")
                    result["steps"].append({"step": "检查密码输入框", "status": "FAIL", "detail": f"期望空值，实际值: '{password_value}'"})
                    
            # 判断整体结果
            failed_steps = [s for s in result["steps"] if s["status"] == "FAIL"]
            if len(failed_steps) == 0:
                result["status"] = "PASS"
                print(f"\n测试用例 {case_id} 通过 [OK]")
            else:
                result["status"] = "FAIL"
                print(f"\n测试用例 {case_id} 失败 [FAILED]")
                
        except Exception as e:
            result["status"] = "ERROR"
            result["error"] = str(e)
            print(f"\n测试用例执行出错: {str(e)}")
            traceback.print_exc()
            
        self.test_results.append(result)
        return result
        
    def tc_login_002_normal_login(self):
        """TC-LOGIN-002: 正常登录流程测试"""
        case_id = "TC-LOGIN-002"
        case_name = "正常登录流程测试"
        print(f"\n{'='*60}")
        print(f"执行测试用例: {case_id} - {case_name}")
        print(f"{'='*60}")
        
        result = {
            "case_id": case_id,
            "case_name": case_name,
            "status": "UNEXECUTED",
            "steps": []
        }
        
        try:
            # 步骤1: 输入账号
            print("步骤1: 输入账号 admin")
            username_input = self.login_page.get_username_input()
            username_input.clear()
            username_input.send_keys("admin")
            time.sleep(0.5)
            username_value = self.get_element_value(username_input)
            print(f"  账号输入框value: '{username_value}'")
            if username_value == "admin":
                print("  [PASS] 账号输入成功")
                result["steps"].append({"step": "输入账号", "status": "PASS"})
            else:
                print(f"  [FAIL] 账号输入失败")
                result["steps"].append({"step": "输入账号", "status": "FAIL"})
                
            # 步骤2: 输入密码
            print("步骤2: 输入密码 admin123")
            password_input = self.login_page.get_password_input()
            password_input.clear()
            password_input.send_keys("admin123")
            time.sleep(0.5)
            password_value = self.get_element_value(password_input)
            print(f"  密码输入框value长度: {len(password_value)}")
            if len(password_value) == 8:
                print("  [PASS] 密码输入成功")
                result["steps"].append({"step": "输入密码", "status": "PASS"})
            else:
                print(f"  [FAIL] 密码输入失败")
                result["steps"].append({"step": "输入密码", "status": "FAIL"})
                
            # 步骤3: 点击登录按钮
            print("步骤3: 点击登录按钮")
            login_button = self.login_page.get_login_button()
            login_button.click()
            print("  [PASS] 已点击登录按钮")
            result["steps"].append({"step": "点击登录按钮", "status": "PASS"})
            
            # 步骤4: 等待并验证登录结果
            print("步骤4: 验证登录结果")
            time.sleep(3)
            current_url = self.driver.current_url
            print(f"  当前URL: {current_url}")
            
            if current_url != self.url:
                print("  [PASS] 页面已跳转")
                result["steps"].append({"step": "验证登录结果", "status": "PASS", "detail": f"跳转至: {current_url}"})
            else:
                # 检查是否有错误提示
                try:
                    error_msg = self.driver.find_element(By.CSS_SELECTOR, ".el-message__content").text
                    print(f"  登录错误: {error_msg}")
                    result["steps"].append({"step": "验证登录结果", "status": "FAIL", "detail": f"未跳转，错误信息: {error_msg}"})
                except:
                    print("  [FAIL] 页面未跳转，也未发现错误提示")
                    result["steps"].append({"step": "验证登录结果", "status": "FAIL", "detail": "页面未跳转"})
                    
            # 判断整体结果
            failed_steps = [s for s in result["steps"] if s["status"] == "FAIL"]
            if len(failed_steps) == 0:
                result["status"] = "PASS"
                print(f"\n测试用例 {case_id} 通过 [OK]")
            else:
                result["status"] = "FAIL"
                print(f"\n测试用例 {case_id} 失败 [FAILED]")
                
            # 返回登录页面以便进行下一个测试
            if current_url != self.url:
                self.driver.get(self.url)
                time.sleep(2)
                
        except Exception as e:
            result["status"] = "ERROR"
            result["error"] = str(e)
            print(f"\n测试用例执行出错: {str(e)}")
            traceback.print_exc()
            
            # 尝试返回登录页面
            self.driver.get(self.url)
            time.sleep(2)
            
        self.test_results.append(result)
        return result
        
    def tc_login_003_empty_username(self):
        """TC-LOGIN-003: 空账号登录测试"""
        case_id = "TC-LOGIN-003"
        case_name = "空账号登录测试"
        print(f"\n{'='*60}")
        print(f"执行测试用例: {case_id} - {case_name}")
        print(f"{'='*60}")
        
        result = {
            "case_id": case_id,
            "case_name": case_name,
            "status": "UNEXECUTED",
            "steps": []
        }
        
        try:
            # 确保在登录页面
            self.driver.get(self.url)
            time.sleep(2)
            
            # 步骤1: 清空账号输入框
            print("步骤1: 清空账号输入框")
            username_input = self.login_page.get_username_input()
            username_input.clear()
            result["steps"].append({"step": "清空账号输入框", "status": "PASS"})
            
            # 步骤2: 输入密码
            print("步骤2: 输入密码")
            password_input = self.login_page.get_password_input()
            password_input.clear()
            password_input.send_keys("admin123")
            result["steps"].append({"step": "输入密码", "status": "PASS"})
            
            # 步骤3: 点击登录按钮
            print("步骤3: 点击登录按钮")
            login_button = self.login_page.get_login_button()
            login_button.click()
            time.sleep(2)
            result["steps"].append({"step": "点击登录按钮", "status": "PASS"})
            
            # 验证结果
            print("验证: 检查页面状态和错误提示")
            current_url = self.driver.current_url
            print(f"  当前URL: {current_url}")
            
            if current_url == self.url:
                print("  [PASS] 页面未跳转")
                result["steps"].append({"step": "验证页面未跳转", "status": "PASS"})
            else:
                print("  [FAIL] 页面发生了跳转")
                result["steps"].append({"step": "验证页面未跳转", "status": "FAIL"})
                self.driver.get(self.url)
                time.sleep(2)
                
            # 判断整体结果
            failed_steps = [s for s in result["steps"] if s["status"] == "FAIL"]
            if len(failed_steps) == 0:
                result["status"] = "PASS"
                print(f"\n测试用例 {case_id} 通过 [OK]")
            else:
                result["status"] = "FAIL"
                print(f"\n测试用例 {case_id} 失败 [FAILED]")
                
        except Exception as e:
            result["status"] = "ERROR"
            result["error"] = str(e)
            print(f"\n测试用例执行出错: {str(e)}")
            traceback.print_exc()
            
            # 尝试返回登录页面
            self.driver.get(self.url)
            time.sleep(2)
            
        self.test_results.append(result)
        return result
        
    def tc_login_004_empty_password(self):
        """TC-LOGIN-004: 空密码登录测试"""
        case_id = "TC-LOGIN-004"
        case_name = "空密码登录测试"
        print(f"\n{'='*60}")
        print(f"执行测试用例: {case_id} - {case_name}")
        print(f"{'='*60}")
        
        result = {
            "case_id": case_id,
            "case_name": case_name,
            "status": "UNEXECUTED",
            "steps": []
        }
        
        try:
            # 确保在登录页面
            self.driver.get(self.url)
            time.sleep(2)
            
            # 步骤1: 输入账号
            print("步骤1: 输入账号")
            username_input = self.login_page.get_username_input()
            username_input.clear()
            username_input.send_keys("admin")
            result["steps"].append({"step": "输入账号", "status": "PASS"})
            
            # 步骤2: 清空密码输入框
            print("步骤2: 清空密码输入框")
            password_input = self.login_page.get_password_input()
            password_input.clear()
            result["steps"].append({"step": "清空密码输入框", "status": "PASS"})
            
            # 步骤3: 点击登录按钮
            print("步骤3: 点击登录按钮")
            login_button = self.login_page.get_login_button()
            login_button.click()
            time.sleep(2)
            result["steps"].append({"step": "点击登录按钮", "status": "PASS"})
            
            # 验证结果
            print("验证: 检查页面状态")
            current_url = self.driver.current_url
            print(f"  当前URL: {current_url}")
            
            if current_url == self.url:
                print("  [PASS] 页面未跳转")
                result["steps"].append({"step": "验证页面未跳转", "status": "PASS"})
            else:
                print("  [FAIL] 页面发生了跳转")
                result["steps"].append({"step": "验证页面未跳转", "status": "FAIL"})
                self.driver.get(self.url)
                time.sleep(2)
                
            # 判断整体结果
            failed_steps = [s for s in result["steps"] if s["status"] == "FAIL"]
            if len(failed_steps) == 0:
                result["status"] = "PASS"
                print(f"\n测试用例 {case_id} 通过 [OK]")
            else:
                result["status"] = "FAIL"
                print(f"\n测试用例 {case_id} 失败 [FAILED]")
                
        except Exception as e:
            result["status"] = "ERROR"
            result["error"] = str(e)
            print(f"\n测试用例执行出错: {str(e)}")
            traceback.print_exc()
            
            # 尝试返回登录页面
            self.driver.get(self.url)
            time.sleep(2)
            
        self.test_results.append(result)
        return result
        
    def tc_login_005_wrong_credentials(self):
        """TC-LOGIN-005: 错误账号密码登录测试"""
        case_id = "TC-LOGIN-005"
        case_name = "错误账号密码登录测试"
        print(f"\n{'='*60}")
        print(f"执行测试用例: {case_id} - {case_name}")
        print(f"{'='*60}")
        
        result = {
            "case_id": case_id,
            "case_name": case_name,
            "status": "UNEXECUTED",
            "steps": []
        }
        
        try:
            # 确保在登录页面
            self.driver.get(self.url)
            time.sleep(2)
            
            # 步骤1: 输入错误账号
            print("步骤1: 输入错误账号 wronguser")
            username_input = self.login_page.get_username_input()
            username_input.clear()
            username_input.send_keys("wronguser")
            result["steps"].append({"step": "输入错误账号", "status": "PASS"})
            
            # 步骤2: 输入错误密码
            print("步骤2: 输入错误密码 wrongpass")
            password_input = self.login_page.get_password_input()
            password_input.clear()
            password_input.send_keys("wrongpass")
            result["steps"].append({"step": "输入错误密码", "status": "PASS"})
            
            # 步骤3: 点击登录按钮
            print("步骤3: 点击登录按钮")
            login_button = self.login_page.get_login_button()
            login_button.click()
            time.sleep(2)
            result["steps"].append({"step": "点击登录按钮", "status": "PASS"})
            
            # 验证结果
            print("验证: 检查页面状态")
            current_url = self.driver.current_url
            print(f"  当前URL: {current_url}")
            
            if current_url == self.url:
                print("  [PASS] 页面未跳转")
                result["steps"].append({"step": "验证页面未跳转", "status": "PASS"})
                
                # 检查是否有错误提示
                try:
                    error_msg = self.driver.find_element(By.CSS_SELECTOR, ".el-message__content").text
                    print(f"  错误提示: {error_msg}")
                    result["steps"].append({"step": "验证错误提示", "status": "PASS", "detail": error_msg})
                except:
                    print("  [SKIP] 未发现错误提示")
                    result["steps"].append({"step": "验证错误提示", "status": "SKIP"})
            else:
                print("  [FAIL] 页面发生了跳转")
                result["steps"].append({"step": "验证页面未跳转", "status": "FAIL"})
                self.driver.get(self.url)
                time.sleep(2)
                
            # 判断整体结果
            failed_steps = [s for s in result["steps"] if s["status"] == "FAIL"]
            if len(failed_steps) == 0:
                result["status"] = "PASS"
                print(f"\n测试用例 {case_id} 通过 [OK]")
            else:
                result["status"] = "FAIL"
                print(f"\n测试用例 {case_id} 失败 [FAILED]")
                
        except Exception as e:
            result["status"] = "ERROR"
            result["error"] = str(e)
            print(f"\n测试用例执行出错: {str(e)}")
            traceback.print_exc()
            
            # 尝试返回登录页面
            self.driver.get(self.url)
            time.sleep(2)
            
        self.test_results.append(result)
        return result
        
    def tc_login_006_remember_password(self):
        """TC-LOGIN-006: 记住密码功能测试"""
        case_id = "TC-LOGIN-006"
        case_name = "记住密码功能测试"
        print(f"\n{'='*60}")
        print(f"执行测试用例: {case_id} - {case_name}")
        print(f"{'='*60}")
        
        result = {
            "case_id": case_id,
            "case_name": case_name,
            "status": "UNEXECUTED",
            "steps": []
        }
        
        try:
            # 确保在登录页面
            self.driver.get(self.url)
            time.sleep(2)
            
            # 步骤1: 点击记住密码复选框
            print("步骤1: 点击记住密码复选框")
            try:
                checkbox_label = self.driver.find_element(*LoginPage.REMEMBER_PASSWORD_LABEL)
                checkbox_label.click()
                print("  [PASS] 已点击记住密码")
                result["steps"].append({"step": "点击记住密码复选框", "status": "PASS"})
            except:
                print("  [SKIP] 未找到记住密码复选框")
                result["steps"].append({"step": "点击记住密码复选框", "status": "SKIP"})
                
            # 步骤2: 输入账号
            print("步骤2: 输入账号")
            username_input = self.login_page.get_username_input()
            username_input.clear()
            username_input.send_keys("admin")
            result["steps"].append({"step": "输入账号", "status": "PASS"})
            
            # 步骤3: 输入密码
            print("步骤3: 输入密码")
            password_input = self.login_page.get_password_input()
            password_input.clear()
            password_input.send_keys("admin123")
            result["steps"].append({"step": "输入密码", "status": "PASS"})
            
            # 步骤4: 点击登录按钮
            print("步骤4: 点击登录按钮")
            login_button = self.login_page.get_login_button()
            login_button.click()
            time.sleep(3)
            result["steps"].append({"step": "点击登录按钮", "status": "PASS"})
            
            # 步骤5: 清除Cookies并刷新页面验证
            print("步骤5: 清除Cookies并刷新页面")
            self.login_page.clear_cookies()
            self.driver.get(self.url)
            time.sleep(2)
            
            inputs = self.get_input_elements()
            if len(inputs) >= 2:
                username_value = self.get_element_value(inputs[0])
                password_value = self.get_element_value(inputs[1])
                print(f"  账号输入框: '{username_value}'")
                print(f"  密码输入框: '{password_value}'")
                
                if username_value == "" and password_value == "":
                    print("  [PASS] 输入框为空，未保存预填信息")
                    result["steps"].append({"step": "验证未保存预填", "status": "PASS"})
                else:
                    print(f"  [INFO] 输入框有预填信息")
                    result["steps"].append({"step": "验证未保存预填", "status": "INFO", "detail": f"账号:'{username_value}', 密码长度:{len(password_value)}"})
                    
            # 判断整体结果
            failed_steps = [s for s in result["steps"] if s["status"] == "FAIL"]
            if len(failed_steps) == 0:
                result["status"] = "PASS"
                print(f"\n测试用例 {case_id} 通过 [OK]")
            else:
                result["status"] = "FAIL"
                print(f"\n测试用例 {case_id} 失败 [FAILED]")
                
        except Exception as e:
            result["status"] = "ERROR"
            result["error"] = str(e)
            print(f"\n测试用例执行出错: {str(e)}")
            traceback.print_exc()
            
            # 尝试返回登录页面
            self.driver.get(self.url)
            time.sleep(2)
            
        self.test_results.append(result)
        return result
        
    def tc_login_007_boundary_test(self):
        """TC-LOGIN-007: 账号输入框边界值测试"""
        case_id = "TC-LOGIN-007"
        case_name = "账号输入框边界值测试"
        print(f"\n{'='*60}")
        print(f"执行测试用例: {case_id} - {case_name}")
        print(f"{'='*60}")
        
        result = {
            "case_id": case_id,
            "case_name": case_name,
            "status": "UNEXECUTED",
            "steps": []
        }
        
        try:
            # 确保在登录页面
            self.driver.get(self.url)
            time.sleep(2)
            
            long_username = "adminadminadminadminadminadminadminadminadminadminadminadmin"
            print(f"步骤1: 输入超长账号 (50字符)")
            username_input = self.login_page.get_username_input()
            username_input.clear()
            username_input.send_keys(long_username)
            time.sleep(0.5)
            
            actual_value = self.get_element_value(username_input)
            print(f"  输入长度: 50, 实际长度: {len(actual_value)}")
            
            if len(actual_value) == 50:
                print("  [PASS] 输入框接受50个字符")
                result["steps"].append({"step": "输入超长账号", "status": "PASS"})
            else:
                print(f"  [FAIL] 输入框只接受{len(actual_value)}个字符")
                result["steps"].append({"step": "输入超长账号", "status": "FAIL", "detail": f"期望50字符，实际{len(actual_value)}字符"})
                
            # 步骤2: 输入密码
            print("步骤2: 输入密码")
            password_input = self.login_page.get_password_input()
            password_input.clear()
            password_input.send_keys("admin123")
            result["steps"].append({"step": "输入密码", "status": "PASS"})
            
            # 步骤3: 点击登录按钮
            print("步骤3: 点击登录按钮")
            login_button = self.login_page.get_login_button()
            login_button.click()
            time.sleep(2)
            result["steps"].append({"step": "点击登录按钮", "status": "PASS"})
            
            # 返回登录页面
            self.driver.get(self.url)
            time.sleep(2)
                
            # 判断整体结果
            failed_steps = [s for s in result["steps"] if s["status"] == "FAIL"]
            if len(failed_steps) == 0:
                result["status"] = "PASS"
                print(f"\n测试用例 {case_id} 通过 [OK]")
            else:
                result["status"] = "FAIL"
                print(f"\n测试用例 {case_id} 失败 [FAILED]")
                
        except Exception as e:
            result["status"] = "ERROR"
            result["error"] = str(e)
            print(f"\n测试用例执行出错: {str(e)}")
            traceback.print_exc()
            
            # 尝试返回登录页面
            self.driver.get(self.url)
            time.sleep(2)
            
        self.test_results.append(result)
        return result
        
    def tc_login_008_special_chars(self):
        """TC-LOGIN-008: 密码输入框特殊字符测试"""
        case_id = "TC-LOGIN-008"
        case_name = "密码输入框特殊字符测试"
        print(f"\n{'='*60}")
        print(f"执行测试用例: {case_id} - {case_name}")
        print(f"{'='*60}")
        
        result = {
            "case_id": case_id,
            "case_name": case_name,
            "status": "UNEXECUTED",
            "steps": []
        }
        
        try:
            # 确保在登录页面
            self.driver.get(self.url)
            time.sleep(2)
            
            # 步骤1: 输入账号
            print("步骤1: 输入账号")
            username_input = self.login_page.get_username_input()
            username_input.clear()
            username_input.send_keys("admin")
            result["steps"].append({"step": "输入账号", "status": "PASS"})
            
            # 步骤2: 输入特殊字符密码
            print("步骤2: 输入特殊字符密码 admin@#$123")
            password_input = self.login_page.get_password_input()
            password_input.clear()
            special_password = "admin@#$123"
            password_input.send_keys(special_password)
            time.sleep(0.5)
            
            actual_value = self.get_element_value(password_input)
            print(f"  输入长度: 11, 实际长度: {len(actual_value)}")
            
            if len(actual_value) == 11:
                print("  [PASS] 输入框接受特殊字符")
                result["steps"].append({"step": "输入特殊字符密码", "status": "PASS"})
            else:
                print(f"  [FAIL] 输入框部分接受 {len(actual_value)} 个字符")
                result["steps"].append({"step": "输入特殊字符密码", "status": "FAIL", "detail": f"期望11字符，实际{len(actual_value)}字符"})
                
            # 步骤3: 点击登录按钮
            print("步骤3: 点击登录按钮")
            login_button = self.login_page.get_login_button()
            login_button.click()
            time.sleep(2)
            result["steps"].append({"step": "点击登录按钮", "status": "PASS"})
                
            # 返回登录页面
            self.driver.get(self.url)
            time.sleep(2)
                
            # 判断整体结果
            failed_steps = [s for s in result["steps"] if s["status"] == "FAIL"]
            if len(failed_steps) == 0:
                result["status"] = "PASS"
                print(f"\n测试用例 {case_id} 通过 [OK]")
            else:
                result["status"] = "FAIL"
                print(f"\n测试用例 {case_id} 失败 [FAILED]")
                
        except Exception as e:
            result["status"] = "ERROR"
            result["error"] = str(e)
            print(f"\n测试用例执行出错: {str(e)}")
            traceback.print_exc()
            
            # 尝试返回登录页面
            self.driver.get(self.url)
            time.sleep(2)
            
        self.test_results.append(result)
        return result
        
    def run_all_tests(self):
        """运行所有测试用例"""
        print(f"\n{'#'*60}")
        print(f"# 登录界面功能测试开始")
        print(f"# 目标URL: {self.url}")
        print(f"{'#'*60}\n")
        
        try:
            self.setup_driver()
            self.open_login_page()
            
            # 执行测试用例
            self.tc_login_001_clear_prefilled_info()
            self.tc_login_002_normal_login()
            self.tc_login_003_empty_username()
            self.tc_login_004_empty_password()
            self.tc_login_005_wrong_credentials()
            self.tc_login_006_remember_password()
            self.tc_login_007_boundary_test()
            self.tc_login_008_special_chars()
            
        except Exception as e:
            print(f"\n测试运行出错: {str(e)}")
            traceback.print_exc()
            
        finally:
            self.print_summary()
            self.teardown()
            
    def print_summary(self):
        """打印测试摘要"""
        print(f"\n{'#'*60}")
        print(f"# 测试执行摘要")
        print(f"{'#'*60}\n")
        
        total = len(self.test_results)
        passed = len([r for r in self.test_results if r["status"] == "PASS"])
        failed = len([r for r in self.test_results if r["status"] == "FAIL"])
        error = len([r for r in self.test_results if r["status"] == "ERROR"])
        
        print(f"总计: {total} 个测试用例")
        print(f"通过: {passed} 个 [OK]")
        print(f"失败: {failed} 个 [FAILED]")
        print(f"错误: {error} 个 [ERROR]\n")
        
        print(f"详细结果:")
        print(f"{'-'*60}")
        for result in self.test_results:
            status_icon = "[OK]" if result["status"] == "PASS" else ("[FAILED]" if result["status"] == "FAIL" else "[ERROR]")
            print(f"{status_icon} [{result['case_id']}] {result['case_name']} - {result['status']}")
            
    def teardown(self):
        """清理资源"""
        if self.driver:
            print(f"\n关闭浏览器...")
            self.driver.quit()


def main():
    """主函数"""
    test_runner = LoginTestRunner()
    test_runner.run_all_tests()


if __name__ == "__main__":
    main()