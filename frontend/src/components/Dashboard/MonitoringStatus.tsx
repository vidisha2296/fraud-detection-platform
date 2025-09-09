import React, { useState } from "react";
import client from "../../ api/client";

interface AgentStatus {
  state: string;
  failures: number;
  last_failure: string | null;
}

interface SystemStatus {
  orchestrator: AgentStatus;
  insights_agent: AgentStatus;
  fraud_agent: AgentStatus;
  kb_agent: AgentStatus;
  compliance_agent: AgentStatus;
  system_status: string;
}

const MonitoringStatus: React.FC = () => {
  const [health, setHealth] = useState<string>("Not fetched");
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchStatus = async () => {
    setLoading(true);
    setError(null);

    try {
      // Service health
      const healthRes = await client.get("/health");
      setHealth(healthRes.data?.status || "Unknown");
    } catch (err: any) {
      console.error("Error fetching service health:", err);
      setHealth("❌ Unreachable");
    }

    try {
      // Fraud system & agents status
      const res = await client.get<SystemStatus>("/fraud/system/status");
      setSystemStatus(res.data);
    } catch (err: any) {
      console.error("Error fetching system status:", err);

      if (err.response?.status === 429) {
        setError(
          `Rate limit exceeded. Try again in ${Math.ceil(
            (err.response.data.detail.retryAfterMs || 30000) / 1000
          )} seconds.`
        );
      } else {
        setError("Unable to fetch system status");
      }

      setSystemStatus(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-2 border rounded-lg bg-gray-50 shadow-md">
      <div className="flex items-center justify-between mb-2">
        <strong>System Monitoring</strong>
        <button
          onClick={fetchStatus}
          disabled={loading}
          className="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? "Loading..." : "Refresh"}
        </button>
      </div>

      <p>
        <strong>Service Health:</strong> {health}
      </p>

      {error && <p className="text-red-600">{error}</p>}

      {systemStatus && (
        <div className="mt-2">
          <p>
            <strong>System Overall Status:</strong> {systemStatus.system_status}
          </p>
          <ul className="list-disc pl-5">
            <li>
              <strong>Orchestrator:</strong> {systemStatus.orchestrator.state} (
              {systemStatus.orchestrator.failures} failures)
            </li>
            <li>
              <strong>Insights Agent:</strong> {systemStatus.insights_agent.state} (
              {systemStatus.insights_agent.failures} failures)
            </li>
            <li>
              <strong>Fraud Agent:</strong> {systemStatus.fraud_agent.state} (
              {systemStatus.fraud_agent.failures} failures)
            </li>
            <li>
              <strong>KB Agent:</strong> {systemStatus.kb_agent.state} (
              {systemStatus.kb_agent.failures} failures)
            </li>
            <li>
              <strong>Compliance Agent:</strong> {systemStatus.compliance_agent.state} (
              {systemStatus.compliance_agent.failures} failures)
            </li>
          </ul>
        </div>
      )}
    </div>
  );
};

export default MonitoringStatus;
