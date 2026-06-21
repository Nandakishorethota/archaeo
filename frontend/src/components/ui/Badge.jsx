import { forwardRef } from "react";
import { cn } from "../../lib/utils";

const Badge = forwardRef(({ className, variant = "default", children, ...props }, ref) => {
  const variants = {
    default: "bg-[#111] text-[#999] border border-[#333]",
    outline: "bg-transparent text-[#999] border border-[#333]",
  };

  return (
    <span
      ref={ref}
      className={cn(
        "inline-flex items-center px-2 py-0.5 rounded text-[10px] font-medium",
        variants[variant],
        className
      )}
      {...props}
    >
      {children}
    </span>
  );
});
Badge.displayName = "Badge";

export { Badge };
