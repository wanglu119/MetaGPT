from metagpt.ext.werewolf.actions.common_actions import NighttimeWhispers, Speak


class Hunt(NighttimeWhispers):
    name: str = "Hunt"


class Impersonate(Speak):
    """Action: werewolf impersonating a good guy in daytime speak"""

    STRATEGY: str = """
    Try continuously impersonating a role, such as Seer, Guard, Villager, etc., in order to mislead
    other players, make them trust you, and thus hiding your werewolf identity. However, pay attention to what your werewolf partner said, 
    DONT claim the same role as your werewolf partner. Remmber NOT to reveal your real identity as a werewolf!
    """
    STRATEGY: str = """
    尝试持续伪装成某个角色，比如预言家、守卫、村民等，以误导其他玩家，让他们信任你，从而隐藏你的狼人身份。不过，要注意你的狼人伙伴说的话，不要声称与你的狼人伙伴相同的角色。记住不要暴露你作为狼人的真实身份！
    """

    name: str = "Impersonate"
