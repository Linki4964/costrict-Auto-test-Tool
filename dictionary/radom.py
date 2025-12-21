import random
import string

def random_phone():
    """
    随机生成一个中国大陆手机号（测试用）
    """
    prefixes = [
        "130", "131", "132", "133", "134", "135", "136", "137", "138", "139",
        "150", "151", "152", "153", "155", "156", "157", "158", "159",
        "170", "171", "172", "173", "175", "176", "177", "178",
        "180", "181", "182", "183", "185", "186", "187", "188", "189"
    ]

    prefix = random.choice(prefixes)
    suffix = ''.join(str(random.randint(0, 9)) for _ in range(8))
    phone_num = prefix + suffix
    print(phone_num)
    return  prefix + suffix

#随机用户名生成器
def random_username(
    prefix="user",
    length=6,
    allow_digits=True
):
    """
    随机生成用户名
    user_ab3f9c
    """
    chars = string.ascii_lowercase
    if allow_digits:
        chars += string.digits

    rand_part = ''.join(random.choice(chars) for _ in range(length))
    return f"{prefix}_{rand_part}"

#随机邮件生成器
def random_email(
    username=None,
    domains=None
):
    """
    随机生成邮箱
    """
    if domains is None:
        domains = ["example.com", "test.com", "mail.test"]

    if username is None:
        username = random_username()

    return f"{username}@{random.choice(domains)}"