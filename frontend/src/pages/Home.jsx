import { useAuth } from '../hooks/useAuth'
import { Link } from 'react-router-dom'
import { ArrowRight, Zap, Shield, TrendingUp } from 'lucide-react'

export default function Home() {
  const { isAuthenticated } = useAuth()

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
      {/* Hero */}
      <section className="max-w-7xl mx-auto px-4 py-20">
        <div className="grid md:grid-cols-2 gap-12 items-center">
          <div>
            <h1 className="text-5xl font-bold mb-4">
              Find Your Perfect <span className="text-luxury-500">Travel Deal</span>
            </h1>
            <p className="text-xl text-gray-600 mb-8">
              Search flights, hotels, and award availability across multiple programs. Compare deals by value and maximize your travel points.
            </p>
            <div className="flex gap-4">
              {isAuthenticated() ? (
                <Link to="/search" className="btn-primary flex items-center gap-2">
                  Start Searching <ArrowRight size={20} />
                </Link>
              ) : (
                <>
                  <Link to="/login" className="btn-primary">
                    Sign In
                  </Link>
                  <Link to="/register" className="btn-secondary">
                    Create Account
                  </Link>
                </>
              )}
            </div>
          </div>
          <div className="bg-gradient-to-br from-luxury-500 to-luxury-600 rounded-2xl h-96 flex items-center justify-center text-white text-6xl">
            ✈️
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="max-w-7xl mx-auto px-4 py-20">
        <h2 className="text-4xl font-bold text-center mb-12">Why Choose Us</h2>
        <div className="grid md:grid-cols-3 gap-8">
          <div className="card">
            <Zap className="text-luxury-500 mb-4" size={32} />
            <h3 className="text-2xl font-bold mb-2">Fast Search</h3>
            <p className="text-gray-600">
              Get results in seconds across flights, hotels, and award programs.
            </p>
          </div>
          <div className="card">
            <TrendingUp className="text-luxury-500 mb-4" size={32} />
            <h3 className="text-2xl font-bold mb-2">Smart Comparison</h3>
            <p className="text-gray-600">
              Compare deals by CPP (cents per point) value to find the best redemptions.
            </p>
          </div>
          <div className="card">
            <Shield className="text-luxury-500 mb-4" size={32} />
            <h3 className="text-2xl font-bold mb-2">Secure & Private</h3>
            <p className="text-gray-600">
              Your data is encrypted and never shared. Full control of your preferences.
            </p>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="bg-luxury-500 text-white py-16">
        <div className="max-w-7xl mx-auto px-4 text-center">
          <h2 className="text-4xl font-bold mb-4">Ready to Save on Travel?</h2>
          <p className="text-xl mb-8 opacity-90">
            Join thousands of savvy travelers finding the best deals
          </p>
          {isAuthenticated() ? (
            <Link to="/search" className="bg-white text-luxury-500 hover:bg-gray-100 px-8 py-3 rounded-lg font-bold inline-block transition-colors">
              Start Searching Now
            </Link>
          ) : (
            <Link to="/register" className="bg-white text-luxury-500 hover:bg-gray-100 px-8 py-3 rounded-lg font-bold inline-block transition-colors">
              Create Free Account
            </Link>
          )}
        </div>
      </section>
    </div>
  )
}
