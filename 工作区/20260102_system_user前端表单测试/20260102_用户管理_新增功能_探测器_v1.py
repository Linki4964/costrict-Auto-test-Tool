from playwright.sync_api import sync_playwright
import json
import time
import re

def detect_form_elements():
    """探测新增用户表单的所有元素"""
    url = "http://192.168.142.146"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        try:
            print("=" * 50)
            print("开始探测用户管理-新增功能表单元素")
            print("=" * 50)
            
            # 步骤1: 访问登录页面
            page.goto(url)
            page.wait_for_load_state("networkidle")
            print("\n[1/8] 访问登录页面完成")
            
            # 步骤2: 登录
            time.sleep(2)
            # 尝试多种定位方式
            try:
                # 方式1: 通过placeholder
                page.get_by_placeholder("用户名").fill("admin")
                page.get_by_placeholder("密码").fill("admin123")
            except:
                try:
                    # 方式2: 通过input类型和顺序
                    inputs = page.locator(".el-form-item input")
                    inputs.nth(0).fill("admin")
                    inputs.nth(1).fill("admin123")
                except:
                    # 方式3: 通过CSS选择器
                    page.locator("input[placeholder]").nth(0).fill("admin")
                    page.locator("input[placeholder][type='password']").fill("admin123")
            
            # 点击登录按钮
            try:
                page.get_by_role("button", name="登 录").click()
            except:
                try:
                    page.get_by_role("button", name="登录").click()
                except:
                    # 通过CSS选择器点击登录
                    page.locator(".el-button--primary").click()
            print("[2/8] 登录操作完成")
            
            # 等待登录成功
            page.wait_for_load_state("networkidle")
            time.sleep(2)
            
            # 步骤3: 点击系统管理菜单
            print("[3/8] 正在点击左侧菜单：系统管理")
            time.sleep(1)
            # 使用更精确的选择器定位系统管理菜单
            page.locator(".el-submenu__title").filter(has_text="系统管理").click()
            time.sleep(1)
            
            # 步骤4: 点击用户管理子菜单
            print("[4/8] 正在点击用户管理菜单")
            # 使用CSS选择器定位用户管理菜单项
            page.locator(".el-menu-item").filter(has_text="用户管理").click()
            time.sleep(2)
            print("[5/8] 进入用户管理页面")
            
            # 步骤5: 点击新增按钮
            print("[6/8] 正在点击新增按钮")
            time.sleep(1)
            try:
                # 方式1: 通过精确文本
                page.get_by_role("button", name="新增", exact=True).click()
            except:
                try:
                    # 方式2: 通过包含文本
                    page.get_by_role("button", name=re.compile("新增")).click()
                except:
                    # 方式3: 通过CSS选择器
                    page.locator(".mb8 .el-button--primary").first.click()
            time.sleep(2)
            print("[7/8] 新增用户对话框已打开")
            
            # 步骤6: 探测表单元素
            print("\n[8/8] 开始探测表单元素...")
            form_elements = {}
            
            # 定位对话框
            dialog = page.locator(".el-dialog").filter(has_text="添加用户")
            
            # 探测输入框
            inputs = dialog.locator("input[type='text'], input[type='password'], textarea")
            input_count = inputs.count()
            print(f"\n探测到 {input_count} 个输入框/文本区域")
            
            for i in range(input_count):
                element = inputs.nth(i)
                try:
                    placeholder = element.get_attribute("placeholder")
                    parent_label = element.locator("xpath=../..").locator("label").text_content()
                    prop = element.locator("xpath=../..").get_attribute("prop")
                    
                    field_key = prop if prop else f"field_{i}"
                    form_elements[field_key] = {
                        "label": parent_label.strip() if parent_label else placeholder,
                        "placeholder": placeholder,
                        "selector": f"[prop='{prop}'] input" if prop else f"input:nth-of-type({i+1})",
                        "element_type": "input"
                    }
                    print(f"  - {field_key}: {parent_label} ({placeholder})")
                except Exception as e:
                    print(f"  - 探测第{i+1}个输入框时出错: {e}")
            
            # 探测下拉框
            selects = dialog.locator(".el-select")
            select_count = selects.count()
            print(f"\n探测到 {select_count} 个下拉框")
            
            for i in range(select_count):
                element = selects.nth(i)
                try:
                    prop = element.get_attribute("prop")
                    label = element.locator("xpath=../..").locator("label").text_content()
                    field_key = prop if prop else f"select_{i}"
                    
                    form_elements[field_key] = {
                        "label": label.strip(),
                        "selector": f"[prop='{prop}'] .el-input__inner" if prop else f".el-select:nth-of-type({i+1})",
                        "element_type": "select"
                    }
                    print(f"  - {field_key}: {label}")
                except Exception as e:
                    print(f"  - 探测第{i+1}个下拉框时出错: {e}")
            
            # 探测树形选择器
            treeselects = dialog.locator(".vue-treeselect")
            treeselect_count = treeselects.count()
            print(f"\n探测到 {treeselect_count} 个树形选择器")
            
            for i in range(treeselect_count):
                element = treeselects.nth(i)
                try:
                    prop = element.locator("xpath=../..").get_attribute("prop")
                    label = element.locator("xpath=../..").locator("label").text_content()
                    field_key = prop if prop else f"treeselect_{i}"
                    
                    form_elements[field_key] = {
                        "label": label.strip(),
                        "selector": f"[prop='{prop}'] .vue-treeselect__control" if prop else f".vue-treeselect:nth-of-type({i+1})",
                        "element_type": "treeselect"
                    }
                    print(f"  - {field_key}: {label}")
                except Exception as e:
                    print(f"  - 探测第{i+1}个树形选择器时出错: {e}")
            
            # 探测对话框按钮
            confirm_btn = dialog.locator(".dialog-footer .el-button--primary")
            cancel_btn = dialog.locator(".dialog-footer .el-button--default")
            
            print(f"\n探测到对话框按钮:")
            print(f"  - 确定按钮: {confirm_btn.count()} 个")
            print(f"  - 取消按钮: {cancel_btn.count()} 个")
            
            form_elements["buttons"] = {
                "confirm": ".dialog-footer .el-button--primary",
                "cancel": ".dialog-footer .el-button--default"
            }
            
            # 关闭对话框
            print("\n关闭对话框...")
            cancel_btn.click()
            time.sleep(1)
            
            # 保存探测结果
            result = {
                "探测时间": time.strftime("%Y-%m-%d %H:%M:%S"),
                "页面": "新增用户",
                "表单字段数量": len(form_elements) - 1,  # 减去buttons
                "表单元素": form_elements
            }
            
            output_path = "工作区/20260102_system_user前端表单测试/detect_result.json"
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            print(f"\n{'=' * 50}")
            print(f"探测完成！结果已保存至: {output_path}")
            print(f"{'=' * 50}")
            
            return result
            
        except Exception as e:
            print(f"\n探测过程中出错: {e}")
            import traceback
            traceback.print_exc()
            return None
        finally:
            time.sleep(3)
            browser.close()

if __name__ == "__main__":
    detect_form_elements()