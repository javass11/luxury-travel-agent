import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { LogOut, Menu, X } from 'lucide-react'
import { useState } from 'react'

export default function Navigation() {
  const { user, logout, isAuthenticated } = useAuth()
  const navigate = useNavigate()
  const [mobileOpen, setMobileOpen] = useState(false)

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <nav className="bg-white shadow-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <Link to="/" className="flex items-center gap-2">
              <div className="w-8 h-8 bg-luxury-500 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold">✈️</span>
              </div>
              <span className="hidden sm:block font-bold text-lg">Luxury Travel</span>
            </Link>
          </div>

          <div className="hidden md:flex items-center gap-8">
            <Link to="/search" className="text-gray-600 hover:text-gray-900">
              Search
            </Link>
            <Link to="/deals" className="text-gray-600 hover:text-gray-900">
              Deals
            </Link>
            <Link to="/redemptions" className="text-gray-600 hover:text-gray-900">
              Redemptions
            </Link>
          </div>

          <div className="flex items-center gap-4">
            {isAuthenticated() ? (
              <>
                <div className="hidden sm:block text-sm text-gray-600">
                  {user?.email}
                </div>
                <button
                  onClick={handleLogout}
                  className="flex items-center gap-2 text-gray-600 hover:text-gray-900"
                >
                  <LogOut size={20} />
                </button>
              </>
            ) : (
              <Link to="/login" className="btn-primary text-sm">
                Sign In
              </Link>
            )}
            <button
              onClick={() => setMobileOpen(!mobileOpen)}
              className="md:hidden"
            >
              {mobileOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
          </div>
        </div>

        {mobileOpen && (
          <div className="md:hidden pb-4 space-y-2">
            <Link to="/search" className="block text-gray-600 hover:text-gray-900 py-2">
              Search
            </Link>
            <Link to="/deals" className="block text-gray-600 hover:text-gray-900 py-2">
              Deals
            </Link>
            <Link to="/redemptions" className="block text-gray-600 hover:text-gray-900 py-2">
              Redemptions
            </Link>
          </div>
        )}
      </div>
    </nav>
  )
}
