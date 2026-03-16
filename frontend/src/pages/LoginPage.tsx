import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { loginUser, registerUser } from '../api/client'
import type { FormEvent } from 'react'

export function LoginPage() {
  const [isRegistering, setIsRegistering] = useState(false)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  
  const { login } = useAuth()
  const navigate = useNavigate()

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    setLoading(true)

    try {
      let data;
      if (isRegistering) {
        data = await registerUser(email, password)
      } else {
        data = await loginUser(email, password)
      }
      login(data.access_token)
      navigate('/') // Navigate to dashboard after login
    } catch (err: any) {
      if (err.response && err.response.data && err.response.data.detail) {
        setError(err.response.data.detail)
      } else {
        setError("An error occurred. Please try again.")
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page" style={{ maxWidth: '400px', margin: '0 auto', marginTop: '10vh' }}>
      <h1 style={{ textAlign: 'center' }}>{isRegistering ? 'Create Account' : 'Welcome Back'}</h1>
      
      <form onSubmit={handleSubmit} className="card">
        <label className="field">
          <span>Email</span>
          <input 
            type="email" 
            value={email} 
            onChange={e => setEmail(e.target.value)} 
            required 
            placeholder="you@example.com"
          />
        </label>
        
        <label className="field">
          <span>Password</span>
          <input 
            type="password" 
            value={password} 
            onChange={e => setPassword(e.target.value)} 
            required 
          />
        </label>
        
        {error && <p className="error" style={{ color: 'red', fontSize: '0.9rem' }}>{error}</p>}
        
        <button type="submit" className="primary" disabled={loading} style={{ width: '100%', marginTop: '1rem' }}>
          {loading ? 'Processing...' : (isRegistering ? 'Register' : 'Login')}
        </button>
      </form>
      
      <div style={{ textAlign: 'center', marginTop: '1rem' }}>
        <button 
          onClick={() => setIsRegistering(!isRegistering)} 
          style={{ background: 'none', border: 'none', color: '#007bff', cursor: 'pointer', textDecoration: 'underline' }}
        >
          {isRegistering ? 'Already have an account? Log in' : "Don't have an account? Register"}
        </button>
      </div>
    </div>
  )
}
