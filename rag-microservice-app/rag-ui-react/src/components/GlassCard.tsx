import { cn } from "@/lib/utils";
import { ReactNode } from "react";

interface GlassCardProps {
  children: ReactNode;
  className?: string;
  title?: string;
  step?: number;
}

export function GlassCard({ children, className, title, step }: GlassCardProps) {
  return (
    <div
      className={cn(
        "relative rounded-2xl p-6 overflow-hidden",
        "bg-gradient-to-br from-card/80 to-card/40",
        "border border-border/50",
        "shadow-[0_8px_32px_hsl(222_47%_3%_/_0.5)]",
        "transition-all duration-300 hover:border-border",
        className
      )}
    >
      {/* Subtle gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent pointer-events-none" />
      
      {title && (
        <div className="relative flex items-center gap-3 mb-5">
          {step && (
            <span className="flex items-center justify-center w-8 h-8 rounded-lg bg-primary/10 text-primary font-semibold text-sm">
              {step}
            </span>
          )}
          <h3 className="text-lg font-semibold text-foreground">{title}</h3>
        </div>
      )}
      
      <div className="relative">{children}</div>
    </div>
  );
}
