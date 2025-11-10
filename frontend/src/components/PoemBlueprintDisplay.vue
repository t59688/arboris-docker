<template>
  <div class="p-8 bg-white rounded-2xl shadow-2xl fade-in">
    <h2 class="text-3xl font-bold text-center text-gray-800 mb-6">你的诗词蓝图已生成！</h2>

    <!-- AI消息 -->
    <div v-if="aiMessage" class="mb-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
      <p class="text-blue-800">{{ aiMessage }}</p>
    </div>

    <div class="prose max-w-none p-6 bg-gray-50 rounded-lg border border-gray-200" v-html="formattedBlueprint"></div>

    <!-- 加载状态 -->
    <div v-if="showActions && isSaving" class="text-center py-8">
      <div class="relative mx-auto mb-6 w-16 h-16">
        <div class="absolute inset-0 border-4 border-green-100 rounded-full"></div>
        <div class="absolute inset-0 border-4 border-transparent border-t-green-500 rounded-full animate-spin"></div>
        <div class="absolute inset-2 bg-green-500 rounded-full flex items-center justify-center">
          <svg class="w-6 h-6 text-white animate-pulse" fill="currentColor" viewBox="0 0 20 20">
            <path d="M7.707 10.293a1 1 0 10-1.414 1.414l3 3a1 1 0 001.414 0l3-3a1 1 0 00-1.414-1.414L11 11.586V6a1 1 0 10-2 0v5.586l-1.293-1.293z"></path>
            <path d="M5 4a2 2 0 012-2h6a2 2 0 012 2v1a1 1 0 11-2 0V4H7v1a1 1 0 11-2 0V4z"></path>
          </svg>
        </div>
      </div>
      <h3 class="text-lg font-semibold text-gray-800 mb-2 animate-pulse">正在保存蓝图...</h3>
      <p class="text-gray-600">即将跳转到工作台，开始您的诗词创作之旅</p>
      <div class="mt-4 w-32 mx-auto">
        <div class="w-full bg-gray-200 rounded-full h-1">
          <div class="h-1 bg-gradient-to-r from-green-400 to-green-600 rounded-full animate-pulse" style="width: 100%"></div>
        </div>
      </div>
    </div>

    <div v-else-if="showActions" class="text-center mt-8 space-x-4">
      <button
        @click="confirmRegenerate"
        class="bg-gray-200 text-gray-700 font-bold py-3 px-8 rounded-full hover:bg-gray-300 transition-all duration-300 transform hover:scale-105"
      >
        <span class="flex items-center justify-center">
          <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clip-rule="evenodd"></path>
          </svg>
          重新生成
        </span>
      </button>
      <button
        @click="confirmBlueprint"
        :disabled="isSaving"
        class="bg-gradient-to-r from-emerald-500 to-teal-600 text-white font-bold py-3 px-8 rounded-full hover:from-emerald-600 hover:to-teal-700 transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
      >
        <span class="flex items-center justify-center">
          <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"></path>
          </svg>
          确认并开始创作
        </span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { globalAlert } from '@/composables/useAlert'
import type { Blueprint } from '@/api/novel'

interface Props {
  blueprint: Blueprint | null
  aiMessage?: string
  showActions?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showActions: true
})

const emit = defineEmits<{
  confirm: []
  regenerate: []
}>()

const isSaving = ref(false)

const confirmRegenerate = async () => {
  const confirmed = await globalAlert.showConfirm('重新生成会覆盖当前蓝图，确定继续吗？', '重新生成确认')
  if (confirmed) {
    emit('regenerate')
  }
}

const confirmBlueprint = async () => {
  isSaving.value = true
  try {
    await emit('confirm')
  } finally {
    isSaving.value = false
  }
}

const formattedBlueprint = computed(() => {
  if (!props.blueprint) {
    return '<p class="text-center text-red-500">抱歉，生成蓝图失败，未能获取到最终数据。</p>'
  }

  const blueprint = props.blueprint as any

  const safe = (value: any, fallback = '待补充') => value || fallback

  const createSection = (title: string, content: string, icon: string, bgColor = 'emerald') => `
    <div class="mb-8 bg-white rounded-xl border border-${bgColor}-100 p-6 shadow-sm hover:shadow-md transition-shadow duration-300">
      <div class="flex items-center mb-4">
        <div class="w-8 h-8 bg-${bgColor}-100 rounded-lg flex items-center justify-center mr-3">
          ${icon}
        </div>
        <h3 class="text-xl font-bold text-gray-800">${title}</h3>
      </div>
      <div class="prose max-w-none text-gray-700">
        ${content}
      </div>
    </div>
  `

  // 图标定义
  const icons = {
    summary: '<svg class="w-5 h-5 text-emerald-600" fill="currentColor" viewBox="0 0 20 20"><path d="M9 4.804A7.968 7.968 0 005.5 4c-1.255 0-2.443.29-3.5.804v10A7.969 7.969 0 015.5 14c1.669 0 3.218.51 4.5 1.385A7.962 7.962 0 0114.5 14c1.255 0 2.443.29 3.5.804v-10A7.968 7.968 0 0014.5 4c-1.255 0-2.443.29-3.5.804V12a1 1 0 11-2 0V4.804z"></path></svg>',
    poetry: '<svg class="w-5 h-5 text-amber-600" fill="currentColor" viewBox="0 0 20 20"><path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z"></path></svg>',
    world: '<svg class="w-5 h-5 text-blue-600" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M4.083 9h1.946c.089-1.546.383-2.97.837-4.118A6.004 6.004 0 004.083 9zM10 2a8 8 0 100 16 8 8 0 000-16zm0 2c-.076 0-.232.032-.465.262-.238.234-.497.623-.737 1.182-.389.907-.673 2.142-.766 3.556h3.936c-.093-1.414-.377-2.649-.766-3.556-.24-.56-.5-.948-.737-1.182C10.232 4.032 10.076 4 10 4zm3.971 5c-.089-1.546-.383-2.97-.837-4.118A6.004 6.004 0 0115.917 9h-1.946zm-2.003 2H8.032c.093 1.414.377 2.649.766 3.556.24.56.5.948.737 1.182.233.23.389.262.465.262.076 0 .232-.032.465-.262.238-.234.498-.623.737-1.182.389-.907.673-2.142.766-3.556zm1.166 4.118c.454-1.147.748-2.572.837-4.118h1.946a6.004 6.004 0 01-2.783 4.118zm-6.268 0C6.412 13.97 6.118 12.546 6.03 11H4.083a6.004 6.004 0 002.783 4.118z" clip-rule="evenodd"></path></svg>',
    structure: '<svg class="w-5 h-5 text-purple-600" fill="currentColor" viewBox="0 0 20 20"><path d="M7 3a1 1 0 000 2h6a1 1 0 100-2H7zM4 7a1 1 0 011-1h10a1 1 0 110 2H5a1 1 0 01-1-1zM2 11a2 2 0 012-2h12a2 2 0 012 2v4a2 2 0 01-2 2H4a2 2 0 01-2-2v-4z"></path></svg>'
  }

  // 头部标题区域（适配诗词）
  const headerHTML = `
    <div class="text-center mb-8 p-6 bg-gradient-to-r from-emerald-500 via-teal-500 to-cyan-500 rounded-xl text-white">
      <h1 class="text-4xl font-bold mb-4">${safe(blueprint.title, '未命名诗作')}</h1>
      <div class="flex flex-wrap justify-center gap-3 mb-4">
        ${blueprint.genre ? `<span class="bg-white/20 backdrop-blur-sm px-4 py-2 rounded-full text-sm font-medium">📜 ${blueprint.genre}</span>` : ''}
        ${blueprint.style ? `<span class="bg-white/20 backdrop-blur-sm px-4 py-2 rounded-full text-sm font-medium">🎨 ${blueprint.style}</span>` : ''}
        ${blueprint.tone ? `<span class="bg-white/20 backdrop-blur-sm px-4 py-2 rounded-full text-sm font-medium">💫 ${blueprint.tone}</span>` : ''}
        ${blueprint.theme ? `<span class="bg-white/20 backdrop-blur-sm px-4 py-2 rounded-full text-sm font-medium">🎭 ${blueprint.theme}</span>` : ''}
      </div>
    </div>
  `

  // 意境概要
  const summaryHTML = createSection(
    '意境概要',
    `
    <div class="bg-gradient-to-r from-emerald-50 to-teal-50 border border-emerald-200 rounded-lg p-5 mb-4">
      <h4 class="font-semibold text-emerald-800 mb-2">核心意境</h4>
      <p class="text-lg italic text-emerald-700">"${safe(blueprint.one_sentence_summary)}"</p>
    </div>
    <div class="prose max-w-none">
      <h4 class="font-semibold text-gray-800 mb-3">章法走向</h4>
      <p class="text-gray-700 leading-relaxed">${safe(blueprint.full_synopsis)}</p>
    </div>
    `,
    icons.summary,
    'emerald'
  )

  // 格律要求（诗词特有）
  let poeticRequirementsHTML = ''
  if (blueprint.poetic_requirements) {
    const req = blueprint.poetic_requirements
    let reqContent = '<div class="space-y-4">'
    
    if (req.meter) {
      reqContent += `
        <div class="bg-amber-50 border-l-4 border-amber-400 p-4 rounded-r-lg">
          <h5 class="font-semibold text-amber-800 mb-2">📏 格律</h5>
          <p class="text-amber-700">${req.meter}</p>
        </div>
      `
    }
    
    if (req.structure && req.structure.length > 0) {
      reqContent += `
        <div class="bg-purple-50 border-l-4 border-purple-400 p-4 rounded-r-lg">
          <h5 class="font-semibold text-purple-800 mb-2">🏗️ 结构</h5>
          <div class="flex flex-wrap gap-2">
            ${req.structure.map((s: string) => `<span class="bg-purple-100 text-purple-700 px-3 py-1 rounded-full text-sm">${s}</span>`).join('')}
          </div>
        </div>
      `
    }
    
    if (req.rhyme) {
      reqContent += `
        <div class="bg-rose-50 border-l-4 border-rose-400 p-4 rounded-r-lg">
          <h5 class="font-semibold text-rose-800 mb-2">🎵 押韵</h5>
          <p class="text-rose-700">${req.rhyme}</p>
        </div>
      `
    }
    
    if (req.must_use_allusions && req.must_use_allusions.length > 0) {
      reqContent += `
        <div class="bg-indigo-50 border-l-4 border-indigo-400 p-4 rounded-r-lg">
          <h5 class="font-semibold text-indigo-800 mb-2">📚 引用典故</h5>
          <ul class="list-disc list-inside text-indigo-700 space-y-1">
            ${req.must_use_allusions.map((a: string) => `<li>${a}</li>`).join('')}
          </ul>
        </div>
      `
    }
    
    if (req.forbidden_words && req.forbidden_words.length > 0) {
      reqContent += `
        <div class="bg-red-50 border-l-4 border-red-400 p-4 rounded-r-lg">
          <h5 class="font-semibold text-red-800 mb-2">🚫 禁用词汇</h5>
          <div class="flex flex-wrap gap-2">
            ${req.forbidden_words.map((w: string) => `<span class="bg-red-100 text-red-700 px-2 py-1 rounded text-sm line-through">${w}</span>`).join('')}
          </div>
        </div>
      `
    }
    
    reqContent += '</div>'
    poeticRequirementsHTML = createSection('格律规范', reqContent, icons.poetry, 'amber')
  }

  // 意象与氛围（诗词特有的world_setting）
  let worldSettingHTML = ''
  if (blueprint.world_setting) {
    const ws = blueprint.world_setting
    let wsContent = '<div class="space-y-4">'
    
    if (ws.key_imagery && ws.key_imagery.length > 0) {
      wsContent += `
        <div class="bg-blue-50 border-l-4 border-blue-400 p-4 rounded-r-lg">
          <h5 class="font-semibold text-blue-800 mb-2">🌸 核心意象</h5>
          <div class="flex flex-wrap gap-2">
            ${ws.key_imagery.map((img: string) => `<span class="bg-blue-100 text-blue-700 px-3 py-1 rounded-full text-sm">${img}</span>`).join('')}
          </div>
        </div>
      `
    }
    
    if (ws.season) {
      wsContent += `
        <div class="bg-teal-50 border-l-4 border-teal-400 p-4 rounded-r-lg">
          <h5 class="font-semibold text-teal-800 mb-2">🍂 时节</h5>
          <p class="text-teal-700">${ws.season}</p>
        </div>
      `
    }
    
    if (ws.location) {
      wsContent += `
        <div class="bg-cyan-50 border-l-4 border-cyan-400 p-4 rounded-r-lg">
          <h5 class="font-semibold text-cyan-800 mb-2">📍 地点</h5>
          <p class="text-cyan-700">${ws.location}</p>
        </div>
      `
    }
    
    wsContent += '</div>'
    worldSettingHTML = createSection('意象与氛围', wsContent, icons.world, 'blue')
  }

  // 章法结构（诗词的"句序/段序"）
  let chapterHTML = ''
  if (blueprint.chapter_outline && blueprint.chapter_outline.length > 0) {
    const chaptersContent = `
      <div class="space-y-4">
        ${blueprint.chapter_outline.map((ch: any) => `
          <div class="group relative overflow-hidden bg-gradient-to-r from-purple-50 to-indigo-50 border border-purple-200 rounded-lg p-5 hover:shadow-md transition-all duration-300">
            <div class="absolute left-0 top-0 bottom-0 w-1 bg-gradient-to-b from-purple-500 to-indigo-600 transform origin-top group-hover:scale-y-110 transition-transform duration-300"></div>
            <div class="flex items-start">
              <div class="flex-shrink-0 w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center mr-4">
                <span class="text-purple-600 font-bold text-sm">${ch.chapter_number}</span>
              </div>
              <div class="flex-1">
                <h4 class="text-lg font-bold text-gray-800 mb-2 group-hover:text-purple-600 transition-colors duration-300">
                  ${ch.title}
                  ${ch.target_lines ? `<span class="text-sm font-normal text-gray-500 ml-2">(${ch.target_lines}句)</span>` : ''}
                </h4>
                <p class="text-gray-600 leading-relaxed mb-3">${ch.summary}</p>
                ${ch.imagery && ch.imagery.length > 0 ? `
                  <div class="flex flex-wrap gap-2 mt-2">
                    ${ch.imagery.map((img: string) => `<span class="bg-purple-100 text-purple-700 px-2 py-1 rounded text-xs">${img}</span>`).join('')}
                  </div>
                ` : ''}
              </div>
            </div>
          </div>
        `).join('')}
      </div>
    `
    chapterHTML = createSection('章法结构', chaptersContent, icons.structure, 'purple')
  }

  return `
    ${headerHTML}
    ${summaryHTML}
    ${poeticRequirementsHTML}
    ${worldSettingHTML}
    ${chapterHTML}
  `
})
</script>

<style scoped>
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.fade-in {
  animation: fadeIn 0.6s ease-out;
}

.transform {
  transition: transform 0.2s ease-in-out;
}

.hover\:scale-105:hover {
  transform: scale(1.05);
}

.disabled\:transform-none:disabled {
  transform: none !important;
}

/* Prose样式 */
.prose h4 {
  font-weight: 600;
  color: #374151;
  margin-bottom: 0.75rem;
}

.prose p {
  line-height: 1.75;
}

.prose ul {
  list-style-type: disc;
  padding-left: 1.5rem;
}
</style>

