import { useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './hooks/useAuth'
import Navigation from './components/Navigation'
import Home from './pages/Home'
import Login from './pages/Login'
import Register from './pages/Register'
import Search from './pages/Search'

function ProtectedRoute({ children }) {
  const { isAuthenticated } = useAuth()
  return isAuthenticated() ? children : <Navigate to="/login" />
}

export default function App() {
  const { checkAuth } = useAuth()

  useEffect(() => {
    checkAuth()
  }, [])

  return (
    <Router>
      <Navigation />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route
          path="/search"
          element={
            <ProtectedRoute>
              <Search />
            </ProtectedRoute>
          }
        />
        <Route path="/deals" element={
          <ProtectedRoute>
            <div className="min-h-screen bg-gray-50 py-8">
              <div className="max-w-7xl mx-auto px-4">
                <h1 className="text-4xl font-bold mb-2">Saved Deals</h1>
                <p className="text-gray-600">Coming soon</p>
              </div>
            </div>
          </ProtectedRoute>
        } />
        <Route path="/redemptions" element={
          <ProtectedRoute>
            <div className="min-h-screen bg-gray-50 py-8">
              <div className="max-w-7xl mx-auto px-4">
                <h1 className="text-4xl font-bold mb-2">Redemption Calculator</h1>
                <p className="text-gray-600">Coming soon</p>
              </div>
            </div>
          </ProtectedRoute>
        } />
      </Routes>
    </Router>
  )
}
