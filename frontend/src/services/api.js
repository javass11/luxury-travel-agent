import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:5000/api'

const apiClient = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
})

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const authService = {
  register: (email, password) =>
    apiClient.post('/auth/register', { email, password }),
  login: (email, password) =>
    apiClient.post('/auth/login', { email, password }),
  refresh: () =>
    apiClient.post('/auth/refresh'),
  getMe: () =>
    apiClient.get('/auth/me'),
}

export const searchService = {
  flights: (origin, destination, departureDate, cabinClass = 'ECONOMY') =>
    apiClient.get('/flights/search', {
      params: { origin, destination, departure_date: departureDate, cabin_class: cabinClass }
    }),
  hotels: (destination, checkinDate, checkoutDate, loyaltyProgram = '') =>
    apiClient.get('/hotels/search', {
      params: { destination, checkin_date: checkinDate, checkout_date: checkoutDate, loyalty_program: loyaltyProgram }
    }),
  awards: (origin, destination, startDate, cabin = 'business') =>
    apiClient.get('/awards/search', {
      params: { origin, destination, start_date: startDate, cabin }
    }),
}

export const redemptionService = {
  evaluate: (options) =>
    apiClient.post('/redemptions/evaluate', { options }),
  visualize: (options, title = 'CPP Comparison') =>
    apiClient.post('/redemptions/visualize', { options, title }),
}

export const dealsService = {
  save: (dealType, dealId, notes = '') =>
    apiClient.post('/deals/save', { deal_type: dealType, deal_id: dealId, notes }),
  analyze: (origin, destination, departureDate, cabinClass, hotelDestination, checkin, checkout) =>
    apiClient.post('/deals/analyze', {
      origin, destination, departure_date: departureDate, cabin_class: cabinClass,
      hotel_destination: hotelDestination, checkin, checkout
    }),
}

export default apiClient
