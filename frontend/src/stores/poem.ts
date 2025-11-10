import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Blueprint, BlueprintGenerationResponse, ConverseResponse, NovelProject, NovelProjectSummary } from '@/api/novel'
import { PoemAPI } from '@/api/poem'

export const usePoemStore = defineStore('poem', () => {
  const projects = ref<NovelProjectSummary[]>([])
  const currentProject = ref<NovelProject | null>(null)
  const currentConversationState = ref<any>({})
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  const projectsCount = computed(() => projects.value.length)
  const hasCurrentProject = computed(() => currentProject.value !== null)

  async function loadProjects() {
    isLoading.value = true
    error.value = null
    try {
      projects.value = await PoemAPI.listPoems()
    } catch (err) {
      error.value = err instanceof Error ? err.message : '加载项目失败'
    } finally {
      isLoading.value = false
    }
  }

  async function createProject(title: string, initialPrompt: string) {
    isLoading.value = true
    error.value = null
    try {
      const project = await PoemAPI.createPoem(title, initialPrompt)
      currentProject.value = project
      currentConversationState.value = {}
      return project
    } catch (err) {
      error.value = err instanceof Error ? err.message : '创建项目失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function loadProject(projectId: string, silent: boolean = false) {
    if (!silent) {
      isLoading.value = true
    }
    error.value = null
    try {
      currentProject.value = await PoemAPI.getPoem(projectId)
    } catch (err) {
      error.value = err instanceof Error ? err.message : '加载项目失败'
      throw err
    } finally {
      if (!silent) {
        isLoading.value = false
      }
    }
  }

  async function sendConversation(userInput: any, projectId?: string): Promise<ConverseResponse> {
    isLoading.value = true
    error.value = null
    try {
      const targetProjectId = await ensureProjectId(projectId)
      const response = await PoemAPI.converse(
        targetProjectId,
        userInput,
        currentConversationState.value
      )
      currentConversationState.value = response.conversation_state
      return response
    } catch (err) {
      error.value = err instanceof Error ? err.message : '对话失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function generateBlueprint(projectId?: string): Promise<BlueprintGenerationResponse> {
    isLoading.value = true
    error.value = null
    try {
      const targetProjectId = await ensureProjectId(projectId)
      return await PoemAPI.generateBlueprint(targetProjectId)
    } catch (err) {
      error.value = err instanceof Error ? err.message : '生成蓝图失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function saveBlueprint(blueprint: Blueprint, projectId?: string) {
    isLoading.value = true
    error.value = null
    try {
      const targetProjectId = await ensureProjectId(projectId)
      currentProject.value = await PoemAPI.saveBlueprint(targetProjectId, blueprint)
    } catch (err) {
      error.value = err instanceof Error ? err.message : '保存蓝图失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function deleteProjects(projectIds: string[]) {
    isLoading.value = true
    error.value = null
    try {
      const response = await PoemAPI.deletePoems(projectIds)
      projects.value = projects.value.filter(project => !projectIds.includes(project.id))
      if (currentProject.value && projectIds.includes(currentProject.value.id)) {
        currentProject.value = null
        currentConversationState.value = {}
      }
      return response
    } catch (err) {
      error.value = err instanceof Error ? err.message : '删除项目失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  function setCurrentProject(project: NovelProject | null) {
    currentProject.value = project
  }

  async function ensureProjectId(fallbackId?: string): Promise<string> {
    if (currentProject.value?.id) {
      return currentProject.value.id
    }
    if (fallbackId) {
      await loadProject(fallbackId, true)
      if (currentProject.value?.id) {
        return currentProject.value.id
      }
    }
    throw new Error('没有当前项目')
  }

  return {
    projects,
    currentProject,
    currentConversationState,
    isLoading,
    error,
    projectsCount,
    hasCurrentProject,
    loadProjects,
    createProject,
    loadProject,
    sendConversation,
    generateBlueprint,
    saveBlueprint,
    deleteProjects,
    setCurrentProject,
  }
})
