"""
用户新增功能探测器脚本
用于探测新增用户对话框的所有表单元素
"""

from playwright.sync_api import sync_playwright, expect
import json

def detect_form_elements():
    """探测新增用户对话框的所有表单元素"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        base_url = "http://192.168.142.146/"
        
        try:
            print("=== 开始探测新增用户表单元素 ===")
            
            # 1. 访问登录页面
            page.goto(base_url + 'login?redirect=%2Findex')
            page.wait_for_load_state("networkidle")
            
            # 2. 登录
            page.get_by_role("button", name="登 录").click()
            page.wait_for_url("**/index", timeout=10000)
            print("登录成功")
            
            # 3. 导航到用户管理
            print("正在展开侧边栏菜单...")
            system_menu = page.locator("li").filter(has_text="系统管理").first
            system_menu.click()
            
            user_link = page.get_by_role("link", name="用户管理")
            user_link.wait_for(state="visible", timeout=5000)
            user_link.click()
            print("已进入用户管理页面")
            page.wait_for_load_state("networkidle")
            
            # 4. 点击新增按钮
            print("点击新增按钮...")
            page.get_by_role("button", name="新增").click()
            
            # 5. 等待对话框出现
            dialog = page.get_by_role("dialog")
            dialog.wait_for(state="visible", timeout=5000)
            print("新增对话框已弹出")
            
            # 6. 探测表单元素
            form_elements = {}
            
            # 探测所有el-form-item标签
            form_items = dialog.locator(".el-form-item")
            count = form_items.count()
            print(f"共找到 {count} 个表单项")
            
            for i in range(count):
                item = form_items.n(i)
                
                # 获取label文本（使用占位符或label）
                try:
                    label = item.locator("label").inner_text(timeout=1000)
                    if not label:
                        # 尝试从placeholder获取
                        placeholder = item.locator("input").get_attribute("placeholder", timeout=1000)
                        if placeholder:
                            label = placeholder.replace("请输入", "").replace("请选择", "")
                except:
                    label = f"字段_{i+1}"
                
                # 获取输入元素类型
                input_type = None
                input_selector = None
                
                # 检查是否有input输入框
                try:
                    input_el = item.locator("input").first
                    input_type = input_el.get_attribute("type")
                    input_placeholder = input_el.get_attribute("placeholder")
                    input_selector = f".el-form-item:nth-child({i+2}) input"
                    form_elements[f"{label}"] = {
                        "type": "input",
                        "input_type": input_type,
                        "placeholder": input_placeholder,
                        "selector": input_selector
                    }
                except:
                    pass
                
                # 检查是否有下拉框
                try:
                    select_el = item.locator(".el-select").first
                    if select_el.is_visible():
                        input_selector = f".el-form-item:nth-child({i+2}) .el-select"
                        form_elements[f"{label}"] = {
                            "type": "select",
                            "selector": input_selector
                        }
                except:
                    pass
                
                # 检查是否有部门树选择器（vue-treeselect）
                try:
                    tree_select = item.locator(".vue-treeselect").first
                    if tree_select.is_visible():
                        input_selector = f".el-form-item:nth-child({i+2}) .vue-treeselect__control"
                        form_elements[f"{label}"] = {
                            "type": "tree_select",
                            "selector": input_selector
                        }
                except:
                    pass
                
                # 检查是否有单选按钮组（性别、状态）
                try:
                    radio_group = item.locator(".el-radio-group").first
                    if radio_group.is_visible():
                        input_selector = f".el-form-item:nth-child({i+2}) .el-radio-group"
                        form_elements[f"{label}"] = {
                            "type": "radio_group",
                            "selector": input_selector
                        }
                except:
                    pass
                
                # 检查是否是多选（岗位、角色）
                try:
                    tags = item.locator(".el-tag").first
                    if tags.is_visible():
                        input_selector = f".el-form-item:nth-child({i+2}) .el-select"
                        form_elements[f"{label}"] = {
                            "type": "multi_select",
                            "selector": input_selector
                        }
                except:
                    pass
                
                # 检查是否有文本域
                try:
                    textarea = item.locator("textarea").first
                    if textarea.is_visible():
                        input_selector = f".el-form-item:nth-child({i+2}) textarea"
                        form_elements[f"{label}"] = {
                            "type": "textarea",
                            "selector": input_selector
                        }
                except:
                    pass
            
            # 探测按钮
            buttons = dialog.locator(".el-dialog__footer button")
            button_count = buttons.count()
            print(f"共找到 {button_count} 个按钮")
            
            form_elements["buttons"] = []
            for i in range(button_count):
                btn = buttons.n(i)
                btn_text = btn.inner_text(timeout=1000)
                form_elements["buttons"].append({
                    "name": btn_text,
                    "selector": f".el-dialog__footer button:nth-child({i+1})"
                })
            
            # 输出探测结果
            result = {
                "success": True,
                "message": "探测成功",
                "form_title": dialog.locator(".el-dialog__title").inner_text(),
                "form_elements": form_elements
            }
            
            print("\n=== 探测结果 ===")
            print(json.dumps(result, ensure_ascii=False, indent=2))
            
            # 保存探测结果到文件
            with open("探测结果.json", "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            print("\n探测结果已保存到 探测结果.json")
            
            # 保持浏览器打开30秒供观察
            page.wait_for_timeout(30000)
            
        except Exception as e:
            print(f"探测过程中发生错误: {str(e)}")
            result = {
                "success": False,
                "message": f"探测失败: {str(e)}"
            }
        finally:
            browser.close()
            print("浏览器已关闭")

if __name__ == "__main__":
    detect_form_elements()