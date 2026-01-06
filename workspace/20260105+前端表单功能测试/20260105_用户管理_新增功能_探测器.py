import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import asyncio
from playwright.async_api import async_playwright, expect

async def detect_form_elements():
    print("===== 开始探测用户管理新增对话框表单元素 =====")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        base_url = "http://192.168.142.146/"
        
        try:
            print(f"[步骤1] 访问登录页面: {base_url}")
            await page.goto(f"{base_url}login?redirect=%2Findex")
            
            print("[步骤2] 点击登录按钮（使用默认凭证）")
            await page.get_by_role("button", name="登 录").click()
            
            print("[步骤3] 等待页面跳转到首页")
            await page.wait_for_url("**/index")
            
            print("[步骤4] 展开侧边栏系统管理菜单")
            system_menu = page.locator("li").filter(has_text="系统管理").first
            await system_menu.click()
            
            print("[步骤5] 点击用户管理菜单项")
            user_link = page.get_by_role("link", name="用户管理")
            await user_link.wait_for(state="visible", timeout=10000)
            await user_link.click()
            print("已进入用户管理页面")
            
            await page.wait_for_timeout(2000)
            
            print("[步骤6] 点击新增按钮")
            add_button = page.get_by_role("button", name="新增")
            await add_button.wait_for(state="visible", timeout=5000)
            await add_button.click()
            
            print("[步骤7] 等待对话框弹出")
            await page.wait_for_timeout(1000)
            dialog = page.get_by_role("dialog")
            await dialog.wait_for(state="visible", timeout=10000)
            print("对话框已弹出，开始探测表单元素...")
            
            elements_info = []
            
            dialog_handle = await dialog.element_handle()
            inputs = await dialog_handle.query_selector_all("input")
            print(f"\n探测到 {len(inputs)} 个输入框:")
            
            for idx, input_elem in enumerate(inputs):
                try:
                    placeholder = await input_elem.get_attribute("placeholder")
                    input_type = await input_elem.get_attribute("type")
                    name = await input_elem.get_attribute("name")
                    
                    elem_info = {
                        "index": idx,
                        "tag": "input",
                        "type": input_type,
                        "placeholder": placeholder,
                        "name": name
                    }
                    elements_info.append(elem_info)
                    print(f"  [{idx}] type={input_type}, placeholder={placeholder}, name={name}")
                except Exception as e:
                    print(f"  [{idx}] 获取属性失败: {e}")
            
            selects = await dialog_handle.query_selector_all("select")
            print(f"\n探测到 {len(selects)} 个下拉选择框:")
            
            for idx, select_elem in enumerate(selects):
                try:
                    options = await select_elem.query_selector_all("option")
                    option_texts = []
                    for opt in options:
                        text = await opt.text_content()
                        option_texts.append(text)
                    
                    elem_info = {
                        "index": idx,
                        "tag": "select",
                        "options_count": len(options),
                        "options": option_texts[:5]
                    }
                    elements_info.append(elem_info)
                    print(f"  [{idx}] 选项数量={len(options)}, 前5个选项: {option_texts[:5]}")
                except Exception as e:
                    print(f"  [{idx}] 获取下拉框信息失败: {e}")
            
            treeselects = await dialog_handle.query_selector_all(".vue-treeselect__control")
            print(f"\n探测到 {len(treeselects)} 个树形选择器:")
            
            for idx, ts_elem in enumerate(treeselects):
                try:
                    elem_info = {
                        "index": idx,
                        "tag": "vue-treeselect",
                        "selector": ".vue-treeselect__control"
                    }
                    elements_info.append(elem_info)
                    print(f"  [{idx}] vue-treeselect 组件")
                    
                    await ts_elem.click()
                    await page.wait_for_timeout(1000)
                    menu_items = await page.query_selector_all(".vue-treeselect__menu div")
                    print(f"      树形菜单项数量: {len(menu_items)}")
                    
                    for item_idx, item in enumerate(menu_items[:10]):
                        try:
                            text = await item.text_content()
                            if text and text.strip():
                                print(f"        [{item_idx}] {text.strip()}")
                        except:
                            pass
                except Exception as e:
                    print(f"  [{idx}] 获取树形选择器信息失败: {e}")
            
            buttons = await dialog_handle.query_selector_all("button")
            print(f"\n探测到 {len(buttons)} 个按钮:")
            
            for idx, btn_elem in enumerate(buttons):
                try:
                    text = await btn_elem.text_content()
                    btn_type = await btn_elem.get_attribute("type")
                    
                    elem_info = {
                        "index": idx,
                        "tag": "button",
                        "text": text,
                        "type": btn_type
                    }
                    elements_info.append(elem_info)
                    print(f"  [{idx}] text={text}, type={btn_type}")
                except Exception as e:
                    print(f"  [{idx}] 获取按钮信息失败: {e}")
            
            print("\n===== 探测完成 =====")
            print(f"总计探测到 {len(elements_info)} 个表单元素")
            
            import json
            with open(r"工作区\20260105+前端表单功能测试\探测结果.json", "w", encoding="utf-8") as f:
                json.dump({
                    "total_elements": len(elements_info),
                    "elements": elements_info
                }, f, ensure_ascii=False, indent=2)
            print("\n探测结果已保存至: 探测结果.json")
            
            await page.wait_for_timeout(5000)
            
        except Exception as e:
            print(f"\n[ERROR] 探测过程中发生错误: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(detect_form_elements())