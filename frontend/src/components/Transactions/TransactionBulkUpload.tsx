import React, { useState } from "react";
import { ingestTransactionsCSV } from"../../ api/transactions";

interface Props {
  onSuccess: () => void;
}

const TransactionBulkUpload: React.FC<Props> = ({ onSuccess }) => {
  const [file, setFile] = useState<File | null>(null);

  const handleUpload = async () => {
    if (!file) return;

    // Wrap file in FormData
    const formData = new FormData();
    formData.append("file", file);

    await ingestTransactionsCSV(formData);
    onSuccess();
  };

  return (
    <div style={{ marginBottom: "1rem" }}>
      <input
        type="file"
        accept=".csv,.zip"
        onChange={(e) => setFile(e.target.files?.[0] ?? null)}
      />
      <button onClick={handleUpload} style={{ padding: "0.5rem 1rem" }}>
        Upload CSV/ZIP
      </button>
    </div>
  );
};

export default TransactionBulkUpload;
