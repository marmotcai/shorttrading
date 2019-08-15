
import os

def mkdir(path):
    # 去除首位空格
    path = path.strip()
    # 去除尾部 \ 符号
    path = path.rstrip("\\")
    # 判断结果
    if not os.path.exists(path):
        # 如果不存在则创建目录
        os.makedirs(path)
        return True
    else:
        return False