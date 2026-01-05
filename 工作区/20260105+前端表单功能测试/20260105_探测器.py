# -*- coding: utf-8 -*-
from playwright.sync_api import sync_playwright
import json
import time

def detect_form_elements():
    """
    探测新增用户表单的所有元素
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=1000)
        page = browser.new_page()
        
        try:
            print("正在打开登录页面...")
            page.goto('http://192.168.142.146/login?redirect=%2Findex')
            
            print("正在登录...")
            page.get_by_placeholder("账号").fill("admin")
            page.get_by_placeholder("密码").fill("admin123")
            page.get_by_role("button", name="登 录").click()
            
            # 等待 URL 跳转到首页
            page.wait_for_url("**/index", timeout=10000)
            print("登录成功")
            
            # 导航到用户管理
            print("正在展开侧边栏菜单...")
            system_menu = page.locator("li").filter(has_text="系统管理").first
            system_menu.click()
            
            user_link = page.get_by_role("link", name="用户管理")
            user_link.wait_for(state="visible", timeout=5000)
            user_link.click()
            print("已进入用户管理页面")
            
            # 等待页面加载完成
            page.wait_for_timeout(2000)
            
            # 点击新增按钮
            print("正在点击新增按钮...")
            page.get_by_role("button", name="新增").click()
            
            # 等待弹窗出现
            print("等待弹窗出现...")
            dialog = page.get_by_role("dialog")
            dialog.wait_for(state="visible", timeout=5000)
            
            print("开始探测表单元素...")
            
            # 探测所有输入框
            inputs = dialog.locator("input").all()
            input_elements = []
            for idx, input_el in enumerate(inputs):
                element_info = {
                    "index": idx,
                    "tag": "input",
                    "type": input_el.get_attribute("type") or "text",
                    "placeholder": input_el.get_attribute("placeholder"),
                    "name": input_el.get_attribute("name"),
                    "id": input_el.get_attribute("id"),
                    "visible": input_el.is_visible(),
                    "enabled": input_el.is_enabled()
                }
                input_elements.append(element_info)
            
            # 探测所有下拉框
            selects = dialog.locator(".el-select").all()
            select_elements = []
            for idx, select_el in enumerate(selects):
                element_info = {
                    "index": idx,
                    "tag": "el-select",
                    "visible": select_el.is_visible(),
                    "enabled": select_el.is_enabled()
                }
                select_elements.append(element_info)
            
            # 探测部门树形选择器
            dept_select = dialog.locator(".vue-treeselect__control")
            dept_info = {
                "tag": "vue-treeselect__control",
                "exists": dept_select.count() > 0,
                "visible": dept_select.count() > 0 and dept_select.is_visible()
            }
            
            # 探测单选按钮和复选框
            radios = dialog.locator(".el-radio").all()
            radio_elements = []
            for idx, radio_el in enumerate(radios):
                element_info = {
                    "index": idx,
                    "tag": "el-radio",
                    "text": radio_el.inner_text(),
                    "visible": radio_el.is_visible()
                }
                radio_elements.append(element_info)
            
            # 探测文本域
            textareas = dialog.locator("textarea").all()
            textarea_elements = []
            for idx, textarea_el in enumerate(textareas):
                element_info = {
                    "index": idx,
                    "tag": "textarea",
                    "placeholder": textarea_el.get_attribute("placeholder"),
                    "visible": textarea_el.is_visible()
                }
                textarea_elements.append(element_info)
            
            # 探测表单标签
            form_labels = dialog.locator(".el-form-item__label").all()
            label_elements = []
            for idx, label_el in enumerate(form_labels):
                element_info = {
                    "index": idx,
                    "tag": "el-form-item__label",
                    "text": label_el.inner_text().strip(),
                    "visible": label_el.is_visible()
                }
                label_elements.append(element_info)
            
            # 探测按钮
            buttons = dialog.locator("button").all()
            button_elements = []
            for idx, btn_el in enumerate(buttons):
                element_info = {
                    "index": idx,
                    "tag": "button",
                    "text": btn_el.inner_text().strip(),
                    "type": btn_el.get_attribute("type"),
                    "visible": btn_el.is_visible()
                }
                button_elements.append(element_info)
            
            # 整合探测结果
            detection_result = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "form_title": "添加用户",
                "dialog_exists": True,
                "form_fields": {
                    "inputs": input_elements,
                    "selects": select_elements,
                    "dept_tree": dept_info,
                    "radios": radio_elements,
                    "textareas": textarea_elements,
                    "labels": label_elements,
                    "buttons": button_elements
                }
            }
            
            # 保存探测结果
            output_file = "工作区/20260105+前端表单功能测试/探测结果.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(detection_result, f, ensure_ascii=False, indent=2)
            
            print(f"\n探测完成！结果已保存到: {output_file}")
            print(f"\n表单字段统计:")
            print(f"  - 输入框: {len(input_elements)} 个")
            print(f"  - 下拉框: {len(select_elements)} 个")
            print(f"  - 单选按钮: {len(radio_elements)} 个")
            print(f"  - 文本域: {len(textarea_elements)} 个")
            print(f"  - 表单标签: {len(label_elements)} 个")
            print(f"  - 按钮: {len(button_elements)} 个")
            
            # 保持浏览器打开一段时间以便查看
            print("\n浏览器将保持打开 10 秒以便查看...")
            page.wait_for_timeout(10000)
            
        except Exception as e:
            print(f"探测过程中发生错误: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            browser.close()

if __name__ == "__main__":
    detect_form_elements()