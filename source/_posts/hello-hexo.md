---
title: 用 Hexo 搭建我的第一个技术博客
date: 2026-11-02 11:30:00
tags: [Hexo, 教程]
categories: [技术]
---

这是一篇示例文章，展示技术博客常用的排版元素。你可以直接复制它、改掉内容，就变成你自己的文章。

## 一、怎么新建一篇文章

打开终端，进入博客目录，运行：

```bash
hexo new "文章标题"
```

它会在 `source/_posts/` 下生成一个 `.md` 文件，你用任意 Markdown 编辑器打开就能写。

## 二、代码高亮

技术博客最常用的就是贴代码，Hexo 自带高亮，写起来很简单：

```python
def fib(n):
    """返回前 n 个斐波那契数"""
    a, b = 0, 1
    result = []
    for _ in range(n):
        result.append(a)
        a, b = b, a + b
    return result

print(fib(10))
```

也可以贴 JavaScript：

```javascript
const sum = (...nums) => nums.reduce((a, b) => a + b, 0);
console.log(sum(1, 2, 3, 4)); // 10
```

## 三、列表与引用

支持无序列表：

- 写文章用 Markdown
- 本地预览用 `hexo server`
- 发布用 `hexo generate` + 部署

也支持引用块：

> 种一棵树最好的时间是十年前，其次是现在。搭建博客也是一样，开始写就成功了一半。

## 四、小结

| 命令 | 作用 |
| --- | --- |
| `hexo new "标题"` | 新建文章 |
| `hexo server` | 本地预览（默认 http://localhost:4000） |
| `hexo generate` | 生成静态文件到 public/ |
| `hexo clean` | 清理缓存和已生成文件 |

就这么简单，开始你的写作吧 🚀
