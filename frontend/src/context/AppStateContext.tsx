import { createContext, useContext, useState, type ReactNode } from 'react'
import type { AnalysisResponse, JobModel, UserSkillProfile } from '../types/api'

interface AppState {
  profile: UserSkillProfile | null
  jobs: JobModel[]
  analysis: AnalysisResponse | null
  setProfile: (profile: UserSkillProfile | null) => void
  setJobs: (jobs: JobModel[]) => void
  setAnalysis: (analysis: AnalysisResponse | null) => void
}

const AppStateContext = createContext<AppState | undefined>(undefined)

export function AppStateProvider({ children }: { children: ReactNode }) {
  const [profile, setProfile] = useState<UserSkillProfile | null>(null)
  const [jobs, setJobs] = useState<JobModel[]>([])
  const [analysis, setAnalysis] = useState<AnalysisResponse | null>(null)

  return (
    <AppStateContext.Provider
      value={{ profile, jobs, analysis, setProfile, setJobs, setAnalysis }}
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

