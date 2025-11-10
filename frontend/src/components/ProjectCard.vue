<template>
  <div
    class="group bg-white rounded-xl border border-gray-200 p-5 hover:shadow-xl hover:-translate-y-1.5 transition-all duration-300 flex flex-col justify-between"
  >
    <div>
      <div class="flex items-center gap-4 mb-4">
        <div :class="themeClasses.bg" class="w-12 h-12 rounded-lg flex items-center justify-center">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            :class="themeClasses.text"
            class="h-6 w-6"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            stroke-width="2"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
            />
          </svg>
        </div>
        <div class="flex-1 cursor-pointer" @click="$emit('detail', project.id)">
          <h3 class="font-bold text-lg text-gray-900 hover:text-indigo-600 transition-colors">{{ project.title }}</h3>
          <p class="text-sm text-gray-500">
            {{ project.genre || '未知类型' }} | {{ getStatusText }}
          </p>
          <p class="text-xs text-gray-400 mt-1">
            最后编辑: {{ project.last_edited }}
          </p>
        </div>
      </div>

      <div class="mb-4">
        <div class="flex justify-between text-sm text-gray-600 mb-1">
          <span>完成进度</span>
          <span>{{ progress }}%</span>
        </div>
        <div class="w-full bg-gray-200 rounded-full h-2">
          <div :class="themeClasses.progress" class="h-2 rounded-full transition-all duration-300" :style="{ width: `${progress}%` }"></div>
        </div>
      </div>

      <!-- 项目信息标签 -->
      <div class="flex flex-wrap gap-2 mb-4">
        <span v-if="project.genre"
              class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
          {{ project.genre }}
        </span>
        <span
          v-if="project.project_type"
          class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-amber-100 text-amber-700"
        >
          {{ project.project_type === 'poem' ? '古诗词' : '小说' }}
        </span>
        <span v-if="chapterCount > 0"
              class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
          {{ chapterCount }} 章节
        </span>
        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-600">
          {{ project.last_edited }}
        </span>
      </div>
    </div>

    <!-- 操作按钮区域 -->
    <div class="flex gap-2">
      <button
        @click.stop="$emit('detail', project.id)"
        class="flex-1 bg-gray-100 hover:bg-gray-200 text-gray-700 text-sm font-medium py-2 px-4 rounded-lg transition-colors duration-200 flex items-center justify-center gap-1"
      >
        <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
          <path d="M10 12a2 2 0 100-4 2 2 0 000 4z"></path>
          <path fill-rule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clip-rule="evenodd"></path>
        </svg>
        查看详情
      </button>
      <button
        @click.stop="handleDelete"
        class="px-3 py-2 bg-red-100 hover:bg-red-200 text-red-600 rounded-lg transition-colors duration-200 flex items-center justify-center"
        title="删除项目"
      >
        <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z" clip-rule="evenodd"></path>
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8 7a1 1 0 012 0v4a1 1 0 11-2 0V7zM12 7a1 1 0 012 0v4a1 1 0 11-2 0V7z" clip-rule="evenodd"></path>
        </svg>
      </button>
      <button
        @click.stop="$emit('continue', project)"
        :class="[themeClasses.bg, themeClasses.text, 'flex-1 text-sm font-semibold py-2 px-4 rounded-lg transition-colors duration-200 flex items-center justify-center gap-1 hover:opacity-80']"
      >
        <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
          <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z"></path>
        </svg>
        继续创作
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { NovelProjectSummary } from '@/api/novel'

interface Props {
  project: NovelProjectSummary
}

const props = defineProps<Props>()

const emit = defineEmits<{
  (e: 'click', id: string): void
  (e: 'detail', id: string): void
  (e: 'continue', project: NovelProjectSummary): void
  (e: 'delete', id: string): void
}>()

const themeClasses = computed(() => {
  const colors = {
    '科幻': { bg: 'bg-indigo-100', text: 'text-indigo-600', progress: 'bg-indigo-500' },
    '悬疑': { bg: 'bg-teal-100', text: 'text-teal-600', progress: 'bg-teal-500' },
    '奇幻': { bg: 'bg-green-100', text: 'text-green-600', progress: 'bg-green-500' },
    '东方奇幻': { bg: 'bg-purple-100', text: 'text-purple-600', progress: 'bg-purple-500' },
    '穿越': { bg: 'bg-pink-100', text: 'text-pink-600', progress: 'bg-pink-500' },
    default: { bg: 'bg-gray-100', text: 'text-gray-600', progress: 'bg-gray-500' }
  }

  // 使用后端返回的 genre 字段进行匹配
  const genre = props.project.genre || ''
  const genreKey = Object.keys(colors).find(key => key !== 'default' && genre.includes(key)) || 'default'

  return colors[genreKey as keyof typeof colors]
})

// 使用后端预计算的进度数据
const progress = computed(() => {
  const { completed_chapters, total_chapters } = props.project
  return total_chapters > 0 ? Math.round((completed_chapters / total_chapters) * 100) : 0
})

const getStatusText = computed(() => {
  const { completed_chapters, total_chapters } = props.project
  
  if (completed_chapters > 0) {
    return `已完成 ${completed_chapters}/${total_chapters} 章`
  } else if (total_chapters > 0) {
    return '准备创作'
  } else {
    return '蓝图完成'
  }
})

// 使用后端返回的预计算数据
const chapterCount = computed(() => {
  return props.project.total_chapters
})

// 由于 NovelProjectSummary 没有 characters 信息，我们暂时返回 0 或者隐藏这个标签
const characterCount = computed(() => {
  return 0 // 后端 Summary 没有提供角色数量
})

const handleDelete = () => {
  emit('delete', props.project.id)
}
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
