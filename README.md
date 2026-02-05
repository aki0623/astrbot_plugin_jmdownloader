# astrbot_plugin_jmdownloader

AstrBot 插件：根据 JM 车号下载漫画并合并为 PDF。基于 [JMComic-Crawler-Python](https://github.com/hect0x7/JMComic-Crawler-Python)（jmcomic）实现。

## 功能

- 下载指定 JM 车号的漫画，并自动合并为 PDF 文件
- 指令格式：`/JMD <车号>`（车号为数字），例如 `/JMD 123456`
- 支持指令别名：`jmd`、`jmdown`

## 安装依赖

在 AstrBot 环境中安装本插件所需依赖：

```bash
pip install -r requirements.txt
```

或手动安装：

```bash
pip install jmcomic img2pdf
```

## 使用说明

1. 确保已安装 AstrBot 并启用本插件
2. 在聊天中发送：`/JMD 车号`（将「车号」替换为实际 JM 本子数字 ID）
3. 机器人会先回复「开始下载…」，下载并合并完成后会发送生成的 PDF 文件

下载文件与 PDF 存放在 AstrBot 的 `data/plugin_data/astrbot_plugin_jmdownloader/` 目录下。

## 参考

- [AstrBot 插件开发文档](https://docs.astrbot.app/dev/star/plugin-new.html)
- [JMComic-Crawler-Python](https://github.com/hect0x7/JMComic-Crawler-Python)
