## Python API for JMComic

[](https://github.com/hect0x7/JMComic-Crawler-Python#python-api-for-jmcomic)

**提供 Python API 访问禁漫天堂（网页端 & 移动端），集成 GitHub Actions 下载器🚀**

[![GitHub](hect0x7jmcomic-crawl/1ec602d5-d171-4240-a5ea-0c883ac7ba77.idunno)](https://github.com/hect0x7) [![Stars](hect0x7jmcomic-crawl/b8f015db-33e3-4ccd-9f75-560904aaa479.idunno)](https://github.com/hect0x7/JMComic-Crawler-Python/stargazers) [![Forks](hect0x7jmcomic-crawl/e6ee2b07-562b-4a6d-ac33-a29ebf19f3be.idunno)](https://github.com/hect0x7/JMComic-Crawler-Python/forks) [![GitHub latest releases](hect0x7jmcomic-crawl/2822ed62-500e-4dd2-9576-eec25a4911e1.idunno)](https://github.com/hect0x7/JMComic-Crawler-Python/releases/latest) [![PyPI - Downloads](hect0x7jmcomic-crawl/cb70008c-fb47-4396-afbd-0d84c863cfd4.idunno)](https://pepy.tech/projects/jmcomic) [![Licence](hect0x7jmcomic-crawl/1bcdfc76-7150-4149-b3b0-6b2e19db4cf8.idunno)](https://github.com/hect0x7/JMComic-Crawler-Python)

> 本项目封装了一套可用于爬取JM的Python API.
> 
> 你可以通过简单的几行Python代码，实现下载JM上的本子到本地，并且是处理好的图片。
> 
> **友情提示：珍爱JM，为了减轻JM的服务器压力，请不要一次性爬取太多本子，西门🙏🙏🙏**.

[【指路】教程：使用GitHub Actions下载禁漫本子](https://github.com/hect0x7/JMComic-Crawler-Python/blob/master/assets/docs/sources/tutorial/1_github_actions.md)

[【指路】教程：导出并下载你的禁漫收藏夹数据](https://github.com/hect0x7/JMComic-Crawler-Python/blob/master/assets/docs/sources/tutorial/10_export_favorites.md)

[![introduction.jpg](hect0x7jmcomic-crawl/introduction.jpg)](https://github.com/hect0x7/JMComic-Crawler-Python/blob/master/assets/docs/sources/images/introduction.jpg)

## 项目介绍

[](https://github.com/hect0x7/JMComic-Crawler-Python#%E9%A1%B9%E7%9B%AE%E4%BB%8B%E7%BB%8D)

本项目的核心功能是下载本子。

基于此，设计了一套方便使用、便于扩展，能满足一些特殊下载需求的框架。

目前核心功能实现较为稳定，项目也处于维护阶段。

除了下载功能以外，也实现了其他的一些禁漫接口，按需实现。目前已有功能：

-   登录
-   搜索本子（支持所有搜索项）
-   图片下载解码
-   分类/排行榜
-   本子/章节详情
-   个人收藏夹
-   接口加解密（APP的接口）

## 安装教程

[](https://github.com/hect0x7/JMComic-Crawler-Python#%E5%AE%89%E8%A3%85%E6%95%99%E7%A8%8B)

> ⚠如果你没有安装过Python，需要先安装Python再执行下面的步骤，且版本需要>=3.7（[点我去python官网下载](https://www.python.org/downloads/)）

-   通过pip官方源安装（推荐，并且更新也是这个命令）
    
    ```shell
    pip install jmcomic -i https://pypi.org/project -U
    ```
    
-   通过源代码安装
    
    ```shell
    pip install git+https://github.com/hect0x7/JMComic-Crawler-Python
    ```
    

## 快速上手

[](https://github.com/hect0x7/JMComic-Crawler-Python#%E5%BF%AB%E9%80%9F%E4%B8%8A%E6%89%8B)

### 1\. 下载本子方法

[](https://github.com/hect0x7/JMComic-Crawler-Python#1-%E4%B8%8B%E8%BD%BD%E6%9C%AC%E5%AD%90%E6%96%B9%E6%B3%95)

只需要使用如下代码，就可以下载本子`JM123`的所有章节的图片：

```python
import jmcomic  # 导入此模块，需要先安装.
jmcomic.download_album('123')  # 传入要下载的album的id，即可下载整个album到本地.
```

上面的 `download_album`方法还有一个参数`option`，可用于控制下载配置，配置包括禁漫域名、网络代理、图片格式转换、插件等等。

你可能需要这些配置项。推荐使用配置文件创建option，用option下载本子，见下章：

### 2\. 使用option配置来下载本子

[](https://github.com/hect0x7/JMComic-Crawler-Python#2-%E4%BD%BF%E7%94%A8option%E9%85%8D%E7%BD%AE%E6%9D%A5%E4%B8%8B%E8%BD%BD%E6%9C%AC%E5%AD%90)

1.  首先，创建一个配置文件，假设文件名为 `option.yml`
    
    该文件有特定的写法，你需要参考这个文档 → [配置文件指南](https://github.com/hect0x7/JMComic-Crawler-Python/blob/master/assets/docs/sources/option_file_syntax.md)
    
    下面做一个演示，假设你需要把下载的图片转为png格式，你应该把以下内容写进`option.yml`
    

```yaml
download:
  image:
    suffix: .png # 该配置用于把下载的图片转为png格式
```

2.  第二步，运行下面的python代码

```python
import jmcomic

# 创建配置对象
option = jmcomic.create_option_by_file('你的配置文件路径，例如 D:/option.yml')
# 使用option对象来下载本子
jmcomic.download_album(123, option)
# 等价写法: option.download_album(123)
```

### 3\. 使用命令行

[](https://github.com/hect0x7/JMComic-Crawler-Python#3-%E4%BD%BF%E7%94%A8%E5%91%BD%E4%BB%A4%E8%A1%8C)

> 如果只想下载本子，使用命令行会比上述方式更加简单直接
> 
> 例如，在windows上，直接按下win+r键，输入jmcomic xxx就可以下载本子。

示例：

下载本子123的命令

```shell
jmcomic 123
```

同时下载本子123, 章节456的命令

```shell
jmcomic 123 p456
```

命令行模式也支持自定义option，你可以使用环境变量或者命令行参数：

a. 通过命令行--option参数指定option文件路径

```shell
jmcomic 123 --option="D:/a.yml"
```

b. 配置环境变量 `JM_OPTION_PATH` 为option文件路径（推荐）

> 请自行google配置环境变量的方式，或使用powershell命令: `setx JM_OPTION_PATH "D:/a.yml"` 重启后生效

```shell
jmcomic 123
```

## 进阶使用

[](https://github.com/hect0x7/JMComic-Crawler-Python#%E8%BF%9B%E9%98%B6%E4%BD%BF%E7%94%A8)

请查阅文档首页→[jmcomic.readthedocs.io](https://jmcomic.readthedocs.io/zh-cn/latest)

（提示：jmcomic提供了很多下载配置项，大部分的下载需求你都可以尝试寻找相关配置项或插件来实现。）

## 项目特点

[](https://github.com/hect0x7/JMComic-Crawler-Python#%E9%A1%B9%E7%9B%AE%E7%89%B9%E7%82%B9)

-   **绕过Cloudflare的反爬虫**
    
-   **实现禁漫APP接口最新的加解密算法 (1.6.3)**
    
-   用法多样：
    
    -   GitHub Actions：网页上直接输入本子id就能下载（[教程：使用GitHub Actions下载禁漫本子](https://github.com/hect0x7/JMComic-Crawler-Python/blob/master/assets/docs/sources/tutorial/1_github_actions.md)）
    -   命令行：无需写Python代码，简单易用（[教程：使用命令行下载禁漫本子](https://github.com/hect0x7/JMComic-Crawler-Python/blob/master/assets/docs/sources/tutorial/2_command_line.md)）
    -   Python代码：最本质、最强大的使用方式，需要你有一定的python编程基础
-   支持**网页端**和**移动端**两种客户端实现，可通过配置切换（**移动端不限ip兼容性好，网页端限制ip地区但效率高**）
    
-   支持**自动重试和域名切换**机制
    
-   **多线程下载**（可细化到一图一线程，效率极高）
    
-   **可配置性强**
    
    -   不配置也能使用，十分方便
    -   配置可以从配置文件生成，支持多种文件格式
    -   配置点有：`请求域名` `客户端实现` `是否使用磁盘缓存` `同时下载的章节/图片数量` `图片格式转换` `下载路径规则` `请求元信息（headers,cookies,proxies)` `中文繁/简转换` 等
-   **可扩展性强**
    
    -   支持自定义本子/章节/图片下载前后的回调函数
    -   支持自定义类：`Downloader（负责调度）` `Option（负责配置）` `Client（负责请求）` `实体类`等
    -   支持自定义日志、异常监听器
    -   **支持Plugin插件，可以方便地扩展功能，以及使用别人的插件，目前内置插件有**：
        -   `登录插件`
        -   `硬件占用监控插件`
        -   `只下载新章插件`
        -   `压缩文件插件`
        -   `下载特定后缀图片插件`
        -   `发送QQ邮件插件`
        -   `自动使用浏览器cookies插件`
        -   `导出收藏夹为csv文件插件`
        -   `合并所有图片为pdf文件插件`
        -   `合并所有图片为长图png插件`
        -   `重复文件检测删除插件`
        -   `网页观看本地章节插件`

## 使用小说明

[](https://github.com/hect0x7/JMComic-Crawler-Python#%E4%BD%BF%E7%94%A8%E5%B0%8F%E8%AF%B4%E6%98%8E)

-   Python >= 3.7，建议3.9以上，因为jmcomic的依赖库可能会不支持3.9以下的版本。
-   个人项目，文档和示例会有不及时之处，可以Issue提问

## 项目文件夹介绍

[](https://github.com/hect0x7/JMComic-Crawler-Python#%E9%A1%B9%E7%9B%AE%E6%96%87%E4%BB%B6%E5%A4%B9%E4%BB%8B%E7%BB%8D)

-   .github：GitHub Actions配置文件
    
-   assets：存放一些非代码的资源文件
    
    -   docs：项目文档
    -   option：存放配置文件
-   src：存放源代码
    
    -   jmcomic：`jmcomic`模块
-   tests：测试目录，存放测试代码，使用unittest
    
-   usage：用法目录，存放示例/使用代码
    

## 感谢以下项目

[](https://github.com/hect0x7/JMComic-Crawler-Python#%E6%84%9F%E8%B0%A2%E4%BB%A5%E4%B8%8B%E9%A1%B9%E7%9B%AE)

### 图片分割算法代码+禁漫移动端API

[](https://github.com/hect0x7/JMComic-Crawler-Python#%E5%9B%BE%E7%89%87%E5%88%86%E5%89%B2%E7%AE%97%E6%B3%95%E4%BB%A3%E7%A0%81%E7%A6%81%E6%BC%AB%E7%A7%BB%E5%8A%A8%E7%AB%AFapi)

  [![Repo Card](hect0x7jmcomic-crawl/b17d0d42-5fc9-4512-9c35-51249e55b86d.idunno)](https://github.com/tonquer/JMComic-qt)