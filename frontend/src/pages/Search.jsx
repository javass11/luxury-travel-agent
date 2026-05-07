import { useState } from 'react'
import { useAuth } from '../hooks/useAuth'
import { Navigate } from 'react-router-dom'
import SearchFlights from '../components/SearchFlights'
import { Plane, Hotel, Award } from 'lucide-react'

export default function Search() {
  const { isAuthenticated } = useAuth()
  const [activeTab, setActiveTab] = useState('flights')

  if (!isAuthenticated()) {
    return <Navigate to="/login" />
  }

  const tabs = [
    { id: 'flights', label: 'Flights', icon: Plane },
    { id: 'hotels', label: 'Hotels', icon: Hotel },
    { id: 'awards', label: 'Awards', icon: Award },
  ]

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4">
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2">Find Your Best Deals</h1>
          <p className="text-gray-600">Search flights, hotels, and award availability</p>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex gap-4 border-b mb-6">
            {tabs.map(({ id, label, icon: Icon }) => (
              <button
                key={id}
                onClick={() => setActiveTab(id)}
                className={`flex items-center gap-2 px-4 py-3 font-medium border-b-2 transition-colors ${
                  activeTab === id
                    ? 'border-luxury-500 text-luxury-500'
                    : 'border-transparent text-gray-600 hover:text-gray-900'
                }`}
              >
                <Icon size={20} />
                {label}
              </button>
            ))}
          </div>

          {activeTab === 'flights' && <SearchFlights />}
          {activeTab === 'hotels' && (
            <div className="text-center py-12 text-gray-600">
              <Hotel size={48} className="mx-auto mb-4 opacity-50" />
              <p>Hotel search coming soon</p>
            </div>
          )}
          {activeTab === 'awards' && (
            <div className="text-center py-12 text-gray-600">
              <Award size={48} className="mx-auto mb-4 opacity-50" />
              <p>Award search coming soon</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
