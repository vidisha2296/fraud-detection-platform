import React, { useEffect, useState } from "react";
import VirtualizedTable from "../components/Tables/VirtualizedTable";
import Pagination from "../utils/Pagination";
import { getTransactions, Transaction } from "../ api/transactions";
import Input from "../components/common/Input";
import TransactionForm from "../components/Transactions/TransactionForm";
import TransactionBulkUpload from "../components/Transactions/TransactionBulkUpload";
import TransactionStream from "../components/Transactions/TransactionStream";

const Transactions: React.FC = () => {
  const [data, setData] = useState<Transaction[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [customerId, setCustomerId] = useState("");
  const [searchId, setSearchId] = useState("");
  const [loading, setLoading] = useState(false);

  const pageSize = 10;

  const fetchTransactions = async () => {
    if (!searchId) return;
    setLoading(true);
    try {
      const res = await getTransactions(searchId, (page - 1) * pageSize, pageSize);
      setData(res.items || []);
      setTotal(res.total || 0);
    } catch (err) {
      console.error(err);
      setData([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTransactions();
  }, [page, searchId]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = customerId.trim();
    if (!trimmed) return;
    setPage(1);
    setSearchId(trimmed);
  };

  const handleSSEUpdate = (newTxn: Transaction) => {
    if (searchId) return;
    setData((prev) => {
      if (prev.find((t) => t.id === newTxn.id)) return prev;
      return [newTxn, ...prev];
    });
    setTotal((prevTotal) => prevTotal + 1);
  };

  const columns = [
    { key: "txn_id", label: "Transaction ID", render: (val: string) => `txn_${val.slice(-5)}` },
    { key: "customer_id", label: "Customer" },
    { key: "merchant", label: "Merchant" },
    { key: "amount", label: "Amount", render: (val: number) => val.toFixed(2) },
    { key: "currency", label: "Currency" },
    { key: "timestamp", label: "Timestamp", render: (val: string) => new Date(val).toLocaleString() },
  ];

  return (
    <div className="container" style={{ maxHeight: "90vh", overflowY: "auto", padding: "1rem" }}>
      <h1>Transactions</h1>

      {/* Search box */}
      <form onSubmit={handleSearch} style={{ display: "flex", gap: "0.5rem", marginBottom: "1rem" }}>
        <Input value={customerId} onChange={setCustomerId} placeholder="Enter Customer ID" />
        <button type="submit" disabled={!customerId.trim()}>Search</button>
      </form>

      {/* Transaction management */}
      {/* <div style={{ display: "flex", gap: "1rem", marginBottom: "1rem", flexWrap: "wrap" }}>
        <TransactionForm onSuccess={fetchTransactions} />
        <TransactionBulkUpload onSuccess={fetchTransactions} />
      </div> */}

      {!searchId && <TransactionStream onMessage={handleSSEUpdate} />}

      {/* Table and Pagination */}
      <div style={{ marginTop: "1rem" }}>
        {loading ? (
          <p>Loading...</p>
        ) : data.length > 0 ? (
          <>
            <div style={{ maxHeight: "60vh", overflowY: "auto" }}>
              <VirtualizedTable columns={columns} data={data} />
            </div>
            {total > pageSize && (
              <div style={{ marginTop: "0.5rem" }}>
                <Pagination currentPage={page} totalItems={total} pageSize={pageSize} onPageChange={setPage} />
              </div>
            )}
          </>
        ) : searchId ? (
          <p>No transactions found for "{searchId}"</p>
        ) : (
          <p>Enter a Customer ID to search transactions.</p>
        )}
      </div>
    </div>
  );
};

export default Transactions;
