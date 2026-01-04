import pytest
import sys
import json
from playwright.sync_api import sync_playwright, Page, Browser
import time
import random
from datetime import datetime

class TestUserAddDetector:
    def __init__(self):
        self.base_url = "http://192.168.142.146/"
        self.login_url = "http://192.168.142.146/login"
        self.username = "admin"
        self.password = "admin123"
        self.result = {
            "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "dialog_info": {},
            "inputs": [],
            "selects": [],
            "multi_selects": [],
            "textarea": [],
            "radio_groups": [],
            "buttons": [],
            "treeselects": []
        }
    
    def run_detection(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.set_default_timeout(10000)
            
            try:
                step1 = self._login(page)
                step2 = self._navigate_to_user_management(page)
                step3 = self._click_add_button(page)
                step4 = self._inspect_dialog_elements(page)
                
                print("\n=== 探测完成，结果如下 ===")
                print(json.dumps(self.result, ensure_ascii=False, indent=2))
                
                self._save_result()
                
            except Exception as e:
                print(f"探测过程中发生错误: {str(e)}")
                import traceback
                traceback.print_exc()
            finally:
                time.sleep(2)
                browser.close()
    
    def _login(self, page: Page) -> bool:
        print("\n[步骤1] 正在登录系统...")
        page.goto(self.login_url)
        time.sleep(1)
        
        username_input = page.locator('input[placeholder*="账号"], input[placeholder*="用户名"], .el-input__inner:first-of-type').first
        username_input.fill(self.username)
        
        password_input = page.locator('input[type="password"], .el-input__inner:has-text("")').nth(1)
        password_input.fill(self.password)
        
        login_button = page.locator('button:has-text("登 录")').first
        login_button.click()
        
        page.wait_for_url("**/index", timeout=10000)
        print("[OK] 登录成功")
        return True
    
    def _navigate_to_user_management(self, page: Page) -> bool:
        print("\n[步骤2] 导航到用户管理...")
        time.sleep(1)
        
        system_menu = page.get_by_text("系统管理").first
        system_menu.click()
        time.sleep(0.5)
        
        user_menu = page.get_by_text("用户管理").first
        user_menu.click()
        
        page.wait_for_load_state("networkidle")
        print("[OK] 已进入用户管理页面")
        return True
    
    def _click_add_button(self, page: Page) -> bool:
        print("\n[步骤3] 点击新增按钮...")
        time.sleep(1)
        
        try:
            add_button = page.locator('button:has-text("新")').first
            add_button.click()
        except:
            add_button = page.locator('.el-button--primary:has(.el-icon-plus)').first
            add_button.click()
        
        time.sleep(1)
        print("[OK] 已点击新增按钮")
        return True
    
    def _inspect_dialog_elements(self, page: Page) -> bool:
        print("\n[步骤4] 检测对话框元素...")
        
        dialog = page.get_by_role("dialog").first
        self.result["dialog_info"] = {
            "visible": dialog.is_visible(),
            "title": dialog.inner_text()
        }
        
        if not dialog.is_visible():
            print("[ERROR] 对话框未出现")
            return False
        
        print("[OK] 对话框已出现")
        
        self._detect_inputs(dialog)
        self._detect_selects(dialog)
        self._detect_textarea(dialog)
        self._detect_radio_buttons(dialog)
        self._detect_treeselect(dialog)
        self._detect_buttons(dialog)
        
        return True
    
    def _detect_inputs(self, dialog):
        print("\n  检测输入框...")
        inputs = dialog.locator('input[type="text"], input[type="password"], input[type="email"]')
        count = inputs.count()
        
        for i in range(count):
            try:
                input_el = inputs.nth(i)
                placeholder = input_el.get_attribute('placeholder')
                input_type = input_el.get_attribute('type')
                name_attr = input_el.get_attribute('name')
                id_attr = input_el.get_attribute('id')
                maxlength = input_el.get_attribute('maxlength')
                
                element_info = {
                    "index": i,
                    "type": input_type,
                    "placeholder": placeholder,
                    "max_length": maxlength,
                    "name": name_attr,
                    "id": id_attr
                }
                
                self.result["inputs"].append(element_info)
                print(f"    - 第{i}个输入框: type={input_type}, placeholder={placeholder}")
                
            except Exception as e:
                print(f"    - 第{i}个输入框检测失败: {str(e)}")
    
    def _detect_selects(self, dialog):
        print("\n  检测下拉框...")
        selects = dialog.locator('select, .el-select, .el-select__input')
        count = selects.count()
        
        for i in range(count):
            try:
                select_el = selects.nth(i)
                element_info = {
                    "index": i,
                    "type": "select",
                    "text": select_el.inner_text(),
                    "placeholder": select_el.get_attribute('placeholder')
                }
                self.result["selects"].append(element_info)
                print(f"    - 第{i}个下拉框: {element_info['text']}")
            except Exception as e:
                print(f"    - 第{i}个下拉框检测失败: {str(e)}")
    
    def _detect_treeselect(self, dialog):
        print("\n  检测部门树选择器...")
        try:
            treeselect = dialog.locator('.vue-treeselect, .el-tree-select')
            count = treeselect.count()
            
            for i in range(count):
                treeselect_el = treeselect.nth(i)
                element_info = {
                    "index": i,
                    "type": "treeselect",
                    "placeholder": treeselect_el.get_attribute('placeholder'),
                    "text": treeselect_el.inner_text()
                }
                self.result["treeselects"].append(element_info)
                print(f"    - 第{i}个树选择器: {element_info['placeholder']}")
        except Exception as e:
            print(f"    - 树选择器检测失败: {str(e)}")
    
    def _detect_textarea(self, dialog):
        print("\n  检测文本区域...")
        try:
            textarea = dialog.locator('textarea')
            count = textarea.count()
            
            for i in range(count):
                textarea_el = textarea.nth(i)
                element_info = {
                    "index": i,
                    "type": "textarea",
                    "placeholder": textarea_el.get_attribute('placeholder')
                }
                self.result["textarea"].append(element_info)
                print(f"    - 第{i}个文本区域: {element_info['placeholder']}")
        except Exception as e:
            print(f"    - 文本区域检测失败: {str(e)}")
    
    def _detect_radio_buttons(self, dialog):
        print("\n  检测单选按钮组...")
        try:
            radio_groups = dialog.locator('.el-radio-group')
            count = radio_groups.count()
            
            for i in range(count):
                group = radio_groups.nth(i)
                label = group.evaluate("el => el.previousElementSibling ? el.previousElementSibling.textContent.trim() : ''")
                
                radios = group.locator('.el-radio')
                options = []
                for j in range(radios.count()):
                    radio_text = radios.nth(j).inner_text()
                    if radio_text:
                        options.append(radio_text)
                
                element_info = {
                    "index": i,
                    "type": "radio_group",
                    "label": label,
                    "options": options
                }
                self.result["radio_groups"].append(element_info)
                print(f"    - 第{i}组单选按钮: {label}, 选项={options}")
        except Exception as e:
            print(f"    - 单选按钮检测失败: {str(e)}")
    
    def _detect_buttons(self, dialog):
        print("\n  检测按钮...")
        try:
            buttons = dialog.locator('button')
            count = buttons.count()
            
            for i in range(count):
                button_el = buttons.nth(i)
                button_text = button_el.inner_text().strip()
                button_type = button_el.get_attribute('type') or button_el.get_attribute('class')
                
                if button_text:
                    element_info = {
                        "index": i,
                        "text": button_text,
                        "type": button_type
                    }
                    self.result["buttons"].append(element_info)
                    print(f"    - 按钮: {button_text} (type={button_type})")
        except Exception as e:
            print(f"    - 按钮检测失败: {str(e)}")
    
    def _save_result(self):
        filename = "探测结果.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.result, f, ensure_ascii=False, indent=2)
        print(f"\n[OK] 探测结果已保存至: {filename}")

if __name__ == "__main__":
    detector = TestUserAddDetector()
    detector.run_detection()