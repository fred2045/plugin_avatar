# encoding:utf-8

import plugins
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from channel.chat_message import ChatMessage
from common.log import logger
from plugins import *
from config import conf


@plugins.register(
    name="avatar",
    desire_priority=99,
    hidden=True,
    desc="A simple plugin that make new avatar",
    version="0.1",
    author="fred",
)


class Avatar(Plugin):
    def __init__(self):
        super().__init__()

        try:
            logger.info("[Avatar] inited")
            self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
        except Exception as e:
            logger.error(f"[Avatar]初始化异常：{e}")
            raise "[Avatar] init failed, ignore "
        
        self.channel = None
        self.channel_type = conf().get("channel_type", "wx")
        if self.channel_type == "wx":
            try:
                from lib import itchat
                self.channel = itchat
            except Exception as e:
                logger.error(f"未安装itchat: {e}")
        else:
            logger.error(f"不支持的channel_type: {self.channel_type}")

    def on_handle_context(self, e_context: EventContext):
        if e_context["context"].type not in [
            ContextType.TEXT,
        ]:
            return
        msg: ChatMessage = e_context["context"]["msg"]
        content = e_context["context"].content
        if content.lower() == "avatar":
            import io
            from PIL import Image, ImageFilter
        
            reply = Reply()
            if e_context["context"]["isgroup"]:
                head_img = self.channel.get_head_img(msg.actual_user_id, msg.from_user_id)
            else:
                head_img = self.channel.get_head_img(msg.from_user_id)
            if isinstance(head_img, bytes):
                head_img = Image.open(io.BytesIO(head_img))

                avatar_contour = head_img.filter(ImageFilter.CONTOUR)

                buf = io.BytesIO()
                avatar_contour.save(buf, format='PNG')
                buf.seek(0)

                reply.type = ReplyType.IMAGE
                reply.content = buf
            else:
                reply.type = ReplyType.TEXT
                reply.content = "get head image failed!"

            e_context["reply"] = reply
            e_context.action = EventAction.BREAK_PASS


    def get_help_text(self, **kwargs):
        help_text = "输入avatar，我会回复你一个新头像\n"
        return help_text