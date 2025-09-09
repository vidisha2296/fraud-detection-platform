import React, { useState } from "react";
import Input from "../components/common/Input";

const KBSearch: React.FC = () => {
  const [query, setQuery] = useState("");

  return (
    <div className="container">
      <h1>Knowledge Base Search</h1>

      <div style={{ marginTop: "1rem" }}>
        <Input label="Search KB" value={query} onChange={setQuery} placeholder="Enter keyword..." />
      </div>

      <div style={{ marginTop: "1rem" }}>
        <p>Search results will appear here (placeholder).</p>
      </div>
    </div>
  );
};

export default KBSearch;
