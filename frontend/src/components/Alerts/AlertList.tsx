import React from "react";
import AlertCard from "./AlertCard";

const AlertList: React.FC = () => {
  // placeholder alerts
  const alerts = [
    { title: "High Risk Transaction", description: "Transaction flagged as high risk", riskLevel: "high" as const },
    { title: "Medium Risk Transaction", description: "Transaction needs review", riskLevel: "medium" as const },
  ];

  return (
    <div>
      {alerts.map((alert, idx) => (
        <AlertCard key={idx} {...alert} />
      ))}
    </div>
  );
};

export default AlertList;
