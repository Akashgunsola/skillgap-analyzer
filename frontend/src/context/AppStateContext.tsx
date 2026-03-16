import { createContext, useContext, useState, type ReactNode } from 'react'
import type { AnalysisResponse, JobModel, UserSkillProfile, RecommendationModel } from '../types/api'

interface AppState {
  profile: UserSkillProfile | null
  jobs: JobModel[]
  analysis: AnalysisResponse | null
  recommendations: RecommendationModel[]
  setProfile: (profile: UserSkillProfile | null) => void
  setJobs: (jobs: JobModel[]) => void
  setAnalysis: (analysis: AnalysisResponse | null) => void
  setRecommendations: (recs: RecommendationModel[]) => void
}

const AppStateContext = createContext<AppState | undefined>(undefined)

export function AppStateProvider({ children }: { children: ReactNode }) {
  const [profile, setProfile] = useState<UserSkillProfile | null>(null)
  const [jobs, setJobs] = useState<JobModel[]>([])
  const [analysis, setAnalysis] = useState<AnalysisResponse | null>(null)
  const [recommendations, setRecommendations] = useState<RecommendationModel[]>([])

  return (
    <AppStateContext.Provider
      value={{ profile, jobs, analysis, recommendations, setProfile, setJobs, setAnalysis, setRecommendations }}
    >
      {children}
    </AppStateContext.Provider>
  )
}

export function useAppState(): AppState {
  const ctx = useContext(AppStateContext)
  if (!ctx) {
    throw new Error('useAppState must be used within AppStateProvider')
  }
  return ctx
}

