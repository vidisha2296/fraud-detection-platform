import React from "react";

interface Column {
  key: string; // field in your data
  label: string; // header label
  render?: (value: any, row?: any) => React.ReactNode; // optional custom renderer
}

interface VirtualizedTableProps {
  columns?: Column[]; // optional
  data?: any[]; // optional
}

const VirtualizedTable: React.FC<VirtualizedTableProps> = ({
  columns = [],
  data = [],
}) => {
  return (
    <div
      style={{
        maxHeight: "400px",
        overflowY: "auto",
        border: "1px solid #ccc",
        borderRadius: "8px",
        backgroundColor: "#fff",
      }}
    >
      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr>
            {columns.map((col, idx) => (
              <th
                key={idx}
                style={{
                  position: "sticky",
                  top: 0,
                  backgroundColor: "#f9f9f9",
                  padding: "0.5rem",
                  borderBottom: "2px solid #ccc",
                  textAlign: "left",
                  zIndex: 1,
                  maxWidth: "150px",
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                  whiteSpace: "nowrap",
                }}
              >
                {col.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.length === 0 ? (
            <tr>
              <td
                colSpan={columns.length}
                style={{ textAlign: "center", padding: "1rem" }}
              >
                No data available
              </td>
            </tr>
          ) : (
            data.map((row, idx) => (
              <tr key={idx}>
                {columns.map((col, cidx) => (
                  <td
                    key={cidx}
                    style={{
                      padding: "0.5rem",
                      borderBottom: "1px solid #eee",
                      maxWidth: "150px",
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                      whiteSpace: "nowrap",
                    }}
                  >
                        {/* {col.render ? col.render(row[col.key], row) : row[col.key] ?? "-"} */}
                        {col.render
  ? col.render(row[col.key] ?? "", row)
  : (row[col.key] ?? "-")}

                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
};

export default VirtualizedTable;
