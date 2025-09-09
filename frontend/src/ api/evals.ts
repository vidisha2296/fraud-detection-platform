import client from "./client";

// Get all eval results
export const getEvals = async () => {
  const res = await client.get("/evals/results", {
    // params: { offset, limit }, // enable if backend supports pagination
  });
  return res.data; // returns eval results array
};


// Fetch eval metrics
export const getEvalMetrics = async () => {
  const res = await client.get("/evals/metrics");
  return res.data; // { total_cases, passed_cases, failed_cases, pass_rate }
};