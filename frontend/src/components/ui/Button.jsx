import { forwardRef } from "react";
import { cn } from "../../lib/utils";

const Button = forwardRef(
  ({ className, variant = "primary", size = "md", children, ...props }, ref) => {
    const variants = {
      primary: "bg-white text-black hover:bg-[#ddd]",
      secondary: "bg-[#111] text-[#999] border border-[#333] hover:bg-[#222] hover:text-white",
      ghost: "text-[#999] hover:text-white hover:bg-[#111]",
    };

    const sizes = {
      sm: "h-7 px-2.5 text-xs gap-1.5",
      md: "h-8 px-3 text-sm gap-2",
      lg: "h-9 px-4 text-sm gap-2",
      icon: "h-8 w-8 p-0 justify-center",
    };

    return (
      <button
        ref={ref}
        className={cn(
          "inline-flex items-center justify-center font-medium rounded transition-colors",
          "focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-white",
          "disabled:opacity-50 disabled:cursor-not-allowed",
          variants[variant],
          sizes[size],
          className
        )}
        {...props}
      >
        {children}
      </button>
    );
  }
);
Button.displayName = "Button";

export { Button };
