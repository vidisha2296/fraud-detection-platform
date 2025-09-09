import React from "react";

interface RiskBadgeProps {
  level: "low" | "medium" | "high";
}

const RiskBadge: React.FC<RiskBadgeProps> = ({ level }) => {
  const colorMap = { low: "green", medium: "orange", high: "red" };
  return (
    <span style={{
      color: "#fff",
      backgroundColor: colorMap[level],
      padding: "0.25rem 0.5rem",
      borderRadius: "4px",
      fontWeight: "bold",
      textTransform: "uppercase"
    }}>
      {level}
    </span>
  );
};

export default RiskBadge;
