# -*- coding: utf-8 -*-
"""
===== LFI 解码脚本（CTF 用，可在 VS Code 里直接运行）=====

这个脚本帮你把 CTF 题目回显的那串 base64，还原成 PHP 源码、并找出 flag。
原理分两步：
    第①步：base64 解码  → 得到「压缩过的二进制数据」（不是文字，直接看是乱码）
    第②步：zlib 解压    → 把压缩数据还原成「UTF-8 明文源码」（这里才有 flag）

注意：本脚本只用 Python 自带的功能，不用 pip 安装任何东西。
"""

import base64
import zlib
import re

# ============================================================
# 把你的 base64 整段粘到下面这一行引号里（替换掉示例内容）
# 示例：B64 = "s7EvyCjgUknLSUy3VcrNT00uSat2cfX1j4+IjIo3NDKuVbLmsrcDAA=="
# ============================================================
B64 = "lZDRToJgHMXveYpvrlumgwm1CO96DyHINpsuu6q1RWRGplRzRQ5XuhK1JdbWcgj1Mt//4+vKVwjeoC7O1fmf8//tSIVqqcqs6OXiNtpAmd2Kpu7rhyKvaHmB01lOVFfZnJDj2OIaJ7I8r+T5LT0nqJp4lFlnNLVUQZnNNAyzN3BHeH7x0xssw0uwJ8S1qDEhTjvunuIgIFaLmlHsNqlnSMqeDNYYz5uJB5ZHzPoyfIAnjwxPiONLNZkOXmBmw/kCrkzStnBwJmVrMo5celwH45M0bsh7n3S+EohsFtHvezL9ILcNeL1Lv0Vu3BmlCI5PvSHY1+igvKMgaDfjcJzQ4egRbB8vnvG8FU/7MDWXYTctSsb4i/5zWpCZXw=="
# ============================================================


def main():
    # 去掉可能混进来的换行、空格，只保留纯 base64 字符
    b64 = "".join(B64.split())

    # 第①步：base64 解码
    data = base64.b64decode(b64)
    print("① base64 解码成功，得到 %d 字节（这是压缩数据，直接看是乱码，正常）" % len(data))

    # 第②步：zlib 解压（参数 -15 表示「裸 deflate」，因为 PHP 的 zlib.deflate 不带 zlib 头）
    text = zlib.decompress(data, -15).decode("utf-8", "replace")
    print("② 解压成功，得到源码明文：\n")
    print(text)

    # 从源码里找出 flag
    m = re.search(r"moectf\{[^}]+\}", text)
    if m:
        print("\n🚩 找到 flag：" + m.group(0))
    else:
        print("\n（没找到 moectf{...}：可能这不是 flag.php 的源码，或你复制的 base64 不完整）")


if __name__ == "__main__":
    main()
