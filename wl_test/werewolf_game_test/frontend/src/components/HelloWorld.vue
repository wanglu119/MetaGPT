<template>

  <div class="" >
    <start-game :channelName="channelName" v-if="startGame"/>

    <human-game :channelName="channelName" v-if="humanGame"/>

    <div class="q-pa-md row items-start q-gutter-md justify-center content-center"
      style="height: 90vh;"
      v-if="!(startGame || humanGame )" >
      <q-card style="min-width: 300px;">
        <q-card-section>
          <div class="text-h6">观看模型玩狼人杀</div>
        </q-card-section>

        <q-separator />

        <q-card-actions vertical>
          <q-btn flat @click="toStartGame">进入游戏</q-btn>
        </q-card-actions>
      </q-card>

      <q-card style="min-width: 300px;">
        <q-card-section>
          <div class="text-h6">与模型一起玩狼人杀</div>
        </q-card-section>

        <q-separator />

        <q-card-actions vertical>
          <q-btn flat @click="toHumanGame">进入游戏</q-btn>
        </q-card-actions>
      </q-card>
    </div>
    
  </div>
</template>

<script lang="ts">
import { defineComponent,ref } from 'vue'

import StartGame from './StartGame.vue'
import HumanGame from './HumanGame.vue'

export default defineComponent({
  components: {
    StartGame,
    HumanGame,
  },
  setup () {
    const startGame = ref<boolean>(false)
    const humanGame = ref<boolean>(false)
    const channelName = ref<string>("")
    
    const toStartGame = ()=>{
      channelName.value = `ch_${(new Date()).getTime()}`
      startGame.value = true
    }

    const toHumanGame = () => {
      channelName.value = `ch_${(new Date()).getTime()}`
      humanGame.value = true
    }

    return {
      startGame,
      humanGame,
      channelName,
      toStartGame,
      toHumanGame,
    }
  }
})
</script>

<style scoped>

</style>