import React from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";

function formatMoney(num) {
  if (num === null || num === undefined || Number.isNaN(num)) return "N/A";

  const absNum = Math.abs(num);

  if (absNum >= 1_000_000_000) return `$${(absNum / 1_000_000_000).toFixed(1)}B`;
  if (absNum >= 1_000_000) return `$${(absNum / 1_000_000).toFixed(0)}M`;

  return `$${absNum.toLocaleString()}`;
}

const CustomTooltip = ({ active, payload }) => {
  if (active && payload && payload.length) {
    const d = payload[0].payload;

    return (
      <div className="bg-card border border-border rounded-lg p-3 shadow-xl">
        <p className="text-sm font-semibold text-foreground mb-1">{d.title}</p>
        <p className="text-xs text-muted-foreground">
          Budget: {formatMoney(d.budget)}
        </p>
        <p className="text-xs text-muted-foreground">
          Revenue: {formatMoney(d.revenue)}
        </p>
        <p
          className={`text-xs font-semibold mt-1 ${
            d.profit >= 0 ? "text-emerald-400" : "text-red-400"
          }`}
        >
          {d.profit >= 0 ? "Profit" : "Loss"}: {formatMoney(d.profit)}
        </p>
      </div>
    );
  }

  return null;
};

export default function RevenueChart({ movies }) {
  if (!movies || movies.length < 2) return null;

  const data = movies.map((m) => {
    const profit = m.profit ?? m.profit_loss ?? m.ticket_profit ?? 0;

    return {
      title: m.title?.length > 20 ? m.title.slice(0, 18) + "…" : m.title,
      budget: m.budget || 0,
      revenue: m.revenue || 0,

      // Use Profit_num from backend
      profit,
    };
  });

  return (
    <div className="w-full rounded-xl border border-border/60 bg-card/50 p-6">
      <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground mb-4">
        Revenue vs Budget
      </h3>

      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={data} barGap={4}>
          <XAxis
            dataKey="title"
            tick={{ fill: "hsl(225, 10%, 50%)", fontSize: 11 }}
            axisLine={{ stroke: "hsl(225, 15%, 16%)" }}
            tickLine={false}
          />

          <YAxis
            tickFormatter={(v) => formatMoney(v)}
            tick={{ fill: "hsl(225, 10%, 50%)", fontSize: 11 }}
            axisLine={false}
            tickLine={false}
          />

          <Tooltip
            content={<CustomTooltip />}
            cursor={{ fill: "hsl(225, 15%, 13%)" }}
          />

          <Bar
            dataKey="budget"
            fill="hsl(225, 15%, 30%)"
            radius={[4, 4, 0, 0]}
            name="Budget"
          />

          <Bar dataKey="revenue" radius={[4, 4, 0, 0]} name="Revenue">
            {data.map((entry, i) => (
              <Cell
                key={i}
                fill={
                  entry.profit >= 0
                    ? "hsl(160, 60%, 45%)"
                    : "hsl(0, 72%, 51%)"
                }
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}