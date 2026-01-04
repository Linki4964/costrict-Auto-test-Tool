# -*- coding: utf-8 -*-
import json
import random
import string
from datetime import datetime
from playwright.sync_api import sync_playwright, expect

def read_config():
    """Read configuration file"""
    with open('configure.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_random_data(prefix='test'):
    """Generate random test data"""
    random_num = ''.join(random.choices(string.digits, k=4))
    return f'{prefix}{random_num}'

def detect_form_elements():
    """Detect all elements of the add user form"""
    config = read_config()
    base_url = config['project_setup']['target_url']
    login_url = config['authentication']['login_page_url']
    username = config['authentication']['username']
    password = config['authentication']['password']
    
    result = {
        'test_info': {
            'url': base_url,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'login': {'username': username, 'password': password}
        },
        'form_elements': [],
        'network_requests': []
    }
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.set_default_timeout(10000)
        
        # 监控网络请求
        def log_request(request):
            if '/api/' in request.url or '/system/' in request.url:
                request_info = {
                    'method': request.method,
                    'url': request.url.replace(base_url, ''),
                    'headers': dict(request.headers)
                }
                result['network_requests'].append(request_info)
        
        page.on('request', log_request)
        
        try:
            # Step 1: Open login page
            print(f"Opening login page: {login_url}")
            page.goto(login_url, wait_until='networkidle')
            
            # Step 2: Input username
            print(f"Inputting username: {username}")
            username_input = page.get_by_placeholder('Username')
            if username_input.count() == 0:
                username_input = page.get_by_placeholder('User name')
            username_input.fill(username)
            
            # Step 3: Input password
            print(f"Inputting password")
            password_input = page.get_by_placeholder('Password')
            password_input.fill(password)
            
            # Step 4: Click login button
            print("Clicking login button")
            login_button = page.locator('button').filter(has_text='Login')
            if login_button.count() == 0:
                login_button = page.get_by_role('button', name='Login')
            if login_button.count() == 0:
                login_button = page.locator('button').filter(has_text='Log In')
            if login_button.count() == 0:
                login_button = page.locator('.el-button--primary').filter(has_text='Sign in')
            login_button.click()
            
            # Wait for login to complete
            print("Waiting for page redirect...")
            page.wait_for_load_state('networkidle', timeout=15000)
            
            # Verify successful login
            expect(page).to_have_url(base_url + 'index')
            print("Login successful!")
            
            # Wait for page to fully load
            page.wait_for_timeout(2000)
            
            # Step 5: Click System Management menu
            print("Clicking 'System Management' menu")
            system_menu = page.locator('span').filter(has_text='System')
            if system_menu.count() == 0:
                system_menu = page.locator('span').filter(has_text='System Management')
            if system_menu.count() == 0:
                system_menu = page.locator('.el-submenu__title').filter(has_text='System')
            system_menu.click()
            page.wait_for_timeout(1000)
            
            # Step 6: Click User Management
            print("Clicking 'User Management' menu")
            user_menu = page.locator('p').filter(has_text='User')
            if user_menu.count() == 0:
                user_menu = page.locator('p').filter(has_text='User Management')
            if user_menu.count() == 0:
                user_menu = page.locator('.el-menu-item').filter(has_text='User')
            user_menu.click()
            
            # Wait for user list page to load
            print("Waiting for user management page to load...")
            page.wait_for_load_state('networkidle', timeout=10000)
            page.wait_for_timeout(2000)
            
            # Step 7: Click Add button
            print("Clicking 'Add' button")
            add_button = page.locator('button').filter(has_text='Add')
            if add_button.count() == 0:
                add_button = page.locator('button').filter(has_text='New')
            if add_button.count() == 0:
                add_button = page.locator('button').filter(has_text='Create')
            if add_button.count() == 0:
                add_button = page.locator('.el-button--primary').nth(0)
            add_button.click()
            
            # Wait for dialog to appear
            print("Waiting for add user dialog...")
            dialog = page.get_by_role('dialog')
            expect(dialog).to_be_visible(timeout=5000)
            page.wait_for_timeout(1000)
            
            print("Starting to detect form elements...")
            
            # Detect dialog title
            try:
                dialog_title = dialog.locator('.el-dialog__title')
                if dialog_title.count() > 0:
                    title_text = dialog_title.text_content()
                    result['form_elements'].append({
                        'element_type': 'dialog_title',
                        'label': title_text,
                        'selector': '.el-dialog__title'
                    })
                    print(f"Detected dialog title: {title_text}")
            except Exception as e:
                print(f"Failed to detect dialog title: {e}")
            
            # Detect all form items with labels
            labels = dialog.locator('.el-form-item__label')
            label_count = labels.count()
            print(f"Detected {label_count} form item labels")
            
            for i in range(label_count):
                try:
                    label_element = labels.nth(i)
                    label_text = label_element.text_content().strip().rstrip('：')
                    
                    # 获取对应的输入框或下拉框
                    parent = label_element.locator('..').locator('..')
                    
                    element_info = {
                        'label': label_text,
                        'index': i,
                        'selector': f'.el-form-item:nth-child({i+1}) .el-form-item__label'
                    }
                    
                    # 检测输入框
                    input_elem = parent.locator('input[type="text"]')
                    if input_elem.count() > 0:
                        placeholder = input_elem.get_attribute('placeholder')
                        element_info.update({
                            'type': 'input_text',
                            'placeholder': placeholder,
                            'selector': '.el-form-item:nth-child({i+1}) input[type="text"]'.format(i=i)
                        })
                    
                    # 检测密码框
                    pwd_elem = parent.locator('input[type="password"]')
                    if pwd_elem.count() > 0:
                        element_info.update({
                            'type': 'input_password',
                            'selector': '.el-form-item:nth-child({i+1}) input[type="password"]'.format(i=i)
                        })
                    
                    # 检测下拉框
                    select_elem = parent.locator('.el-select')
                    if select_elem.count() > 0:
                        element_info.update({
                            'type': 'select',
                            'selector': '.el-form-item:nth-child({i+1}) .el-select'.format(i=i)
                        })
                        
                        # 尝试获取选项
                        try:
                            placeholder = input_elem.get_attribute('placeholder')
                            if placeholder:
                                element_info['placeholder'] = placeholder
                        except:
                            pass
                    
                    # 检测树选择器
                    tree_elem = parent.locator('.vue-treeselect')
                    if tree_elem.count() > 0:
                        element_info.update({
                            'type': 'treeselect',
                            'selector': '.el-form-item:nth-child({i+1}) .vue-treeselect'.format(i=i)
                        })
                    
                    # 检测文本域
                    textarea_elem = parent.locator('textarea')
                    if textarea_elem.count() > 0:
                        element_info.update({
                            'type': 'textarea',
                            'selector': '.el-form-item:nth-child({i+1}) textarea'.format(i=i)
                        })
                    
                    # 检测单选框组
                    radio_elem = parent.locator('.el-radio-group')
                    if radio_elem.count() > 0:
                        element_info.update({
                            'type': 'radio_group',
                            'selector': '.el-form-item:nth-child({i+1}) .el-radio-group'.format(i=i)
                        })
                        # 获取单选选项
                        radios = radio_elem.locator('.el-radio')
                        radio_count = radios.count()
                        options = []
                        for j in range(radio_count):
                            radio_text = radios.nth(j).text_content().strip()
                            options.append(radio_text)
                        if options:
                            element_info['options'] = options
                    
                    result['form_elements'].append(element_info)
                    print(f"探测到元素 [{i+1}/{label_count}]: {label_text} - {element_info.get('type', 'unknown')}")
                    
                except Exception as e:
                    print(f"Failed to detect form item {i+1}: {e}")
                    continue
            
            # Detect buttons
            print("\nDetecting dialog buttons...")
            dialog_footer = dialog.locator('.el-dialog__footer')
            if dialog_footer.count() > 0:
                buttons = dialog_footer.locator('button')
                button_count = buttons.count()
                for i in range(button_count):
                    try:
                        button_text = buttons.nth(i).text_content().strip()
                        element_info = {
                            'element_type': 'button',
                            'label': button_text,
                            'index': i,
                            'selector': f'.el-dialog__footer button:nth-child({i+1})'
                        }
                        result['form_elements'].append(element_info)
                        print(f"探测到按钮: {button_text}")
                    except Exception as e:
                        print(f"Failed to detect button {i+1}: {e}")
            
            # Save screenshot
            screenshot_path = '工作区\\20260104_用户新增功能测试\\dialog_screenshot.png'
            dialog.screenshot(path=screenshot_path)
            print(f"Dialog screenshot saved: {screenshot_path}")
            
            # Close dialog
            cancel_button = page.locator('button').filter(has_text='Cancel')
            if cancel_button.count() == 0:
                cancel_button = page.get_by_role('button', name='Cancel')
            if cancel_button.count() == 0:
                cancel_button = page.locator('button[type="button"]').nth(1)
            if cancel_button.count() > 0:
                cancel_button.click()
                print("Closed add user dialog")
            
            page.wait_for_timeout(1000)
            
            # Logout
            print("Logging out...")
            user_avatar = page.locator('.el-dropdown-link')
            user_avatar.click()
            page.wait_for_timeout(500)
            
            logout_button = page.locator('a').filter(has_text='Logout')
            if logout_button.count() == 0:
                logout_button = page.locator('a').filter(has_text='Log Out')
            if logout_button.count() == 0:
                logout_button = page.locator('.el-dropdown-menu__item').filter(has_text='Logout')
            logout_button.click()
            
            page.wait_for_load_state('networkidle')
            print("Logged out")
            
        except Exception as e:
            print(f"Error during detection: {e}")
            result['error'] = str(e)
        finally:
            browser.close()
    
    # 保存探测结果
    output_path = '工作区/20260104_用户新增功能测试/探测结果.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\nDetection completed! Results saved to: {output_path}")
    print(f"Total detected {len(result['form_elements'])} form elements")
    
    return result

if __name__ == '__main__':
    detect_form_elements()