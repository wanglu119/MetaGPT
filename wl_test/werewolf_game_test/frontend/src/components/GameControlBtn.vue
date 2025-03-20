<template>
    <q-page-sticky position="bottom-right" :offset="[18, 18]">
        <q-btn fab round 
            :icon="gameStatus?'pause':'play_arrow'" 
            :color="gameStatus?'blue':'green'" 
            @click="pauseStartGame"
        >
            <q-tooltip>
                {{ gameStatus?'暂停':'开始' }}
            </q-tooltip>
        </q-btn>
        <q-btn fab icon="close" color="red" @click="toStopGame">
            <q-tooltip>
                退出
            </q-tooltip>
        </q-btn>
    </q-page-sticky>
</template>

<script lang="ts">
import { Channel, Socket } from '@heroiclabs/nakama-js';
import { defineComponent,Ref,ref,inject } from 'vue'

export default defineComponent({
    setup (props,{attrs}) {
        const sock = inject('sock') as Ref<Socket>
        const chat = inject('chat') as Ref<Channel>
        const stopGame = attrs.stopGame as CallableFunction
        const gameStatus = ref<boolean>(true)
        
        const pauseStartGame = async()=>{
            if(gameStatus.value) {
                await sock.value.writeChatMessage(chat.value?.id,{"sent_from":"page_control","content": "pause"})
            } else {
                await sock.value.writeChatMessage(chat.value?.id,{"sent_from":"page_control","content": "start"})
            }
            gameStatus.value = !gameStatus.value
        }

        const toStopGame = async()=>{
            stopGame()
        }

        return {
            gameStatus,
            pauseStartGame,
            toStopGame,
        }
    }
})
</script>

<style scoped>

</style>