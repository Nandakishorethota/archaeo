import { forwardRef } from "react";
import { cn } from "../../lib/utils";

const Skeleton = forwardRef(({ className, ...props }, ref) => {
  return (
    <div
      ref={ref}
      className={cn("animate-pulse rounded bg-[#111]", className)}
      {...props}
    />
  );
});

Skeleton.displayName = "Skeleton";

export { Skeleton };
