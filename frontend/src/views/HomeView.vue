<script setup>
import { ref } from 'vue';
import NavBar from '../components/NavBar.vue';
import HeroSection from '../components/HeroSection.vue';
import ChartsBoard from '../components/charts/ChartsBoard.vue';
import WishCard from '../components/WishCard.vue';
import WishForm from '../components/WishForm.vue';
import { onMounted } from 'vue';  // 添加 onMounted
import { showToast } from 'vant';  // 添加 showToast
import { wishAPI } from '@/api';
import { useUserStore } from '@/stores/user';

const userStore = useUserStore();
const showForm = ref(false);
const chartsBoardRef = ref(null);
const particles = ref([]); // Background animation particles

const wishes = ref([]);

// Load wishes from backend
const loadWishes = async () => {
  try {
    const response = await wishAPI.getWishes({ 
      page: 1, 
      per_page: 20,
      user_uid: userStore.userInfo?.id  // Pass current user_uid to get user_liked status
    });
    if (response && response.wishes && response.wishes.length > 0) {
      wishes.value = response.wishes.map(wish => ({
        ...wish,
        likes: wish.likes ?? 0,
        comments: wish.comments ?? []
      }));
    } else {
      // No wishes from backend - show empty state
      wishes.value = [];
    }
  } catch (error) {
    console.error('Failed to load wishes from backend:', error);
    showToast('加载心愿失败，请检查网络连接');
    wishes.value = [];
  }
};

// Load wishes on mount
onMounted(() => {
  loadWishes();
  
  // Initialize background particles for "Red Pulse" effect
  particles.value = Array.from({ length: 18 }, (_, i) => ({
    id: i,
    style: {
      left: `${Math.random() * 100}%`,
      top: `${Math.random() * 120}%`,
      width: `${Math.random() * 10 + 10}px`, // Larger size for stars (10-20px)
      height: `${Math.random() * 10 + 10}px`,
      animationDuration: `${Math.random() * 15 + 20}s`,
      animationDelay: `${Math.random() * -20}s`,
      opacity: Math.random() * 0.3 + 0.1
    }
  }));
});

const handlePublishWish = () => {
  showForm.value = true;
}

const handleWishSubmitted = async (newWish) => {
  // ensure fields for likes/comments
  newWish.likes = newWish.likes ?? 0
  newWish.comments = newWish.comments ?? []
  newWish.created_at = newWish.created_at || new Date().toISOString()
  
  // 1. 本地立即显示（优化体验）
  wishes.value.unshift(newWish)

  // 2. 重新加载心愿列表，确保看到他人新发布的心愿
  await loadWishes()
  
  // 刷新图表数据
  if (chartsBoardRef.value) {
    chartsBoardRef.value.refreshCharts()
  }
  
  // 如果 ai_response 是占位文本则轮询更新
  const placeholder = '回响中......'
  if (newWish.ai_response === placeholder) {
    const maxAttempts = 30 // 最多尝试 30 次
    const intervalMs = 2000 // 每 2 秒请求一次
    let attempts = 0

    const poll = async () => {
      attempts += 1
      try {
        const res = await wishAPI.getWish(newWish.id, { user_uid: userStore.userInfo?.id })
        if (res && res.ai_response && res.ai_response !== placeholder) {
          handleUpdateWish(res)
          return
        }
      } catch (e) {
        // 忽略网络临时错误，继续重试
        console.error('Polling wish failed:', e)
      }

      if (attempts < maxAttempts) {
        setTimeout(poll, intervalMs)
      } else {
        console.warn('Polling for AI response timed out for wish', newWish.id)
      }
    }

    setTimeout(poll, intervalMs)
  }
}

const handleDeleteWish = (id) => {
  const idx = wishes.value.findIndex(w => w.id === id)
  if (idx !== -1) {
    wishes.value.splice(idx, 1)
    // 删除心愿后刷新图表
    if (chartsBoardRef.value) {
      chartsBoardRef.value.refreshCharts()
    }
  }
}

const handleUpdateWish = (updated) => {
  const idx = wishes.value.findIndex(w => w.id === updated.id)
  if (idx !== -1) wishes.value[idx] = { ...wishes.value[idx], ...updated }
}

const refreshing = ref(false)
const handleManualRefresh = async () => {
  if (refreshing.value) return
  refreshing.value = true
  try {
    await loadWishes()
    if (chartsBoardRef.value) {
      await chartsBoardRef.value.refreshCharts()
    }
    showToast({ type: 'success', message: '已更新最新心愿' })
  } catch (e) {
    showToast('刷新失败')
  } finally {
    setTimeout(() => { refreshing.value = false }, 500) // min spin time
  }
}
</script>

<template>
  <div class="min-h-screen relative pb-20 overflow-hidden bg-slate-50">
    <!-- Red Culture Background Animation -->
    <div class="fixed inset-0 z-0 pointer-events-none">
      <!-- Base Gradient -->
      <div class="absolute inset-0 bg-gradient-to-br from-red-50/60 via-white/80 to-amber-50/50"></div>
      
      <!-- Animated Shapes (Red Ribbons/Clouds) -->
      <div class="absolute -top-40 -left-20 w-[40rem] h-[40rem] bg-red-100/40 rounded-full blur-3xl animate-pulse-slow"></div>
      <div class="absolute top-1/2 -right-40 w-[30rem] h-[30rem] bg-orange-100/40 rounded-full blur-3xl animate-pulse-slow animation-delay-2000"></div>
      <div class="absolute bottom-0 left-1/3 w-full h-96 bg-gradient-to-t from-red-50 to-transparent blur-2xl opacity-60"></div>
      
      <!-- Floating Particles (Stars/Sparks) -->
      <div 
        v-for="p in particles" 
        :key="p.id"
        class="absolute animate-float-up text-brand-red/20"
        :style="p.style"
      >
        <svg viewBox="0 0 24 24" fill="currentColor" class="w-full h-full">
          <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
        </svg>
      </div>
    </div>

    <!-- Main Content -->
    <div class="relative z-10">
      <NavBar @publish="handlePublishWish" />
      
      <main>
      <HeroSection />
      
      <!-- Charts Visualization Section -->
      <ChartsBoard ref="chartsBoardRef" />
      
      <!-- Wish Cards Grid -->
      <div class="max-w-5xl mx-auto px-4 mt-8">
        <h3 class="text-xl font-serif font-bold mb-6 flex items-center gap-2">
           <span class="w-1 h-6 bg-brand-red rounded-full"></span>
           最新心愿墙
        </h3>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <WishCard 
            v-for="(wish, index) in wishes" 
            :key="wish.id" 
            :wish="wish"
            :index="index"
            @delete-wish="handleDeleteWish"
            @update-wish="handleUpdateWish"
          />
        </div>
      </div>
    </main>
    
    <WishForm 
      v-model:show="showForm" 
      @submitted="handleWishSubmitted"
    />

    <!-- Fixed Floating Refresh Button -->
    <button 
      @click="handleManualRefresh"
      class="fixed bottom-24 right-4 z-40 bg-white p-3 rounded-full shadow-lg shadow-gray-200 border border-gray-100 text-gray-600 hover:text-brand-red active:scale-95 transition-all text-xs flex flex-col items-center justify-center w-14 h-14"
      :class="{ 'opacity-80': refreshing }"
    >
      <svg 
        class="w-6 h-6 mb-0.5" 
        :class="{ 'animate-spin': refreshing }"
        fill="none" 
        stroke="currentColor" 
        viewBox="0 0 24 24"
      >
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
      </svg>
      <span class="scale-90 font-medium">刷新</span>
    </button>

    <!-- Footer -->
    <footer class="mt-20 py-8 text-center text-gray-400 text-xs border-t border-gray-100">
      <p>© 2026 数字传承 · 红色德兴 项目组</p>
      <p class="mt-1">Powered by Vue 3 & Flask</p>
    </footer>
    </div>
  </div>
</template>

<style scoped>
.animate-pulse-slow {
  animation: pulse-slow 8s ease-in-out infinite;
}
.animation-delay-2000 {
  animation-delay: 2s;
}

@keyframes pulse-slow {
  0%, 100% { opacity: 0.4; transform: scale(1); }
  50% { opacity: 0.7; transform: scale(1.05); }
}

@keyframes float-up {
  0% { transform: translateY(0) rotate(0deg); opacity: 0; }
  10% { opacity: var(--tw-bg-opacity, 1); }
  90% { opacity: var(--tw-bg-opacity, 1); }
  100% { transform: translateY(-120vh) rotate(180deg); opacity: 0; }
}
.animate-float-up {
  animation: float-up linear infinite;
}
</style>
