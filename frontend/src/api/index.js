import axios from 'axios'

// API 基础配置
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'

// 创建 axios 实例
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
apiClient.interceptors.request.use(
  config => {
    // 可以在这里添加 token 等
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
apiClient.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    // 统一错误处理
    const message = error.response?.data?.error || error.message || '请求失败'
    console.error('API Error:', message)
    return Promise.reject(new Error(message))
  }
)

// API 方法
export const wishAPI = {
  // 获取心愿列表
  getWishes(params = {}) {
    return apiClient.get('/api/wishes', { params })
  },

  // 发布心愿
  createWish(data) {
    return apiClient.post('/api/wishes', data)
  },

  // 删除心愿
  deleteWish(wishId, userUid) {
    return apiClient.delete(`/api/wishes/${wishId}`, {
      data: { user_uid: userUid }
    })
  },

  // 点赞/取消点赞
  toggleLike(wishId, userUid, action = 'like') {
    return apiClient.post(`/api/wishes/${wishId}/like`, {
      user_uid: userUid,
      action
    })
  },

  // 获取评论列表
  getComments(wishId) {
    return apiClient.get(`/api/wishes/${wishId}/comments`)
  },

  // 添加评论
  createComment(wishId, data) {
    return apiClient.post(`/api/wishes/${wishId}/comments`, data)
  },

  // 删除评论
  deleteComment(wishId, commentId, userUid) {
    return apiClient.delete(`/api/wishes/${wishId}/comments/${commentId}`, {
      data: { user_uid: userUid }
    })
  },

  // 评论点赞/取消点赞
  toggleCommentLike(wishId, commentId, userUid, action = 'like') {
    return apiClient.post(`/api/wishes/${wishId}/comments/${commentId}/like`, {
      user_uid: userUid,
      action
    })
  },

  // 获取统计数据
  getStats() {
    return apiClient.get('/api/stats')
  }
}

export default apiClient
