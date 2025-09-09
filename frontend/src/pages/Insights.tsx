import React from "react";
import VirtualizedTable from "../components/Tables/VirtualizedTable";

const Insights: React.FC = () => {
  const categories = [
    { Category: "Food", Total: "$500" },
    { Category: "Travel", Total: "$300" },
  ];

  const topMerchants = [
    { Merchant: "Amazon", Amount: "$250" },
    { Merchant: "Uber", Amount: "$120" },
  ];

  return (
    <div className="container">
      <h1>Insights</h1>

      <div style={{ marginTop: "1rem" }}>
        <h2>Categories</h2>
        {/* <VirtualizedTable columns={["Category", "Total"]} data={categories} /> */}
      </div>

      <div style={{ marginTop: "2rem" }}>
        <h2>Top Merchants</h2>
        {/* <VirtualizedTable columns={["Merchant", "Amount"]} data={topMerchants} /> */}
      </div>
    </div>
  );
};

export default Insights;
