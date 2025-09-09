// components/Drawer/TriageDrawer.tsx
import React from "react";
import RiskBadge from "./RiskBadge";
import ActionButton from "../Actions/ActionButton";
import { FraudAlert } from "../Alerts/FraudAlerts";

interface TriageDrawerProps {
  alert: FraudAlert;
  onClose: () => void;
  onFreezeCard: (alertId: string, txnId: string) => void;
  onOpenDispute: (alertId: string) => void;
}

const TriageDrawer: React.FC<TriageDrawerProps> = ({ alert, onClose ,onFreezeCard,
  onOpenDispute,}) => {
  const traceSteps = [
    { step: "Validate Transaction", status: "ok", duration: "50ms", details: "Redacted" },
    { step: "Check KB", status: "error", duration: "120ms", details: "Redacted" },
    { step: "Risk Scoring", status: "ok", duration: "80ms", details: "Redacted" },
  ];

  return (
    <div style={{
      position: "fixed",
      right: 0,
      top: 0,
      height: "100%",
      width: "400px",
      backgroundColor: "#f9f9f9",
      boxShadow: "-2px 0 5px rgba(0,0,0,0.2)",
      padding: "1rem",
      overflowY: "auto",
      zIndex: 1000
    }}>
      <button
        onClick={onClose}
        style={{ position: "absolute", top: 10, right: 10, fontSize: 18 }}
      >
        ✕
      </button>

      <h2>Triage Details</h2>

      <div style={{ marginBottom: "1rem" }}>
        <h3>Risk Score</h3>
        <RiskBadge level={alert.score > 70 ? "high" : "medium"} />
      </div>

      <div style={{ marginBottom: "1rem" }}>
        <h3>Transaction Details</h3>
        <p><strong>Transaction ID:</strong> {alert.txn_id}</p>
        <p><strong>Customer ID:</strong> {alert.customer_id}</p>
        <p><strong>Reasons:</strong> {alert.reasons.join(", ") || "N/A"}</p>
      </div>

      <div style={{ marginBottom: "1rem" }}>
        <h3>Trace Steps</h3>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr>
              <th style={{ borderBottom: "1px solid #ccc" }}>Step</th>
              <th style={{ borderBottom: "1px solid #ccc" }}>Status</th>
              <th style={{ borderBottom: "1px solid #ccc" }}>Duration</th>
              <th style={{ borderBottom: "1px solid #ccc" }}>Details</th>
            </tr>
          </thead>
          <tbody>
            {traceSteps.map((step, idx) => (
              <tr key={idx}>
                <td>{step.step}</td>
                <td>{step.status}</td>
                <td>{step.duration}</td>
                <td>{step.details}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div style={{ marginTop: "1rem" }}>
        <h3>Actions</h3>
        <ActionButton
          label="Freeze Card"
          onClick={() => onFreezeCard(alert.customer_id,alert.txn_id)}
        />
        {/* <ActionButton
          label="Open Dispute"
          onClick={() => onOpenDispute(alert.txn_id)}
        /> */}
      </div>
    </div>
  );
};

export default TriageDrawer;
