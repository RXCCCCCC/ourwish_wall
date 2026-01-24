<script setup>
import { ref, onMounted } from 'vue';
import { useUserStore } from '@/stores/user';

const userStore = useUserStore();

const showWelcome = ref(false)
const nick = ref('')

onMounted(() => {
  if (!userStore.checkLogin()) {
    // show our custom welcome modal so user can choose a generated id or set a nickname
    showWelcome.value = true
  }
})

function useGenerated() {
  userStore.login()
  showWelcome.value = false
  userStore.setShowProfileGuide(true)
}

function useNickname() {
  const name = nick.value && nick.value.trim()
  if (name) {
    userStore.login(name)
    showWelcome.value = false
    userStore.setShowProfileGuide(true)
  } else {
    userStore.login()
    showWelcome.value = false
    userStore.setShowProfileGuide(true)
  }
}
</script>

<template>
  <div class="min-h-screen flex flex-col">
    <RouterView />

    <!-- Welcome / Identity modal (mobile-first) -->
    <div v-if="showWelcome" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4" @click.self="showWelcome = false">
      <div class="bg-white rounded-2xl w-full max-w-sm p-6 shadow-2xl" @click.stop>
        <h3 class="text-lg font-semibold mb-3">欢迎加入红脉行动</h3>
        <p class="text-sm text-gray-500 mb-4">为记录您的心愿，系统可以为您生成一个代号，或输入自定义昵称。</p>

        <input v-model="nick" type="text" placeholder="输入昵称（可选）" class="w-full px-4 py-3 rounded-lg border border-gray-200 mb-4" maxlength="12" />

        <div class="flex gap-3">
          <button @click="useGenerated" class="flex-1 py-2 rounded-lg bg-gray-100">直接生成</button>
          <button @click="useNickname" class="flex-1 py-2 rounded-lg bg-brand-red text-white">保存并使用</button>
        </div>

        <p class="text-xs text-gray-400 mt-3">提示：您可随时在右上角“个人形象设置”中更改昵称与颜色。</p>
      </div>
    </div>
  </div>
</template>
