<template>
    <q-page class="flex flex-center column" >
      <div class="q-gutter-sm">
        <q-chip v-for="p in playerStatus" :key="p.name">
            <q-avatar :color="p.status=='alive'?'yellow':'red'" text-color="white" v-if="p.is_human">{{ p.status }}</q-avatar>
            <q-avatar :color="p.status=='alive'?'green':'red'" text-color="white" v-else>{{ p.status }}</q-avatar>
            {{ p.name }}({{ p.role }})
        </q-chip>
      </div>
      <q-scroll-area ref="scrollRef" style="height: 65vh; min-width: 80%; border:1px solid red ;">
        <q-list bordered>
          <q-item v-for="msg in recvMsgs" :key="msg.msg_id" class="q-my-sm" clickable v-ripple>
            <q-item-section avatar>
              <q-avatar color="primary" text-color="white">
                {{ msg.sent_from }}
              </q-avatar>
            </q-item-section>
  
            <q-item-section>
              <q-item-label>{{ msg.sent_from }}({{msg.role}})({{ msg.step_idx }})</q-item-label>
              <q-item-label caption lines="3">{{ msg.content }}</q-item-label>
            </q-item-section>
  
            <q-item-section side>
              <q-icon name="chat_bubble" color="green" />
            </q-item-section>
          </q-item>
        </q-list>
      </q-scroll-area>

      <div class="q-gutter-sm" style="min-width: 80%">
        <q-card bordered v-show="humanToInput != ''">
            <q-card-section>
                <q-input v-model="humanInput" label="请输入" @keypress.enter="toHumanInput"/>
            </q-card-section>
        </q-card>
       
      </div>

      
    </q-page>
  </template>
  
  <script lang="ts">
  import { defineComponent,ref,onUnmounted } from 'vue'
  import Axios from 'axios'
  
  import {Client,Socket,Session,Channel, ChannelMessage} from "@heroiclabs/nakama-js";
  import { QScrollArea } from 'quasar';

  import UtilApi from '@/services/util'
  
  interface WerewolfMsgContent {
    msg_id:string
    id:string
    sent_from:string
    role:string
    round_cnt:string
    content:string
    step_idx:number
  }

  interface PlayerStatus {
    name:string
    role:string
    status:string
    is_human:boolean
  }
  
  export default defineComponent({
    setup (props,{attrs}) {
      const channelName = attrs.channelName as string
      const serverNkHostname = UtilApi.GetNkHostname()
      const serverApiHostname = UtilApi.GetApiHostname()

      const scrollRef = ref<QScrollArea>()
      const useSSL = false; // Enable if server is run with an SSL certificate.
      const client = new Client("defaultkey", serverNkHostname, "7350", useSSL);
      const sockSession =  ref<Session>()
      const sock = ref<Socket>()
      const chat = ref<Channel>()
  
      const timer = ref<number>()
  
      const recvMsgs = ref<WerewolfMsgContent[]>([])
      const playerStatus = ref<PlayerStatus[]>([])
      const humanToInput = ref<string>("")
      const humanInput = ref<string>("")
  
      const secure = false; // Enable if server is run with an SSL certificate 
      const trace = false;
  
      const roomname = channelName
      const type = 1
      const persistence = false
      const hidden = false

      const startGame = async()=>{
        await Axios.get(`http://${serverApiHostname}:5000/api/human_and_model_player?channelName=${channelName}`)
      }
  
      const auth = async() => {
        var email = `lu.wang@tusen.ai`;
        var password = "password";
        sockSession.value = await client.authenticateEmail(email, password);
  
        sock.value = client.createSocket(secure,trace)
        sock.value.ondisconnect = (evt:Event) => {
          console.log("Disconnected sockA")
        }
        sockSession.value = await sock.value.connect(sockSession.value,false)
  
        chat.value = await sock.value.joinChat(roomname,type,persistence,hidden)

        await startGame()
  
        sock.value.onchannelmessage = (cmsg:ChannelMessage)=>{
          if(cmsg.sender_id != sockSession.value?.user_id) {
            console.log("sockA:",cmsg)
   
            const wMsg = cmsg.content as WerewolfMsgContent
            if(cmsg.message_id) {
              wMsg.msg_id = cmsg.message_id
            }

            if (wMsg.sent_from =="系统") {
                console.log(wMsg)
                const ps = JSON.parse(wMsg.content)
                playerStatus.value = []
                for(let i = 0;i<ps.length;i++) {
                    const pe = ps[i] as PlayerStatus
                    playerStatus.value.push(pe)
                }
            } else if (wMsg.sent_from =="human_to_input") {
                humanToInput.value = wMsg.content
                console.log(humanToInput.value)
            } else {
                const c = wMsg.content.indexOf("|")
                if(c>0) {
                wMsg.round_cnt = wMsg.content.substring(0,c)
                wMsg.content = wMsg.content.substring(c+1)
                }
                if (wMsg.role === "Moderator") {
                wMsg.role = "主持人"
                }
                if (wMsg.role === "Werewolf") {
                wMsg.role = "狼人"
                }
                if (wMsg.role === "Villager") {
                wMsg.role = "村民"
                }
                if(wMsg.role === "Witch") {
                wMsg.role = "女巫"
                }
                if(wMsg.role === "Seer") {
                wMsg.role = "预言家"
                }
                if(wMsg.role === "Guard") {
                    wMsg.role = "守卫"
                }
                
                recvMsgs.value.push(wMsg)
            }
            
            
            if(scrollRef.value) {
              scrollRef.value.setScrollPosition("vertical",10000)
            }
          }
        }
      }
  
      try{
        auth()
      }catch(e) {
        console.log(e)
      }

      const toHumanInput = async()=>{
        console.log(humanInput.value)
        if(chat.value) {
            await sock.value?.writeChatMessage(chat.value?.id,{"sent_from":"human_to_output","content": humanInput.value})
        }
        
        humanInput.value = ""
        humanToInput.value = ""
      }
      
  
      onUnmounted(()=>{
        if(timer.value) {
          console.log("timerA:",timer.value)
          clearInterval(timer.value)
        }
        if(sock.value) {
          if(chat.value) {
            sock.value.leaveChat(chat.value.id)
          }
          sock.value.disconnect(true)
        }
      })
  
      return {
        scrollRef,
        recvMsgs,
        chat,
        playerStatus,
        humanToInput,
        humanInput,
        toHumanInput,
      }
    }
  })
  </script>
  
  <style scoped>
  
  </style>
  