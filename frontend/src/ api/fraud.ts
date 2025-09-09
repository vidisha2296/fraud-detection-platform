// api/fraud.ts
import { FraudAlert } from "../components/Alerts/FraudAlerts";
import client from "./client";

// Get alerts for a customer with pagination
export const getFraudAlerts = async (customerId: string, offset = 0, limit = 10) => {
  const res = await client.get(`/fraud/customer/${customerId}`, {
    params: { offset, limit },
  });
  return res.data; // { items: FraudAlert[], total: number }
};

// Get a single alert by ID
export const getFraudAlertById = async (alertId: string): Promise<FraudAlert> => {
  const res = await client.get(`/fraud/${alertId}`);
  return res.data;
};

// Create a new fraud alert
export const createFraudAlert = async (data: Partial<FraudAlert>) => {
  const res = await client.post(`/fraud/`, data);
  return res.data;
};

// Get fraud score for a customer
export const getFraudScore = async (customerId: string) => {
  const res = await client.get(`/fraud/score/${customerId}`);
  return res.data; // assuming { score: number }
};

// Assess fraud for a single customer/alert
export const assessFraud = async (data: { customer_id: string; alert_id?: string }) => {
  const res = await client.post(`/fraud/assess`, data);
  return res.data;
};

// Assess fraud in batch
export const assessFraudBatch = async (data: { customer_ids: string[] }) => {
  const res = await client.post(`/fraud/assess/batch`, data);
  return res.data;
};

// Get system status
export const getAgentSystemStatus = async () => {
  const res = await client.get(`/fraud/system/status`);
  return res.data; // e.g., { status: string, last_run: string, ... }
};

// Reset agent system
export const resetAgentSystem = async () => {
  const res = await client.post(`/fraud/system/reset`);
  return res.data;
};


// Freeze a card for a given alert
export const freezeCard = async (customer_id: string,txn_id: string) => {
  const res = await client.post(`/actions/freeze/${customer_id}/${txn_id}`);
  return res.data; // { success: boolean, message: string }
};

// Open dispute for a given alert
export const openDispute = async (txn_id: string) => {
  const res = await client.post(`/actions/dispute/${txn_id}`);
  return res.data; // { success: boolean, message: string }
};