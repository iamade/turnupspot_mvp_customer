import React from "react";

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  className?: string;
}

const Input: React.FC<InputProps> = ({ className = "", ...props }) => (
  <input className={`border rounded px-3 py-2 ${className}`} {...props} />
);

export default Input;
