// import React from "react";
// import KPIWidget from "./KPIWidget";
// import AlertList from "components/Alerts/AlertList";
// import ActionButton from "components/Actions/ActionButton";
// import TriageDrawer from "components/Drawer/TriageDrawer";
// import { useDrawer } from " hooks/useDrawer";

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



import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom"; // <-- import Link
import KPIWidget from "./KPIWidget";
import AlertList from "components/Alerts/AlertList";
import InsightsCharts from "components/Dashboard/InsightsCharts";
import MonitoringStatus from "components/Dashboard/MonitoringStatus";

const DashboardLayout: React.FC = () => {
  const [customerId, setCustomerId] = useState("");
  const [activeCustomer, setActiveCustomer] = useState<string | null>(null);

  const [kpis, setKpis] = useState({
    totalSpend: "$0",
    highRiskPct: "0%",
    disputesOpened: "0",
    avgTriageTime: "0s",
  });

  useEffect(() => {
    if (!activeCustomer) return;
    // TODO: fetch KPI data for activeCustomer
  }, [activeCustomer]);

  return (
    <div className="container">
      <h1>Dashboard</h1>

      {/* Navigation Links */}
      <div className="flex gap-4 mb-4">
        <Link to="/transactions" className="text-blue-600 hover:underline">Transactions</Link>
        <Link to="/fraud" className="text-blue-600 hover:underline">Fraud Alerts</Link>
        <Link to="/insights" className="text-blue-600 hover:underline">Insights</Link>
        <Link to="/kb" className="text-blue-600 hover:underline">Knowledge Base</Link>
        <Link to="/evals" className="text-blue-600 hover:underline">Evaluations</Link>
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
        <button
          onClick={() => setActiveCustomer(customerId)}
          disabled={!customerId}
        >
          Search
        </button>
      </div>

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
    </div>
  );
};

export default DashboardLayout;
