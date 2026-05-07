import { create } from 'zustand'
import { authService } from '../services/api'

export const useAuth = create((set) => ({
  user: null,
  loading: false,
  error: null,

  login: async (email, password) => {
    set({ loading: true, error: null })
    try {
      const { data } = await authService.login(email, password)
      localStorage.setItem('access_token', data.access_token)
      localStorage.setItem('refresh_token', data.refresh_token)
      set({ user: data.user, loading: false })
      return data
    } catch (error) {
      const message = error.response?.data?.error || 'Login failed'
      set({ error: message, loading: false })
      throw error
    }
  },

  register: async (email, password) => {
    set({ loading: true, error: null })
    try {
      const { data } = await authService.register(email, password)
      localStorage.setItem('access_token', data.access_token)
      localStorage.setItem('refresh_token', data.refresh_token)
      set({ user: data.user, loading: false })
      return data
    } catch (error) {
      const message = error.response?.data?.error || 'Registration failed'
      set({ error: message, loading: false })
      throw error
    }
  },

  logout: () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    set({ user: null })
  },

  checkAuth: async () => {
    const token = localStorage.getItem('access_token')
    if (!token) {
      set({ user: null })
      return
    }
    try {
      const { data } = await authService.getMe()
      set({ user: data.user })
    } catch {
      set({ user: null })
      localStorage.removeItem('access_token')
    }
  },

  isAuthenticated: () => !!localStorage.getItem('access_token'),
}))
