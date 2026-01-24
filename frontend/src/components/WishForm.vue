<script setup>
import { ref } from 'vue';
import { useUserStore } from '@/stores/user';
import { showToast } from 'vant';
import { wishAPI } from '@/api';
import { CATEGORY_COLORS } from '@/constants';

const props = defineProps({
  show: Boolean
});

const emit = defineEmits(['update:show', 'submitted']);
const userStore = useUserStore();

const category = ref('红色传承');
const content = ref('');
const loading = ref(false);

const categories = [
  { text: '红色传承', value: '红色传承' },
  { text: '乡村建设', value: '乡村建设' },
  { text: '产业发展', value: '产业发展' },
  { text: '生态环保', value: '生态环保' },
];

const onSubmit = async () => {
  if (!content.value.trim()) {
    showToast('请输入您的心愿内容');
    return;
  }
  
  loading.value = true;
  
  try {
    // Call real backend API
    const newWish = await wishAPI.createWish({
      user_uid: userStore.userInfo.id,
      nickname: userStore.userInfo.name,
      category: category.value,
      content: content.value
    });
    
    // Ensure fields exist for frontend and attach user color
    newWish.likes = newWish.likes ?? 0;
    newWish.comments = newWish.comments ?? [];
    newWish.color = userStore.userInfo?.color || null;
    
    emit('submitted', newWish);
    content.value = '';
    emit('update:show', false);
    showToast({ type: 'success', message: '发布成功' });
    
  } catch (error) {
    console.error('Failed to create wish:', error);
    showToast({ type: 'fail', message: error.message || '发布失败，请重试' });
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <van-popup 
    :show="show" 
    @update:show="$emit('update:show', $event)" 
    position="bottom" 
    round 
    :style="{ height: '60%' }"
  >
    <div class="p-6">
      <h3 class="text-xl font-serif font-bold mb-6 text-center">发布红色心愿</h3>
      
      <div class="mb-4">
        <label class="text-sm text-gray-500 mb-2 block">心愿类别</label>
        <div class="flex flex-wrap gap-2">
          <button 
            v-for="cat in categories" 
            :key="cat.value"
            @click="category = cat.value"
            class="px-3 py-1.5 rounded-full text-xs transition-colors border"
            :style="category === cat.value 
              ? { backgroundColor: CATEGORY_COLORS[cat.value], borderColor: CATEGORY_COLORS[cat.value], color: '#fff' } 
              : { backgroundColor: '#f3f4f6', borderColor: '#f3f4f6', color: '#4b5563' }"
          >
            {{ cat.text }}
          </button>
        </div>
      </div>
      
      <div class="mb-6">
         <label class="text-sm text-gray-500 mb-2 block">心愿内容</label>
         <textarea 
            v-model="content"
            rows="4"
            class="w-full bg-gray-50 border-0 rounded-lg p-3 text-sm focus:ring-1 focus:ring-red-500 outline-none resize-none"
            placeholder="写下您对德兴红色文化传承的寄语..."
         ></textarea>
      </div>
      
      <button 
        @click="onSubmit"
        :disabled="loading"
        class="w-full bg-brand-dark text-white py-3 rounded-xl font-medium shadow-lg shadow-gray-200 active:scale-95 transition-transform flex items-center justify-center"
      >
        <span v-if="loading" class="mr-2">发布中...</span>
        <span v-else>确认发布</span>
      </button>
    </div>
  </van-popup>
</template>
