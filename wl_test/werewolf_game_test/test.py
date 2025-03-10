from metagpt.ext.werewolf.roles import Guard, Moderator, Seer, Villager, Werewolf, Witch
import asyncio
import time
import threading

from nakama.nk_client import NakamaClient
from nakama.nk_socket import NakamaSocket

from metagpt.ext.werewolf.werewolf_game import WerewolfGame
from metagpt.logs import logger

from human_player import prepare_human_player
from functools import partial

def _send_msg(sock, msg):
    print("human to input: ",msg)
    sock.channel.send_message({"sent_from":"human_to_input","content":"请输入:"})
    while True:
        if sock.humanInput == "":
            time.sleep(1)
            print("wait human input ---------------------------------")
            continue

        humanInput = sock.humanInput
        sock.humanInput = ""
        break
    return humanInput

async def start_game(
    channelName:str,
    investment: float = 3.0,
    n_round: int = 5,
    shuffle: bool = True,
    add_human: bool = False,
    use_reflection: bool = True,
    use_experience: bool = False,
    use_memory_selection: bool = False,
    new_experience_version: str = "",
):
    game = WerewolfGame()

    client = NakamaClient('192.168.0.201', 7350, 'defaultkey')
    resp = client.account.authenticate.email("testPython@tusen.ai","password")
    client.session.token = resp["token"]
    client.session.channelName = channelName
    
    sock = NakamaSocket(client=client)

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
        num_werewolf=2,
        num_villager=2,
        shuffle=shuffle,
        add_human=add_human,
        use_reflection=use_reflection,
        use_experience=use_experience,
        use_memory_selection=use_memory_selection,
        new_experience_version=new_experience_version,
        prepare_human_player=f,
    )
    logger.info(f"{game_setup}")

    players = [Moderator()] + players
    game.hire(players)
    game.invest(investment)
    game.run_project(game_setup)

    await game.run(n_round=n_round)
    
    
def main(
    channelName:str,
    investment: float = 20.0,
    n_round: int = 100,
    shuffle: bool = True,
    add_human: bool = False,
    use_reflection: bool = True,
    use_experience: bool = False,
    use_memory_selection: bool = False,
    new_experience_version: str = "",
):
    asyncio.run(
      start_game(
          channelName,
          investment,
          n_round,
          shuffle,
          add_human,
          use_reflection,
          use_experience,
          use_memory_selection,
          new_experience_version,
      )
    )
    

if __name__ == "__main__":
    main("mychannel",add_human=True)
