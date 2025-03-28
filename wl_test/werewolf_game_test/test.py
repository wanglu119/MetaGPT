from metagpt.ext.werewolf.roles import Guard, Moderator, Seer, Villager, Werewolf, Witch
import asyncio
import time
import threading

from nakama.nk_client import NakamaClient
from nakama.nk_socket import NakamaSocket

from metagpt.ext.werewolf.werewolf_game import WerewolfGame
from metagpt.logs import logger,define_log_level
from metagpt.environment.werewolf.const import STEP_INSTRUCTIONS

from human_player import prepare_human_player
from functools import partial

def _send_msg(sock, msg):
    sock.channel.send_message({"sent_from":"human_to_input","content":"请输入:"})
    while True:
        if sock.humanInput == "":
            time.sleep(1)
            continue

        humanInput = sock.humanInput
        sock.humanInput = ""
        break
    return humanInput

async def start_game(
    channel_name:str,
    investment: float = 3.0,
    n_round: int = 5,
    shuffle: bool = True,
    add_human: bool = False,
    use_reflection: bool = True,
    use_experience: bool = False,
    use_memory_selection: bool = False,
    new_experience_version: str = "",
    human_player_role_name: str = "",
    num_werewolf=2,
    num_villager=2,
):
    game = WerewolfGame()
    game.env.promptDict = promptDict

    client = NakamaClient('192.168.0.201', 7350, 'defaultkey')
    resp = client.account.authenticate.email("testPython@tusen.ai","password")
    client.session.token = resp["token"]
    client.session.channelName = channel_name
    
    def procControlMsg(msg:dict):
        sentFrom = msg.get("sent_from","")
        if sentFrom == 'page_control':
            content = msg.get('content','')
            game.env.gameStatus = content

    sock = NakamaSocket(client=client)
    sock.messageHandles.append(procControlMsg)

    def runNakama():
        sock.connect()
    t = threading.Thread(target=runNakama)
    t.setDaemon(True)
    t.start()
    while True:
        if not sock.wsOpen:
            time.sleep(1)
        else:
            game.env.set_nakama(sock.channel)
            break
    
    sendMsg = partial(_send_msg,sock)
    f = partial(prepare_human_player,sendMsg)
    game_setup, players = game.env.init_game_setup(
        role_uniq_objs=[Villager, Werewolf, Guard, Seer, Witch],
        num_werewolf=num_werewolf,
        num_villager=num_villager,
        shuffle=shuffle,
        add_human=add_human,
        use_reflection=use_reflection,
        use_experience=use_experience,
        use_memory_selection=use_memory_selection,
        new_experience_version=new_experience_version,
        prepare_human_player=f,
        human_player_role_name=human_player_role_name,
    )
    logger.info(f"{game_setup}")

    players = [Moderator()] + players
    game.hire(players)
    game.invest(investment)
    game.run_project(game_setup)

    await game.run(n_round=n_round)
    sock.websocket.close()
    print("------------------------------------游戏结束了")
    
    
def main(
    channel_name:str,
    investment: float = 20.0,
    n_round: int = 100,
    shuffle: bool = True,
    add_human: bool = False,
    use_reflection: bool = True,
    use_experience: bool = False,
    use_memory_selection: bool = False,
    new_experience_version: str = "",
    human_player_role_name: str = "",
    num_werewolf=2,
    num_villager=2,
):
    logger = define_log_level("ERROR")
    asyncio.run(
      start_game(
          channel_name,
          investment,
          n_round,
          shuffle,
          add_human,
          use_reflection,
          use_experience,
          use_memory_selection,
          new_experience_version,
          human_player_role_name,
          num_werewolf,
          num_villager,
      )
    )

promptDict = {
    "Speak": {
        "PROMPT_TEMPLATE":"""
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
""",
        "STRATEGY":'''
根据利弊决定是否揭示你的身份，提供有用的信息，并投票淘汰最可疑的人。
如果你有特殊能力，要注意那些虚假声称是你角色的人，因为他们可能是狼人。
'''
    },
    "NighttimeWhispers": {
        "PROMPT_TEMPLATE":'''
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
''',
        "STRATEGY":'''
决定哪个玩家对你威胁最大或最需要你的支持，然后相应地采取行动。
'''
    },
    "Reflect": {
        "PROMPT_TEMPLATE":'''
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
''',
    },
    "WitchSave":{
        "THOUGHTS":"现在是晚上。请返回你决定是否拯救今晚刚被杀的玩家的思考步骤。",
        "RESPONSE":"根据主持人的指示，决定你是否想要拯救那个人。返回Save或Pass。",
    },
    "WitchPoison": {
        "STRATEGY":"只有在你确信某人是狼人时才毒他/她。不要随意毒人，也不要在第一晚下毒。如果有人声称自己是女巫，就毒他/她，因为你是唯一的女巫，他/她只能是狼人。"
    },
    "WerewolfImpersonate": {
        "STRATEGY":"尝试持续伪装成某个角色，比如预言家、守卫、村民等，以误导其他玩家，让他们信任你，从而隐藏你的狼人身份。不过，要注意你的狼人伙伴说的话，不要声称与你的狼人伙伴相同的角色。记住不要暴露你作为狼人的真实身份！"
    }
}

def test_STEP_INSTRUCTIONS():
    STEP_INSTRUCTIONS[0]['content'] =  "It’s dark, everyone close your eyes. I will talk with you/your team secretly at night."
    STEP_INSTRUCTIONS[1]['content'] =  "Guard, please open your eyes!"
    STEP_INSTRUCTIONS[2]['content'] =  '''
    Guard, now tell me who you protect tonight?
    You only choose one from the following living options please: {living_players}.
    Or you can pass. For example: Protect ...
    '''
    STEP_INSTRUCTIONS[3]['content'] =  "Guard, close your eyes"
    STEP_INSTRUCTIONS[4]['content'] =  "Werewolves, please open your eyes!"
    STEP_INSTRUCTIONS[5]['content'] =  """
    Werewolves, I secretly tell you that {werewolf_players} are
    all of the {werewolf_num} werewolves! Keep in mind you are teammates. The rest players are not werewolves.
    choose one from the following living options please:
    {living_players}. For example: Kill ...
    """
    STEP_INSTRUCTIONS[6]['content'] =  "Werewolves, close your eyes"
    STEP_INSTRUCTIONS[7]['content'] =  "Witch, please open your eyes!"
    STEP_INSTRUCTIONS[8]['content'] =  """
    Witch, tonight {player_hunted} has been killed by the werewolves.
    You have a bottle of antidote, would you like to save him/her? If so, say "Save", else, say "Pass".
    """
    STEP_INSTRUCTIONS[9]['content'] =  """
    Witch, you also have a bottle of poison, would you like to use it to kill one of the living players?
    Choose one from the following living options: {living_players}.
    If so, say ONLY "Poison PlayerX", replace PlayerX with the actual player name, else, say "Pass".
    """
    STEP_INSTRUCTIONS[10]['content'] =  "Witch, close your eyes"
    STEP_INSTRUCTIONS[11]['content'] =  "Seer, please open your eyes!"
    STEP_INSTRUCTIONS[12]['content'] =  """
    Seer, you can check one player's identity. Who are you going to verify its identity tonight?
    Choose only one from the following living options:{living_players}.
    """
    STEP_INSTRUCTIONS[13]['content'] =  "Seer, close your eyes"
    STEP_INSTRUCTIONS[14]['content'] =  "It's daytime. Everyone woke up except those who had been killed."
    STEP_INSTRUCTIONS[15]['content'] =  "{player_current_dead} was killed last night!"
    STEP_INSTRUCTIONS[16]['content'] =  """
    Living players: {living_players}, now freely talk about the current situation based on your observation and
    reflection with a few sentences. Decide whether to reveal your identity based on your reflection.
    """
    STEP_INSTRUCTIONS[17]['content'] =  """
    Now vote and tell me who you think is the werewolf. Don’t mention your role.
    You only choose one from the following living options please:
    {living_players}. Say ONLY: I vote to eliminate ...
    """
    STEP_INSTRUCTIONS[18]['content'] =  """{player_current_dead} was eliminated."""


if __name__ == "__main__":
    # main("mychannel",add_human=True)
    Villager.name
