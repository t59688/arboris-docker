import {
  API_BASE_URL,
  API_PREFIX,
  request,
  type Blueprint,
  type BlueprintGenerationResponse,
  type ConverseResponse,
  type NovelProject,
  type NovelProjectSummary,
  type DeleteNovelsResponse
} from '@/api/novel'

const POEMS_BASE = `${API_BASE_URL}${API_PREFIX}/poems`

export class PoemAPI {
  static async createPoem(title: string, initialPrompt: string): Promise<NovelProject> {
    return request(POEMS_BASE, {
      method: 'POST',
      body: JSON.stringify({ title, initial_prompt: initialPrompt })
    })
  }

  static async getPoem(projectId: string): Promise<NovelProject> {
    return request(`${POEMS_BASE}/${projectId}`)
  }

  static async listPoems(): Promise<NovelProjectSummary[]> {
    return request(POEMS_BASE)
  }

  static async converse(
    projectId: string,
    userInput: any,
    conversationState: any = {}
  ): Promise<ConverseResponse> {
    const formattedUserInput = userInput || { id: null, value: null }
    return request(`${POEMS_BASE}/${projectId}/concept/converse`, {
      method: 'POST',
      body: JSON.stringify({
        user_input: formattedUserInput,
        conversation_state: conversationState
      })
    })
  }

  static async generateBlueprint(projectId: string): Promise<BlueprintGenerationResponse> {
    return request(`${POEMS_BASE}/${projectId}/blueprint/generate`, {
      method: 'POST'
    })
  }

  static async saveBlueprint(projectId: string, blueprint: Blueprint): Promise<NovelProject> {
    return request(`${POEMS_BASE}/${projectId}/blueprint/save`, {
      method: 'POST',
      body: JSON.stringify(blueprint)
    })
  }

  static async generatePoemContent(projectId: string): Promise<{
    status: string
    versions: Array<{
      version_number: number
      content: string
      title: string
      notes: string
    }>
    message: string
  }> {
    return request(`${POEMS_BASE}/${projectId}/generate`, {
      method: 'POST'
    })
  }

  static async deletePoems(projectIds: string[]): Promise<DeleteNovelsResponse> {
    return request(POEMS_BASE, {
      method: 'DELETE',
      body: JSON.stringify(projectIds)
    })
  }
}
