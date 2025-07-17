import React from "react";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode;
  className?: string;
}

const Button: React.FC<ButtonProps> = ({
  children,
  className = "",
  ...props
}) => (
  <button className={`focus:outline-none ${className}`} {...props}>
    {children}
  </button>
);

export default Button;
