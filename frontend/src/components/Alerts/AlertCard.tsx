import React from "react";

interface AlertCardProps {
  title: string;
  description: string;
  riskLevel: "low" | "medium" | "high";
}

const AlertCard: React.FC<AlertCardProps> = ({ title, description, riskLevel }) => {
  const colorMap = { low: "green", medium: "orange", high: "red" };
  return (
    <div style={{ border: `1px solid ${colorMap[riskLevel]}`, borderRadius: "8px", padding: "1rem", marginBottom: "1rem", backgroundColor: "#fff" }}>
      <h3>{title}</h3>
      <p>{description}</p>
      <span style={{ color: colorMap[riskLevel], fontWeight: "bold" }}>{riskLevel.toUpperCase()}</span>
    </div>
  );
};

export default AlertCard;
