<template>

  <div class="" >
    <start-game :channelName="channelName" v-if="startGame" :hasHuman="hasHuman"/>

    <div class="q-pa-md row items-start q-gutter-md justify-center content-center"
      style="height: 90vh;"
      v-if="!startGame " >
      <q-card style="min-width: 300px;">
        <q-card-section>
          <div class="text-h6">观看模型玩狼人杀</div>
        </q-card-section>

        <q-separator />

        <q-card-actions vertical>
          <q-btn flat @click="toStartGame(false)">进入游戏</q-btn>
        </q-card-actions>
      </q-card>

      <q-card style="min-width: 300px;">
        <q-card-section>
          <div class="text-h6">与模型一起玩狼人杀</div>
        </q-card-section>

        <q-separator />

        <q-card-actions vertical>
          <q-btn flat @click="toStartGame(true)">进入游戏</q-btn>
        </q-card-actions>
      </q-card>
    </div>
    
  </div>
</template>

<script lang="ts">
import { defineComponent,ref } from 'vue'

import StartGame from './StartGame.vue'

export default defineComponent({
  components: {
    StartGame,
  },
  setup () {
    const startGame = ref<boolean>(false)
    const hasHuman = ref<boolean>(false)
    const channelName = ref<string>("")
    
    const toStartGame = (has:boolean)=>{
      channelName.value = `ch_${(new Date()).getTime()}`
      hasHuman.value = has
      startGame.value = true
    }

    return {
      startGame,
      hasHuman,
      channelName,
      toStartGame,
    }
  }
})
</script>

<style scoped>

</style>