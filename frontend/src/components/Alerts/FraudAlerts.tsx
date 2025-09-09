import React, { useEffect, useState } from "react";
import { getFraudAlerts, getFraudAlertById, openDispute,freezeCard } from "../../ api/fraud";
import Pagination from "../../utils/Pagination";
import TriageDrawer from "../Drawer/TriageDrawer";
export interface FraudAlert {
  id: string;
  txn_id: string;
  score: number;
  reasons: string[];
  customer_id: string;
  action_taken?: string;
  timestamp: string;
}

interface FraudAlertsProps {
  customerId: string;
}

const pageSize = 10;

const FraudAlerts: React.FC<FraudAlertsProps> = ({ customerId }) => {
  const [alerts, setAlerts] = useState<FraudAlert[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [selectedAlert, setSelectedAlert] = useState<FraudAlert | null>(null);

  const fetchAlerts = async () => {
    if (!customerId) return;
    setLoading(true);
    try {
      const res = await getFraudAlerts(customerId, (page - 1) * pageSize, pageSize);
      setAlerts(res.items || []);
      setTotal(res.total || 0);
    } catch (err) {
      console.error(err);
      setAlerts([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
  }, [customerId, page]);

  const viewDetails = async (alertId: string) => {
    try {
      const res = await getFraudAlertById(alertId);
      setSelectedAlert(res);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="p-6 bg-gray-50 rounded-xl shadow-md">
      <h2 className="text-xl font-semibold mb-4 text-gray-800">Fraud Alerts</h2>

      {loading ? (
        <p className="text-gray-500">Loading alerts...</p>
      ) : alerts.length === 0 ? (
        <p className="text-gray-500">No alerts for this customer.</p>
      ) : (
        <>
          <div className="overflow-x-auto">
            <table className="w-full border-collapse bg-white shadow rounded-lg">
              <thead>
                <tr className="bg-gray-100 text-gray-700 text-sm">
                  <th className="p-3 text-left">Alert ID</th>
                  <th className="p-3 text-left">Transaction ID</th>
                  <th className="p-3 text-left">Score</th>
                  <th className="p-3 text-left">Reasons</th>
                  <th className="p-3 text-left">Action Taken</th>
                  <th className="p-3 text-left">Created At</th>
                  <th className="p-3 text-center">Action</th>
                </tr>
              </thead>
              <tbody>
                {alerts.map((alert, idx) => (
                  <tr
                    key={alert.id}
                    className={`text-sm ${
                      idx % 2 === 0 ? "bg-white" : "bg-gray-50"
                    } hover:bg-gray-100`}
                  >
                    <td className="p-3">{alert.id}</td>
                    <td className="p-3">{alert.txn_id}</td>
                    <td className="p-3 font-semibold text-red-600">{alert.score}</td>
                    <td className="p-3">
                      {alert.reasons?.length > 0
                        ? alert.reasons.join(", ")
                        : "N/A"}
                    </td>
                    <td className="p-3 capitalize">{alert.action_taken || "N/A"}</td>
                    <td className="p-3">{new Date(alert.timestamp).toLocaleString()}</td>
                    <td className="p-3 text-center">
                      <button
                        onClick={() => viewDetails(alert.id)}
                        className="px-3 py-1 text-sm bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition"
                      >
                        View
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {total > pageSize && (
            <div className="mt-4">
              <Pagination
                currentPage={page}
                totalItems={total}
                pageSize={pageSize}
                onPageChange={setPage}
              />
            </div>
          )}
        </>
      )}

      {selectedAlert && (
      <TriageDrawer
  alert={selectedAlert}
  onClose={() => setSelectedAlert(null)}
  onFreezeCard={async (alertId: string, txnId: string) => {
    try {
      const res = await freezeCard(alertId, txnId);
      alert(res.message || "Card frozen successfully");
      fetchAlerts();
      setSelectedAlert(null);
    } catch (err: any) {
      console.error("Freeze card error:", err);
      alert(err.response?.data?.message || "Failed to freeze card");
    }
  }}
  onOpenDispute={async (alertId: string) => {
    try {
      const res = await openDispute(alertId);
      alert(res.message || "Dispute opened successfully");
      fetchAlerts();
      setSelectedAlert(null);
    } catch (err: any) {
      console.error("Open dispute error:", err);
      alert(err.response?.data?.message || "Failed to open dispute");
    }
  }}
/>

)}

    </div>
  );
};

export default FraudAlerts;
