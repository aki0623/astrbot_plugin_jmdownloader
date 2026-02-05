# astrbot_plugin_jmdownloader

基于 [JMComic-Crawler-Python](https://github.com/hect0x7/JMComic-Crawler-Python)（`jmcomic`）实现的 AstrBot JM 漫画下载与收藏插件，支持下载、查询、收藏、随机推荐等功能。

## 功能一览

- **下载漫画并合并为 PDF**
  - 指令：`/JMD <车号>`，例如：`/JMD 123456`
  - 行为：下载指定 JM 本子的全部章节，并自动使用 `img2pdf` 合并为单个 PDF 文件
  - 附加：下载成功后会同时发送一条**漫画简介聊天记录**（封面 + 文本信息）

- **查询漫画信息**
  - 指令：`/jmcx <车号>`
  - 行为：根据 JM 车号查询漫画信息，并以**聊天记录形式**发送：
    - 第一条消息：封面图片
    - 第二条消息：文本信息（标题、编号、标签列表）

- **收藏漫画**
  - 指令：`/jmsc <车号>`
  - 行为：将指定 JM 车号加入本地收藏列表，存储在 `favorites.json` 中

- **从收藏夹随机推荐一部漫画**
  - 指令：`/jmsj`
  - 行为：从收藏列表中随机选取一部漫画，发送其简介（同上：封面 + 文本信息）

- **从收藏夹删除漫画**
  - 指令：`/jmde <车号>`
  - 行为：从收藏列表中移除指定 JM 车号

> 注：收藏数据文件路径为 `data/plugin_data/astrbot_plugin_jmdownloader/favorites.json`。

## 安装依赖

在 AstrBot 运行环境中安装本插件所需依赖：

```bash
pip install -r requirements.txt
```

或手动安装：

```bash
pip install jmcomic img2pdf
```

## 使用说明

1. 确保已安装 AstrBot 并将本插件放入 AstrBot 插件目录，启用插件
2. 按需使用不同指令：
   - 下载并生成 PDF：`/JMD 车号`
   - 查询信息：`/jmcx 车号`
   - 收藏：`/jmsc 车号`
   - 随机推荐：`/jmsj`
   - 删除收藏：`/jmde 车号`
3. 机器人会根据指令回复对应的 PDF 文件、聊天记录形式简介或操作结果提示

下载的图片与 PDF 文件默认存放在 AstrBot 数据目录下的：  
`data/plugin_data/astrbot_plugin_jmdownloader/`

## 参考

- [AstrBot 插件开发文档](https://docs.astrbot.app/dev/star/plugin-new.html)
- [JMComic-Crawler-Python](https://github.com/hect0x7/JMComic-Crawler-Python)
