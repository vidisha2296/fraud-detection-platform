// src/components/Dashboard/Metrics.tsx
import React, { useEffect, useState } from "react";
import client from "../../ api/client";

interface EvalsMetrics {
  total: number;
  passed: number;
  success_rate: number;
}

interface Metrics {
  transactions: number;
  fraud_alerts: number;
  evals: EvalsMetrics;
}

const MetricsComponent: React.FC = () => {
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchMetrics = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await client.get<Metrics>("/metrics");
        setMetrics(res.data);
      } catch (err) {
        console.error("Error fetching metrics:", err);
        setError("Failed to load metrics");
      } finally {
        setLoading(false);
      }
    };

    fetchMetrics();
  }, []);

  if (loading) return <p>Loading metrics...</p>;
  if (error) return <p style={{ color: "red" }}>{error}</p>;
  if (!metrics) return null;

  return (
    <div style={{ display: "flex", gap: "2rem", marginTop: "1rem" }}>
      <div>
        <h3>Transactions</h3>
        <p>{metrics.transactions}</p>
      </div>

      <div>
        <h3>Fraud Alerts</h3>
        <p>{metrics.fraud_alerts}</p>
      </div>

      <div>
        <h3>Evals</h3>
        <p>
          Total: {metrics.evals.total} <br />
          Passed: {metrics.evals.passed} <br />
          Success Rate: {metrics.evals.success_rate}%
        </p>
      </div>
    </div>
  );
};

export default MetricsComponent;
