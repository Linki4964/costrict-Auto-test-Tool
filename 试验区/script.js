cript.js</path>
document.addEventListener('DOMContentLoaded', function() {
    // 获取DOM元素
    const loginForm = document.getElementById('loginForm');
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const errorMessage = document.getElementById('errorMessage');
    
    // 后端接口地址配置（可根据实际环境修改）
    const API_URL = 'https://api.example.com/login';
    
    // 表单提交事件处理
    loginForm.addEventListener('submit', function(event) {
        event.preventDefault();
        
        // 重置错误信息
        errorMessage.style.display = 'none';
        errorMessage.textContent = '';
        
        // 获取输入值
        const username = usernameInput.value.trim();
        const password = passwordInput.value.trim();
        
        // 前端验证
        if (!validateForm(username, password)) {
            return;
        }
        
        // 显示加载状态
        const loginButton = document.getElementById('loginButton');
        const originalButtonText = loginButton.textContent;
        loginButton.textContent = '登录中...';
        loginButton.disabled = true;
        
        // 调用登录函数
        login(username, password)
            .then(response => {
                // 登录成功处理
                console.log('登录成功:', response);
                alert('登录成功！');
                // 这里可以添加页面跳转逻辑
                // window.location.href = '/dashboard';
            })
            .catch(error => {
                // 登录失败处理
                showError(error.message || '登录失败，请稍后重试');
            })
            .finally(() => {
                // 恢复按钮状态
                loginButton.textContent = originalButtonText;
                loginButton.disabled = false;
            });
    });
    
    /**
     * 表单验证函数
     * @param {string} username - 用户名
     * @param {string} password - 密码
     * @returns {boolean} - 验证是否通过
     */
    function validateForm(username, password) {
        // 验证用户名不能为空
        if (!username) {
            showError('用户名不能为空');
            return false;
        }
        
        // 验证密码不能为空
        if (!password) {
            showError('密码不能为空');
            return false;
        }
        
        // 可选：验证密码长度（至少6位）
        if (password.length < 6) {
            showError('密码长度至少为6位');
            return false;
        }
        
        // 可选：验证用户名格式（例如邮箱格式）
        // const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        // if (!emailRegex.test(username)) {
        //     showError('请输入有效的邮箱地址');
        //     return false;
        // }
        
        return true;
    }
    
    /**
     * 显示错误信息
     * @param {string} message - 错误信息
     */
    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';
    }
    
    /**
     * 登录函数，用于向后端发送登录请求
     * @param {string} username - 用户名
     * @param {string} password - 密码
     * @returns {Promise} - 返回Promise对象
     */
    async function login(username, password) {
        // 构建请求体
        const loginData = {
            username: username,
            password: password
        };
        
        try {
            // 发送POST请求到后端
            // 注意：这里使用了fetch API，如果需要兼容旧浏览器，可能需要添加polyfill或使用其他方法
            const response = await fetch(API_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(loginData)
            });
            
            // 检查响应状态
            if (!response.ok) {
                // 如果HTTP状态码不是200-299，则抛出错误
                const errorData = await response.json();
                throw new Error(errorData.message || '登录失败');
            }
            
            // 解析响应数据
            return await response.json();
        } catch (error) {
            // 如果是网络错误或请求被阻止，则抛出错误
            if (error.name === 'TypeError' && error.message.includes('Failed to fetch')) {
                throw new Error('网络连接错误，请检查您的网络设置');
            }
            throw error;
        }
    }
    
    /**
     * 更新API端点URL的函数
     * @param {string} newUrl - 新的API端点URL
     */
    function setApiUrl(newUrl) {
        API_URL = newUrl;
        console.log('API URL已更新为:', API_URL);
    }
    
    // 将setApiUrl函数暴露到全局作用域，便于外部调用
    window.setApiUrl = setApiUrl;
});