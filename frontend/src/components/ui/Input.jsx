import { forwardRef } from "react";
import { cn } from "../../lib/utils";

const Input = forwardRef(
  ({ className, type = "text", error, ...props }, ref) => {
    return (
      <input
        ref={ref}
        type={type}
        className={cn(
          "flex h-8 w-full rounded border bg-black px-3 py-1.5 text-sm text-white",
          "placeholder:text-[#666]",
          "focus:outline-none focus:border-[#555]",
          "disabled:cursor-not-allowed disabled:opacity-50",
          "transition-colors",
          error ? "border-[#ff4444] focus:border-[#ff4444]" : "border-[#333] hover:border-[#444]",
          className
        )}
        {...props}
      />
    );
  }
);

Input.displayName = "Input";

export { Input };
