<template>
  <div class="flex items-center justify-center min-h-screen p-4">
    <!-- 删除提示消息 -->
    <div v-if="deleteMessage" 
         :class="[
           'fixed top-4 right-4 z-60 px-4 py-3 rounded-lg shadow-lg transition-all duration-300',
           deleteMessage.type === 'success' ? 'bg-green-500 text-white' : 'bg-red-500 text-white'
         ]">
      <div class="flex items-center gap-2">
        <svg v-if="deleteMessage.type === 'success'" class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"></path>
        </svg>
        <svg v-else class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd"></path>
        </svg>
        <span>{{ deleteMessage.text }}</span>
      </div>
    </div>
    
    <div class="w-full max-w-7xl mx-auto">
      <div class="p-8 bg-white/95 backdrop-blur-sm rounded-2xl shadow-2xl fade-in">
        <div class="flex justify-between items-center mb-8">
          <div class="flex items-center space-x-4">
            <h2 class="text-3xl font-bold text-gray-800">我的小说项目</h2>
            <router-link v-if="authStore.user?.is_admin" to="/admin" class="text-sm text-indigo-600 hover:text-indigo-800">管理后台</router-link>
          </div>
          <button
            @click="goBack"
            class="text-gray-500 hover:text-gray-800 transition-colors"
          >
            ← 返回
          </button>
        </div>

        <!-- 加载状态 -->
        <div v-if="isLoadingOverall" class="flex justify-center items-center py-8">
          <div class="loader"></div>
        </div>

        <!-- 错误状态 -->
        <div v-else-if="errorMessage" class="text-red-500 text-center py-8">
          {{ errorMessage }}
          <button
            @click="loadProjects"
            class="block mt-4 mx-auto px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600 transition-all duration-300 transform hover:scale-105"
          >
            重试
          </button>
        </div>

        <!-- 项目列表 -->
        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <!-- 空状态 -->
          <div v-if="allProjects.length === 0" class="col-span-full text-center py-8">
            <p class="text-gray-500 mb-4">还没有项目，快去开启灵感模式创建一个吧！</p>
            <button
              @click="goToInspiration"
              class="px-6 py-3 bg-indigo-500 text-white rounded-lg hover:bg-indigo-600 transition-all duration-300 transform hover:scale-105"
            >
              开始创作
            </button>
          </div>

          <!-- 项目卡片 -->
          <ProjectCard
            v-for="project in allProjects"
            :key="project.id"
            :project="project"
            @click="enterProject(project)"
            @detail="viewProjectDetail"
            @continue="enterProject"
            @delete="handleDeleteProject"
          />

          <!-- 创建新项目卡片 -->
          <div
            @click="goToInspiration"
            class="flex items-center justify-center p-5 bg-transparent border-2 border-dashed border-gray-300 rounded-xl hover:bg-gray-50 hover:border-indigo-400 transition-colors duration-300 cursor-pointer group min-h-[180px]"
          >
            <div class="text-center text-gray-500 group-hover:text-indigo-500 transition-colors">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="mx-auto h-8 w-8 mb-2"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                stroke-width="2"
              >
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4" />
              </svg>
              <span class="font-semibold">创建新项目</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 删除确认对话框 -->
    <div v-if="showDeleteDialog" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
      <div class="bg-white rounded-2xl shadow-2xl max-w-md w-full">
        <div class="p-6">
          <div class="flex items-center gap-3 mb-4">
            <div class="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center">
              <svg class="w-6 h-6 text-red-600" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z" clip-rule="evenodd"></path>
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8 7a1 1 0 012 0v4a1 1 0 11-2 0V7zM12 7a1 1 0 012 0v4a1 1 0 11-2 0V7z" clip-rule="evenodd"></path>
              </svg>
            </div>
            <div>
              <h3 class="text-lg font-semibold text-gray-900">确认删除</h3>
              <p class="text-sm text-gray-600">此操作无法撤销</p>
            </div>
          </div>
          
          <p class="text-gray-700 mb-6">
            确定要删除项目 "{{ projectToDelete?.title }}" 吗？所有相关数据将被永久删除。
          </p>
          
          <div class="flex gap-3 justify-end">
            <button
              @click="cancelDelete"
              class="px-4 py-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors"
            >
              取消
            </button>
            <button
              @click="confirmDelete"
              :disabled="isDeleting"
              class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              <svg v-if="isDeleting" class="w-4 h-4 animate-spin" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clip-rule="evenodd"></path>
              </svg>
              {{ isDeleting ? '删除中...' : '确认删除' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useNovelStore } from '@/stores/novel'
import { usePoemStore } from '@/stores/poem'
import { useAuthStore } from '@/stores/auth'
import { globalAlert } from '@/composables/useAlert'
import ProjectCard from '@/components/ProjectCard.vue'
import type { NovelProjectSummary } from '@/api/novel'

const router = useRouter()
const novelStore = useNovelStore()
const poemStore = usePoemStore()
const authStore = useAuthStore()

// 删除相关状态
const showDeleteDialog = ref(false)
const projectToDelete = ref<NovelProjectSummary | null>(null)
const isDeleting = ref(false)
const deleteMessage = ref<{type: 'success' | 'error', text: string} | null>(null)
const allProjects = computed(() => {
  const merged = [...novelStore.projects, ...poemStore.projects]
  return merged.sort((a, b) => {
    const da = new Date(a.last_edited).getTime()
    const db = new Date(b.last_edited).getTime()
    return db - da
  })
})

const isLoadingOverall = computed(() => novelStore.isLoading || poemStore.isLoading)
const errorMessage = computed(() => novelStore.error || poemStore.error)

const goBack = () => {
  router.push('/')
}

const goToInspiration = () => {
  router.push('/inspiration')
}

const viewProjectDetail = (projectId: string) => {
  const project = allProjects.value.find(p => p.id === projectId)
  if (project?.project_type === 'poem') {
    // 跳转到诗词详情页
    router.push(`/poem/${projectId}`)
    return
  }
  router.push(`/detail/${projectId}`)
}

const enterProject = (project: NovelProjectSummary) => {
  const projectType = project.project_type || 'novel'
  const shouldUseInspiration =
    projectType === 'poem' ||
    project.title === '未命名灵感'

  if (shouldUseInspiration) {
    router.push(`/inspiration?project_id=${project.id}&type=${projectType}`)
    return
  }

  router.push(`/novel/${project.id}`)
}

const loadProjects = async () => {
  await Promise.all([
    novelStore.loadProjects(),
    poemStore.loadProjects()
  ])
}

// 删除相关方法
const handleDeleteProject = (projectId: string) => {
  const project = allProjects.value.find(p => p.id === projectId)
  if (!project) return

  projectToDelete.value = project
  showDeleteDialog.value = true
}

const cancelDelete = () => {
  showDeleteDialog.value = false
  projectToDelete.value = null
}

const confirmDelete = async () => {
  if (!projectToDelete.value) return
  
  isDeleting.value = true
  try {
    const targetStore = projectToDelete.value.project_type === 'poem' ? poemStore : novelStore
    await targetStore.deleteProjects([projectToDelete.value.id])
    deleteMessage.value = { type: 'success', text: `项目 "${projectToDelete.value.title}" 已成功删除` }
    showDeleteDialog.value = false
    projectToDelete.value = null
    
    // 3秒后清除消息
    setTimeout(() => {
      deleteMessage.value = null
    }, 3000)
  } catch (error) {
    console.error('删除项目失败:', error)
    deleteMessage.value = { type: 'error', text: '删除项目失败，请重试' }
    
    // 3秒后清除消息
    setTimeout(() => {
      deleteMessage.value = null
    }, 3000)
  } finally {
    isDeleting.value = false
  }
}

onMounted(() => {
  loadProjects()
})
</script>
