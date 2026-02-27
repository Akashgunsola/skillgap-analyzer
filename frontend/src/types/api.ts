export interface UserSkill {
  skill_id: string
  name: string
  proficiency: number
  evidence_count: number
}

export interface UserSkillProfile {
  skills: UserSkill[]
}

export interface ResumeUploadResponse {
  profile: UserSkillProfile
}

export interface JobRequirement {
  skill_id: string
  weight: number
  required_level: number
}

export interface JobModel {
  title: string
  extracted_skills: JobRequirement[]
}

export interface JobInput {
  title: string
  description: string
}

export interface JobListRequest {
  jobs: JobInput[]
}

export interface JobListResponse {
  jobs: JobModel[]
}

export interface FitScorePerJob {
  job: JobModel
  fit_score: number
  category: string
}

export interface GapItem {
  skill_id: string
  name: string
  weight: number
  difficulty: number
  learning_hours: number
  gap_score: number
}

export interface RoadmapItem {
  timeframe: string
  learning_focus: string
  learning_hours: number
  priority_score: number
}

export interface AnalysisRequest {
  profile: UserSkillProfile
  jobs: JobModel[]
  weekly_hours?: number
}

export interface AnalysisResponse {
  fit_results: FitScorePerJob[]
  gaps: GapItem[]
  roadmap: RoadmapItem[]
}

