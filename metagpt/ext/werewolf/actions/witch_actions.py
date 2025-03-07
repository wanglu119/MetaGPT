from metagpt.environment.werewolf.const import RoleActionRes
from metagpt.ext.werewolf.actions.common_actions import NighttimeWhispers


class Save(NighttimeWhispers):
    name: str = "Save"

    def _update_prompt_json(
        self, prompt_json: dict, role_profile: str, role_name: str, context: str, reflection: str, experiences: str
    ) -> dict:
        del prompt_json["ACTION"]
        del prompt_json["ATTENTION"]

        prompt_json["OUTPUT_FORMAT"][
            "THOUGHTS"
        ] = "It is night time. Return the thinking steps of your decision of whether to save the player JUST killed this night."

        prompt_json["OUTPUT_FORMAT"][
            "THOUGHTS"
        ] ="现在是晚上。请返回你决定是否拯救今晚刚被杀的玩家的思考步骤。"
        prompt_json["OUTPUT_FORMAT"][
            "RESPONSE"
        ] = "Follow the Moderator's instruction, decide whether you want to save that person or not. Return SAVE or PASS."

        prompt_json["OUTPUT_FORMAT"][
            "RESPONSE"
        ] = "根据主持人的指示，决定你是否想要拯救那个人。返回“Save”或“Pass”。"

        return prompt_json

    async def run(self, *args, **kwargs):
        rsp = await super().run(*args, **kwargs)
        action_name, rsp = rsp.split()
        return rsp  # 只需回复SAVE或PASS，不需要带上action名


class Poison(NighttimeWhispers):
    STRATEGY: str = """
    Only poison a player if you are confident he/she is a werewolf. Don't poison a player randomly or at first night.
    If someone claims to be the witch, poison him/her, because you are the only witch, he/she can only be a werewolf.
    """
    STRATEGY: str = """
    只有在你确信某人是狼人时才毒他/她。不要随意毒人，也不要在第一晚下毒。如果有人声称自己是女巫，就毒他/她，因为你是唯一的女巫，他/她只能是狼人。
    """

    name: str = "Poison"

    def _update_prompt_json(
        self, prompt_json: dict, role_profile: str, role_name: str, context: str, reflection: str, experiences: str
    ) -> dict:
        prompt_json["OUTPUT_FORMAT"]["RESPONSE"] += "Or if you want to PASS, return PASS."
        return prompt_json

    async def run(self, *args, **kwargs):
        rsp = await super().run(*args, **kwargs)
        if RoleActionRes.PASS.value in rsp.lower():
            action_name, rsp = rsp.split()  # 带PASS，只需回复PASS，不需要带上action名，否则是Poison PlayerX，无需改动
        return rsp
