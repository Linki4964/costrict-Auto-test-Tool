"""
登录页面探测器 v2
改进版：更全面地探测登录按钮和其他元素
"""

from playwright.sync_api import sync_playwright
import json
import time
from datetime import datetime

class LoginPageDetectorV2:
    """登录页面元素探测器 v2 - 改进版"""
    
    def __init__(self, url):
        self.url = url
        self.result = {
            "metadata": {
                "scan_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "target_url": url,
                "detector_version": "2.0"
            },
            "elements": {}
        }
    
    def detect_elements(self, page):
        """探测页面元素"""
        print("开始探测页面元素...")
        
        # 探测用户名输入框
        username_info = self._detect_input(page, [
            "input[type='text']",
            "input[name*='user']",
            "input[placeholder*='用户名']",
            "input[placeholder*='账号']",
            "input[id*='user']"
        ], "username")
        self.result["elements"]["username_input"] = username_info
        
        # 探测密码输入框
        password_info = self._detect_input(page, [
            "input[type='password']",
            "input[name*='pass']",
            "input[placeholder*='密码']",
            "input[id*='pass']"
        ], "password")
        self.result["elements"]["password_input"] = password_info
        
        # 探测登录按钮 - 改进版
        login_button_info = self._detect_login_button(page)
        self.result["elements"]["login_button"] = login_button_info
        
        # 探测验证码元素
        captcha_info = self._detect_element(page, [
            "img[alt*='验证码']",
            "img[src*='captcha']",
            "[class*='captcha']",
            "#captchaImg"
        ], "captcha")
        self.result["elements"]["captcha"] = captcha_info
        
        # 探测错误提示元素
        error_info = self._detect_element(page, [
            ".el-message--error",
            ".ant-message-error",
            ".error-message",
            ".error-text",
            "[class*='error']"
        ], "error_message")
        self.result["elements"]["error_message"] = error_info
        
        # 探测成功提示元素
        success_info = self._detect_element(page, [
            ".el-message--success",
            ".ant-message-success",
            ".success-message"
        ], "success_message")
        self.result["elements"]["success_message"] = success_info
        
        # 探测页面的form元素
        form_info = self._detect_form(page)
        self.result["elements"]["login_form"] = form_info
        
        # 探测登出相关元素
        logout_info = self._detect_logout_elements(page)
        self.result["elements"]["logout_elements"] = logout_info
        
        # 探测所有可能的按钮元素
        all_buttons = self._detect_all_buttons(page)
        self.result["elements"]["all_buttons"] = all_buttons
        
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
    
    def _detect_login_button(self, page):
        """探测登录按钮 - 改进版"""
        info = {
            "type": "login_button",
            "found": False,
            "candidates": []
        }
        
        # 方法1：查找包含"登录"文字的按钮
        try:
            buttons = page.query_selector_all("button, input[type='submit'], a[role='button']")
            for i, btn in enumerate(buttons):
                text = btn.inner_text() or btn.get_attribute("value") or ""
                class_name = btn.get_attribute("class") or ""
                type_attr = btn.get_attribute("type") or ""
                
                # 检查是否是登录按钮
                is_login = (
                    "登录" in text or "Login" in text.lower() or
                    "login" in class_name.lower() or
                    type_attr == "submit"
                )
                
                if is_login:
                    candidate = {
                        "index": i,
                        "text": text,
                        "class": class_name,
                        "type": type_attr,
                        "tag": btn.evaluate("el => el.tagName"),
                        "visible": btn.is_visible(),
                        "enabled": btn.is_enabled()
                    }
                    info["candidates"].append(candidate)
                    
                    if not info["found"]:
                        info["found"] = True
                        info["selectors"]["primary"] = f"button:nth-of-type({i+1})"
                        info["attributes"] = candidate
        except Exception as e:
            pass
        
        # 方法2：查找表单内的提交按钮
        try:
            forms = page.query_selector_all("form")
            for form in forms:
                submit_buttons = form.query_selector_all("button[type='submit'], input[type='submit']")
                for btn in submit_buttons:
                    if not info["found"]:
                        info["found"] = True
                        info["selectors"]["form_submit"] = "button[type='submit']"
                        break
        except:
            pass
        
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
                    for i, element in enumerate(elements[:3]):
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
            "a:has-text('退出')",
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
    
    def _detect_all_buttons(self, page):
        """探测页面上所有按钮"""
        info = {
            "total_buttons": 0,
            "buttons": []
        }
        
        try:
            buttons = page.query_selector_all("button, input[type='submit'], a[role='button']")
            info["total_buttons"] = len(buttons)
            
            for i, btn in enumerate(buttons):
                button_info = {
                    "index": i,
                    "tag": btn.evaluate("el => el.tagName"),
                    "text": btn.inner_text() or btn.get_attribute("value") or "",
                    "class": btn.get_attribute("class") or "",
                    "type": btn.get_attribute("type") or "",
                    "visible": btn.is_visible(),
                    "enabled": btn.is_enabled()
                }
                info["buttons"].append(button_info)
        except:
            pass
        
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
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()
        
        try:
            print(f"正在访问页面：{target_url}")
            page.goto(target_url, timeout=30000)
            time.sleep(2)
            
            detector = LoginPageDetectorV2(target_url)
            result = detector.detect_elements(page)
            
            output_file = "工作区/20251231_161059+登录界面功能测试/20251231_登录界面_探测器结果_v2.json"
            detector.save_result(output_file)
            
            print("\n=== 探测结果摘要 ===")
            print(f"用户名输入框: {'Found' if result['elements']['username_input']['found'] else 'Not Found'}")
            print(f"密码输入框: {'Found' if result['elements']['password_input']['found'] else 'Not Found'}")
            print(f"登录按钮: {'Found' if result['elements']['login_button']['found'] else 'Not Found'}")
            print(f"登录按钮候选数: {len(result['elements']['login_button'].get('candidates', []))}")
            print(f"验证码元素: {'Found' if result['elements']['captcha']['found'] else 'Not Found'}")
            print(f"错误提示: {'Found' if result['elements']['error_message']['found'] else 'Not Found'}")
            print(f"总按钮数: {result['elements']['all_buttons']['total_buttons']}")
            
            print("\n所有按钮详情:")
            for btn in result['elements']['all_buttons']['buttons']:
                print(f"  - [{btn['tag']}] Text: '{btn['text']}', Class: '{btn['class']}', Visible: {btn['visible']}")
            
            print("\n浏览器将保持打开10秒...")
            time.sleep(10)
            
        except Exception as e:
            print(f"Error: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    main()