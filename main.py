# -*- coding: utf-8 -*-
"""
AstrBot JM漫画下载插件：根据 JM 车号下载漫画并合并为 PDF。
"""
import asyncio
import os
from pathlib import Path

from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger

# 插件数据目录名（用于存储下载文件）
PLUGIN_DATA_DIR_NAME = "astrbot_plugin_jmdownloader"


def _get_plugin_data_path() -> Path:
    """获取插件数据目录（大文件存储规范：data/plugin_data/{plugin_name}/）"""
    try:
        from astrbot.core.utils.astrbot_path import get_astrbot_data_path
        return get_astrbot_data_path() / "plugin_data" / PLUGIN_DATA_DIR_NAME
    except Exception:
        # 兼容：若无法获取则使用当前工作目录下的 plugin_data
        return Path.cwd() / "data" / "plugin_data" / PLUGIN_DATA_DIR_NAME


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

    async def terminate(self):
        pass
