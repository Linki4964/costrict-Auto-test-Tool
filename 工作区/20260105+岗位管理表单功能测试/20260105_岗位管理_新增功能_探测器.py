# -*- coding: utf-8 -*-
from playwright.sync_api import sync_playwright
import json

def detect_form_elements():
    """
    探测岗位管理新增功能的表单元素
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        # 访问登录页面
        page.goto("http://192.168.142.146/login?redirect=%2Findex")
        
        # 等待页面加载
        page.wait_for_load_state("networkidle")
        
        # 点击登录按钮（默认已填充凭证）
        page.get_by_role("button", name="登 录").click()
        
        # 等待跳转到首页
        page.wait_for_url("**/index", timeout=5000)
        
        # 导航到岗位管理
        print("正在展开侧边栏菜单...")
        system_menu = page.locator("li").filter(has_text="系统管理").first
        system_menu.click()
        
        # 等待岗位管理链接可见
        user_link = page.get_by_role("link", name="岗位管理")
        user_link.wait_for(state="visible", timeout=5000)
        user_link.click()
        print("已进入岗位管理页面")
        
        # 点击新增按钮
        add_button = page.get_by_role("button", name="新增")
        add_button.click()
        
        # 等待对话框出现
        dialog = page.get_by_role("dialog")
        dialog.wait_for(state="visible", timeout=5000)
        
        # 探测表单元素
        form_elements = []
        
        # 探测所有 input 元素
        inputs = dialog.locator("input").all()
        for idx, input_elem in enumerate(inputs):
            try:
                placeholder = input_elem.get_attribute("placeholder") or ""
                input_type = input_elem.get_attribute("type") or "text"
                name = input_elem.get_attribute("name") or ""
                role = input_elem.get_attribute("role") or ""
                
                elem_info = {
                    "tag": "input",
                    "index": idx,
                    "type": input_type,
                    "placeholder": placeholder,
                    "name": name,
                    "role": role
                }
                form_elements.append(elem_info)
            except Exception as e:
                print(f"探测input元素{idx}失败: {e}")
        
        # 探测所有 textarea 元素
        textareas = dialog.locator("textarea").all()
        for idx, textarea in enumerate(textareas):
            try:
                placeholder = textarea.get_attribute("placeholder") or ""
                elem_info = {
                    "tag": "textarea",
                    "index": idx,
                    "placeholder": placeholder
                }
                form_elements.append(elem_info)
            except Exception as e:
                print(f"探测textarea元素{idx}失败: {e}")
        
        # 探测所有 label 元素（用于单选按钮等）
        labels = dialog.locator("label").all()
        for idx, label in enumerate(labels):
            try:
                text = label.inner_text()
                if text.strip():
                    elem_info = {
                        "tag": "label",
                        "index": idx,
                        "text": text.strip()
                    }
                    form_elements.append(elem_info)
            except Exception as e:
                print(f"探测label元素{idx}失败: {e}")
        
        # 探测按钮
        buttons = dialog.locator("button").all()
        for idx, button in enumerate(buttons):
            try:
                text = button.inner_text()
                elem_info = {
                    "tag": "button",
                    "index": idx,
                    "text": text.strip()
                }
                form_elements.append(elem_info)
            except Exception as e:
                print(f"探测button元素{idx}失败: {e}")
        
        # 输出探测结果
        result = {
            "dialog_title": dialog.inner_text().split('\n')[0] if dialog.inner_text() else "未知",
            "form_elements": form_elements
        }
        
        print("\n" + "="*50)
        print("表单元素探测结果:")
        print("="*50)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # 保存探测结果到JSON文件
        with open("工作区/20260105+岗位管理表单功能测试/detection_result.json", "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print("\n探测结果已保存到 detection_result.json")
        
        # 等待用户查看
        input("按回车键关闭浏览器...")
        
        browser.close()

if __name__ == "__main__":
    detect_form_elements()