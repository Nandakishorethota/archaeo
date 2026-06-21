import { forwardRef, useRef, useEffect } from "react";
import { cn } from "../../lib/utils";

const ScrollArea = forwardRef(({ className, children, ...props }, ref) => {
  const scrollRef = useRef(null);
  const composedRef = (node) => {
    scrollRef.current = node;
    if (typeof ref === "function") ref(node);
    else if (ref) ref.current = node;
  };

  return (
    <div
      ref={composedRef}
      className={cn("overflow-auto scrollbar-thin scrollbar-thumb-[#333] scrollbar-track-transparent", className)}
      {...props}
    >
      {children}
    </div>
  );
});

ScrollArea.displayName = "ScrollArea";

export { ScrollArea };
