import { useState } from 'react'
import { searchService } from '../services/api'
import { Search, AlertCircle, Loader } from 'lucide-react'

export default function SearchFlights() {
  const [formData, setFormData] = useState({
    origin: 'JFK',
    destination: 'LHR',
    departureDate: '2026-07-15',
    cabinClass: 'ECONOMY',
  })
  const [flights, setFlights] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  const handleSearch = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      const { data } = await searchService.flights(
        formData.origin,
        formData.destination,
        formData.departureDate,
        formData.cabinClass
      )
      setFlights(data.flights || [])
    } catch (err) {
      setError(err.response?.data?.error || 'Search failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <form onSubmit={handleSearch} className="card">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium mb-2">From</label>
            <input
              type="text"
              name="origin"
              value={formData.origin}
              onChange={handleChange}
              placeholder="JFK"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-luxury-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">To</label>
            <input
              type="text"
              name="destination"
              value={formData.destination}
              onChange={handleChange}
              placeholder="LHR"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-luxury-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Date</label>
            <input
              type="date"
              name="departureDate"
              value={formData.departureDate}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-luxury-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Cabin</label>
            <select
              name="cabinClass"
              value={formData.cabinClass}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-luxury-500"
            >
              <option value="ECONOMY">Economy</option>
              <option value="BUSINESS">Business</option>
              <option value="FIRST">First</option>
            </select>
          </div>
        </div>
        <button
          type="submit"
          disabled={loading}
          className="btn-primary mt-4 flex items-center gap-2 w-full md:w-auto justify-center"
        >
          {loading ? <Loader size={20} className="animate-spin" /> : <Search size={20} />}
          {loading ? 'Searching...' : 'Search Flights'}
        </button>
      </form>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex gap-3">
          <AlertCircle className="text-red-600 flex-shrink-0" />
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {flights.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-xl font-bold">{flights.length} Flights Found</h3>
          <div className="grid gap-4">
            {flights.map((flight) => (
              <div key={flight.id} className="card">
                <div className="flex justify-between items-start mb-3">
                  <div>
                    <div className="font-bold text-lg">{flight.airline}</div>
                    <div className="text-sm text-gray-600">{flight.origin} → {flight.destination}</div>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold text-luxury-500">${flight.cash_price}</div>
                    <div className="text-sm text-gray-600">{flight.cabin_class}</div>
                  </div>
                </div>
                <div className="grid grid-cols-3 gap-4 text-sm pt-3 border-t">
                  <div>
                    <div className="text-gray-600">CPP</div>
                    <div className="font-bold">{flight.cpp?.toFixed(2)}</div>
                  </div>
                  <div>
                    <div className="text-gray-600">Miles</div>
                    <div className="font-bold">{flight.miles_cost?.toLocaleString()}</div>
                  </div>
                  <div>
                    <div className="text-gray-600">Stops</div>
                    <div className="font-bold">{flight.stops}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
