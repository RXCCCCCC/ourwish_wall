<script setup>
import { ref } from 'vue'
import { useUserStore } from '@/stores/user'
import { showToast } from 'vant'

const props = defineProps({
  onPublish: {
    type: Function,
    default: () => {}
  }
})

const userStore = useUserStore()

const colorInput = ref(null)
const showSettings = ref(false)
const inputName = ref('')

function openSettings() {
  if (!userStore.userInfo) return
  inputName.value = userStore.userInfo.name
  showSettings.value = true
}

function saveSettings() {
  if (inputName.value.trim()) {
    userStore.setName(inputName.value.trim())
  }
  showSettings.value = false
  showToast({ type: 'success', message: '设置已保存', duration: 1500 })
}

function triggerColorPicker() {
  colorInput.value?.click()
}

function onColorInput(e) {
  const v = e.target.value
  userStore.setColor(v)
}
</script>

<template>
  <nav class="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-gray-100 px-4 md:px-8 h-20 flex items-center justify-between">
    <!-- Left Logo Area -->
    <div class="flex items-center gap-3">
      <div class="w-10 h-10 bg-brand-red rounded-lg flex items-center justify-center shadow-lg shadow-red-200">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-6 h-6 text-white">
          <path fill-rule="evenodd" d="M10.788 3.21c.448-1.077 1.976-1.077 2.424 0l2.082 5.007 5.404.433c1.164.093 1.636 1.545.749 2.305l-4.117 3.527 1.257 5.273c.271 1.136-.964 2.033-1.96 1.425L12 18.354 7.373 21.18c-.996.608-2.231-.29-1.96-1.425l1.257-5.273-4.117-3.527c-.887-.76-.415-2.212.749-2.305l5.404-.433 2.082-5.006z" clip-rule="evenodd" />
        </svg>
      </div>
      <div class="flex flex-col">
        <h1 class="font-serif font-bold text-base md:text-xl text-gray-900 tracking-wide leading-tight md:leading-none whitespace-nowrap">数字传承 · 红色德兴</h1>
        <span class="text-[10px] text-gray-400 font-sans tracking-wider mt-0.5 whitespace-nowrap hidden sm:block">DIGITAL INHERITANCE OF RED GENES</span>
      </div>
    </div>

    <!-- Right Action Area -->
    <div class="flex items-center gap-3">
      <!-- User Settings Trigger -->
      <button 
        v-if="userStore.userInfo"
        @click="openSettings"
        class="flex items-center gap-2 px-3 py-1.5 rounded-full border border-gray-100 bg-white shadow-sm hover:shadow-md transition-all active:scale-95"
      >
        <span :style="{ backgroundColor: userStore.userInfo.color }" class="w-6 h-6 rounded-full shadow-inner border border-black/5"></span>
        <span class="text-xs font-medium text-gray-700 max-w-[4rem] truncate">{{ userStore.userInfo.name }}</span>
      </button>

      <button 
        @click="onPublish"
        class="bg-brand-dark text-white px-4 py-2 rounded-full text-xs md:text-sm font-medium hover:bg-gray-800 transition-colors shadow-lg shadow-gray-200 flex items-center gap-1"
      >
        <span>+</span> 发布心愿
      </button>
    </div>

    <!-- Settings Modal -->
    <div v-if="showSettings" class="fixed inset-0 z-[100] flex items-center justify-center bg-black/40 backdrop-blur-sm p-4" @click="showSettings = false">
      <div class="bg-white rounded-2xl w-full max-w-sm shadow-2xl overflow-hidden relative" @click.stop>
        <!-- Close Button -->
        <button 
          @click="showSettings = false"
          class="absolute top-3 right-3 text-gray-400 hover:text-gray-600 hover:bg-gray-100 p-2 rounded-full transition-colors z-10"
          aria-label="关闭"
        >
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor" class="w-5 h-5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>

        <div class="p-6">
          <h3 class="text-xl font-serif font-bold text-gray-900 mb-6 text-center">个人形象设置</h3>
          
          <div class="flex flex-col gap-3">
            <!-- Name Input Field -->
            <div class="flex flex-col gap-2">
              <label class="text-sm font-bold text-gray-700">我的昵称</label>
              <input 
                v-model="inputName"
                type="text" 
                class="w-full px-4 py-2.5 rounded-lg bg-gray-50 border border-gray-200 focus:bg-white focus:border-brand-red focus:ring-2 focus:ring-red-500/20 outline-none transition-all text-gray-900 placeholder-gray-400 font-medium"
                placeholder="请输入您的昵称"
                maxlength="10"
              />
            </div>

            <!-- Color Picker Field -->
            <div class="flex flex-col gap-2 mt-2">
              <label class="text-sm font-bold text-gray-700">专属颜色</label>
              <div 
                class="h-12 rounded-lg border border-gray-300 flex items-center justify-center cursor-pointer hover:border-brand-red hover:bg-red-50 transition-all group relative overflow-hidden"
                @click="triggerColorPicker"
              >
                 <div class="absolute inset-0 opacity-20 transition-colors" :style="{ backgroundColor: userStore.userInfo?.color }"></div>
                 <div class="relative z-10 flex items-center gap-3">
                    <span :style="{ backgroundColor: userStore.userInfo?.color }" class="w-6 h-6 rounded-full border-2 border-white shadow-sm ring-1 ring-gray-100"></span>
                    <span class="font-semibold text-gray-600 group-hover:text-brand-red">点击更换颜色</span>
                 </div>
              </div>
              <input ref="colorInput" type="color" class="hidden" @input="onColorInput" />
            </div>
          </div>
          
          <!-- Save Button -->
          <div class="mt-4">
            <button 
              @click="saveSettings"
              class="w-full py-2.5 rounded-lg bg-brand-red text-white font-bold text-base shadow-md shadow-red-200 hover:bg-red-600 active:scale-[0.98] transition-all mt-3"
            >
              保存并生效
            </button>
          </div>
        </div>
      </div>
    </div>
  </nav>
</template>

