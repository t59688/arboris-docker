<template>
  <div class="min-h-screen bg-gradient-to-br from-emerald-50 via-teal-50/30 to-cyan-50/40 p-4 sm:p-6 lg:p-8">
    <!-- Header -->
    <header class="max-w-5xl mx-auto mb-6">
      <div class="bg-white/90 backdrop-blur-lg rounded-2xl shadow-lg border border-emerald-100 p-4 sm:p-6">
        <div class="flex items-center justify-between">
          <!-- Title & Meta -->
          <div class="flex-1 min-w-0 mr-4">
            <div class="flex items-center gap-3 mb-2">
              <div class="w-3 h-3 rounded-full bg-gradient-to-r from-emerald-500 to-teal-500 animate-pulse"></div>
              <h1 class="text-2xl sm:text-3xl lg:text-4xl font-bold text-gray-800 truncate">
                {{ project?.title || '未命名诗作' }}
              </h1>
            </div>
            <div class="flex flex-wrap items-center gap-3 text-sm text-gray-600">
              <span v-if="project?.blueprint?.genre" class="flex items-center gap-1">
                <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9 4.804A7.968 7.968 0 005.5 4c-1.255 0-2.443.29-3.5.804v10A7.969 7.969 0 015.5 14c1.669 0 3.218.51 4.5 1.385A7.962 7.962 0 0114.5 14c1.255 0 2.443.29 3.5.804v-10A7.968 7.968 0 0014.5 4c-1.255 0-2.443.29-3.5.804V12a1 1 0 11-2 0V4.804z"></path>
                </svg>
                {{ project.blueprint.genre }}
              </span>
              <span v-if="project?.updated_at" class="flex items-center gap-1">
                <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clip-rule="evenodd"></path>
                </svg>
                {{ formatDate(project.updated_at) }}
              </span>
            </div>
          </div>

          <!-- Actions -->
          <div class="flex items-center gap-2 flex-shrink-0">
            <button
              @click="goBack"
              class="px-3 py-2 sm:px-4 text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 border border-gray-200 rounded-lg transition-all duration-200 hover:shadow-md"
            >
              <span class="hidden sm:inline">返回</span>
              <span class="sm:hidden">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path>
                </svg>
              </span>
            </button>
            <button
              @click="editBlueprint"
              class="px-3 py-2 sm:px-4 text-sm font-medium text-white bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 rounded-lg transition-all duration-200 shadow-md hover:shadow-lg"
            >
              <span class="hidden sm:inline">编辑蓝图</span>
              <span class="sm:hidden">
                <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z"></path>
                </svg>
              </span>
            </button>
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-5xl mx-auto">
      <!-- Loading State -->
      <div v-if="isLoading" class="bg-white/90 backdrop-blur-lg rounded-2xl shadow-lg border border-emerald-100 p-12">
        <div class="flex flex-col items-center justify-center">
          <div class="relative">
            <div class="w-16 h-16 border-4 border-emerald-100 rounded-full"></div>
            <div class="absolute top-0 left-0 w-16 h-16 border-4 border-emerald-600 border-t-transparent rounded-full animate-spin"></div>
          </div>
          <p class="mt-4 text-gray-600">加载中...</p>
        </div>
      </div>

      <!-- Error State -->
      <div v-else-if="errorMessage" class="bg-white/90 backdrop-blur-lg rounded-2xl shadow-lg border border-red-100 p-12">
        <div class="flex flex-col items-center justify-center space-y-4">
          <div class="w-16 h-16 bg-red-50 rounded-full flex items-center justify-center">
            <svg class="w-8 h-8 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <p class="text-gray-700 text-center">{{ errorMessage }}</p>
          <button
            @click="loadProject"
            class="px-6 py-2.5 text-sm font-medium text-white bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 rounded-lg shadow-md hover:shadow-lg transition-all duration-200"
          >
            重试
          </button>
        </div>
      </div>

      <!-- No Blueprint State -->
      <div v-else-if="!project?.blueprint || Object.keys(project.blueprint).length === 0" class="bg-white/90 backdrop-blur-lg rounded-2xl shadow-lg border border-yellow-100 p-12">
        <div class="flex flex-col items-center justify-center space-y-4">
          <div class="w-16 h-16 bg-yellow-50 rounded-full flex items-center justify-center">
            <svg class="w-8 h-8 text-yellow-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <p class="text-gray-700 text-center">该诗词项目还没有生成蓝图</p>
          <button
            @click="createBlueprint"
            class="px-6 py-2.5 text-sm font-medium text-white bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 rounded-lg shadow-md hover:shadow-lg transition-all duration-200"
          >
            开始创作
          </button>
        </div>
      </div>

      <!-- Blueprint Display -->
      <div v-else class="space-y-6">
        <!-- 蓝图卡片 -->
        <div class="bg-white/90 backdrop-blur-lg rounded-2xl shadow-lg border border-emerald-100 overflow-hidden">
          <PoemBlueprintDisplay
            :blueprint="project.blueprint"
            :show-actions="false"
            class="blueprint-display-embedded"
          />
          
          <!-- Action Bar -->
          <div class="border-t border-emerald-100 bg-emerald-50/50 p-6">
            <div class="flex justify-center gap-4">
              <button
                @click="startGeneration"
                :disabled="isGenerating"
                class="px-6 py-3 text-sm font-medium text-white bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 rounded-lg transition-all duration-200 shadow-md hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                <svg v-if="!isGenerating" class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z"></path>
                </svg>
                <svg v-else class="w-5 h-5 animate-spin" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clip-rule="evenodd"></path>
                </svg>
                {{ isGenerating ? '生成中...' : '开始创作' }}
              </button>
              <button
                @click="editBlueprint"
                class="px-6 py-3 text-sm font-medium text-emerald-700 bg-white hover:bg-emerald-50 border border-emerald-200 rounded-lg transition-all duration-200 hover:shadow-md flex items-center gap-2"
              >
                <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z"></path>
                </svg>
                编辑蓝图
              </button>
              <button
                @click="goBack"
                class="px-6 py-3 text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 border border-gray-200 rounded-lg transition-all duration-200 hover:shadow-md flex items-center gap-2"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path>
                </svg>
                返回工作台
              </button>
            </div>
          </div>
        </div>

        <!-- 生成的诗词版本 -->
        <div v-if="poemVersions.length > 0" class="bg-white/90 backdrop-blur-lg rounded-2xl shadow-lg border border-emerald-100 p-6 sm:p-8">
          <div class="mb-6">
            <h2 class="text-2xl font-bold text-gray-800 mb-2">生成的诗词作品</h2>
            <p class="text-gray-600">AI 为您创作了 {{ poemVersions.length }} 个不同风格的版本，请选择您最满意的一个</p>
          </div>

          <div class="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            <div
              v-for="version in poemVersions"
              :key="version.version_number"
              class="group relative bg-gradient-to-br from-emerald-50 to-teal-50 rounded-xl border-2 border-emerald-200 p-6 hover:shadow-lg transition-all duration-300 cursor-pointer hover:border-emerald-400"
            >
              <!-- 版本标识 -->
              <div class="absolute top-4 right-4 w-8 h-8 bg-emerald-500 text-white rounded-full flex items-center justify-center font-bold text-sm">
                {{ version.version_number }}
              </div>

              <!-- 诗题 -->
              <h3 class="text-xl font-bold text-emerald-900 mb-4 pr-10">{{ version.title }}</h3>

              <!-- 诗词内容 -->
              <div class="mb-4 text-gray-800 leading-relaxed whitespace-pre-line font-serif text-lg">
                {{ version.content }}
              </div>

              <!-- 创作说明 -->
              <div class="pt-4 border-t border-emerald-200">
                <p class="text-sm text-gray-600 italic">{{ version.notes }}</p>
              </div>

              <!-- 选择按钮 -->
              <button
                class="mt-4 w-full py-2 px-4 text-sm font-medium text-emerald-700 bg-white hover:bg-emerald-50 border border-emerald-300 rounded-lg transition-all duration-200"
              >
                选择此版本
              </button>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { usePoemStore } from '@/stores/poem'
import { globalAlert } from '@/composables/useAlert'
import { PoemAPI } from '@/api/poem'
import PoemBlueprintDisplay from '@/components/PoemBlueprintDisplay.vue'

interface PoemVersion {
  version_number: number
  content: string
  title: string
  notes: string
}

const router = useRouter()
const route = useRoute()
const poemStore = usePoemStore()

const projectId = route.params.id as string
const project = ref(poemStore.currentProject)
const isLoading = ref(false)
const errorMessage = ref('')
const isGenerating = ref(false)
const poemVersions = ref<PoemVersion[]>([])

const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffMins < 1) return '刚刚'
  if (diffMins < 60) return `${diffMins}分钟前`
  if (diffHours < 24) return `${diffHours}小时前`
  if (diffDays < 7) return `${diffDays}天前`
  return date.toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' })
}

const loadProject = async () => {
  if (!projectId) {
    errorMessage.value = '项目ID无效'
    return
  }

  isLoading.value = true
  errorMessage.value = ''

  try {
    await poemStore.loadProject(projectId)
    project.value = poemStore.currentProject
    
    if (!project.value) {
      errorMessage.value = '项目不存在'
    }
  } catch (error) {
    console.error('加载项目失败:', error)
    errorMessage.value = error instanceof Error ? error.message : '加载失败，请重试'
  } finally {
    isLoading.value = false
  }
}

const goBack = () => {
  router.push('/workspace')
}

const editBlueprint = async () => {
  if (!project.value) return

  const confirmed = await globalAlert.showConfirm(
    '编辑蓝图会重新进入灵感模式。\n\n当前蓝图内容将作为初始状态，您可以继续对话来修改。',
    '确认编辑'
  )

  if (confirmed) {
    router.push(`/inspiration?project_id=${projectId}&type=poem`)
  }
}

const createBlueprint = () => {
  router.push(`/inspiration?project_id=${projectId}&type=poem`)
}

const startGeneration = async () => {
  if (!project.value) return

  isGenerating.value = true
  poemVersions.value = []

  try {
    const result = await PoemAPI.generatePoemContent(projectId)
    
    if (result.status === 'success' && result.versions) {
      poemVersions.value = result.versions
      globalAlert.showAlert(
        `成功生成 ${result.versions.length} 个诗词版本！`,
        'success',
        '创作完成'
      )
    } else {
      throw new Error('生成结果格式错误')
    }
  } catch (error) {
    console.error('生成诗词失败:', error)
    globalAlert.showAlert(
      error instanceof Error ? error.message : '生成诗词失败，请重试',
      'error',
      '生成失败'
    )
  } finally {
    isGenerating.value = false
  }
}

onMounted(() => {
  loadProject()
})
</script>

<style scoped>
/* 嵌入式蓝图显示样式调整 */
.blueprint-display-embedded {
  padding: 0;
  background: transparent;
  box-shadow: none;
  border-radius: 0;
}

.blueprint-display-embedded :deep(.fade-in) {
  animation: none;
}

/* 移除内部的 padding，因为外层卡片已经有了 */
.blueprint-display-embedded :deep(> div) {
  padding: 2rem 2rem 0 2rem;
}

@media (max-width: 640px) {
  .blueprint-display-embedded :deep(> div) {
    padding: 1.5rem 1.5rem 0 1.5rem;
  }
}
</style>

