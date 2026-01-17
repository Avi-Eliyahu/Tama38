import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Projects from './pages/Projects';
import ProjectDetail from './pages/ProjectDetail';
import ProjectWizard from './pages/ProjectWizard';
import Buildings from './pages/Buildings';
import BuildingDetail from './pages/BuildingDetail';
import UnitDetail from './pages/UnitDetail';
import Owners from './pages/Owners';
import OwnerDetail from './pages/OwnerDetail';
import Interactions from './pages/Interactions';
import Tasks from './pages/Tasks';
import Approvals from './pages/Approvals';
import Alerts from './pages/Alerts';
import Reports from './pages/Reports';
import SignDocument from './pages/SignDocument';
import AgentMobile from './pages/AgentMobile';
import Layout from './components/Layout';
import { authService } from './services/auth';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  if (!authService.isAuthenticated()) {
    return <Navigate to="/login" replace />;
  }
  return <Layout>{children}</Layout>;
}

function NavigateToDefault() {
  const user = authService.getCurrentUserSync();
  // Agents default to agent mobile view, others to dashboard
  const defaultPath = user?.role === 'AGENT' ? '/agent' : '/dashboard';
  return <Navigate to={defaultPath} replace />;
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/sign/:token" element={<SignDocument />} />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/projects"
          element={
            <ProtectedRoute>
              <Projects />
            </ProtectedRoute>
          }
        />
        <Route
          path="/projects/new"
          element={
            <ProtectedRoute>
              <ProjectWizard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/projects/:projectId"
          element={
            <ProtectedRoute>
              <ProjectDetail />
            </ProtectedRoute>
          }
        />
        <Route
          path="/buildings"
          element={
            <ProtectedRoute>
              <Buildings />
            </ProtectedRoute>
          }
        />
        <Route
          path="/buildings/:buildingId"
          element={
            <ProtectedRoute>
              <BuildingDetail />
            </ProtectedRoute>
          }
        />
        <Route
          path="/units/:unitId"
          element={
            <ProtectedRoute>
              <UnitDetail />
            </ProtectedRoute>
          }
        />
        <Route
          path="/owners"
          element={
            <ProtectedRoute>
              <Owners />
            </ProtectedRoute>
          }
        />
        <Route
          path="/owners/:ownerId"
          element={
            <ProtectedRoute>
              <OwnerDetail />
            </ProtectedRoute>
          }
        />
        <Route
          path="/interactions"
          element={
            <ProtectedRoute>
              <Interactions />
            </ProtectedRoute>
          }
        />
        <Route
          path="/tasks"
          element={
            <ProtectedRoute>
              <Tasks />
            </ProtectedRoute>
          }
        />
        <Route
          path="/approvals"
          element={
            <ProtectedRoute>
              <Approvals />
            </ProtectedRoute>
          }
        />
        <Route
          path="/alerts"
          element={
            <ProtectedRoute>
              <Alerts />
            </ProtectedRoute>
          }
        />
        <Route
          path="/reports"
          element={
            <ProtectedRoute>
              <Reports />
            </ProtectedRoute>
          }
        />
        <Route
          path="/agent"
          element={
            <ProtectedRoute>
              <AgentMobile />
            </ProtectedRoute>
          }
        />
        <Route path="/" element={<NavigateToDefault />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;


