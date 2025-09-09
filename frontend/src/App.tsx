import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import Transactions from "./pages/Transactions";
import FraudAlerts from "./pages/FraudAlerts";
import Insights from "./pages/Insights";
import KBSearch from "./pages/KBSearch";
import Evaluations from "./pages/Evaluations";

const App: React.FC = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/transactions" element={<Transactions />} />
        <Route path="/fraud" element={<FraudAlerts />} />
        <Route path="/insights" element={<Insights />} />
        <Route path="/kb" element={<KBSearch />} />
        <Route path="/evals" element={<Evaluations />} />
      </Routes>
    </Router>
  );
};

export default App;
