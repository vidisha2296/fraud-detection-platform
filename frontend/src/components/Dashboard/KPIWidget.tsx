import React from "react";

interface KPIWidgetProps {
  title: string;
  value: string | number;
}

const KPIWidget: React.FC<KPIWidgetProps> = ({ title, value }) => {
  return (
    <div style={{ padding: "1rem", backgroundColor: "#fff", borderRadius: "8px", flex: 1, boxShadow: "0 2px 4px rgba(0,0,0,0.1)" }}>
      <h3>{title}</h3>
      <p style={{ fontSize: "1.5rem", fontWeight: "bold" }}>{value}</p>
    </div>
  );
};

export default KPIWidget;
