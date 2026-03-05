import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center rounded-[99px] px-4 py-2 text-xs font-semibold uppercase tracking-tight transition-colors",
  {
    variants: {
      variant: {
        default: "bg-[#84a584] text-[#1c1a1f]",
        secondary: "bg-[#2c3833] text-[#f9f5df]",
        outline: "border border-[#cecece] text-[#f9f5df]",
        sage: "bg-[#84a584] text-[#1c1a1f]",
        olive: "bg-[#898a7d] text-white",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <span className={cn(badgeVariants({ variant }), className)} {...props} />
  );
}

export { Badge, badgeVariants };
