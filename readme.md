# 项目简介

## 虚拟机镜像

账号:debian<br>
密码:debian

mysql:<br>
账号:root<br>
密码:root

使用步骤:
1. 用wmare打开虚拟机
2. 登录debian用户
3. ip ad查看一下ip地址，保证虚拟机可以联网（我没有装ipconfig）
4. 在~/RuoYi-Vue/ruoyi-admin下面运行 `mvn spring-boot:run`
![alt text](image/image.png)
看到这个就是成功了
5. 然后用物理机或者虚拟机可以连通该虚拟机的机器的浏览器访问 `http://ip/即可
![alt text](/image/image1.png)