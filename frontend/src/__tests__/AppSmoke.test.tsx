import { describe, it, expect } from 'vitest'
import { render } from '@testing-library/react'
import App from '../App'

describe('App shell', () => {
  it('renders without crashing', () => {
    const { getByText } = render(<App />)
    expect(getByText(/SkillGap Analyzer/i)).toBeDefined()
  })
})

