import React from "react";

interface ActionButtonProps {
  label: string;
  disabled?: boolean;
  onClick?: () => void;
}

const ActionButton: React.FC<ActionButtonProps> = ({ label, disabled, onClick }) => {
  return (
    <button
      disabled={disabled}
      onClick={onClick}
      style={{
        padding: "0.5rem 1rem",
        backgroundColor: disabled ? "#ccc" : "#007bff",
        color: "#fff",
        border: "none",
        borderRadius: "4px",
        marginRight: "0.5rem"
      }}
    >
      {label}
    </button>
  );
};

export default ActionButton;
