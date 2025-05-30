# LLM Tree

**文档:** [🇺🇸 English](../README.md) | [🇷🇺 Русский](RU.md) | [🇩🇪 Deutsch](DE.md) | [🇯🇵 日本語](JA.md) | [🇨🇳 中文](CH.md)

一个用于为大语言模型（LLM）准备项目数据的命令行工具。它会生成一个包含项目结构和源代码内容的 Markdown 文件。

## 安装

```bash
pip install -e .
```

或全局安装：

```bash
pip install llmtree
```

## 快速开始

```bash
# 处理当前目录
llmtree .

# 处理指定目录
llmtree /path/to/project

# 使用指定配置文件
llmtree . -p python

# 配置管理
llmtree --config
```

## 主要功能

### 配置文件（Profiles）

* **default**：适用于大多数项目的通用配置
* **python**：针对 Python 项目优化
* 可通过交互式菜单创建自定义配置文件

### 交互式使用

运行 `llmtree .` 时：

* **Enter** 键生成 `4llm.md` 文件
* **空格键** 打开设置菜单

### 配置选项

* 包含文件的模式
* 排除文件的模式
* 是否包含目录树结构
* 文件大小限制
* 是否添加行号
* 自定义标题与页脚

## 配置文件结构

配置文件保存在 `~/.llmtree/config.json` 中：

```json
{
  "default": {
    "name": "default",
    "include_patterns": ["*.py", "*.js", "*.md"],
    "exclude_patterns": ["node_modules/*", ".git/*"],
    "include_tree": true,
    "max_file_size": 100000,
    "encoding": "utf-8",
    "add_line_numbers": false,
    "include_hidden": false,
    "tree_depth": 3,
    "custom_header": "",
    "custom_footer": ""
  }
}
```

## 使用示例

### 创建前端项目配置

```bash
llmtree --config
# 选择 "Create new profile"
# 名称：frontend
# 包含模式：*.js,*.jsx,*.ts,*.tsx,*.vue,*.css,*.scss,package.json
# 排除模式：node_modules/*,dist/*,build/*
```

### 创建文档配置

```bash
llmtree --config
# 创建名为 "docs" 的配置
# 包含模式：*.md,*.rst,*.txt
# 启用目录树结构
# 不添加行号
```

## 命令行用法

```
usage: llmtree [-h] [-p PROFILE] [-o OUTPUT] [--config] [path]

位置参数:
  path                  目标目录路径（默认：当前目录）

可选参数:
  -h, --help            显示帮助信息并退出
  -p, --profile PROFILE 使用的配置文件（默认：default）
  -o, --output OUTPUT   输出文件名（默认：4llm.md）
  --config              启动交互式配置
```

## 输出格式

生成的 `4llm.md` 文件包括：

1. 自定义标题（如果有设置）
2. 项目目录结构（tree）
3. 源文件内容（带语法高亮）
4. 自定义页脚（如果有设置）

输出示例：

```markdown
## 项目结构

```

.
├── src/
│   ├── main.py
│   └── utils.py
├── tests/
│   └── test\_main.py
└── README.md

````

## 源代码文件

### src/main.py
```python
def main():
    print("Hello, World!")
````

### README.md

```markdown
# 我的项目
```

## 许可证

MIT 许可证
