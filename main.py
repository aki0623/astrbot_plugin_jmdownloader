# -*- coding: utf-8 -*-
"""
AstrBot JM漫画下载插件：根据 JM 车号下载漫画并合并为 PDF，并提供收藏功能。
"""
import asyncio
import os
import json
from pathlib import Path

from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger

# 插件数据目录名（用于存储下载文件与收藏数据）
PLUGIN_DATA_DIR_NAME = "astrbot_plugin_jmdownloader"


def _get_plugin_data_path() -> Path:
    """获取插件数据目录（大文件存储规范：data/plugin_data/{plugin_name}/）"""
    try:
        from astrbot.core.utils.astrbot_path import get_astrbot_data_path
        return get_astrbot_data_path() / "plugin_data" / PLUGIN_DATA_DIR_NAME
    except Exception:
        # 兼容：若无法获取则使用当前工作目录下的 plugin_data
        return Path.cwd() / "data" / "plugin_data" / PLUGIN_DATA_DIR_NAME


def _get_fav_json_path() -> Path:
    """收藏 JSON 文件路径"""
    return _get_plugin_data_path() / "favorites.json"


def _get_album_info_sync(jm_id: str) -> dict:
    """
    同步获取漫画信息：标题、编号、封面、标签。
    返回字典：{id, title, tags, cover_url}
    """
    import jmcomic

    jm_id = (jm_id or "").strip()
    if not jm_id.isdigit():
        raise ValueError("JM 车号必须是数字")

    # 使用默认配置创建客户端，只请求元信息
    option = jmcomic.JmOption.default()
    client = option.new_jm_client()
    album = client.get_album_detail(jm_id)

    title = getattr(album, "title", None) or getattr(album, "name", f"JM{jm_id}")
    tags = getattr(album, "tags", [])

    cover_url = ""
    for attr in ("cover", "cover_url", "img", "logo"):
        value = getattr(album, attr, None)
        if isinstance(value, str) and value:
            cover_url = value
            break

    return {
        "id": str(getattr(album, "id", jm_id)),
        "title": str(title),
        "tags": tags,
        "cover_url": cover_url,
    }


def _build_album_message_chain(info: dict, event: AstrMessageEvent | None = None):
    """
    根据漫画信息构建 AstrBot 消息链（聊天记录形式）：
    - 第一条消息：封面
    - 第二条消息：文本信息（标题 / 编号 / 标签）
    """
    import astrbot.api.message_components as Comp

    # 文本信息
    lines = [
        f"标题：{info.get('title', '')}",
        f"编号：JM{info.get('id', '')}",
    ]

    tags = info.get("tags")
    if tags:
        if isinstance(tags, (list, tuple, set)):
            tag_str = "、".join(map(str, tags))
        else:
            tag_str = str(tags)
        lines.append(f"标签：{tag_str}")

    text_plain = Comp.Plain("\n".join(lines))

    # 作为聊天记录（合并转发）里的发送者信息
    uin = ""
    name = "JMComic"
    try:
        if event is not None:
            # 这里使用发送者信息，实际效果类似聊天记录
            uin = str(event.get_self_id())
            name = event.get_self_name() or name
    except Exception:
        pass

    nodes: list = []

    # 第一条：封面
    cover_url = info.get("cover_url") or ""
    if cover_url:
        try:
            cover_node = Comp.Node(
                uin=uin,
                name=name,
                content=[Comp.Image.fromURL(cover_url)],
            )
            nodes.append(cover_node)
        except Exception as e:
            logger.warning(f"封面图片发送失败：{e}")

    # 第二条：文字信息
    info_node = Comp.Node(
        uin=uin,
        name=name,
        content=[text_plain],
    )
    nodes.append(info_node)

    return nodes


def _build_jm_option(base_dir: str):
    """构建 jmcomic 下载选项：指定目录并启用 after_album 时合并为 PDF"""
    import jmcomic
    base_dir = base_dir.replace("\\", "/").rstrip("/")
    pdf_dir = f"{base_dir}/pdf/"
    # 使用 YAML 字符串创建 option，避免手写完整 default_dict
    yml = f"""
dir_rule:
  base_dir: "{base_dir}"
  rule: Bd_Pname
plugins:
  after_album:
    - plugin: img2pdf
      kwargs:
        pdf_dir: "{pdf_dir}"
        filename_rule: Aname
        delete_original_file: true
"""
    return jmcomic.create_option_by_str(yml.strip())


def _download_album_to_pdf(album_id: str, base_dir: str):
    """
    同步下载指定 JM 本子并合并为 PDF。
    返回 (success, result)：成功时 result 为 PDF 文件路径，失败时为错误信息字符串。
    """
    import jmcomic
    from jmcomic.jm_option import DirRule

    album_id = str(album_id).strip()
    if not album_id.isdigit():
        return False, "JM 车号必须是数字"

    try:
        option = _build_jm_option(base_dir)
        album, dler = jmcomic.download_album(album_id, option=option, check_exception=True)
        # 下载器已在下载完成后自动调用 after_album，img2pdf 已生成 PDF
        # PDF 路径：pdf_dir + Aname + .pdf
        pdf_dir = os.path.join(base_dir, "pdf")
        filename = DirRule.apply_rule_to_filename(album, None, "Aname") + ".pdf"
        pdf_path = os.path.join(pdf_dir, filename)
        if os.path.isfile(pdf_path):
            return True, pdf_path
        return False, "PDF 未生成，请检查是否已安装 img2pdf：pip install img2pdf"
    except Exception as e:
        logger.exception(f"JMD 下载失败 album_id={album_id}")
        return False, str(e)


@register(
    "jmdownloader",
    "AstrBot",
    "JM漫画下载：根据 JM 车号下载漫画并转为 PDF，指令 JMD <车号>",
    "1.0.0",
)
class JMDownloaderPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    async def initialize(self):
        """插件初始化时确保插件数据目录存在"""
        path = _get_plugin_data_path()
        path.mkdir(parents=True, exist_ok=True)
        (path / "pdf").mkdir(exist_ok=True)

    @filter.command("JMD", alias={"jmd", "jmdown"})
    async def cmd_jmd(self, event: AstrMessageEvent, jm_id: str):
        """下载指定 JM 车号的漫画并转为 PDF。用法：/JMD <车号>，例如 /JMD 123456"""
        jm_id = (jm_id or "").strip()
        if not jm_id:
            yield event.plain_result("请提供 JM 车号。用法：/JMD <车号>，例如 /JMD 123456")
            return

        base_dir = str(_get_plugin_data_path())
        yield event.plain_result(f"开始下载 JM{jm_id}，完成后将合并为 PDF，请稍候…")

        loop = asyncio.get_event_loop()
        success, result = await loop.run_in_executor(
            None, _download_album_to_pdf, jm_id, base_dir
        )

        if not success:
            yield event.plain_result(f"下载失败：{result}")
            return

        pdf_path = result
        if not os.path.isfile(pdf_path):
            yield event.plain_result(f"未找到生成的 PDF：{pdf_path}")
            return

        # 下载成功后，顺带查询并发送漫画信息（聊天记录形式：封面+信息）
        try:
            info = await loop.run_in_executor(None, _get_album_info_sync, jm_id)
            meta_chain = _build_album_message_chain(info, event)
            if meta_chain:
                yield event.chain_result(meta_chain)
        except Exception as e:
            logger.warning(f"查询漫画信息失败 JM{jm_id}：{e}")

        try:
            import astrbot.api.message_components as Comp
            name = os.path.basename(pdf_path)
            yield event.chain_result([
                Comp.Plain("下载完成，PDF 文件："),
                Comp.File(file=pdf_path, name=name),
            ])
        except Exception as e:
            logger.exception("发送 PDF 文件失败")
            yield event.plain_result(f"PDF 已生成：{pdf_path}，但发送文件失败：{e}")

    @filter.command("jmsc")
    async def cmd_jmsc(self, event: AstrMessageEvent, jm_id: str):
        """收藏指定 JM 车号到本地 JSON。用法：/jmsc <车号>，例如 /jmsc 123456"""
        jm_id = (jm_id or "").strip()
        if not jm_id:
            yield event.plain_result("请提供要收藏的 JM 车号。用法：/jmsc <车号>，例如 /jmsc 123456")
            return

        if not jm_id.isdigit():
            yield event.plain_result("JM 车号必须是数字，例如：/jmsc 123456")
            return

        fav_path = _get_fav_json_path()
        fav_path.parent.mkdir(parents=True, exist_ok=True)

        # 读取已有收藏
        favorites = []
        if fav_path.is_file():
            try:
                with fav_path.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        favorites = [str(x) for x in data]
            except Exception as e:
                logger.warning(f"读取收藏文件失败，将重新创建: {e}")

        if jm_id in favorites:
            yield event.plain_result(f"JM{jm_id} 已在收藏列表中。")
            return

        favorites.append(jm_id)
        try:
            with fav_path.open("w", encoding="utf-8") as f:
                json.dump(favorites, f, ensure_ascii=False, indent=2)
            yield event.plain_result(f"已收藏 JM{jm_id}。当前共收藏 {len(favorites)} 本漫画。")
        except Exception as e:
            logger.exception("写入收藏文件失败")
            yield event.plain_result(f"收藏 JM{jm_id} 失败：{e}")

    @filter.command("jmde")
    async def cmd_jmde(self, event: AstrMessageEvent, jm_id: str):
        """从收藏列表中删除指定 JM 车号。用法：/jmde <车号>，例如 /jmde 123456"""
        jm_id = (jm_id or "").strip()
        if not jm_id:
            yield event.plain_result("请提供要删除的 JM 车号。用法：/jmde <车号>，例如 /jmde 123456")
            return

        if not jm_id.isdigit():
            yield event.plain_result("JM 车号必须是数字，例如：/jmde 123456")
            return

        fav_path = _get_fav_json_path()
        if not fav_path.is_file():
            yield event.plain_result("当前没有收藏数据，无需删除。")
            return

        favorites: list[str] = []
        try:
            with fav_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    favorites = [str(x) for x in data]
        except Exception as e:
            logger.warning(f"读取收藏文件失败：{e}")
            yield event.plain_result("读取收藏数据失败，请稍后再试。")
            return

        if jm_id not in favorites:
            yield event.plain_result(f"收藏列表中不存在 JM{jm_id}，无需删除。")
            return

        favorites = [x for x in favorites if x != jm_id]

        try:
            with fav_path.open("w", encoding="utf-8") as f:
                json.dump(favorites, f, ensure_ascii=False, indent=2)
            yield event.plain_result(f"已从收藏列表中删除 JM{jm_id}。当前剩余 {len(favorites)} 本收藏。")
        except Exception as e:
            logger.exception("写入收藏文件失败")
            yield event.plain_result(f"删除 JM{jm_id} 失败：{e}")

    @filter.command("jmcx")
    async def cmd_jmcx(self, event: AstrMessageEvent, jm_id: str):
        """查询指定 JM 车号的漫画信息（标题 / 编号 / 封面 / 标签）。用法：/jmcx <车号>"""
        jm_id = (jm_id or "").strip()
        if not jm_id:
            yield event.plain_result("请提供要查询的 JM 车号。用法：/jmcx <车号>，例如 /jmcx 123456")
            return

        if not jm_id.isdigit():
            yield event.plain_result("JM 车号必须是数字，例如：/jmcx 123456")
            return

        loop = asyncio.get_event_loop()
        try:
            info = await loop.run_in_executor(None, _get_album_info_sync, jm_id)
        except Exception as e:
            logger.warning(f"查询漫画信息失败 JM{jm_id}：{e}")
            yield event.plain_result(f"查询 JM{jm_id} 失败：{e}")
            return

        chain = _build_album_message_chain(info, event)
        if not chain:
            yield event.plain_result(f"未获取到 JM{jm_id} 的详细信息。")
            return

        yield event.chain_result(chain)

    @filter.command("jmsj")
    async def cmd_jmsj(self, event: AstrMessageEvent):
        """从收藏列表中随机抽取一部漫画并发送简介。用法：/jmsj"""
        import random

        fav_path = _get_fav_json_path()
        if not fav_path.is_file():
            yield event.plain_result("当前还没有收藏任何漫画，请先使用 /jmsc <车号> 进行收藏。")
            return

        favorites: list[str] = []
        try:
            with fav_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    favorites = [str(x) for x in data if str(x).isdigit()]
        except Exception as e:
            logger.warning(f"读取收藏文件失败：{e}")
            yield event.plain_result("读取收藏数据失败，请稍后再试。")
            return

        if not favorites:
            yield event.plain_result("收藏列表为空，请先使用 /jmsc <车号> 添加一些收藏。")
            return

        jm_id = random.choice(favorites)

        loop = asyncio.get_event_loop()
        try:
            info = await loop.run_in_executor(None, _get_album_info_sync, jm_id)
        except Exception as e:
            logger.warning(f"随机漫画信息获取失败 JM{jm_id}：{e}")
            yield event.plain_result(f"随机到 JM{jm_id}，但查询失败：{e}")
            return

        chain = _build_album_message_chain(info, event)
        if not chain:
            yield event.plain_result(f"随机到 JM{jm_id}，但未获取到详细信息。")
            return

        yield event.chain_result(chain)

    async def terminate(self):
        pass
