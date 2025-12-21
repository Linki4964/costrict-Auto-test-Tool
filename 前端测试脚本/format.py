import time
from playwright.sync_api import sync_playwright, expect

def test_add_user_module():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        try:
            print("=== 开始执行：新增用户模块测试 ===")
            page.goto('http://192.168.142.146/login?redirect=%2Findex')
            
            # 1. 登录
            page.get_by_role("button", name="登 录").click()
            # 等待 URL 跳转到首页，确保页面加载完成
            page.wait_for_url("**/index") 

            # 2. 导航到用户管理 (加固版)
            print("正在展开侧边栏菜单...")
            # 找到包含“系统管理”文字的菜单项并点击
            system_menu = page.locator("li").filter(has_text="系统管理").first
            system_menu.click()
            
            # 给一点点缓冲时间让菜单展开动画完成（或显式等待子菜单可见）
            user_link = page.get_by_role("link", name="用户管理")
            user_link.wait_for(state="visible", timeout=5000)
            user_link.click()
            print("已进入用户管理页面")

            # 3. 点击新增按钮
            # 若依的新增按钮通常带有特定的类名，或者可以用文本匹配
            page.get_by_role("button", name="新增").click()

            # 4. 填写表单 (使用你提供的诊断逻辑)
            dialog = page.get_by_role("dialog")
            # 自动生成一个随机后缀，防止重复无法提交
            import random
            test_id = random.randint(1000, 9999)
            
            print(f"填写用户信息: ai_test_{test_id}")
            dialog.get_by_placeholder("请输入用户昵称").fill(f"昵称_{test_id}")
            
            # 部门选择 (Vue-treeselect 容易出错，改用更通用的定位器)
            page.locator(".vue-treeselect__control").click()
            page.locator(".vue-treeselect__menu").get_by_text("若依科技").first.click()

            dialog.get_by_placeholder("请输入手机号码").fill(f"1380000{test_id}")
            dialog.get_by_placeholder("请输入邮箱").fill(f"test{test_id}@qq.com")
            dialog.get_by_placeholder("请输入用户名称").fill(f"user_{test_id}")
            dialog.get_by_placeholder("请输入用户密码").fill("123456") # 若依新增通常需要密码

            # 提交与验证
            print("提交表单...")
            page.locator(".el-dialog__footer").get_by_role("button", name="确 定").click()

            # 检查成功提示
            success_msgs = ["操作成功", "新增成功", "保存成功"]
            success_found = False
            for msg in success_msgs:
                try:
                    # 降低 timeout 以便快速切换检查
                    expect(page.get_by_text(msg)).to_be_visible(timeout=2000)
                    success_found = True
                    print(f"[PASS] 找到提示: {msg}")
                    break
                except:
                    continue
            
            if not success_found:
                # 额外检查是否有表单校验报错提示
                error_msg = page.locator(".el-form-item__error").first
                if error_msg.is_visible():
                    print(f"[FAIL] 表单校验未通过: {error_msg.inner_text()}")
                else:
                    print("[WARN] 未找到提示，请检查截图")

        except Exception as e:
            print(f"\n[FAIL] 测试执行中出错: {e}")
            page.screenshot(path="debug_error.png")
            raise 
        finally:
            time.sleep(2) # 留出观察时间
            browser.close()

if __name__ == "__main__":
    test_add_user_module()