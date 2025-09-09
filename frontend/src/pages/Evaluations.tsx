// import React from "react";
// import VirtualizedTable from "../components/Tables/VirtualizedTable";
// import ActionButton from "../components/Actions/ActionButton";

// const Evaluations: React.FC = () => {
//   const evals = [
//     { Candidate: "John Doe", Score: "85%", Status: "Pass" },
//     { Candidate: "Jane Smith", Score: "70%", Status: "Review" },
//   ];

//   return (
//     <div className="container">
//       <h1>Evaluations</h1>

//       <div style={{ marginTop: "1rem" }}>
//         {/* <VirtualizedTable columns={["Candidate", "Score", "Status"]} data={evals} /> */}
//       </div>

//       <div style={{ marginTop: "2rem" }}>
//         <ActionButton label="Run Eval" />
//       </div>
//     </div>
//   );
// };

// export default Evaluations;


import React, { useEffect, useState } from "react";
import VirtualizedTable from "../components/Tables/VirtualizedTable";
import ActionButton from "../components/Actions/ActionButton";
import { getEvals } from "../ api/evals"; // 🔥 import API

const Evaluations: React.FC = () => {
  const [results, setResults] = useState<any[]>([]);

  useEffect(() => {
    const fetchResults = async () => {
      try {
        const data = await getEvals();
        setResults(data);
      } catch (err) {
        console.error("Failed to fetch eval results", err);
      }
    };
    fetchResults();
  }, []);

  const columns = [
  { key: "eval_case_id", label: "Eval Case ID", dataKey: "eval_case_id", width: 250 },
  { key: "passed", label: "Passed", dataKey: "passed", width: 100 },
  { key: "execution_time", label: "Execution Time", dataKey: "execution_time", width: 150 },
  { key: "created_at", label: "Created At", dataKey: "created_at", width: 200 },
];


  const formattedData = results.map((r) => ({
    eval_case_id: r.eval_case_id,
    passed: r.passed === 1 ? "✅ Pass" : "❌ Fail",
    execution_time: r.execution_time.toFixed(6),
    created_at: new Date(r.created_at).toLocaleString(),
  }));

  return (
    <div className="container">
      <h1>Evaluations</h1>

      <div style={{ marginTop: "1rem" }}>
        <VirtualizedTable columns={columns} data={formattedData} />
      </div>

      <div style={{ marginTop: "2rem" }}>
        <ActionButton label="Run Eval" />
      </div>
    </div>
  );
};

export default Evaluations;
