#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Desc   : MG Werewolf Env

from typing import Iterable
import json
import time

from pydantic import Field

from metagpt.environment.base_env import Environment
from metagpt.environment.werewolf.werewolf_ext_env import WerewolfExtEnv
from metagpt.schema import Message


class WerewolfEnv(WerewolfExtEnv, Environment):
    round_cnt: int = Field(default=0)
    chat: object = Field(default=None)
    gameStatus:str = Field(default="")
    game_round_cnt: int = Field(default=0)
    promptDict:dict = Field(default={})

    def add_roles(self, roles: Iterable["Role"]):
        """增加一批在当前环境的角色
        Add a batch of characters in the current environment
        """
        for role in roles:
            self.roles[role.name] = role  # use name as key here, due to multi-player can have same profile

        for role in roles:  # setup system message with roles
            role.context = self.context
            role.set_env(self)

    def publish_message(self, message: Message, add_timestamp: bool = True):
        """Post information to the current environment"""
        if add_timestamp:
            # Because the content of the message may be repeated, for example, killing the same person in two nights
            # Therefore, a unique round_cnt prefix needs to be added so that the same message will not be automatically deduplicated when added to the memory.
            message.content = f"{self.round_cnt} | " + message.content

        if self.chat:
            self.chat.send_message({"id":message.id,"role":message.role, 
                                    "sent_from":message.sent_from,"content":message.content,"step_idx":self.step_idx})
            
        super().publish_message(message)

    async def run(self, k=1):
        """Process all Role runs by order"""
        if self.step_idx % self.per_round_steps == 0:
            self.game_round_cnt = self.game_round_cnt + 1
        if self.chat:
            pStatus = []
            for p,s in self.players_state.items():
                ps = {
                    "name":p,
                    "role": s[0],
                    "status": s[1].value,
                }
                for name,r in self.roles.items():
                    if name == p :
                        ps["is_human"] = r.is_human
                    
                pStatus.append(ps)

            content = json.dumps(pStatus)
            self.chat.send_message({"sent_from":"系统","content":content, "game_round_cnt":self.game_round_cnt,})

        hasWin = False
        if self.winner:
            hasWin = True
        for _ in range(k):
            for role in self.roles.values():
                await role.run()
                if self.gameStatus == "pause":
                    while True:
                        if self.gameStatus != "pause":
                            break
                        else:
                            time.sleep(1)
                if self.gameStatus == "stop":
                    return
            self.round_cnt += 1
        
        if self.chat:
            pStatus = []
            for p,s in self.players_state.items():
                ps = {
                    "name":p,
                    "role": s[0],
                    "status": s[1].value,
                }
                for name,r in self.roles.items():
                    if name == p :
                        ps["is_human"] = r.is_human
                pStatus.append(ps)

            content = json.dumps(pStatus)
            self.chat.send_message({"sent_from":"系统","content":content,"game_round_cnt":self.game_round_cnt,})

        if hasWin:
            self.gameStatus = "stop"

    def set_nakama(self,chat):
        self.chat = chat
