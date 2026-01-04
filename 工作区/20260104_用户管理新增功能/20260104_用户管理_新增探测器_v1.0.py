# -*- coding: utf-8 -*-
"""
用户管理新增功能探测器
用于探测新增用户表单的所有元素
"""

from playwright.sync_api import sync_playwright
import json
import time
import sys
import io

# 设置标准输出为UTF-8编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def detect_form_elements():
    """探测新增用户表单的所有元素"""
    with sync_playwright() as p:
        # 创建浏览器实例（有头模式）
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        try:
            # 第一步：登录系统
            print("正在登录系统...")
            page.goto("http://192.168.142.146/login?redirect=%2Findex")
            
            # 输入用户名（根据实际HTML结构使用placeholder定位）
            page.wait_for_selector('input[placeholder="账号"]', timeout=15000)
            page.fill('input[placeholder="账号"]', "admin")
            print("已输入用户名：admin")
            
            # 输入密码（根据实际HTML结构使用placeholder定位）
            page.fill('input[placeholder="密码"]', "admin123")
            print("已输入密码：admin123")
            
            # 点击登录按钮（根据实际HTML结构使用文本定位）
            page.click('button:has-text("登 录")')
            print("已点击登录按钮")
            
            # 等待登录成功
            page.wait_for_load_state('networkidle')
            time.sleep(2)
            print("登录成功")
            
            # 第二步：导航到用户管理页面
            print("\n正在导航到用户管理页面...")
            
            # 直接导航到用户管理页面（更可靠的方式）
            print("正在直接导航到用户管理页面...")
            page.goto("http://192.168.142.146/#/system/user", timeout=15000)
            time.sleep(2)
            print("已导航到用户管理页面")
            
            # 第三步：验证当前是否在用户管理页面
            print("\n验证当前页面...")
            current_url = page.url
            print(f"当前URL: {current_url}")
            
            # 检查页面标题或内容
            page_content = page.content()
            if "用户管理" in page_content:
                print("确认：当前是用户管理页面")
            elif "岗位" in page_content:
                print("警告：当前是岗位管理页面！")
            
            # 查找页面上的所有按钮
            print("\n正在查找页面元素...")
            all_buttons = page.locator('button').all()
            print(f"页面上共有 {len(all_buttons)} 个按钮")
            
            # 打印所有按钮的文本
            for i, btn in enumerate(all_buttons[:10]):  # 只打印前10个
                text = btn.text_content().strip()
                btn_type = btn.get_attribute("type")
                print(f"  按钮 {i}: '{text}' (type={btn_type})")
            
            # 查找新增按钮
            add_buttons = page.locator('button:has-text("新增")').all()
            print(f"\n找到 {len(add_buttons)} 个包含'新增'文本的按钮")
            
            # 如果没找到，尝试查找其他可能的按钮
            if len(add_buttons) == 0:
                print("未找到新增按钮，尝试查找其他按钮...")
                # 查找带el-icon-plus图标的按钮
                icon_buttons = page.locator('button i.el-icon-plus').locator('..').all()
                print(f"找到 {len(icon_buttons)} 个带el-icon-plus图标的按钮")
                
                if len(icon_buttons) > 0:
                    icon_buttons[0].click()
                    print("已点击带el-icon-plus图标的按钮")
                else:
                    # 打印页面HTML片段用于调试
                    print("\n打印页面头部HTML用于调试...")
                    body_html = page.locator('body').inner_html()[:2000]
                    print(body_html)
                    raise Exception("未找到新增按钮或图标按钮")
            else:
                # 点击第一个新增按钮
                add_buttons[0].click()
                print("已点击第一个新增按钮")
            
            # 等待对话框出现
            time.sleep(2)
            
            # 再次验证页面
            dialog_count = page.locator('div[role="dialog"]').count()
            print(f"找到 {dialog_count} 个对话框")
            
            # 第四步：探测表单元素
            print("\n开始探测表单元素...")
            
            # 探测对话框（等待对话框出现）
            dialog = page.locator('div[role="dialog"]').first
            try:
                dialog.wait_for(state='visible', timeout=5000)
                print(f"找到对话框: 可见")
            except:
                print(f"对话框状态: {dialog.count()} 个对话框")
            
            # 探测所有表单项
            form_elements = {
                "dialog_info": {
                    "visible": dialog.is_visible(),
                    "title": dialog.locator('span.el-dialog__title').text_content() if dialog.locator('span.el-dialog__title').count() > 0 else None
                }
            }
            
            # 探测所有输入框
            inputs = page.locator('div[role="dialog"] input').all()
            print(f"\n找到 {len(inputs)} 个输入框")
            
            input_elements = []
            for i, input_elem in enumerate(inputs):
                elem_info = {
                    "index": i,
                    "type": input_elem.get_attribute("type"),
                    "placeholder": input_elem.get_attribute("placeholder"),
                    "max_length": input_elem.get_attribute("maxlength"),
                    "name": input_elem.get_attribute("name"),
                    "id": input_elem.get_attribute("id")
                }
                
                # 获取label
                parent = input_elem.locator('..')
                label = parent.locator('label').first
                if label.count() > 0:
                    elem_info["label"] = label.text_content().strip()
                
                input_elements.append(elem_info)
                print(f"  输入框 {i}: {elem_info}")
            
            form_elements["inputs"] = input_elements
            
            # 探测选择框（包括下拉框和树形选择）
            selects_info = []
            
            # 查找treeselect组件
            treeselects = page.locator('div[role="dialog"] .vue-treeselect__control').all()
            print(f"\n找到 {len(treeselects)} 个树形选择框")
            
            for i, treeselect in enumerate(treeselects):
                elem_info = {
                    "index": i,
                    "type": "treeselect",
                    "placeholder": treeselect.get_attribute("placeholder")
                }
                
                # 获取label
                parent = treeselect.locator('..').locator('..')
                label = parent.locator('label').first
                if label.count() > 0:
                    elem_info["label"] = label.text_content().strip()
                
                selects_info.append(elem_info)
                print(f"  树形选择框 {i}: {elem_info}")
            
            # 查找普通的select
            el_selects = page.locator('div[role="dialog"] select').all()
            print(f"\n找到 {len(el_selects)} 个下拉选择框")
            
            for i, el_select in enumerate(el_selects):
                elem_info = {
                    "index": i,
                    "type": "select"
                }
                
                # 获取label
                parent = el_select.locator('..').locator('..')
                label = parent.locator('label').first
                if label.count() > 0:
                    elem_info["label"] = label.text_content().strip()
                
                selects_info.append(elem_info)
                print(f"  下拉选择框 {i}: {elem_info}")
            
            form_elements["selects"] = selects_info
            
            # 探测单选按钮组
            radio_groups = []
            radio_groups_elements = page.locator('div[role="dialog"] .el-radio-group').all()
            print(f"\n找到 {len(radio_groups_elements)} 个单选按钮组")
            
            for i, radio_group in enumerate(radio_groups_elements):
                elem_info = {
                    "index": i,
                    "type": "radio_group"
                }
                
                # 获取label
                parent = radio_group.locator('..').locator('..')
                label = parent.locator('label').first
                if label.count() > 0:
                    elem_info["label"] = label.text_content().strip()
                
                # 获取选项
                radios = radio_group.locator('.el-radio').all()
                options = []
                for radio in radios:
                    option_text = radio.text_content().strip()
                    options.append(option_text)
                elem_info["options"] = options
                
                radio_groups.append(elem_info)
                print(f"  单选按钮组 {i}: {elem_info}")
            
            form_elements["radio_groups"] = radio_groups
            
            # 探测多选下拉框
            multi_selects = []
            # 通过查找多选select来识别
            multi_select_inputs = page.locator('div[role="dialog"] input[multiple]').all()
            print(f"\n找到 {len(multi_select_inputs)} 个多选输入框")
            
            for i, multi_input in enumerate(multi_select_inputs):
                elem_info = {
                    "index": i,
                    "type": "select_multiple"
                }
                
                # 获取label
                parent = multi_input.locator('..').locator('..')
                label = parent.locator('label').first
                if label.count() > 0:
                    elem_info["label"] = label.text_content().strip()
                
                multi_selects.append(elem_info)
                print(f"  多选框 {i}: {elem_info}")
            
            form_elements["multi_selects"] = multi_selects
            
            # 探测文本域
            textareas = page.locator('div[role="dialog"] textarea').all()
            print(f"\n找到 {len(textareas)} 个文本域")
            
            textarea_elements = []
            for i, textarea in enumerate(textareas):
                elem_info = {
                    "index": i,
                    "type": "textarea",
                    "placeholder": textarea.get_attribute("placeholder")
                }
                
                # 获取label
                parent = textarea.locator('..')
                label = parent.locator('label').first
                if label.count() > 0:
                    elem_info["label"] = label.text_content().strip()
                
                textarea_elements.append(elem_info)
                print(f"  文本域 {i}: {elem_info}")
            
            form_elements["textareas"] = textarea_elements
            
            # 探测底部按钮
            buttons = page.locator('div[role="dialog"] .dialog-footer button').all()
            print(f"\n找到 {len(buttons)} 个底部按钮")
            
            button_elements = []
            for i, button in enumerate(buttons):
                elem_info = {
                    "index": i,
                    "text": button.text_content().strip(),
                    "type": button.get_attribute("type")
                }
                button_elements.append(elem_info)
                print(f"  按钮 {i}: {elem_info}")
            
            form_elements["buttons"] = button_elements
            
            # 输出探测结果
            print("\n===== 探测结果 =====")
            print(json.dumps(form_elements, ensure_ascii=False, indent=2))
            
            # 保存探测结果到文件
            import os
            result_file = os.path.join(os.path.dirname(__file__), "探测结果.json")
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(form_elements, f, ensure_ascii=False, indent=2)
            print(f"\n探测结果已保存到: {result_file}")
            
            # 保持浏览器打开一段时间以便查看
            print("\n浏览器将保持打开30秒...")
            time.sleep(30)
            
        except Exception as e:
            print(f"\n发生错误: {e}")
            print("浏览器将保持打开以便调试...")
            time.sleep(60)
        
        finally:
            browser.close()


if __name__ == "__main__":
    detect_form_elements()