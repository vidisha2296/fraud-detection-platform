import React from "react";
import ActionButton from "./ActionButton";

interface ActionModalProps {
  open: boolean;
  onClose: () => void;
}

const ActionModal: React.FC<ActionModalProps> = ({ open, onClose }) => {
  if (!open) return null;

  return (
    <div style={{ position: "fixed", top: 0, left: 0, width: "100%", height: "100%", backgroundColor: "rgba(0,0,0,0.5)", display: "flex", justifyContent: "center", alignItems: "center" }}>
      <div style={{ backgroundColor: "#fff", padding: "2rem", borderRadius: "8px" }}>
        <h2>Action Modal</h2>
        <p>Modal content goes here.</p>
        <ActionButton label="Close" onClick={onClose} />
      </div>
    </div>
  );
};

export default ActionModal;
