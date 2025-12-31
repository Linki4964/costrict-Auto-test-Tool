"""
登录页面探测器
用于探测登录页面中用户可能使用的重要元素
"""

from playwright.sync_api import sync_playwright
import json
import time
from datetime import datetime

class LoginPageDetector:
    """登录页面元素探测器"""
    
    def __init__(self, url):
        self.url = url
        self.result = {
            "metadata": {
                "scan_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "target_url": url,
                "detector_version": "1.0"
            },
            "elements": {}
        }
    
    def detect_elements(self, page):
        """探测页面元素"""
        print("开始探测页面元素...")
        
        # 探测用户名输入框
        username_selectors = [
            "input[type='text']",
            "input[name='username']",
            "input[placeholder*='用户名']",
            "input[placeholder*='账号']",
            "input[placeholder*='User']",
            "input[id*='username']",
            "input[id*='user']"
        ]
        
        username_info = self._detect_input(page, username_selectors, "username")
        self.result["elements"]["username_input"] = username_info
        
        # 探测密码输入框
        password_selectors = [
            "input[type='password']",
            "input[name='password']",
            "input[placeholder*='密码']",
            "input[placeholder*='Password']",
            "input[id*='password']"
        ]
        
        password_info = self._detect_input(page, password_selectors, "password")
        self.result["elements"]["password_input"] = password_info
        
        # 探测登录按钮
        login_button_selectors = [
            "button[type='submit']",
            "button:has-text('登录')",
            "button:has-text('Login')",
            ".login-btn",
            "[class*='login-button']",
            "[class*='login-btn']",
            "input[type='submit']:has-text('登录')",
            "input[type='submit']:has-text('Login')"
        ]
        
        login_button_info = self._detect_button(page, login_button_selectors, "login_button")
        self.result["elements"]["login_button"] = login_button_info
        
        # 探测验证码相关元素
        captcha_selectors = [
            "img[alt*='验证码']",
            "img[alt*='captcha']",
            "img[src*='captcha']",
            "[class*='captcha']",
            "#captchaImg"
        ]
        
        captcha_info = self._detect_element(page, captcha_selectors, "captcha")
        self.result["elements"]["captcha"] = captcha_info
        
        # 探测记住我复选框
        remember_selectors = [
            "input[type='checkbox']:has-text('记住')",
            "input[type='checkbox'][name*='remember']",
            "[class*='remember']"
        ]
        
        remember_info = self._detect_element(page, remember_selectors, "remember_me")
        self.result["elements"]["remember_me"] = remember_info
        
        # 探测错误提示元素
        error_selectors = [
            ".error-message",
            ".error-text",
            "[class*='error']",
            ".el-message--error",
            ".ant-message-error",
            ".ivu-message-error"
        ]
        
        error_info = self._detect_element(page, error_selectors, "error_message")
        self.result["elements"]["error_message"] = error_info
        
        # 探测成功提示元素
        success_selectors = [
            ".success-message",
            ".el-message--success",
            ".ant-message-success",
            ".ivu-message-success"
        ]
        
        success_info = self._detect_element(page, success_selectors, "success_message")
        self.result["elements"]["success_message"] = success_info
        
        # 探测页面的form元素
        form_info = self._detect_form(page)
        self.result["elements"]["login_form"] = form_info
        
        # 探测登出相关元素（如果在登录后页面）
        logout_info = self._detect_logout_elements(page)
        self.result["elements"]["logout_elements"] = logout_info
        
        print("页面元素探测完成！")
        return self.result
    
    def _detect_input(self, page, selectors, element_type):
        """探测输入框元素"""
        info = {
            "type": element_type,
            "found": False,
            "selectors": {},
            "attributes": {}
        }
        
        for selector in selectors:
            try:
                element = page.wait_for_selector(selector, timeout=2000)
                if element:
                    info["found"] = True
                    info["selectors"]["primary"] = selector
                    info["attributes"] = {
                        "placeholder": element.get_attribute("placeholder") or "",
                        "type": element.get_attribute("type") or "",
                        "name": element.get_attribute("name") or "",
                        "id": element.get_attribute("id") or "",
                        "class": element.get_attribute("class") or "",
                        "visible": element.is_visible(),
                        "enabled": element.is_enabled()
                    }
                    info["text"] = element.input_value() or ""
                    break
            except:
                continue
        
        return info
    
    def _detect_button(self, page, selectors, element_type):
        """探测按钮元素"""
        info = {
            "type": element_type,
            "found": False,
            "selectors": {},
            "attributes": {}
        }
        
        for selector in selectors:
            try:
                element = page.wait_for_selector(selector, timeout=2000)
                if element:
                    info["found"] = True
                    info["selectors"]["primary"] = selector
                    info["attributes"] = {
                        "type": element.get_attribute("type") or "",
                        "name": element.get_attribute("name") or "",
                        "id": element.get_attribute("id") or "",
                        "class": element.get_attribute("class") or "",
                        "text": element.inner_text() or "",
                        "visible": element.is_visible(),
                        "enabled": element.is_enabled()
                    }
                    break
            except:
                continue
        
        return info
    
    def _detect_element(self, page, selectors, element_type):
        """探测通用元素"""
        info = {
            "type": element_type,
            "found": False,
            "selectors": {}
        }
        
        for selector in selectors:
            try:
                elements = page.query_selector_all(selector)
                if elements:
                    info["found"] = True
                    info["selectors"]["primary"] = selector
                    info["count"] = len(elements)
                    for i, element in enumerate(elements[:3]):  # 最多记录3个匹配元素
                        info[f"element_{i+1}"] = {
                            "class": element.get_attribute("class") or "",
                            "id": element.get_attribute("id") or "",
                            "visible": element.is_visible()
                        }
                    break
            except:
                continue
        
        return info
    
    def _detect_form(self, page):
        """探测表单元素"""
        info = {
            "found": False,
            "attributes": {}
        }
        
        try:
            forms = page.query_selector_all("form")
            if forms:
                info["found"] = True
                info["count"] = len(forms)
                for i, form in enumerate(forms):
                    info[f"form_{i+1}"] = {
                        "action": form.get_attribute("action") or "",
                        "method": form.get_attribute("method") or "",
                        "id": form.get_attribute("id") or "",
                        "class": form.get_attribute("class") or ""
                    }
        except:
            pass
        
        return info
    
    def _detect_logout_elements(self, page):
        """探测登出相关元素"""
        info = {
            "found": False,
            "selectors": {}
        }
        
        logout_selectors = [
            "button:has-text('退出')",
            "button:has-text('登出')",
            "button:has-text('Logout')",
            "a:has-text('退出')",
            "a:has-text('登出')",
            "[class*='logout']",
            ".logout",
            "#logout"
        ]
        
        for selector in logout_selectors:
            try:
                elements = page.query_selector_all(selector)
                if elements:
                    info["found"] = True
                    info["selectors"]["primary"] = selector
                    info["count"] = len(elements)
                    break
            except:
                continue
        
        return info
    
    def save_result(self, filepath):
        """保存探测结果到JSON文件"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.result, f, ensure_ascii=False, indent=2)
        print(f"探测结果已保存至：{filepath}")

def main():
    """主函数"""
    target_url = "http://192.168.142.146/login?"
    
    with sync_playwright() as playwright:
        # 启动浏览器（非无头模式，确保可见）
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()
        
        try:
            print(f"正在访问页面：{target_url}")
            page.goto(target_url, timeout=30000)
            time.sleep(2)  # 等待页面加载
            
            # 创建探测器并执行探测
            detector = LoginPageDetector(target_url)
            result = detector.detect_elements(page)
            
            # 保存探测结果
            output_file = "工作区/20251231_161059+登录界面功能测试/20251231_登录界面_探测器结果_v1.json"
            detector.save_result(output_file)
            
            # 打印摘要
            print("\n=== 探测结果摘要 ===")
            print(f"用户名输入框: {'✓' if result['elements']['username_input']['found'] else '✗'}")
            print(f"密码输入框: {'✓' if result['elements']['password_input']['found'] else '✗'}")
            print(f"登录按钮: {'✓' if result['elements']['login_button']['found'] else '✗'}")
            print(f"验证码元素: {'✓' if result['elements']['captcha']['found'] else '✗'}")
            print(f"记住我选项: {'✓' if result['elements']['remember_me']['found'] else '✗'}")
            print(f"错误提示: {'✓' if result['elements']['error_message']['found'] else '✗'}")
            print(f"登出元素: {'✓' if result['elements']['logout_elements']['found'] else '✗'}")
            
            # 保持浏览器打开一段时间，让用户可以看到
            print("\n浏览器将保持打开10秒，您可以查看页面...")
            time.sleep(10)
            
        except Exception as e:
            print(f"探测过程中发生错误: {str(e)}")
        finally:
            browser.close()

if __name__ == "__main__":
    main()