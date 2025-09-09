import client from "./client";

export interface Transaction {
  id: string;
  customer_id: string;
  txn_id: string;
  merchant: string;
  category?: string | null;
  mcc?: string | null;
  amount: number;
  currency: string;
  timestamp: string;
  created_at?: string;
  updated_at?: string;
  action_type?: string;
  details?: Record<string, any>;
  status?: string;
}

// Response for paginated transactions
export interface TransactionResponse {
  items: Transaction[];
  total: number;
}

// GET transactions by customer (last 90 days)
export const getTransactions = async (
  customerId: string,
  skip: number = 0,
  limit: number = 10
): Promise<TransactionResponse> => {
  try {
    const response = await client.get(`/transactions/customer/${customerId}`, {
      params: { skip, limit },
    });
    return response.data;
  } catch (err) {
    console.error("Failed to fetch transactions", err);
    return { items: [], total: 0 };
  }
};

// POST ingest single or multiple transactions
export const ingestTransactions = async (
  data: Partial<Transaction> | Partial<Transaction>[]
) => {
  try {
    const payload = Array.isArray(data) ? data : [data];
    const response = await client.post(`/transactions/ingest`, payload);
    return response.data;
  } catch (err) {
    console.error("Failed to ingest transactions", err);
    return null;
  }
};

// POST ingest CSV/ZIP file
export const ingestTransactionsCSV = async (formData: FormData) => {
  try {
    const response = await client.post(`/transactions/ingest/csv`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return response.data;
  } catch (err) {
    console.error("Failed to ingest CSV/ZIP", err);
    return null;
  }
};

// NOTE: For live streaming, use TransactionStream component with EventSource
// getTransactionStream is kept only if you need a one-time fetch of stream data
export const getTransactionStream = async (): Promise<Transaction[]> => {
  try {
    const response = await client.get(`/transactions/stream`);
    return response.data;
  } catch (err) {
    console.error("Failed to fetch transaction stream", err);
    return [];
  }
};
