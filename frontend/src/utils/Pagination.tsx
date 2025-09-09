import React from "react";

interface PaginationProps {
  currentPage: number;
  totalItems: number;
  pageSize: number;
  onPageChange: (page: number) => void;
}

const Pagination: React.FC<PaginationProps> = ({
  currentPage,
  totalItems,
  pageSize,
  onPageChange,
}) => {
  const totalPages = Math.ceil(totalItems / pageSize);

  if (totalPages === 1) return null; // no need to show pagination

  const handlePrev = () => {
    if (currentPage > 1) {
      onPageChange(currentPage - 1);
    }
  };

  const handleNext = () => {
    if (currentPage < totalPages) {
      onPageChange(currentPage + 1);
    }
  };

  return (
    <div style={{ display: "flex", justifyContent: "center", margin: "1rem 0" }}>
      <button
        onClick={handlePrev}
        disabled={currentPage === 1}
        style={{
          padding: "0.5rem 1rem",
          marginRight: "0.5rem",
          borderRadius: "6px",
          border: "1px solid #ccc",
          backgroundColor: currentPage === 1 ? "#eee" : "#fff",
          cursor: currentPage === 1 ? "not-allowed" : "pointer",
        }}
      >
        Prev
      </button>

      <span style={{ alignSelf: "center" }}>
        Page {currentPage} of {totalPages}
      </span>

      <button
        onClick={handleNext}
        disabled={currentPage === totalPages}
        style={{
          padding: "0.5rem 1rem",
          marginLeft: "0.5rem",
          borderRadius: "6px",
          border: "1px solid #ccc",
          backgroundColor: currentPage === totalPages ? "#eee" : "#fff",
          cursor: currentPage === totalPages ? "not-allowed" : "pointer",
        }}
      >
        Next
      </button>
    </div>
  );
};

export default Pagination;
