import pytest
import json
import time
import re
from playwright.sync_api import Page, expect, Error
import os

BASE_URL = "http://192.168.142.146"
USERNAME = "admin"
PASSWORD = "admin123"
OUTPUT_FILE = "工作区/20251231_211221+表单提交测试/20251231_用户管理_探测器结果_v1.json"


class TestUserFormProber:
    def __init__(self):
        self.prober_result = {
            "probe_time": "",
            "page_info": {},
            "form_fields": [],
            "dialog_info": {},
            "buttons": [],
            "network_requests": []
        }

    def get_perception_script(self):
        """增强型表单元素感知脚本"""
        return """
        (() => {
            const visibleDialogs = Array.from(document.querySelectorAll('.el-dialog'))
                .filter(d => {
                    const style = window.getComputedStyle(d);
                    return style.display !== 'none' && style.visibility !== 'hidden';
                });
            
            const dialog = visibleDialogs[visibleDialogs.length - 1] || document.querySelector('.el-dialog') || document.body;
            
            const allForms = dialog.querySelectorAll('form, .el-form');
            const form = allForms.length > 0 ? allForms[allForms.length - 1] : dialog;
            
            const items = form.querySelectorAll('.el-form-item, .form-item, [class*="form-item"]');
            
            console.log('Visible dialogs:', visibleDialogs.length);
            console.log('Found forms in dialog:', allForms.length);
            console.log('Found form items:', items.length);
            
            const results = [];
            
            for (let i = 0; i < items.length; i++) {
                const item = items[i];
                
                const labelEl = item.querySelector('.el-form-item__label, label, [class*="label"]');
                const wrapper = item.querySelector('.el-form-item__content, .el-input, .el-select');
                const input = item.querySelector('input, textarea, .el-select, .el-cascader, .vue-treeselect');
                
                if (!labelEl && !input && !wrapper) continue;
                
                const label = labelEl ? labelEl.innerText.trim().replace(/[:：*]/g, '') : '';
                const placeholder = input?.placeholder || input?.getAttribute('placeholder') || '';
                const inputElement = input || wrapper || item;
                
                let fieldType = 'input';
                let multiple = false;
                let componentName = '';
                
                if (item.querySelector('.vue-treeselect') || inputElement.className?.includes('treeselect')) {
                    fieldType = 'treeselect';
                    componentName = 'vue-treeselect';
                } else if (item.querySelector('.el-select') || inputElement.classList.contains('el-select')) {
                    fieldType = 'select';
                    multiple = inputElement.multiple || item.querySelector('.el-select__tags');
                } else if (item.querySelector('.el-cascader') || inputElement.classList.contains('el-cascader')) {
                    fieldType = 'cascader';
                } else if (inputElement && inputElement.type === 'password') {
                    fieldType = 'password';
                } else if (item.querySelector('textarea') || inputElement?.tagName === 'TEXTAREA') {
                    fieldType = 'textarea';
                } else if (item.querySelector('.el-radio-group')) {
                    fieldType = 'radio';
                } else if (item.querySelector('.el-checkbox-group')) {
                    fieldType = 'checkbox';
                }
                
                const inputId = input?.id || input?.getAttribute('name') || '';
                const inputClass = input?.className || '';
                const parentClass = item.className || '';
                
                results.push({
                    label: label || '未命名字段',
                    field_id: inputId,
                    field_name: label || '未命名字段',
                    type: fieldType,
                    component: componentName,
                    placeholder: placeholder,
                    class_name: inputClass,
                    parent_class: parentClass,
                    multiple: multiple,
                    required: item.classList.contains('is-required'),
                    has_label: !!labelEl
                });
            }
            
            return results;
        })()
        """

    def probe_form_fields(self, page: Page):
        """探测表单字段"""
        try:
            console_messages = []
            
            def handle_console(msg):
                console_messages.append(f"{msg.type}: {msg.text}")
            
            page.on("console", handle_console)
            
            execution_script = self.get_perception_script()
            field_result = page.evaluate(execution_script)
            
            page.remove_listener("console", handle_console)
            
            if console_messages:
                print("浏览器控制台日志:")
                for msg in console_messages:
                    print(f"  {msg}")
            
            print(f"探测到 {len(field_result)} 个表单字段")
            for i, field in enumerate(field_result[:5]):
                print(f"  [{i}] {field['label']} ({field['type']}) - 必填: {field.get('required', False)}")
            
            self.prober_result["form_fields"] = field_result
            
            return field_result
        except Exception as e:
            print(f"探测表单字段失败: {e}")
            import traceback
            traceback.print_exc()
            return []

    def setup_page(self, page: Page):
        """页面初始化设置"""
        page.set_default_timeout(30000)
        page.set_viewport_size({"width": 1920, "height": 1080})

    def login(self, page: Page):
        """登录系统"""
        try:
            page.goto(BASE_URL + "/login", wait_until="domcontentloaded")
            time.sleep(1)
            
            username_selectors = [
                "input[name='username']",
                "input[type='text']:first-of-type",
                "input[placeholder*='账号']",
                "input[placeholder*='用户名']"
            ]
            
            password_selectors = [
                "input[name='password']",
                "input[type='password']",
                "input[placeholder*='密码']"
            ]
            
            username_input = None
            for selector in username_selectors:
                try:
                    element = page.locator(selector).first
                    if element.is_visible():
                        username_input = element
                        print(f"找到用户名输入框: {selector}")
                        break
                except:
                    continue
            
            if not username_input:
                raise Exception("无法找到用户名输入框")
            
            password_input = None
            for selector in password_selectors:
                try:
                    element = page.locator(selector).first
                    if element.is_visible():
                        password_input = element
                        print(f"找到密码输入框: {selector}")
                        break
                except:
                    continue
            
            if not password_input:
                raise Exception("无法找到密码输入框")
            
            username_input.fill(USERNAME)
            password_input.fill(PASSWORD)
            
            submit_btn_selectors = [
                'button:has-text("登 录")',
                'button:has-text("登录")',
                'button[type="submit"]',
                '.el-button--primary'
            ]
            
            submit_btn = None
            for selector in submit_btn_selectors:
                try:
                    element = page.locator(selector).first
                    if element.is_visible():
                        submit_btn = element
                        print(f"找到登录按钮: {selector}")
                        break
                except:
                    continue
            
            if submit_btn:
                submit_btn.click()
            else:
                raise Exception("无法找到登录按钮")
            
            page.wait_for_load_state("networkidle", timeout=10000)
            time.sleep(2)
            print("登录成功")
            return True
        except Exception as e:
            print(f"登录失败: {e}")
            return False

    def navigate_to_user_management(self, page: Page):
        """导航到用户管理页面"""
        try:
            page.wait_for_selector('.sidebar-container, .el-aside, aside', timeout=5000)
            time.sleep(1)
            
            menu_selectors = [
                'span:has-text("系统管理")',
                'a:has-text("系统管理")',
                'div[title="系统管理"]'
            ]
            
            menu_clicked = False
            for selector in menu_selectors:
                try:
                    element = page.locator(selector).first
                    if element.is_visible():
                        element.click()
                        menu_clicked = True
                        print(f"点击了系统管理菜单: {selector}")
                        time.sleep(0.5)
                        break
                except:
                    continue
            
            if not menu_clicked:
                print("尝试直接导航到用户管理页面")
                page.goto(BASE_URL + "/system/user", wait_until="domcontentloaded")
                time.sleep(1)
            else:
                user_menu_selectors = [
                    'span:has-text("用户管理")',
                    'a:has-text("用户管理")',
                    'li:has-text("用户管理")'
                ]
                
                user_clicked = False
                for selector in user_menu_selectors:
                    try:
                        element = page.locator(selector).first
                        if element.is_visible():
                            element.click()
                            user_clicked = True
                            print(f"点击了用户管理菜单: {selector}")
                            time.sleep(0.5)
                            break
                    except:
                        continue
                
                if not user_clicked:
                    print("无法找到用户管理菜单，尝试直接导航")
                    page.goto(BASE_URL + "/system/user", wait_until="domcontentloaded")
                    time.sleep(1)
            
            page.wait_for_selector('.el-table, table', timeout=10000)
            print("成功进入用户管理页面")
            return True
        except Exception as e:
            print(f"导航到用户管理页面失败: {e}")
            return False

    def open_add_user_dialog(self, page: Page):
        """打开新增用户对话框"""
        try:
            add_btn_selectors = [
                'button:has-text("新增")',
                '.el-button:has-text("新增")'
            ]
            
            add_btn = None
            for selector in add_btn_selectors:
                try:
                    element = page.locator(selector)
                    if element.count() > 0:
                        add_btn = element.first
                        print(f"找到新增按钮: {selector}, 数量: {element.count()}")
                        break
                except:
                    continue
            
            if not add_btn:
                print("正在页面上查找所有按钮...")
                all_buttons = page.locator('button')
                print(f"页面上共有 {all_buttons.count()} 个按钮")
                for i in range(min(all_buttons.count(), 10)):
                    btn_text = all_buttons.nth(i).inner_text()
                    print(f"  按钮 {i}: '{btn_text}'")
                raise Exception("无法找到新增按钮")
            
            add_btn.click()
            print("已点击新增按钮")
            
            time.sleep(1)
            
            dialog_count = page.locator('.el-dialog').count()
            print(f"检测到 {dialog_count} 个dialog元素")
            
            visible_dialog = page.locator('.el-dialog[style*="display"]')
            if visible_dialog.count() > 0:
                print(f"可见dialog数量: {visible_dialog.count()}")
            
            has_overlay = page.locator('.v-modal, .el-overlay').count() > 0
            print(f"遮罩层存在: {has_overlay}")
            
            all_dialogs = page.locator('.el-dialog')
            for i in range(min(all_dialogs.count(), 3)):
                try:
                    dialog_style = all_dialogs.nth(i).get_attribute('style') or ''
                    dialog_class = all_dialogs.nth(i).get_attribute('class') or ''
                    print(f"Dialog {i}: style={dialog_style[:50]}, class={dialog_class}")
                except:
                    pass
            
            time.sleep(1)
            print("等待完成，继续探测表单字段")
            return True
        except Exception as e:
            print(f"打开新增用户对话框失败: {e}")
            return False

    def probe_form_fields(self, page: Page):
        """探测表单字段"""
        try:
            execution_script = self.get_perception_script()
            field_result = page.evaluate(execution_script)
            self.prober_result["form_fields"] = field_result
            print(f"探测到 {len(field_result)} 个表单字段")
            return field_result
        except Exception as e:
            print(f"探测表单字段失败: {e}")
            return []

    def probe_dialog_info(self, page: Page):
        """探测对话框信息"""
        try:
            dialog = page.locator('.el-dialog, .ant-modal').first
            dialog_title = dialog.locator('.el-dialog__title, .ant-modal-title').inner_text()
            
            confirm_btn = page.locator('.el-dialog__footer button:has-text("确定"), .dialog-footer :text("确定")')
            cancel_btn = page.locator('.el-dialog__footer button:has-text("取消"), .dialog-footer :text("取消")')
            
            self.prober_result["dialog_info"] = {
                "title": dialog_title,
                "visible": dialog.is_visible(),
                "confirm_button_visible": confirm_btn.count() > 0,
                "cancel_button_visible": cancel_btn.count() > 0
            }
            print(f"对话框标题: {dialog_title}")
        except Exception as e:
            print(f"探测对话框信息失败: {e}")

    def probe_buttons(self, page: Page):
        """探测页面按钮"""
        try:
            buttons_info = []
            
            add_btn = page.locator('button:has-text("新增")').first
            buttons_info.append({
                "text": "新增",
                "visible": add_btn.count() > 0,
                "type": "add"
            })
            
            add_dialog_btns = page.locator('.el-dialog__footer button')
            dialog_btn_count = add_dialog_btns.count()
            if dialog_btn_count > 0:
                for i in range(dialog_btn_count):
                    btn_text = add_dialog_btns.nth(i).inner_text()
                    buttons_info.append({
                        "text": btn_text,
                        "visible": True,
                        "type": "dialog_action"
                    })
            
            self.prober_result["buttons"] = buttons_info
        except Exception as e:
            print(f"探测按钮失败: {e}")

    def gather_context(self, page: Page):
        """收集页面上下文信息"""
        try:
            self.prober_result["page_info"] = {
                "url": page.url,
                "title": page.title(),
                "has_table": page.locator('.el-table, table').count() > 0,
                "has_sidebar": page.locator('.sidebar-container, .el-aside, aside').count() > 0
            }
        except Exception as e:
            print(f"收集页面信息失败: {e}")


def test_probe_user_form_fields(page: Page):
    """主探测测试函数"""
    import datetime
    prober = TestUserFormProber()
    
    prober.prober_result["probe_time"] = datetime.datetime.now().isoformat()
    
    try:
        prober.setup_page(page)
        
        if not prober.login(page):
            pytest.fail("登录失败")
        
        if not prober.navigate_to_user_management(page):
            pytest.fail("导航到用户管理页面失败")
        
        prober.gather_context(page)
        prober.probe_buttons(page)
        
        if not prober.open_add_user_dialog(page):
            pytest.fail("打开新增用户对话框失败")
        
        time.sleep(1)
        
        prober.probe_dialog_info(page)
        prober.probe_form_fields(page)
        
        output_dir = os.path.dirname(OUTPUT_FILE)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(prober.prober_result, f, ensure_ascii=False, indent=2)
        
        print(f"\n探测器结果已保存至: {OUTPUT_FILE}")
        print(f"\n探测到的表单字段:")
        for field in prober.prober_result["form_fields"]:
            print(f"  - {field['label']} ({field['type']}) - 必填: {field.get('required', False)}")
        
        assert len(prober.prober_result["form_fields"]) > 0, "未探测到表单字段"
        
    except Exception as e:
        pytest.fail(f"探测过程失败: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "--headless=false"])