import { Link, Outlet, useNavigate } from 'react-router-dom';
import { Moon, Sun, LogOut, BookOpen, FolderOpen, Home } from 'lucide-react';
import { useAppStore } from '../store/appStore';
import { Button } from './ui/button';

export default function Layout() {
  const navigate = useNavigate();
  const { theme, toggleTheme } = useAppStore();

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  return (
    <div className="flex flex-col min-h-screen">
      <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container flex h-14 items-center justify-between">
          <div className="flex items-center gap-6">
            <Link to="/" className="flex items-center space-x-2">
              <BookOpen className="h-6 w-6" />
              <span className="font-bold">Research Discovery</span>
            </Link>
            <nav className="flex items-center gap-4">
              <Link to="/" className="flex items-center text-sm font-medium text-muted-foreground hover:text-foreground">
                <Home className="h-4 w-4 mr-1" />
                Home
              </Link>
              <Link to="/analysis" className="flex items-center text-sm font-medium text-muted-foreground hover:text-foreground">
                <BookOpen className="h-4 w-4 mr-1" />
                Analysis
              </Link>
              <Link to="/projects" className="flex items-center text-sm font-medium text-muted-foreground hover:text-foreground">
                <FolderOpen className="h-4 w-4 mr-1" />
                Projects
              </Link>
            </nav>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="icon" onClick={toggleTheme}>
              {theme === 'light' ? (
                <Moon className="h-5 w-5" />
              ) : (
                <Sun className="h-5 w-5" />
              )}
            </Button>
            <Button variant="ghost" size="icon" onClick={handleLogout}>
              <LogOut className="h-5 w-5" />
            </Button>
          </div>
        </div>
      </header>
      <main className="flex-1 container py-6">
        <Outlet />
      </main>
      <footer className="border-t py-6 md:py-0">
        <div className="container flex flex-col items-center justify-between gap-4 md:h-16 md:flex-row">
          <p className="text-sm text-muted-foreground">
            © 2024 Research Topic Discovery Platform. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
}
