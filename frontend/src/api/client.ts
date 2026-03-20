import axios from 'axios'
import type {
  AnalysisRequest,
  AnalysisResponse,
  JobInput,
  JobListResponse,
  ResumeUploadResponse,
} from '../types/api'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api'

const http = axios.create({
  baseURL: API_BASE_URL,
})

export async function parseResumeFromFile(file: File): Promise<ResumeUploadResponse> {
  const formData = new FormData()
  formData.append('file', file)

  const { data } = await http.post<ResumeUploadResponse>('/resume/parse', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}

export async function parseResumeFromText(text: string): Promise<ResumeUploadResponse> {
  const formData = new FormData()
  formData.append('text', text)

  const { data } = await http.post<ResumeUploadResponse>('/resume/parse', formData)
  return data
}

export async function extractJobs(jobs: JobInput[]): Promise<JobListResponse> {
  const { data } = await http.post<JobListResponse>('/jobs/extract', { jobs })
  return data
}

export async function runAnalysis(payload: AnalysisRequest): Promise<AnalysisResponse> {
  const { data } = await http.post<AnalysisResponse>('/analyze/', payload)
  return data
}

export async function getRecommendations(profile: any): Promise<any[]> {
  const { data } = await http.post<any[]>('/analyze/recommend', profile)
  return data
}

export async function registerUser(email: string, password: string): Promise<{access_token: string, token_type: string}> {
  const { data } = await http.post<{access_token: string, token_type: string}>('/auth/register', { email, password })
  return data
}

export async function loginUser(email: string, password: string): Promise<{access_token: string, token_type: string}> {
  const formData = new URLSearchParams()
  formData.append('username', email)
  formData.append('password', password)

  const { data } = await http.post<{access_token: string, token_type: string}>('/auth/login', formData, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
  })
  return data
}
