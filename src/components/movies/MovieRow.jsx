import React from "react";
import { TrendingUp, TrendingDown } from "lucide-react";

function formatMoney(num) {
  if (num === null || num === undefined || Number.isNaN(num)) return "N/A";

  const absNum = Math.abs(num);

  if (absNum >= 1_000_000_000) return `$${(absNum / 1_000_000_000).toFixed(1)}B`;
  if (absNum >= 1_000_000) return `$${(absNum / 1_000_000).toFixed(0)}M`;

  return `$${absNum.toLocaleString()}`;
}

export default function MovieRow({ movie, index }) {
  // Use Profit_num from backend, not revenue - budget
  const profit =
    movie.profit ?? movie.profit_loss ?? movie.ticket_profit ?? 0;

  const isProfit =
    movie.is_profit !== undefined ? movie.is_profit : profit >= 0;

  const roi =
    movie.roi !== undefined && movie.roi !== null
      ? Number(movie.roi).toFixed(0)
      : movie.budget
        ? ((profit / movie.budget) * 100).toFixed(0)
        : "N/A";

  return (
    <tr className="border-b border-border/40 hover:bg-secondary/50 transition-colors group">
      <td className="py-4 px-4 text-muted-foreground text-sm font-mono">
        {index + 1}
      </td>

      <td className="py-4 px-4">
        <p className="font-medium text-foreground">{movie.title}</p>
      </td>

      <td className="py-4 px-4 text-sm text-muted-foreground">
        {movie.year || "N/A"}
      </td>

      <td className="py-4 px-4 text-sm text-muted-foreground">
        {formatMoney(movie.budget)}
      </td>

      <td className="py-4 px-4 text-sm text-muted-foreground">
        {formatMoney(movie.revenue)}
      </td>

      <td className="py-4 px-4">
        <span
          className={`inline-flex items-center gap-1.5 text-sm font-semibold ${
            isProfit ? "text-emerald-400" : "text-red-400"
          }`}
        >
          {isProfit ? (
            <TrendingUp className="w-4 h-4" />
          ) : (
            <TrendingDown className="w-4 h-4" />
          )}
          {formatMoney(profit)}
        </span>
      </td>

      <td className="py-4 px-4 text-sm">
        <span
          className={`font-medium ${
            isProfit ? "text-emerald-400" : "text-red-400"
          }`}
        >
          {roi !== "N/A" ? `${roi}%` : "N/A"}
        </span>
      </td>
    </tr>
  );
}