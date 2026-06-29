import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

export function DashboardLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = (e: React.MouseEvent) => {
    e.preventDefault();
    logout();
    navigate('/login');
  };

  const navLinkClass = ({ isActive }: { isActive: boolean }) =>
    `flex items-center gap-3 px-4 py-3 rounded-lg font-bold transition-all duration-200 ease-in-out active:scale-95 ${
      isActive
        ? 'bg-primary-container text-on-primary-container'
        : 'text-secondary dark:text-secondary-fixed-dim hover:bg-surface-container-low hover:bg-surface-container-high dark:hover:bg-on-surface-variant transition-colors'
    }`;

  return (
    <div className="bg-background text-on-background min-h-screen flex font-body-md text-body-md antialiased selection:bg-primary-container selection:text-on-primary-container">
      {/* SideNavBar */}
      <nav className="hidden md:flex flex-col fixed left-0 top-0 h-screen w-64 bg-surface dark:bg-inverse-surface border-r border-outline-variant dark:border-outline p-md z-40">
        <div className="mb-xl px-4">
          <h1 className="font-headline-md text-headline-md font-bold text-primary dark:text-primary-fixed">Eco Plug</h1>
          <p className="font-label-sm text-label-sm text-secondary">Workspace</p>
        </div>
        <ul className="flex-1 space-y-sm">
          <li>
            <NavLink to="/" end className={navLinkClass}>
              <span className="material-symbols-outlined" style={{ fontVariationSettings: "'FILL' 1" }}>
                dashboard
              </span>
              <span className="font-label-md text-label-md">Dashboard</span>
            </NavLink>
          </li>
          <li>
            <NavLink to="/feedback" className={navLinkClass}>
              <span className="material-symbols-outlined">chat_bubble</span>
              <span className="font-label-md text-label-md">Feedback</span>
            </NavLink>
          </li>
          <li>
            <NavLink to="/complaints" className={navLinkClass}>
              <span className="material-symbols-outlined">report_problem</span>
              <span className="font-label-md text-label-md">Complaints</span>
            </NavLink>
          </li>
          <li>
            <NavLink to="/analytics" className={navLinkClass}>
              <span className="material-symbols-outlined">analytics</span>
              <span className="font-label-md text-label-md">Analytics</span>
            </NavLink>
          </li>
          <li>
            <NavLink
              to="/settings"
              className={navLinkClass}
            >
              <span className="material-symbols-outlined">settings</span>
              <span className="font-label-md text-label-md">Settings</span>
            </NavLink>
          </li>
          <li>
            <a
              href="#"
              className="flex items-center gap-3 px-4 py-3 text-secondary dark:text-secondary-fixed-dim hover:bg-surface-container-low transition-colors rounded-lg transition-all duration-200 ease-in-out active:scale-95 hover:bg-surface-container-high dark:hover:bg-on-surface-variant"
            >
              <span className="material-symbols-outlined">account_circle</span>
              <span className="font-label-md text-label-md">Profile</span>
            </a>
          </li>
        </ul>
        <div className="mt-auto pt-md border-t border-outline-variant">
          <a
            href="#"
            onClick={handleLogout}
            className="flex items-center gap-3 px-4 py-3 text-error hover:bg-error-container hover:text-on-error-container transition-colors rounded-lg transition-all duration-200 ease-in-out active:scale-95"
          >
            <span className="material-symbols-outlined">logout</span>
            <span className="font-label-md text-label-md">Logout</span>
          </a>
        </div>
      </nav>

      {/* Main Content Wrapper */}
      <div className="flex-1 flex flex-col md:ml-64 h-screen overflow-hidden pt-16">
        {/* TopNavBar */}
        <header className="hidden md:flex fixed top-0 right-0 w-[calc(100%-16rem)] h-16 bg-surface dark:bg-surface-dim border-b border-outline-variant dark:border-outline justify-end items-center px-lg z-30 transition-all duration-200">
          <div className="flex items-center gap-md">
            <div className="flex items-center gap-3 cursor-pointer hover:bg-surface-container-high px-3 py-1.5 rounded-full transition-colors">
              <div className="w-8 h-8 rounded-full bg-primary-container text-on-primary-container flex items-center justify-center font-bold">
                {user?.full_name?.charAt(0) || 'U'}
              </div>
              <span className="font-label-md text-label-md text-on-surface font-medium">
                {user?.full_name || 'User'}
              </span>
              <span className="material-symbols-outlined text-secondary text-sm">expand_more</span>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <Outlet />
      </div>
    </div>
  );
}
