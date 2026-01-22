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

const wishes = ref([]);

// Fallback data in case backend is unavailable
const fallbackWishes = [
  {
    id: 1,
    content: "愿德兴的红色故事代代相传，家乡越来越美！",
    category: "红色传承",
    nickname: "张建国",
    created_at: new Date('2026-01-22').toISOString(),
    ai_response: "薪火相传，初心不忘。愿红色基因在数字时代绽放新的光芒。",
    likes: 88,
    comments: []
  },
  {
    id: 2,
    content: "希望能用VR技术复原当年的革命旧址，让年轻人身临其境。",
    category: "产业发展",
    nickname: "文旅探索者",
    created_at: "2026年1月22日",
    ai_response: "科技赋能历史，让岁月的回响更加清晰。您的创意将连接过去与未来。",
    likes: 45,
    comments: []
  },
  {
    id: 3,
    content: "期待看到更多关于红军医院的数字地图，让那段历史鲜活起来。",
    category: "红色传承",
    nickname: "李小红",
    created_at: new Date('2026-01-21').toISOString(),
    ai_response: "数字地图将成为时光的索引，指引我们探寻先辈的足迹。",
    likes: 24,
    comments: []
  },
  {
    id: 4,
    content: "希望不仅是旅游，还能通过APP学到更多中医药与红色结合的知识。",
    category: "产业发展",
    nickname: "养生达人",
    created_at: new Date('2026-01-21').toISOString(),
    ai_response: "红色康养融合创新，让传统智慧与革命精神共同守护健康。",
    likes: 12,
    comments: []
  }
];

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
      // Use fallback data if no wishes from backend
      wishes.value = fallbackWishes;
    }
  } catch (error) {
    console.error('Failed to load wishes from backend:', error);
    showToast('加载心愿失败，显示示例数据');
    wishes.value = fallbackWishes;
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
  if (idx !== -1) wishes.value.splice(idx, 1)
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
      <ChartsBoard />
      
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
