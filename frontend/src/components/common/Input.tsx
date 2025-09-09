import React from "react";

interface InputProps {
  value: string;
  onChange: (val: string) => void;
  label?: string;
  placeholder?: string;
}

const Input: React.FC<InputProps> = ({ value, onChange, label, placeholder }) => {
  return (
    <div style={{ marginBottom: "1rem" }}>
      {label && <label>{label}</label>}
      <input
        value={value}
        onChange={(e: React.ChangeEvent<HTMLInputElement>) => onChange(e.target.value)}
        placeholder={placeholder}
        style={{ width: "100%", padding: "0.5rem", borderRadius: "4px", border: "1px solid #ccc" }}
      />
    </div>
  );
};

export default Input;
