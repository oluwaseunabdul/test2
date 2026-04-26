import { Routes, Route, Navigate } from 'react-router-dom';
import { useAppStore } from './store/appStore';
import Layout from './components/Layout';
import HomePage from './pages/HomePage';
import AnalysisPage from './pages/AnalysisPage';
import ProjectsPage from './pages/ProjectsPage';
import LoginPage from './pages/LoginPage';

function App() {
  const { theme } = useAppStore();

  return (
    <div className={theme}>
      <div className="min-h-screen bg-background">
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/" element={<Layout />}>
            <Route index element={<HomePage />} />
            <Route path="analysis" element={<AnalysisPage />} />
            <Route path="projects" element={<ProjectsPage />} />
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </div>
  );
}

export default App;
