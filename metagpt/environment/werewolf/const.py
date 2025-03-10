#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Desc   :

from enum import Enum

from metagpt.const import MESSAGE_ROUTE_TO_ALL


class RoleType(Enum):
    VILLAGER = "Villager"
    WEREWOLF = "Werewolf"
    GUARD = "Guard"
    SEER = "Seer"
    WITCH = "Witch"
    MODERATOR = "Moderator"

    # VILLAGER = "村民"
    # WEREWOLF = "狼人"
    # GUARD = "守卫"
    # SEER = "预言家"
    # WITCH = "女巫"
    # MODERATOR = "主持人"


class RoleState(Enum):
    ALIVE = "alive"  # the role is alive
    DEAD = "dead"  # killed or poisoned
    KILLED = "killed"  # killed by werewolf or voting
    POISONED = "poisoned"  # killed by poison
    SAVED = "saved"  # saved by antidote
    PROTECTED = "projected"  # projected by guard

    # ALIVE = "存活"
    # DEAD = "死亡"
    # KILLED = "被杀"
    # POISONED = "中毒"
    # SAVED = "获救"
    # PROTECTED = "被守护"



class RoleActionRes(Enum):
    SAVE = "save"
    PASS = "pass"  # ignore current action output

    # SAVE = "救人"
    # PASS = "跳过"


empty_set = set()

# the ordered rules by the moderator to announce to everyone each step
STEP_INSTRUCTIONS = {
    0: {
        "content": "It’s dark, everyone close your eyes. I will talk with you/your team secretly at night.",
        "send_to": {RoleType.MODERATOR.value},  # for moderator to continue speaking
        "restricted_to": empty_set,
    },
    1: {
        "content": "Guard, please open your eyes!",
        "send_to": {RoleType.MODERATOR.value},  # for moderator to continue speaking
        "restricted_to": empty_set,
    },
    2: {
        "content": """Guard, now tell me who you protect tonight?
You only choose one from the following living options please: {living_players}.
Or you can pass. For example: Protect ...""",
        "send_to": {RoleType.GUARD.value},
        "restricted_to": {RoleType.MODERATOR.value, RoleType.GUARD.value},
    },
    3: {"content": "Guard, close your eyes", "send_to": {RoleType.MODERATOR.value}, "restricted_to": empty_set},
    4: {
        "content": "Werewolves, please open your eyes!",
        "send_to": {RoleType.MODERATOR.value},
        "restricted_to": empty_set,
    },
    5: {
        "content": """Werewolves, I secretly tell you that {werewolf_players} are
all of the {werewolf_num} werewolves! Keep in mind you are teammates. The rest players are not werewolves.
choose one from the following living options please:
{living_players}. For example: Kill ...""",
        "send_to": {RoleType.WEREWOLF.value},
        "restricted_to": {RoleType.MODERATOR.value, RoleType.WEREWOLF.value},
    },
    6: {"content": "Werewolves, close your eyes", "send_to": {RoleType.MODERATOR.value}, "restricted_to": empty_set},
    7: {"content": "Witch, please open your eyes!", "send_to": {RoleType.MODERATOR.value}, "restricted_to": empty_set},
    8: {
        "content": """Witch, tonight {player_hunted} has been killed by the werewolves.
You have a bottle of antidote, would you like to save him/her? If so, say "Save", else, say "Pass".""",
        "send_to": {RoleType.WITCH.value},
        "restricted_to": {RoleType.MODERATOR.value, RoleType.WITCH.value},
    },  # 要先判断女巫是否有解药，再去询问女巫是否使用解药救人
    9: {
        "content": """Witch, you also have a bottle of poison, would you like to use it to kill one of the living players?
Choose one from the following living options: {living_players}.
If so, say ONLY "Poison PlayerX", replace PlayerX with the actual player name, else, say "Pass".""",
        "send_to": {RoleType.WITCH.value},
        "restricted_to": {RoleType.MODERATOR.value, RoleType.WITCH.value},
    },  #
    10: {"content": "Witch, close your eyes", "send_to": {RoleType.MODERATOR.value}, "restricted_to": empty_set},
    11: {"content": "Seer, please open your eyes!", "send_to": {RoleType.MODERATOR.value}, "restricted_to": empty_set},
    12: {
        "content": """Seer, you can check one player's identity. Who are you going to verify its identity tonight?
Choose only one from the following living options:{living_players}.""",
        "send_to": {RoleType.SEER.value},
        "restricted_to": {RoleType.MODERATOR.value, RoleType.SEER.value},
    },
    13: {"content": "Seer, close your eyes", "send_to": {RoleType.MODERATOR.value}, "restricted_to": empty_set},
    # The 1-st daytime
    14: {
        "content": """It's daytime. Everyone woke up except those who had been killed.""",
        "send_to": {RoleType.MODERATOR.value},
        "restricted_to": empty_set,
    },
    15: {
        "content": "{player_current_dead} was killed last night!",
        "send_to": {RoleType.MODERATOR.value},
        "restricted_to": empty_set,
    },
    16: {
        "content": """Living players: {living_players}, now freely talk about the current situation based on your observation and
reflection with a few sentences. Decide whether to reveal your identity based on your reflection.""",
        "send_to": {MESSAGE_ROUTE_TO_ALL},  # send to all to speak in daytime
        "restricted_to": empty_set,
    },
    17: {
        "content": """Now vote and tell me who you think is the werewolf. Don’t mention your role.
You only choose one from the following living options please:
{living_players}. Say ONLY: I vote to eliminate ...""",
        "send_to": {MESSAGE_ROUTE_TO_ALL},
        "restricted_to": empty_set,
    },
    18: {
        "content": """{player_current_dead} was eliminated.""",
        "send_to": {RoleType.MODERATOR.value},
        "restricted_to": empty_set,
    },
}


# the ordered rules by the moderator to announce to everyone each step
STEP_INSTRUCTIONS = {
    0: {
        "content": "天黑请闭眼，我将在夜晚与您/您的团队秘密交谈。",
        "send_to": {RoleType.MODERATOR.value},  # for moderator to continue speaking
        "restricted_to": empty_set,
    },
    1: {
        "content": "守卫请睁眼！",
        "send_to": {RoleType.MODERATOR.value},  # for moderator to continue speaking
        "restricted_to": empty_set,
    },
    2: {
        "content": """守卫，请告诉我你今晚要守护谁？
请从以下存活玩家中选择一位：{living_players}.
或选择放弃行动 示例：守护 ...""",
        "send_to": {RoleType.GUARD.value},
        "restricted_to": {RoleType.MODERATOR.value, RoleType.GUARD.value},
    },
    3: {"content": "守卫，请闭眼。", "send_to": {RoleType.MODERATOR.value}, "restricted_to": empty_set},
    4: {
        "content": "狼人，请睁眼！",
        "send_to": {RoleType.MODERATOR.value},
        "restricted_to": empty_set,
    },
    5: {
        "content": """狼人，我悄悄告诉你们， {werewolf_players} 是所有 {werewolf_num} 名狼人！
        记住你们是队友。其他玩家不是狼人。
        请从以下在世玩家中选择一个：
        {living_players}. 例如：杀死...""",
        "send_to": {RoleType.WEREWOLF.value},
        "restricted_to": {RoleType.MODERATOR.value, RoleType.WEREWOLF.value},
    },
    6: {"content": "狼人，请闭眼。", "send_to": {RoleType.MODERATOR.value}, "restricted_to": empty_set},
    7: {"content": "女巫，请睁眼！", "send_to": {RoleType.MODERATOR.value}, "restricted_to": empty_set},
    8: {
        "content": """女巫，今晚 {player_hunted} 被狼人杀害。
        你有一瓶解药，想要救他/她吗？ 如果是，请说 "Save", 否则, 请说 "Pass".""",
        "send_to": {RoleType.WITCH.value},
        "restricted_to": {RoleType.MODERATOR.value, RoleType.WITCH.value},
    },  # 要先判断女巫是否有解药，再去询问女巫是否使用解药救人
    9: {
        "content": """女巫，你还有一瓶毒药，想用它杀死一名在世玩家吗？
请从以下在世玩家中选择：{living_players}。
如果是，请只说 "Poison PlayerX", 将 PlayerX 替换为实际玩家名，否则， 请说 "Pass".""",
        "send_to": {RoleType.WITCH.value},
        "restricted_to": {RoleType.MODERATOR.value, RoleType.WITCH.value},
    },  #
    10: {"content": "女巫，请闭眼。", "send_to": {RoleType.MODERATOR.value}, "restricted_to": empty_set},
    11: {"content": "预言家，请睁眼！", "send_to": {RoleType.MODERATOR.value}, "restricted_to": empty_set},
    12: {
        "content": """预言家，你可以查验一名玩家的身份。今晚你想验证谁的身份？
请从以下在世玩家中选择一位：{living_players}.""",
        "send_to": {RoleType.SEER.value},
        "restricted_to": {RoleType.MODERATOR.value, RoleType.SEER.value},
    },
    13: {"content": "预言家，请闭眼。", "send_to": {RoleType.MODERATOR.value}, "restricted_to": empty_set},
    # The 1-st daytime
    14: {
        "content": """天亮了。除了被杀的玩家，其他人都醒来了。""",
        "send_to": {RoleType.MODERATOR.value},
        "restricted_to": empty_set,
    },
    15: {
        "content": "{player_current_dead} 昨晚被杀了！",
        "send_to": {RoleType.MODERATOR.value},
        "restricted_to": empty_set,
    },
    16: {
        "content": """在世玩家：{living_players}，现在根据你的观察和思考自由讨论当前情况。
用几句话表达，根据你的反思决定是否揭示自己的身份。""",
        "send_to": {MESSAGE_ROUTE_TO_ALL},  # send to all to speak in daytime
        "restricted_to": empty_set,
    },
    17: {
        "content": """现在投票，告诉我你认为谁是狼人。 不要提及你的角色。
        请仅从以下在世选项中选择一人：{living_players}。只说：I vote to eliminate ...""",
        "send_to": {MESSAGE_ROUTE_TO_ALL},
        "restricted_to": empty_set,
    },
    18: {
        "content": """{player_current_dead} 被淘汰了。""",
        "send_to": {RoleType.MODERATOR.value},
        "restricted_to": empty_set,
    },
}
