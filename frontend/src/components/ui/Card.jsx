import { forwardRef } from "react";
import { cn } from "../../lib/utils";

const Card = forwardRef(({ className, variant = "default", children, ...props }, ref) => {
  const variants = {
    default: "bg-[#0a0a0a] border border-[#222] rounded",
    subtle: "bg-[#111] border border-[#222] rounded",
    padded: "bg-[#0a0a0a] border border-[#222] rounded p-6 space-y-4",
  };

  return (
    <div ref={ref} className={cn(variants[variant], className)} {...props}>
      {children}
    </div>
  );
});
Card.displayName = "Card";

const CardContent = forwardRef(({ className, children, ...props }, ref) => (
  <div ref={ref} className={cn("p-6 pt-0", className)} {...props}>
    {children}
  </div>
));
CardContent.displayName = "CardContent";

const CardTitle = forwardRef(({ className, children, ...props }, ref) => (
  <h3 ref={ref} className={cn("text-sm font-medium text-white", className)} {...props}>
    {children}
  </h3>
));
CardTitle.displayName = "CardTitle";

export { Card, CardContent, CardTitle };
