import React from "react";
import { clsx } from "clsx";

interface BadgeProps {
  children: React.ReactNode;
  variant?: "blue" | "green" | "amber" | "rose" | "slate" | "form-w" | "form-d" | "form-l" | "verified" | "neutral" | "success" | "default";
  size?: "sm" | "md";
  className?: string;
}

export default function Badge({
  children,
  variant = "slate",
  size = "sm",
  className,
}: BadgeProps) {
  const normalizedVariant =
    variant === "verified" || variant === "success"
      ? "green"
      : variant === "neutral" || variant === "default"
      ? "slate"
      : variant;

  const variantStyles = {
    green: "bg-[#E6F0E7] text-[#174B32] border-[#C3DEC7] font-semibold",
    blue: "bg-[#E8F0FE] text-[#003399] border-[#C2D6FD] font-semibold",
    amber: "bg-[#FEF3C7] text-[#92400E] border-[#FDE68A] font-semibold",
    rose: "bg-[#FEE2E2] text-[#991B1B] border-[#FECACA] font-semibold",
    slate: "bg-[#F4F8F4] text-[#26332B] border-[#E2EAE3]",
    "form-w": "bg-[#246B45] text-white font-bold border-[#174B32]",
    "form-d": "bg-[#D9A441] text-white font-bold border-[#B45309]",
    "form-l": "bg-[#C65B56] text-white font-bold border-[#991B1B]",
  }[normalizedVariant];

  const sizeStyles = {
    sm: "px-2 py-0.5 text-[10px]",
    md: "px-2.5 py-1 text-xs",
  }[size];

  return (
    <span
      className={clsx(
        "inline-flex items-center justify-center font-mono rounded border uppercase tracking-wider",
        variantStyles,
        sizeStyles,
        className
      )}
    >
      {children}
    </span>
  );
}
