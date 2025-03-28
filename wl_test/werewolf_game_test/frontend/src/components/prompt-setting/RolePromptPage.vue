<template>
    <div>
        <q-tabs
        v-model="tab"
        class="text-teal"
      >
        <q-tab name="werewolf" label="狼人提示词" />
        <q-tab name="witch" label="女巫提示词" />
      </q-tabs>

      <q-tab-panels v-model="tab" animated v-if="actionPrompt">
          <q-tab-panel name="werewolf">
            <q-input label="伪装策略" v-model="actionPrompt.WerewolfImpersonate.STRATEGY" autogrow/>
          </q-tab-panel>
          <q-tab-panel name="witch">
            <q-input label="拯救思考" v-model="actionPrompt.WitchSave.THOUGHTS" autogrow/>
            <q-input label="拯救反馈" v-model="actionPrompt.WitchSave.RESPONSE" autogrow/>
            <q-input label="毒杀策略" v-model="actionPrompt.WitchPoison.STRATEGY"  autogrow/>
          </q-tab-panel>
      </q-tab-panels>

      <q-page-sticky position="bottom-right" :offset="[36, 36]">
        <q-btn fab icon="save" color="green" @click="setActionPrompt">
            <q-tooltip>保存</q-tooltip>
        </q-btn>
    </q-page-sticky>
    </div>
</template>

<script lang="ts">
import { defineComponent,ref,onMounted } from 'vue'
import Axios from 'axios'

import UtilApi from '@/services/util'
import {ActionPrompt} from './model'


export default defineComponent({
    setup () {
        const actionPrompt = ref<ActionPrompt>()
        const serverApiHostname = UtilApi.GetApiHostname()
        const tab = ref<string>('werewolf')

        const getActionPrompt = async() => {
            actionPrompt.value = (await Axios.get(`http://${serverApiHostname}:5000/api/get_prompts`)).data
        }
        const setActionPrompt = async() => {
            await Axios.post(`http://${serverApiHostname}:5000/api/set_prompts`,actionPrompt.value )
            getActionPrompt()
        }
        
        onMounted(()=>{
            getActionPrompt()
        })

        return {
            tab,
            actionPrompt,
            setActionPrompt,
        }
    }
})
</script>

<style scoped>

</style>