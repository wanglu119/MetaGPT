#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Desc   :

import json

from tenacity import retry, stop_after_attempt, wait_fixed

from metagpt.actions import Action
from metagpt.logs import logger
from metagpt.utils.common import parse_json_code_block


def log_and_parse_json(name: str, rsp: str) -> dict:
    rsp = rsp.replace("\n", " ")
    logger.debug(f"{name} result: {rsp}")
    json_blocks = parse_json_code_block(rsp)
    rsp_json = json.loads(json_blocks[0])
    return rsp_json


class Speak(Action):
    """Action: Any speak action in a game"""

    PROMPT_TEMPLATE: str = """
    {
    "BACKGROUND": "It's a Werewolf game, in this game, we have 2 werewolves, 2 villagers, 1 guard, 1 witch, 1 seer. You are __profile__. Note that villager, seer, guard and witch are all in villager side, they have the same objective. Werewolves can collectively hunt ONE player at night."
    ,"HISTORY": "You have knowledge to the following conversation: __context__"
    ,"ATTENTION": "You can NOT VOTE a player who is NOT ALIVE now!"
    ,"REFLECTION": "__reflection__"
    ,"STRATEGY": __strategy__
    ,"PAST_EXPERIENCES": "__experiences__"
    ,"MODERATOR_INSTRUCTION": __latest_instruction__,
    ,"RULE": "Please follow the moderator's latest instruction, figure out if you need to speak your opinion or directly to vote:
              1. If the instruction is to SPEAK, speak in 200 words. Remember the goal of your role and try to achieve it using your speech;
              2. If the instruction is to VOTE, you MUST vote and ONLY say 'I vote to eliminate PlayerX', replace PlayerX with the actual player name, DO NOT include any other words."
    ,"OUTPUT_FORMAT":
        {
        "ROLE": "Your role, in this case, __profile__"
        ,"PLAYER_NAME": "Your name, in this case, __name__"
        ,"LIVING_PLAYERS": "List living players based on MODERATOR_INSTRUCTION. Return a json LIST datatype."
        ,"THOUGHTS": "Based on `MODERATOR_INSTRUCTION` and `RULE`, carefully think about what to say or vote so that your chance of win as __profile__ maximizes.
                      If you find similar situation in `PAST_EXPERIENCES`, you may draw lessons from them to refine your strategy, take better vote action, or improve your speech.
                      Give your step-by-step thought process, you should think no more than 3 steps. For example: My step-by-step thought process:..."
        ,"RESPONSE": "Based on `MODERATOR_INSTRUCTION`, `RULE`, and the 'THOUGHTS' you had, express your opinion or cast a vote."
        }
    }
    """


    PROMPT_TEMPLATE: str ="""
    {
    "BACKGROUND": "这是一个狼人游戏，在这个游戏中，我们有2个狼人，2个村民，1个守卫，1个女巫，1个预言家。你是 __profile__ 。注意，村民、预言家、守卫和女巫都属于村民阵营，他们有相同的目标。狼人可以在晚上集体猎杀一名玩家。",
    "HISTORY": "你了解以下对话：__context__",
    "ATTENTION": "你不能投票给现在不活着的玩家！",
    "REFLECTION": "__reflection__",
    "STRATEGY": "__strategy__",
    "PAST_EXPERIENCES": "__experiences__",
    "MODERATOR_INSTRUCTION": "__latest_instruction__",
    "RULE": '''请遵循主持人的最新指示，确定你需要发表意见还是直接投票： 
        1. 如果指示是发言，请用200字发言。记住你角色的目标，并通过发言实现它； 
        2. 如果指示是投票，你必须投票，并且只能说‘我投票淘汰PlayerX’，将PlayerX替换为实际玩家姓名，不要包含其他词。''',
    "OUTPUT_FORMAT": {
        "ROLE": "你的角色，在这种情况下是__profile__",
        "PLAYER_NAME": "你的名字，在这种情况下是__name__",
        "LIVING_PLAYERS": "根据 MODERATOR_INSTRUCTION 列出活着的玩家。返回一个JSON列表数据类型。",
        "THOUGHTS": "根据`MODERATOR_INSTRUCTION`和`RULE`，仔细考虑要说什么或投票，以最大化你作为__profile__获胜的机会。如果在`PAST_EXPERIENCES`中发现类似情况，可以从中汲取教训以优化策略，采取更好的投票行动或改善发言。给出你的逐步思考过程，不超过3步。例如：我的逐步思考过程：...",
        "RESPONSE": "根据`MODERATOR_INSTRUCTION`、`RULE`和你的‘THOUGHTS’，表达你的意见或投票。"
    }
    }

    """
    STRATEGY: str = """
    Decide whether to reveal your identity based on benefits vs. risks, provide useful information, and vote to eliminate the most suspicious.
    If you have special abilities, pay attention to those who falsely claims your role, for they are probably werewolves.
    """
    STRATEGY: str = """
    根据利弊决定是否揭示你的身份，提供有用的信息，并投票淘汰最可疑的人。
    如果你有特殊能力，要注意那些虚假声称是你角色的人，因为他们可能是狼人。
    """

    name: str = "Speak"

    @retry(stop=stop_after_attempt(2), wait=wait_fixed(1))
    async def run(
        self,
        profile: str,
        name: str,
        context: str,
        latest_instruction: str,
        reflection: str = "",
        experiences: str = "",
    ):
        prompt = (
            self.PROMPT_TEMPLATE.replace("__context__", context)
            .replace("__profile__", profile)
            .replace("__name__", name)
            .replace("__latest_instruction__", latest_instruction)
            .replace("__strategy__", self.STRATEGY)
            .replace("__reflection__", reflection)
            .replace("__experiences__", experiences)
        )

        rsp = await self._aask(prompt)
        rsp_json = log_and_parse_json(self.name, rsp)

        return rsp_json["RESPONSE"]


class NighttimeWhispers(Action):
    """

    Action: nighttime whispers with thinking processes

    Usage Example:

        class Hunt(NighttimeWhispers):
            def __init__(self, name="Hunt", context=None, llm=None):
                super().__init__(name, context, llm)

        class Protect(NighttimeWhispers):
            def __init__(self, name="Protect", context=None, llm=None):
                super().__init__(name, context, llm)

        class Verify(NighttimeWhispers):
            def __init__(self, name="Verify", context=None, llm=None):
                super().__init__(name, context, llm)

        class Save(NighttimeWhispers):
            def __init__(self, name="Save", context=None, llm=None):
                super().__init__(name, context, llm)

            def _update_prompt_json(self, prompt_json: dict, profile: str, name: str, context: str, **kwargs):
                del prompt_json['ACTION']
                del prompt_json['ATTENTION']
                prompt_json["OUTPUT_FORMAT"]["THOUGHTS"] = "It is night time. Return the thinking steps of your decision of whether to save the player JUST be killed at this night."
                prompt_json["OUTPUT_FORMAT"]["RESPONSE"] = "Follow the Moderator's instruction, decide whether you want to save that person or not. Return SAVE or PASS."
                return prompt_json

        class Poison(NighttimeWhispers):
            def __init__(self, name="Poison", context=None, llm=None):
                super().__init__(name, context, llm)

            def _update_prompt_json(self, prompt_json: dict, profile: str, name: str, context: str, **kwargs):
                prompt_json["OUTPUT_FORMAT"]["RESPONSE"] += "Or if you want to PASS, return PASS."
                return prompt_json
    """

    PROMPT_TEMPLATE: str = """
    {
    "BACKGROUND": "It's a Werewolf game, in this game, we have 2 werewolves, 2 villagers, 1 guard, 1 witch, 1 seer. You are __profile__. Note that villager, seer, guard and witch are all in villager side, they have the same objective. Werewolves can collectively hunt ONE player at night."
    ,"HISTORY": "You have knowledge to the following conversation: __context__"
    ,"ACTION": "Choose one living player to __action__."
    ,"ATTENTION": "1. You can only __action__ a player who is alive this night! And you can not __action__ a player who is dead this night!  2. `HISTORY` is all the information you observed, DONT hallucinate other player actions!"
    ,"REFLECTION": "__reflection__"
    ,"STRATEGY": "__strategy__"
    ,"PAST_EXPERIENCES": "__experiences__"
    ,"OUTPUT_FORMAT":
        {
        "ROLE": "Your role, in this case, __profile__"
        ,"PLAYER_NAME": "Your name, in this case, __name__"
        ,"LIVING_PLAYERS": "List the players who is alive based on moderator's latest instruction. Return a json LIST datatype."
        ,"THOUGHTS": "Choose one living player from `LIVING_PLAYERS` to __action__ this night. Return the reason why you choose to __action__ this player. If you observe nothing at first night, DONT imagine unexisting player actions! If you find similar situation in `PAST_EXPERIENCES`, you may draw lessons from them to refine your strategy and take better actions. Give your step-by-step thought process, you should think no more than 3 steps. For example: My step-by-step thought process:..."
        ,"RESPONSE": "As a __profile__, you should choose one living player from `LIVING_PLAYERS` to __action__ this night according to the THOUGHTS you have just now. Return the player name ONLY."
        }
    }
    """
    PROMPT_TEMPLATE: str = """
    {
        "BACKGROUND": "这是一个狼人游戏。在这个游戏中，我们有2个狼人，2个村民，1个守卫，1个女巫，1个预言家。你是__profile__。注意，村民、预言家、守卫和女巫都属于村民阵营，他们有相同的目标。狼人可以在晚上集体猎杀一名玩家。",
        "HISTORY": "你知道以下对话内容：__context__",
        "ACTION": "选择一名活着的玩家进行__action__。",
        "ATTENTION": "1. 你只能对今晚活着的玩家进行__action__！你不能对今晚死去的玩家进行__action__！ 2. `HISTORY` 是你观察到的所有信息，不要幻想其他玩家的动作！",
        "REFLECTION": "__reflection__",
        "STRATEGY": "__strategy__",
        "PAST_EXPERIENCES": "__experiences__",
        "OUTPUT_FORMAT": {
            "ROLE": "你的角色，在这种情况下，__profile__",
            "PLAYER_NAME": "你的名字，在这种情况下，__name__",
            "LIVING_PLAYERS": "根据主持人的最新指示列出存活的玩家。返回一个 JSON 列表数据类型。",
            "THOUGHTS": "从 `LIVING_PLAYERS` 中选择一名玩家在今晚进行__action__。返回你选择对该玩家进行__action__的原因。如果你在第一晚没有观察到任何情况，不要想象不存在的玩家动作！如果你在 `PAST_EXPERIENCES` 中发现类似情况，可以从中汲取教训以完善你的策略并采取更好的行动。给出你的逐步思考过程，不超过3步。例如：我的逐步思考过程：...",
            "RESPONSE": "作为__profile__，你应该根据刚才的THOUGHTS从 `LIVING_PLAYERS` 中选择一名玩家在今晚进行__action__。仅返回玩家姓名。"
        }
    }
    """
    STRATEGY: str = """
    Decide which player is most threatening to you or most needs your support, take your action correspondingly.
    """
    STRATEGY: str =  """
    决定哪个玩家对你威胁最大或最需要你的支持，然后相应地采取行动。
    """

    name: str = "NightTimeWhispers"

    def _construct_prompt_json(
        self, role_profile: str, role_name: str, context: str, reflection: str, experiences: str, **kwargs
    ):
        prompt_template = self.PROMPT_TEMPLATE

        def replace_string(prompt_json: dict):
            k: str
            for k in prompt_json.keys():
                if isinstance(prompt_json[k], dict):
                    prompt_json[k] = replace_string(prompt_json[k])
                    continue
                prompt_json[k] = prompt_json[k].replace("__profile__", role_profile)
                prompt_json[k] = prompt_json[k].replace("__name__", role_name)
                prompt_json[k] = prompt_json[k].replace("__context__", context)
                prompt_json[k] = prompt_json[k].replace("__action__", self.name)
                prompt_json[k] = prompt_json[k].replace("__strategy__", self.STRATEGY)
                prompt_json[k] = prompt_json[k].replace("__reflection__", reflection)
                prompt_json[k] = prompt_json[k].replace("__experiences__", experiences)

            return prompt_json

        prompt_json: dict = json.loads(prompt_template)

        prompt_json = replace_string(prompt_json)

        prompt_json: dict = self._update_prompt_json(
            prompt_json, role_profile, role_name, context, reflection, experiences, **kwargs
        )
        assert isinstance(prompt_json, dict)

        prompt: str = json.dumps(prompt_json, indent=4, ensure_ascii=False)

        return prompt

    def _update_prompt_json(
        self, prompt_json: dict, role_profile: str, role_name: str, context: str, reflection: str, experiences: str
    ) -> dict:
        # one can modify the prompt_json dictionary here
        return prompt_json

    @retry(stop=stop_after_attempt(2), wait=wait_fixed(1))
    async def run(self, context: str, profile: str, name: str, reflection: str = "", experiences: str = ""):
        prompt = self._construct_prompt_json(
            role_profile=profile, role_name=name, context=context, reflection=reflection, experiences=experiences
        )

        rsp = await self._aask(prompt)
        rsp_json = log_and_parse_json(self.name, rsp)

        return f"{self.name} " + rsp_json["RESPONSE"]


class Reflect(Action):
    PROMPT_TEMPLATE: str = """
    {
    "BACKGROUND": "It's a Werewolf game, in this game, we have 2 werewolves, 2 villagers, 1 guard, 1 witch, 1 seer. You are __profile__. Note that villager, seer, guard and witch are all in villager side, they have the same objective. Werewolves can collectively hunt ONE player at night."
    ,"HISTORY": "You have knowledge to the following conversation: __context__"
    ,"MODERATOR_INSTRUCTION": __latest_instruction__,
    ,"OUTPUT_FORMAT" (a json):
        {
        "ROLE": "Your role, in this case, __profile__"
        ,"PLAYER_NAME": "Your name, in this case, __name__"
        "GAME_STATES": "You are about to follow `MODERATOR_INSTRUCTION`, but before taking any action, analyze each player, including the living and the dead, and summarize the game states.
                        For each player, your reflection should be a ONE-LINE json covering the following dimension, return a LIST of jsons (return an empty LIST for the first night):
                        [
                            {"TARGET": "the player you will analyze, if the player is yourself or your werewolf partner, indicate it" ,"STATUS": "living or dead, if dead, how was he/she possibly killed?", "CLAIMED_ROLE": "claims a role or not, if so, what role, any contradiction to others? If there is no claim, return 'None'", "SIDE_WITH": "sides with which players? If none, return 'None'", "ACCUSE": "accuses which players? If none, return 'None'"}
                            ,{...}
                            ,...
                        ]"
        ,"REFLECTION": "Based on the whole `GAME_STATES`, return a json (return an empty string for the first night):
                       {
                            "Player1": "the true role (werewolf / special role / villager, living or dead) you infer about him/her, and why is this role? If the player is yourself or your werewolf partner, indicate it."
                            ,...
                            ,"Player7": "the true role (werewolf / special role / villager, living or dead) you infer about him/her, and why is this role? If the player is yourself or your werewolf partner, indicate it."
                            ,"GAME_STATE_SUMMARIZATION": "summarize the current situation from your standpoint in one sentence, your summarization should catch the most important information from your reflection, such as conflicts, number of living werewolves, special roles, and villagers."
                       }"
        }
    }
    """

    PROMPT_TEMPLATE: str = """
    {
        "BACKGROUND": "这是一个狼人游戏。在这个游戏中，我们有2个狼人，2个村民，1个守卫，1个女巫，1个预言家。你是__profile__。注意，村民、预言家、守卫和女巫都属于村民阵营，他们有相同的目标。狼人可以在晚上集体猎杀一名玩家。",
        "HISTORY": "你知道以下对话内容：__context__",
        "MODERATOR_INSTRUCTION": __latest_instruction__,
        "OUTPUT_FORMAT" (a json): {
            "ROLE": "你的角色，在这种情况下，__profile__",
            "PLAYER_NAME": "你的名字，在这种情况下，__name__",
            "GAME_STATES": "你即将遵循 `MODERATOR_INSTRUCTION`，但在采取任何行动之前，分析每个玩家，包括活着的和死去的，并总结游戏状态。
                对于每个玩家，你的反思应为一个单行 json，涵盖以下维度，返回一个 json 列表 (第一晚返回空字符串)：
                [ 
                    {"TARGET": "你要分析的玩家，如果是你自己或你的狼人伙伴，请注明", 
                    "STATUS": "存活或死亡，如果死亡，可能是如何被杀的？", 
                    "CLAIMED_ROLE": "是否声称某个角色，如果是，是什么角色，与其他人有矛盾吗？如果没有声称，返回 'None'", 
                    "SIDE_WITH": "与哪些玩家站在同一阵营？如果没有，返回 'None'", 
                    "ACCUSE": "指责哪些玩家？如果没有，返回 'None'" }, {...}, ... ]",
            "REFLECTION": "基于整个 `GAME_STATES`，返回一个 json（第一晚返回空字符串）： 
            { "Player1": "你推测出的他的真实角色（狼人/特殊角色/村民，存活或死亡），以及为什么是这个角色？如果是你自己或你的狼人伙伴，请注明。", 
                ..., 
                "Player7": "你推测出的他的真实角色（狼人/特殊角色/村民，存活或死亡），以及为什么是这个角色？如果是你自己或你的狼人伙伴，请注明。", 
                "GAME_STATE_SUMMARIZATION": "从你的角度用一句话总结当前情况，你的总结应抓住反思中最重要的信息，如冲突、存活的狼人数量、特殊角色和村民。" 
            }"
        }
    }
    """

    name: str = "Reflect"

    @retry(stop=stop_after_attempt(2), wait=wait_fixed(1))
    async def run(self, profile: str, name: str, context: str, latest_instruction: str):
        prompt = (
            self.PROMPT_TEMPLATE.replace("__context__", context)
            .replace("__profile__", profile)
            .replace("__name__", name)
            .replace("__latest_instruction__", latest_instruction)
        )

        rsp = await self._aask(prompt)
        rsp_json = log_and_parse_json(self.name, rsp)

        return json.dumps(rsp_json["REFLECTION"])
