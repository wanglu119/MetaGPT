<template>

  <div class="" >
    <start-game v-if="startGame" :param="state"/>

    <div class="q-pa-md row items-start q-gutter-md justify-center content-center"
      style="height: 90vh;"
      v-if="!startGame ">

      <q-card style="min-width: 300px;">
        <q-card-section>
          <img src="favicon.png" />
        </q-card-section>

        <q-separator />

        <q-card-actions vertical>
          <q-btn flat @click="showDialg=true">进入游戏</q-btn>
        </q-card-actions>
      </q-card>
    </div>

    <q-dialog v-model="showDialg" backdrop-filter="blur(4px)" persistent >
      <q-card dence style="width: 900px;">
        <q-card-section >
        <q-bar>
          游戏设置
          <q-space />
          <q-btn dense flat icon="close" @click="showDialg=false">
            <q-tooltip class="bg-white text-primary">关闭</q-tooltip>
          </q-btn>
        </q-bar>
      </q-card-section>
        <q-card-section>
          <q-badge color="secondary">
            村民数量: {{ state.num_villager }} 
          </q-badge>
          <q-slider v-model="state.num_villager" :min="1" :max="6" label />
          <q-badge color="secondary">
            狼人数量: {{ state.num_werewolf }} 
          </q-badge>
          <q-slider v-model="state.num_werewolf" :min="1" :max="6" label />
          <q-toggle
            v-model="state.add_human"
            label="参与游戏"
          />
          <q-option-group v-show="state.add_human"
            :options="roleNames"
            inline
            type="radio"
            v-model="state.human_player_role_name"
          />
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="开始游戏" color="primary" @click="toStartGame()" />
        </q-card-actions>
      </q-card>
    </q-dialog>
    
  </div>
</template>

<script lang="ts">
import { defineComponent,ref,reactive } from 'vue'

import StartGame from './StartGame.vue'

export default defineComponent({
  components: {
    StartGame,
  },
  setup () {
    const showDialg = ref<boolean>(false)
    const startGame = ref<boolean>(false)

    const roleNames = ref([
      { label: '村民', value: 'Villager' },
      { label: '狼人', value: 'Werewolf' },
      { label: '守卫', value: 'Guard' },
      { label: '预言家', value: 'Seer' },
      { label: '女巫', value: 'Witch' },
    ])
    const state = reactive({
      num_villager:2,
      num_werewolf:2,
      add_human:false,
      human_player_role_name:"",
      channel_name:'',
    })
    
    const toStartGame = ()=>{
      state.channel_name = `ch_${(new Date()).getTime()}`
      startGame.value = true
      showDialg.value = false
    }

    return {
      startGame,
      roleNames,
      state,
      toStartGame,
      showDialg,
    }
  }
})
</script>

<style scoped>

</style>