// import React from "react";
// import KPIWidget from "../components/Dashboard/KPIWidget";
// import AlertList from "../components/Alerts/AlertList";
// import ActionButton from "../components/Actions/ActionButton";
// import TriageDrawer from "../components/Drawer/TriageDrawer";
// import { useDrawer } from "../ hooks/useDrawer";

// const DashboardLayout: React.FC = () => {
//   const { open, openDrawer, closeDrawer } = useDrawer();

//   return (
//     <div className="container">
//       <h1>Dashboard</h1>

//       {/* KPI Widgets */}
//       <div style={{ display: "flex", gap: "1rem", marginTop: "1rem" }}>
//         <KPIWidget title="Total Spend" value="$0" />
//         <KPIWidget title="% High-Risk Alerts" value="0%" />
//         <KPIWidget title="Disputes Opened" value="0" />
//         <KPIWidget title="Avg Triage Time" value="0s" />
//       </div>

//       {/* Alerts */}
//       <div style={{ marginTop: "2rem" }}>
//         <h2>Alerts</h2>
//         <AlertList />
//       </div>

//       {/* Actions */}
//       <div style={{ marginTop: "2rem" }}>
//         <h2>Actions</h2>
//         <ActionButton label="Open Triage Drawer" onClick={openDrawer} />
//         <ActionButton label="Freeze Card" />
//       </div>

//       {/* Triage Drawer */}
//       {/* {open && <TriageDrawer />} */}
//     </div>
//   );
// };

// export default DashboardLayout;



import React, { useState, useEffect, useRef } from "react";
import { Link } from "react-router-dom";
import KPIWidget from "../components/Dashboard/KPIWidget";
import AlertList from "../components/Alerts/AlertList";
import InsightsCharts from "../components/Dashboard/InsightsCharts";
import MonitoringStatus from "../components/Dashboard/MonitoringStatus";
import Metrics from "../components/Dashboard/Metrics";
import apiClient from "../ api/client";

const RATE_LIMIT_MS = 5000; // Minimum 5 seconds between requests

const DashboardLayout: React.FC = () => {
  const [customerId, setCustomerId] = useState("");
  const [activeCustomer, setActiveCustomer] = useState<string | null>(null);
  const [kpis, setKpis] = useState({
    totalSpend: "$0",
    highRiskPct: "0%",
    disputesOpened: "0",
    avgTriageTime: "0s",
  });
  const lastFetchRef = useRef<number>(0); // Timestamp of last API call
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!activeCustomer) return;

    const now = Date.now();
    if (now - lastFetchRef.current < RATE_LIMIT_MS) {
      console.warn("Rate limit: Please wait before fetching again.");
      return;
    }

    const fetchMetrics = async () => {
      setLoading(true);
      setError(null);

      try {
        const response = await apiClient.get(`/fraud/customer-metrics/${activeCustomer}`);
        const data = response.data;

        setKpis({
          totalSpend: `$${data.totalSpend.toFixed(2)}`,
          highRiskPct: `${data.highRiskPct.toFixed(1)}%`,
          disputesOpened: data.disputesOpened.toString(),
          avgTriageTime: data.avgTriageTime ? `${data.avgTriageTime.toFixed(0)}s` : "N/A",
        });

        lastFetchRef.current = Date.now(); // Update last fetch timestamp
      } catch (err) {
        console.error("Failed to fetch customer metrics:", err);
        setError("Failed to fetch metrics. Try again later.");
        setKpis({
          totalSpend: "$0",
          highRiskPct: "0%",
          disputesOpened: "0",
          avgTriageTime: "N/A",
        });
      } finally {
        setLoading(false);
      }
    };

    fetchMetrics();
  }, [activeCustomer]);

  const handleSearch = () => {
    if (!customerId) return;
    setActiveCustomer(customerId);
  };

  return (
    <div className="dashboard-container" style={{ height: "100vh", overflowY: "auto", padding: "1rem", boxSizing: "border-box" }}>
      <h1>Dashboard</h1>

      {/* Dashboard Navigation Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4 mb-6">
        <Link to="/transactions" className="flex flex-col items-center justify-center p-4 bg-white shadow rounded-lg hover:shadow-lg transition cursor-pointer">
          <span className="text-3xl mb-2">💳</span>
          <span className="font-semibold text-center">Transactions</span>
        </Link>
        <Link to="/fraud" className="flex flex-col items-center justify-center p-4 bg-white shadow rounded-lg hover:shadow-lg transition cursor-pointer">
          <span className="text-3xl mb-2">🚨</span>
          <span className="font-semibold text-center">Fraud Alerts</span>
        </Link>
        <Link to="/insights" className="flex flex-col items-center justify-center p-4 bg-white shadow rounded-lg hover:shadow-lg transition cursor-pointer">
          <span className="text-3xl mb-2">📊</span>
          <span className="font-semibold text-center">Insights</span>
        </Link>
        <Link to="/kb" className="flex flex-col items-center justify-center p-4 bg-white shadow rounded-lg hover:shadow-lg transition cursor-pointer">
          <span className="text-3xl mb-2">📚</span>
          <span className="font-semibold text-center">Knowledge Base</span>
        </Link>
        <Link to="/evals" className="flex flex-col items-center justify-center p-4 bg-white shadow rounded-lg hover:shadow-lg transition cursor-pointer">
          <span className="text-3xl mb-2">🧪</span>
          <span className="font-semibold text-center">Evaluations</span>
        </Link>
      </div>

      {/* Search Field */}
      <div style={{ marginTop: "1rem", marginBottom: "1.5rem" }}>
        <input
          type="text"
          placeholder="Enter Customer ID"
          value={customerId}
          onChange={(e) => setCustomerId(e.target.value)}
          style={{ padding: "0.5rem", marginRight: "0.5rem" }}
        />
        <button onClick={handleSearch} disabled={!customerId || loading}>
          {loading ? "Fetching..." : "Search"}
        </button>
      </div>

      {error && <p style={{ color: "red" }}>{error}</p>}

      {activeCustomer ? (
        <>
          {/* KPI Widgets */}
          <div style={{ display: "flex", gap: "1rem", marginTop: "1rem" }}>
            <KPIWidget title="Total Spend" value={kpis.totalSpend} />
            <KPIWidget title="% High-Risk Alerts" value={kpis.highRiskPct} />
            <KPIWidget title="Disputes Opened" value={kpis.disputesOpened} />
            <KPIWidget title="Avg Triage Time" value={kpis.avgTriageTime} />
          </div>

          {/* Alerts Preview */}
          <div style={{ marginTop: "2rem" }}>
            <h2>Recent Fraud Alerts</h2>
            {/* You can uncomment below when AlertList supports fetching by customerId */}
            {/* <AlertList customerId={activeCustomer} limit={5} /> */}
          </div>

          {/* Insights */}
          <div style={{ marginTop: "2rem" }}>
            <h2>Insights</h2>
            <InsightsCharts customerId={activeCustomer} />
          </div>
        </>
      ) : (
        <p style={{ marginTop: "2rem" }}>🔍 Please enter a Customer ID to view dashboard data.</p>
      )}

      {/* Monitoring */}
      <div style={{ marginTop: "2rem" }}>
        <h2>System Monitoring</h2>
        <MonitoringStatus />
      </div>

      {/* Metrics */}
      <div style={{ marginTop: "2rem", marginBottom: "2rem" }}>
        <h2>Metrics</h2>
        <Metrics />
      </div>
    </div>
  );
};

export default DashboardLayout;
