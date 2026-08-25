import Link from "next/link";
import { cn } from "@/lib/utils";

export function LogoMark({ className }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 48 48"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={cn("h-8 w-8", className)}
      aria-hidden="true"
    >
      <defs>
        <linearGradient id="psf-grad" x1="4" y1="4" x2="44" y2="44" gradientUnits="userSpaceOnUse">
          <stop stopColor="#6366F1" />
          <stop offset="1" stopColor="#8B5CF6" />
        </linearGradient>
        <linearGradient id="psf-sheen" x1="24" y1="2" x2="24" y2="46" gradientUnits="userSpaceOnUse">
          <stop stopColor="#ffffff" stopOpacity="0.25" />
          <stop offset="0.5" stopColor="#ffffff" stopOpacity="0" />
        </linearGradient>
      </defs>
      <rect x="2" y="2" width="44" height="44" rx="13" fill="url(#psf-grad)" />
      <rect x="2" y="2" width="44" height="44" rx="13" fill="url(#psf-sheen)" />
      <path
        d="M10 31.5C15 31.5 16.5 19.5 22 19.5C27.5 19.5 27 26 31 26C34.6 26 35.5 17 38 13.5"
        stroke="#ffffff"
        strokeWidth="4"
        strokeLinecap="round"
      />
      <circle cx="38" cy="13.5" r="3" fill="#ffffff" />
    </svg>
  );
}

interface LogoProps {
  className?: string;
  markClassName?: string;
  href?: string;
  size?: "sm" | "md" | "lg";
}

export function Logo({ className, markClassName, href, size = "md" }: LogoProps) {
  const sizes = {
    sm: { mark: "h-7 w-7", text: "text-base", badge: "text-[9px] px-1 py-px" },
    md: { mark: "h-9 w-9", text: "text-lg", badge: "text-[10px] px-1.5 py-0.5" },
    lg: { mark: "h-14 w-14", text: "text-2xl", badge: "text-xs px-2 py-0.5" },
  }[size];

  const content = (
    <span className={cn("inline-flex items-center gap-2.5 select-none", className)}>
      <LogoMark className={cn(sizes.mark, markClassName)} />
      <span className="flex items-center gap-1.5">
        <span
          className={cn(
            "font-bold tracking-tight bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent",
            sizes.text
          )}
        >
          PyFinFlow
        </span>
        <span
          className={cn(
            "font-bold uppercase leading-none rounded-md bg-accent/15 text-accent border border-accent/30",
            sizes.badge
          )}
        >
          AI
        </span>
      </span>
    </span>
  );

  if (href) {
    return (
      <Link href={href} className="transition-opacity hover:opacity-80">
        {content}
      </Link>
    );
  }
  return content;
}
