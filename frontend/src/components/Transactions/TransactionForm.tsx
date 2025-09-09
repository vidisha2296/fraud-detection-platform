import React, { useState } from "react";
import { ingestTransactions } from "../../ api/transactions";
import Input from "../common/Input"; // adjust path as needed

interface Props {
  onSuccess: () => void;
}
type TransactionCreate = {
  customer_id: string;
  txn_id: string;
  merchant: string;
  category?: string | null;
  amount: number;
  currency: string;
  mcc?: string | null;
  timestamp: string;
};

const TransactionForm: React.FC<Props> = ({ onSuccess }) => {
  const [form, setForm] = useState<TransactionCreate>({
    customer_id: "",
    txn_id: "",
    merchant: "",
    amount: 0,
    currency: "USD",
    timestamp: new Date().toISOString(),
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await ingestTransactions(form);
    onSuccess();
  };

  return (
    <form onSubmit={handleSubmit} style={{ marginBottom: "1rem" }}>
      <Input
        label="Customer ID"
        value={form.customer_id}
        onChange={(val) => setForm({ ...form, customer_id: val })}
      />
      <Input
        label="Transaction ID"
        value={form.txn_id}
        onChange={(val) => setForm({ ...form, txn_id: val })}
      />
      <Input
        label="Merchant"
        value={form.merchant}
        onChange={(val) => setForm({ ...form, merchant: val })}
      />
      <Input
        label="Amount"
        value={form.amount.toString()}
        onChange={(val) =>
          setForm({ ...form, amount: parseFloat(val) || 0 })
        }
      />
      <button type="submit" style={{ padding: "0.5rem 1rem" }}>
        Add Transaction
      </button>
    </form>
  );
};

export default TransactionForm;
