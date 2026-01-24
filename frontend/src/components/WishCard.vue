<script setup>
import { ref, computed, watch } from 'vue'
import { useUserStore } from '@/stores/user'
import { wishAPI } from '@/api'
import { showConfirmDialog } from 'vant'
import { CATEGORY_COLORS, CATEGORY_DEFAULT_COLOR } from '@/constants'

const props = defineProps({
	wish: {
		type: Object,
		required: true
	},
	index: {
		type: Number,
		default: 0
	}
})

const emit = defineEmits(['delete-wish', 'update-wish'])

const userStore = useUserStore()

const categoryColor = computed(() => CATEGORY_COLORS[props.wish.category] || CATEGORY_DEFAULT_COLOR)

function formatChineseDate(d) {
	if (!d) return ''
	if (typeof d === 'string' && d.includes('年')) return d
	const date = d instanceof Date ? d : new Date(d)
	if (isNaN(date.getTime())) return d
	const y = date.getFullYear()
	const m = date.getMonth() + 1
	const day = date.getDate()
	return `${y}年${m}月${day}日`
}

function nameToColor(name) {
	if (!name) return 'hsl(200 20% 50%)'
	let hash = 0
	for (let i = 0; i < name.length; i++) {
		hash = name.charCodeAt(i) + ((hash << 5) - hash)
	}
	const hue = Math.abs(hash) % 360
	return `hsl(${hue} 60% 45%)`
}

const likedIds = ref(JSON.parse(localStorage.getItem('liked_wishes') || '[]'))
const likes = ref(props.wish.likes ?? 0)
// Prefer backend user_liked state over local storage
const liked = ref(props.wish.user_liked ?? likedIds.value.includes(props.wish.id))

// Watch for prop updates to sync state (e.g. after refresh or AI update)
watch(() => props.wish, (newVal) => {
	if (!newVal) return
	
	// Sync likes count
	likes.value = newVal.likes ?? 0
	
	// Sync liked status - trust backend if explicit (boolean), else fallback
	if (typeof newVal.user_liked === 'boolean') {
		liked.value = newVal.user_liked
	} else {
		liked.value = likedIds.value.includes(newVal.id)
	}
	
	// Sync comments
	if (newVal.comments) {
		comments.value = [...newVal.comments]
		// Rebuild comment likes map
		commentLikesMap.value = new Map(
			comments.value.map(c => [c.id, c.likes ?? 0])
		)
	}
}, { deep: true })

async function toggleLike() {
	const id = props.wish.id
	if (!id) return
	
	// Optimistic update
	const wasLiked = liked.value
	const oldLikes = likes.value
	const oldLikedIds = [...likedIds.value]
	
	if (wasLiked) {
		liked.value = false
		likedIds.value = likedIds.value.filter(x => x !== id)
		likes.value = Math.max(0, likes.value - 1)
	} else {
		liked.value = true
		likedIds.value.push(id)
		likes.value += 1
	}
	localStorage.setItem('liked_wishes', JSON.stringify(likedIds.value))
	
	// Call backend API
	try {
		const action = wasLiked ? 'unlike' : 'like'
		const userUid = userStore.userInfo?.id
		await wishAPI.toggleLike(id, userUid, action)
	} catch (error) {
		console.error('Failed to toggle like:', error)
		// Check if error is "already liked" - sync state instead of rollback
		if (error.message && error.message.includes('已经点赞')) {
			// Sync local state to match backend
			liked.value = true
			if (!likedIds.value.includes(id)) {
				likedIds.value.push(id)
				localStorage.setItem('liked_wishes', JSON.stringify(likedIds.value))
			}
		} else if (error.message && error.message.includes('还未点赞')) {
			// Sync local state to match backend
			liked.value = false
			likedIds.value = likedIds.value.filter(x => x !== id)
			localStorage.setItem('liked_wishes', JSON.stringify(likedIds.value))
		} else {
			// Other errors: rollback
			liked.value = wasLiked
			likedIds.value = oldLikedIds
			likes.value = oldLikes
			localStorage.setItem('liked_wishes', JSON.stringify(oldLikedIds))
		}
	}
}

const comments = ref(props.wish.comments ? [...props.wish.comments] : [])
const newComment = ref('')

// Comment likes state
const commentLikedIds = ref(JSON.parse(localStorage.getItem('liked_comments') || '[]'))
const commentLikesMap = ref(new Map(
	comments.value.map(c => [c.id, c.likes ?? 0])
))

function isCommentLiked(commentId) {
	return commentLikesMap.value.has(commentId) && 
		(comments.value.find(c => c.id === commentId)?.user_liked ?? commentLikedIds.value.includes(commentId))
}

function getCommentLikes(commentId) {
	return commentLikesMap.value.get(commentId) ?? 0
}

async function toggleCommentLike(comment) {
	const cid = comment.id
	if (!cid) return
	
	// Optimistic update
	const wasLiked = isCommentLiked(cid)
	const oldLikes = commentLikesMap.value.get(cid) ?? 0
	const oldLikedIds = [...commentLikedIds.value]
	
	if (wasLiked) {
		commentLikedIds.value = commentLikedIds.value.filter(x => x !== cid)
		commentLikesMap.value.set(cid, Math.max(0, oldLikes - 1))
	} else {
		commentLikedIds.value.push(cid)
		commentLikesMap.value.set(cid, oldLikes + 1)
	}
	localStorage.setItem('liked_comments', JSON.stringify(commentLikedIds.value))
	
	// Update comment user_liked in comments array
	const idx = comments.value.findIndex(c => c.id === cid)
	if (idx !== -1) {
		comments.value[idx].user_liked = !wasLiked
		comments.value[idx].likes = commentLikesMap.value.get(cid)
	}
	
	// Call backend API
	try {
		const action = wasLiked ? 'unlike' : 'like'
		const userUid = userStore.userInfo?.id
		await wishAPI.toggleCommentLike(props.wish.id, cid, userUid, action)
	} catch (error) {
		console.error('Failed to toggle comment like:', error)
		// Check if error is "already liked" - sync state instead of rollback
		if (error.message && error.message.includes('已经点赞')) {
			if (!commentLikedIds.value.includes(cid)) {
				commentLikedIds.value.push(cid)
				localStorage.setItem('liked_comments', JSON.stringify(commentLikedIds.value))
			}
			if (idx !== -1) comments.value[idx].user_liked = true
		} else if (error.message && error.message.includes('还未点赞')) {
			commentLikedIds.value = commentLikedIds.value.filter(x => x !== cid)
			localStorage.setItem('liked_comments', JSON.stringify(commentLikedIds.value))
			if (idx !== -1) comments.value[idx].user_liked = false
		} else {
			// Other errors: rollback
			commentLikedIds.value = oldLikedIds
			commentLikesMap.value.set(cid, oldLikes)
			localStorage.setItem('liked_comments', JSON.stringify(oldLikedIds))
			if (idx !== -1) {
				comments.value[idx].user_liked = wasLiked
				comments.value[idx].likes = oldLikes
			}
		}
	}
}

async function addComment() {
	const content = newComment.value && newComment.value.trim()
	if (!content) return
	
	// Optimistic update (no avatar, use nickname only)
	const tempComment = {
		id: Date.now(),
		content,
		nickname: userStore.userInfo?.name || '匿名',
		user_uid: userStore.userInfo?.id || null,
		color: userStore.userInfo?.color || nameToColor(userStore.userInfo?.name),
		likes: 0,
		user_liked: false,
		created_at: new Date().toISOString()
	}
	comments.value.push(tempComment)
	commentLikesMap.value.set(tempComment.id, 0)
	newComment.value = ''
	
	// Call backend API
	try {
		const newCommentData = await wishAPI.createComment(props.wish.id, {
			user_uid: userStore.userInfo?.id,
			nickname: userStore.userInfo?.name || '匿名',
			content
		})
		// Replace temp comment with real one from backend
		const idx = comments.value.findIndex(c => c.id === tempComment.id)
		if (idx !== -1) {
			comments.value[idx] = newCommentData
			// Initialize comment likes map for new comment
			if (newCommentData.likes !== undefined) {
				commentLikesMap.value.set(newCommentData.id, newCommentData.likes)
			}
		}
		const updated = { ...props.wish, comments: comments.value }
		emit('update-wish', updated)
	} catch (error) {
		console.error('Failed to add comment:', error)
		// Remove temp comment on error
		comments.value = comments.value.filter(c => c.id !== tempComment.id)
	}
}

async function deleteComment(cid) {
	const idx = comments.value.findIndex(c => c.id === cid)
	if (idx === -1) return
	const comment = comments.value[idx]
	if (comment.user_uid && userStore.userInfo && comment.user_uid !== userStore.userInfo.id) {
		return
	}

	// Confirm with styled dialog
	// Use Vant Dialog if available, otherwise fallback to native confirm
	if (typeof showConfirmDialog === 'function') {
		try {
			await showConfirmDialog({
				title: '删除评论',
				message: '确定删除该评论？此操作无法撤销。',
				confirmButtonText: '删除',
				cancelButtonText: '取消',
				confirmButtonColor: '#ef4444', 
			})
		} catch (e) {
			return
		}
	} else {
		if (!window.confirm('确定删除该评论？此操作无法撤销。')) return
	}

	// Optimistic update
	const deletedComment = comments.value[idx]
	comments.value.splice(idx, 1)
	emit('update-wish', { ...props.wish, comments: comments.value })
	
	// Call backend API
	try {
		await wishAPI.deleteComment(props.wish.id, cid, userStore.userInfo?.id)
	} catch (error) {
		console.error('Failed to delete comment:', error)
		// Rollback on error
		comments.value.splice(idx, 0, deletedComment)
		emit('update-wish', { ...props.wish, comments: comments.value })
	}
}

function canDeleteWish() {
	// Allow deletion based on stable user id (user_uid), not mutable nickname
	return userStore.userInfo && props.wish.user_uid === userStore.userInfo.id
}

async function handleDeleteWish() {
	if (!canDeleteWish()) return
	// Use Vant Dialog if available, otherwise fallback to native confirm
	if (typeof showConfirmDialog === 'function') {
		try {
			await showConfirmDialog({
				title: '删除心愿',
				message: '确定删除此心愿？此操作无法撤销。',
				confirmButtonText: '删除',
				cancelButtonText: '取消',
				confirmButtonColor: '#ef4444', 
			})
		} catch (e) {
			return
		}
	} else {
		if (!window.confirm('确定删除此心愿？此操作无法撤销。')) return
	}
	
	// Optimistically emit delete
	emit('delete-wish', props.wish.id)
	
	// Call backend API
	try {
		await wishAPI.deleteWish(props.wish.id, userStore.userInfo?.id)
	} catch (error) {
		console.error('Failed to delete wish:', error)
		// Note: rollback would require parent to re-add the wish
		// For simplicity, we keep the optimistic delete
	}
}
</script>

<template>
	<div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden hover:shadow-md transition-shadow duration-300">
		<div class="flex h-full">
			<div class="w-1 flex-shrink-0" :style="{ backgroundColor: categoryColor }"></div>

			<div class="p-4 md:p-6 flex-1 flex flex-col">
				<div class="flex justify-between items-start mb-3 md:mb-4">
					<div class="flex items-center gap-2">
						<span class="w-2 h-2 rounded-full" :style="{ backgroundColor: categoryColor }"></span>
						<span class="text-xs text-gray-400">{{ formatChineseDate(props.wish.created_at) || '刚刚' }}</span>
					</div>
					<div class="text-gray-200 flex items-center gap-2">
						<div class="flex items-center gap-2" :style="{ color: categoryColor }">
							<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-6 h-6 opacity-30">
								<path d="M4 3v18l6-3 6 3V3l-6 3-6-3z" />
							</svg>
							<span class="text-xs">{{ props.wish.category }}</span>
						</div>
					</div>
				</div>

				<p class="mb-6 leading-relaxed wish-font">
					{{ props.wish.content }}
				</p>

				<div class="bg-gray-50 rounded-lg p-4 border border-gray-100">
					<div class="flex items-center gap-1.5 mb-2 text-red-500 font-bold text-xs">
						<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-3 h-3">
							<path fill-rule="evenodd" d="M14.615 1.595a.75.75 0 01.359.852L12.982 9.75h7.268a.75.75 0 01.548 1.262l-10.5 11.25a.75.75 0 01-1.272-.71l1.992-7.302H3.75a.75.75 0 01-.548-1.262l10.5-11.25a.75.75 0 01.913-.143z" clip-rule="evenodd" />
						</svg>
						红色回响
					</div>
					<div class="text-xs text-gray-500 leading-relaxed">
						<div v-if="props.wish.ai_response === aiPlaceholder" class="flex items-center gap-2">
							<svg class="w-4 h-4 text-gray-400 animate-spin" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
								<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
								<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"></path>
							</svg>
							<span>{{ props.wish.ai_response }}</span>
						</div>
						<div v-else>
							{{ props.wish.ai_response || '您的心愿已收录，智能助手正在生成回复...' }}
						</div>
					</div>
				</div>

				<div class="mt-4">
					<div v-for="c in comments" :key="c.id" class="flex items-start gap-3 py-3 border-b last:border-b-0">
							<div :style="{ backgroundColor: (c.user_uid === userStore.userInfo?.id ? userStore.userInfo?.color : (c.color || nameToColor(c.nickname))) }" class="w-8 h-8 rounded-full text-white flex-shrink-0 flex items-center justify-center text-xs">
								{{ (c.user_uid === userStore.userInfo?.id ? userStore.userInfo.name : c.nickname)?.charAt(0) }}
								</div>
						<div class="flex-1">
							<div class="flex items-center justify-between">
								<div class="text-sm font-medium text-gray-700">{{ c.user_uid === userStore.userInfo?.id ? userStore.userInfo.name : c.nickname }}</div>
								<div class="text-[11px] text-gray-400">{{ formatChineseDate(c.created_at) }}</div>
							</div>
							<div class="text-sm text-gray-600 mt-1">{{ c.content }}</div>
							<div class="mt-2 flex items-center justify-between">
								<button @click="toggleCommentLike(c)" class="flex items-center gap-1 text-xs" :class="isCommentLiked(c.id) ? 'text-red-500' : 'text-gray-400'">
									<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-3 h-3">
										<path d="M12 21s-6.716-4.95-9.07-8.06C-0.02 8.62 3.4 4 7.5 4c2.08 0 3.54 1.05 4.5 2.1C12.96 5.05 14.42 4 16.5 4 20.6 4 24.02 8.62 21.07 12.94 18.716 16.05 12 21 12 21z" />
									</svg>
									<span>{{ getCommentLikes(c.id) }}</span>
								</button>
								<button v-if="c.user_uid && userStore.userInfo && c.user_uid === userStore.userInfo.id" @click="deleteComment(c.id)" class="text-xs text-red-500">删除</button>
							</div>
						</div>
					</div>
				</div>

				<div class="mt-3 flex gap-2 items-start">
					<textarea v-model="newComment" rows="2" class="flex-1 bg-gray-50 border-0 rounded-md p-2 text-sm resize-none" placeholder="发表评论..."></textarea>
					<button @click="addComment" class="px-3 py-2 bg-brand-dark text-white rounded-md text-sm">发布</button>
				</div>

				<div class="flex items-center justify-between mt-4 border-t border-gray-50 pt-3">
							<div class="flex items-center gap-2">
								<div :style="{ backgroundColor: (props.wish.user_uid === userStore.userInfo?.id ? userStore.userInfo?.color : (props.wish.color || nameToColor(props.wish.nickname))) }" class="w-6 h-6 rounded-full text-white flex items-center justify-center text-[10px]">
									<span>{{ (props.wish.user_uid === userStore.userInfo?.id ? userStore.userInfo.name : props.wish.nickname)?.charAt(0) }}</span>
								</div>
						<span class="text-xs text-gray-500 font-medium">{{ props.wish.user_uid === userStore.userInfo?.id ? userStore.userInfo.name : props.wish.nickname }}</span>
					</div>

					<div class="flex items-center gap-3">
						<button @click="toggleLike" class="flex items-center gap-1 text-sm" :class="liked ? 'text-red-500' : 'text-gray-400'">
							<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-4 h-4">
								<path d="M12 21s-6.716-4.95-9.07-8.06C-0.02 8.62 3.4 4 7.5 4c2.08 0 3.54 1.05 4.5 2.1C12.96 5.05 14.42 4 16.5 4 20.6 4 24.02 8.62 21.07 12.94 18.716 16.05 12 21 12 21z" />
							</svg>
							<span class="text-xs">{{ likes }}</span>
						</button>

						<div v-if="canDeleteWish()">
							<button @click="handleDeleteWish" class="text-xs text-gray-400">删除心愿</button>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>


