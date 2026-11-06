import { Link, NavLink, Outlet, useNavigate } from 'react-router'
import { useAuth } from '../context/AuthContext'

const navLinkClass = ({ isActive }) =>
  `whitespace-nowrap ${isActive ? 'font-semibold underline underline-offset-8' : 'text-gray-600 hover:text-gray-900'}`

export default function Layout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  function handleLogout() {
    logout()
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900">
      <header className="border-b border-gray-200 bg-white">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-x-3 gap-y-2 px-4 py-3">
          <nav className="flex min-w-0 flex-wrap items-center gap-x-4 gap-y-1 sm:gap-x-6">
            <Link to="/" className="text-xl font-bold">
              Retroteka
            </Link>
            <NavLink to="/" end className={navLinkClass}>
              Search
            </NavLink>
            {user && (
              <NavLink to="/collections" className={navLinkClass}>
                My collections
              </NavLink>
            )}
            <NavLink to="/public" className={navLinkClass}>
              Public collections
            </NavLink>
          </nav>
          {user ? (
            <div className="ml-auto flex min-w-0 items-center gap-3">
              <span className="hidden truncate font-medium sm:inline">{user.username}</span>
              <button
                type="button"
                onClick={handleLogout}
                className="shrink-0 rounded-md border border-gray-300 px-2.5 py-1.5 font-medium whitespace-nowrap hover:bg-gray-100 sm:px-3"
              >
                Log out
              </button>
            </div>
          ) : (
            <div className="ml-auto flex items-center gap-2 sm:gap-3">
              <Link
                to="/login"
                className="rounded-md border border-gray-300 px-2.5 py-1.5 font-medium whitespace-nowrap hover:bg-gray-100 sm:px-3"
              >
                Log in
              </Link>
              <Link
                to="/register"
                className="rounded-md bg-gray-800 px-2.5 py-1.5 font-medium whitespace-nowrap text-white hover:bg-gray-700 sm:px-3"
              >
                Sign up
              </Link>
            </div>
          )}
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-4 py-6">
        <Outlet />
      </main>
    </div>
  )
}
