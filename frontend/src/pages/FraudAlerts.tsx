// pages/FraudAlertsPage.tsx
import React, { useState } from "react";
import FraudAlerts from "../components/Alerts/FraudAlerts";
import ActionButton from "../components/Actions/ActionButton";
import {
  getFraudScore,
  assessFraud,
  assessFraudBatch,
  getAgentSystemStatus,
  resetAgentSystem,
} from "../ api/fraud";

interface FraudScore {
  customerId: string;
  score: number;
  reasons: string[];
  action: string | null;
}

const FraudAlertsPage: React.FC = () => {
  const [customerId, setCustomerId] = useState<string>("");
  const [selectedCustomer, setSelectedCustomer] = useState<string>("");
  const [fraudScore, setFraudScore] = useState<FraudScore | null>(null);
  const [systemStatus, setSystemStatus] = useState<any>(null);

  const handleSelectCustomer = () => {
    setSelectedCustomer(customerId);
    setFraudScore(null); // reset when customer changes
  };

  const handleInvestigate = async () => {
    if (!selectedCustomer) return;
    try {
      await assessFraud({ customer_id: selectedCustomer });
      alert("Fraud assessment triggered successfully");
    } catch (err) {
      console.error(err);
      alert("Failed to trigger fraud assessment");
    }
  };

  const handleBatchInvestigate = async () => {
    if (!selectedCustomer) return;
    try {
      await assessFraudBatch({ customer_ids: [selectedCustomer] });
      alert("Batch fraud assessment triggered successfully");
    } catch (err) {
      console.error(err);
      alert("Failed to trigger batch fraud assessment");
    }
  };

  const handleContactCustomer = () => {
    if (!selectedCustomer) return;
    alert(`Contact process triggered for Customer ${selectedCustomer}`);
  };

  const handleGetFraudScore = async () => {
    if (!selectedCustomer) return;
    try {
      const res = await getFraudScore(selectedCustomer);
      setFraudScore(res);
    } catch (err) {
      console.error(err);
      alert("Failed to fetch fraud score");
    }
  };

  const handleGetSystemStatus = async () => {
  try {
    const res = await getAgentSystemStatus();
    setSystemStatus(res);
  } catch (err: any) {
    console.error(err);
    if (err.response?.status === 429) {
      const retryAfter = err.response.data?.detail?.retryAfterMs || 0;
      alert(
        `Rate limit exceeded. Please try again after ${Math.ceil(
          retryAfter / 1000
        )} seconds.`
      );
    } else {
      alert("Failed to fetch system status");
    }
  }
};

  const handleResetSystem = async () => {
    try {
    const res = await resetAgentSystem();
     alert("Agent system reset successfully");
    setSystemStatus(null);
  } catch (err: any) {
    console.error(err);
    if (err.response?.status === 429) {
  const retryAfter = err.response.data?.detail?.retryAfterMs || 0;
  alert(
    `Rate limit exceeded. Please try again after ${Math.ceil(retryAfter / 1000)} seconds.`
  );
} else {
      alert("Failed to fetch system status");
    }
  }
  };

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-2xl font-bold mb-6">Fraud Alerts Dashboard</h1>

      {/* Customer selection */}
      <div className="flex items-center gap-2 mb-6">
        <input
          type="text"
          placeholder="Enter Customer ID"
          value={customerId}
          onChange={(e) => setCustomerId(e.target.value)}
          className="border px-3 py-2 rounded w-64"
        />
        <ActionButton label="Load Alerts" onClick={handleSelectCustomer} />
      </div>

      {/* Alerts */}
      {selectedCustomer && (
        <div className="mb-6">
          <FraudAlerts customerId={selectedCustomer} />
        </div>
      )}

      {/* Actions */}
      {selectedCustomer && (
        <div className="mb-8">
          <h2 className="text-xl font-semibold mb-4">Actions</h2>
          <div className="flex flex-wrap gap-3">
            {/* <ActionButton label="Investigate" onClick={handleInvestigate} />
            <ActionButton
              label="Batch Investigate"
              onClick={handleBatchInvestigate}
            />
            <ActionButton
              label="Contact Customer"
              onClick={handleContactCustomer}
            /> */}
            <ActionButton
              label="Get Fraud Score"
              onClick={handleGetFraudScore}
            />
          </div>

          {fraudScore && (
            <div className="mt-4 p-4 bg-gray-50 rounded-lg shadow border w-fit">
              <p>
                <strong>Customer:</strong> {fraudScore.customerId}
              </p>
              <p>
                <strong>Score:</strong> {fraudScore.score}
              </p>
              <p>
                <strong>Reasons:</strong>{" "}
                {fraudScore.reasons?.length > 0
                  ? fraudScore.reasons.join(", ")
                  : "None"}
              </p>
              <p>
                <strong>Action:</strong> {fraudScore.action || "None"}
              </p>
            </div>
          )}
        </div>
      )}

      {/* System controls */}
       <div>
  <h2 className="text-xl font-semibold mb-4">System Controls</h2>
  <div className="flex gap-4 mb-6">
    <ActionButton label="Get System Status" onClick={handleGetSystemStatus} />
    <ActionButton label="Reset System" onClick={handleResetSystem} />
  </div>

  {/* Agent + System status */}
  {systemStatus && (
    <div>
      <h2 className="text-xl font-semibold mb-4">Agent Status</h2>
      <div className="flex gap-4 overflow-x-auto pb-2">
        {Object.entries(systemStatus)
          .filter(([key]) => key !== "system_status")
          .map(([agentName, agent]: any) => (
            <div
              key={agentName}
              className="flex-shrink-0 flex flex-col justify-between border rounded-lg shadow-md p-4 w-64 bg-white"
            >
              <h3 className="text-lg font-medium capitalize">
                {agent.name.replace("_", " ")}
              </h3>
              <p className="text-sm">
                <strong>State:</strong>{" "}
                <span
                  className={`px-2 py-1 rounded ${
                    agent.state === "closed"
                      ? "bg-green-100 text-green-700"
                      : "bg-red-100 text-red-700"
                  }`}
                >
                  {agent.state}
                </span>
              </p>
              <p className="text-sm">
                <strong>Failures:</strong> {agent.failures}
              </p>
              <p className="text-sm">
                <strong>Last Failure:</strong> {agent.last_failure || "None"}
              </p>
            </div>
          ))}

        {/* System status card */}
        <div className="flex-shrink-0 flex flex-col justify-center border rounded-lg shadow-md p-4 w-64 bg-gray-50">
          <h3 className="text-lg font-medium">System Status</h3>
          <p className="mt-2 font-semibold">
            <span className="px-2 py-1 rounded bg-green-100 text-green-700">
              {systemStatus.system_status}
            </span>
          </p>
        </div>
      </div>
    </div>
  )}
</div>

    </div>
  );
};

export default FraudAlertsPage;
