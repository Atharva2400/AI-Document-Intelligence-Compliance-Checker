import { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import {
  Brain,
  LayoutDashboard,
  FileSearch,
  ShieldCheck,
  AlertTriangle,
  GitCompare,
  FileBarChart2,
  Menu,
  X,
  BadgeCheck,
  ChevronRight,
} from 'lucide-react';

const navLinks = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/analyze', label: 'Analyze', icon: FileSearch },
  { to: '/compliance', label: 'Compliance', icon: ShieldCheck },
  { to: '/risk', label: 'Risk Analysis', icon: AlertTriangle },
  { to: '/compare', label: 'Version Compare', icon: GitCompare },
  { to: '/reports', label: 'Reports', icon: FileBarChart2 },
];

export default function Navbar() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();

  return (
    <header className="sticky top-0 z-50 bg-white border-b border-slate-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2.5 shrink-0">
            <div className="flex items-center justify-center w-9 h-9 rounded-xl bg-gradient-to-br from-blue-600 to-violet-600 shadow-md shadow-blue-200">
              <Brain className="w-5 h-5 text-white" />
            </div>
            <div className="hidden sm:block">
              <span className="text-sm font-bold text-slate-900 leading-none block">AI Document</span>
              <span className="text-xs font-medium text-blue-600 leading-none">Intelligence</span>
            </div>
          </Link>

          {/* Desktop Nav */}
          <nav className="hidden lg:flex items-center gap-1">
            {navLinks.map(({ to, label, icon: Icon }) => {
              const active = location.pathname === to;
              return (
                <Link
                  key={to}
                  to={to}
                  className={`flex items-center gap-1.5 px-3.5 py-2 rounded-lg text-sm font-medium transition-all duration-150 ${
                    active
                      ? 'bg-blue-50 text-blue-700'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {label}
                </Link>
              );
            })}
          </nav>

          {/* Right actions */}
          <div className="hidden lg:flex items-center gap-3">
            <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-amber-50 border border-amber-200 text-xs font-semibold text-amber-700">
              <BadgeCheck className="w-3.5 h-3.5" />
              Demo Mode
            </span>
            <button
              onClick={() => navigate('/analyze')}
              className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-gradient-to-r from-blue-600 to-violet-600 text-white text-sm font-semibold shadow-sm hover:shadow-md hover:from-blue-700 hover:to-violet-700 transition-all duration-200"
            >
              <FileSearch className="w-4 h-4" />
              Analyze Document
              <ChevronRight className="w-3.5 h-3.5" />
            </button>
          </div>

          {/* Mobile hamburger */}
          <button
            className="lg:hidden p-2 rounded-lg text-slate-600 hover:bg-slate-100 transition-colors"
            onClick={() => setMobileOpen(!mobileOpen)}
            aria-label="Toggle menu"
          >
            {mobileOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {/* Mobile menu */}
      {mobileOpen && (
        <div className="lg:hidden border-t border-slate-100 bg-white px-4 pb-4 pt-2 space-y-1">
          {navLinks.map(({ to, label, icon: Icon }) => {
            const active = location.pathname === to;
            return (
              <Link
                key={to}
                to={to}
                onClick={() => setMobileOpen(false)}
                className={`flex items-center gap-2 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  active
                    ? 'bg-blue-50 text-blue-700'
                    : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                }`}
              >
                <Icon className="w-4 h-4" />
                {label}
              </Link>
            );
          })}
          <div className="pt-3 border-t border-slate-100 flex flex-col gap-2">
            <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-amber-50 border border-amber-200 text-xs font-semibold text-amber-700 w-fit">
              <BadgeCheck className="w-3.5 h-3.5" />
              Demo Mode
            </span>
            <button
              onClick={() => { navigate('/analyze'); setMobileOpen(false); }}
              className="flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg bg-gradient-to-r from-blue-600 to-violet-600 text-white text-sm font-semibold"
            >
              <FileSearch className="w-4 h-4" />
              Analyze Document
            </button>
          </div>
        </div>
      )}
    </header>
  );
}
