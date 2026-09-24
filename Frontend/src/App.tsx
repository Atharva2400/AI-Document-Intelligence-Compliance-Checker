import { useState } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import Analyze from './pages/Analyze';
import Compliance from './pages/Compliance';
import RiskAnalysis from './pages/RiskAnalysis';
import VersionCompare from './pages/VersionCompare';
import Reports from './pages/Reports';
import { AnalysisProvider } from './context/AnalysisContext';
import './index.css';

function App() {
  const [analysisComplete, setAnalysisComplete] = useState(false);

  return (
    <AnalysisProvider>
      <BrowserRouter>
        <div className="min-h-screen bg-slate-50">
          <Navbar />
          <main>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route
                path="/analyze"
                element={
                  <Analyze
                    analysisComplete={analysisComplete}
                    setAnalysisComplete={setAnalysisComplete}
                  />
                }
              />
              <Route path="/compliance" element={<Compliance />} />
              <Route path="/risk" element={<RiskAnalysis />} />
              <Route path="/compare" element={<VersionCompare />} />
              <Route path="/reports" element={<Reports />} />
            </Routes>
          </main>
        </div>
      </BrowserRouter>
    </AnalysisProvider>
  );
}

export default App;
