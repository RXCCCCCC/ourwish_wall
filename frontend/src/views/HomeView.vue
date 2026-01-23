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
});

const handlePublishWish = () => {
  showForm.value = true;
}

const handleWishSubmitted = (newWish) => {
  // ensure fields for likes/comments
  newWish.likes = newWish.likes ?? 0
  newWish.comments = newWish.comments ?? []
  newWish.created_at = newWish.created_at || new Date().toISOString()
  wishes.value.unshift(newWish)
  
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
</script>

<template>
  <div class="pb-20">
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

    <!-- Footer -->
    <footer class="mt-20 py-8 text-center text-gray-400 text-xs border-t border-gray-100">
      <p>© 2026 数字传承 · 红色德兴 项目组</p>
      <p class="mt-1">Powered by Vue 3 & Flask</p>
    </footer>
  </div>
</template>
