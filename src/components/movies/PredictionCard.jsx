import React from "react";
import { motion } from "framer-motion";
import { TrendingUp, TrendingDown, Sparkles, DollarSign, BarChart3, Percent } from "lucide-react";

function formatMoney(num) {
  if (!num && num !== 0) return "N/A";
  if (num >= 1_000_000_000) return `$${(num / 1_000_000_000).toFixed(1)}B`;
  if (num >= 1_000_000) return `$${(num / 1_000_000).toFixed(0)}M`;
  return `$${num.toLocaleString()}`;
}

export default function PredictionCard({ prediction }) {
  if (!prediction) return null;

  const isProfit = prediction.prediction === "profit";

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, ease: "easeOut" }}
      className="w-full"
    >
      <div className="flex items-center gap-3 mb-6">
        <div className="p-2.5 rounded-lg bg-primary/10 border border-primary/20">
          <Sparkles className="w-5 h-5 text-primary" />
        </div>
        <h2 className="text-xl font-display font-semibold text-foreground">
          Next Movie Prediction
        </h2>
      </div>

      <div className={`relative rounded-xl border overflow-hidden ${
        isProfit
          ? "border-emerald-500/30 bg-emerald-500/5"
          : "border-red-500/30 bg-red-500/5"
      }`}>
        {/* Glow effect */}
        <div className={`absolute top-0 left-1/2 -translate-x-1/2 w-64 h-32 rounded-full blur-3xl opacity-20 ${
          isProfit ? "bg-emerald-500" : "bg-red-500"
        }`} />

        <div className="relative p-8">
          {/* Prediction result */}
          <div className="flex items-center justify-center gap-4 mb-8">
            <div className={`p-4 rounded-2xl ${
              isProfit ? "bg-emerald-500/15" : "bg-red-500/15"
            }`}>
              {isProfit ? (
                <TrendingUp className="w-10 h-10 text-emerald-400" />
              ) : (
                <TrendingDown className="w-10 h-10 text-red-400" />
              )}
            </div>
            <div>
              <p className="text-sm text-muted-foreground font-medium uppercase tracking-wider mb-1">
                Predicted Outcome
              </p>
              <p className={`text-3xl font-display font-bold ${
                isProfit ? "text-emerald-400" : "text-red-400"
              }`}>
                {isProfit ? "PROFIT" : "LOSS"}
              </p>
            </div>
          </div>

          {/* Stats grid */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="bg-secondary/40 rounded-lg p-4 text-center">
              <DollarSign className="w-5 h-5 text-primary mx-auto mb-2" />
              <p className="text-xs text-muted-foreground mb-1">Est. Budget</p>
              <p className="text-lg font-semibold text-foreground">
                {formatMoney(prediction.estimated_budget)}
              </p>
            </div>
            <div className="bg-secondary/40 rounded-lg p-4 text-center">
              <BarChart3 className="w-5 h-5 text-primary mx-auto mb-2" />
              <p className="text-xs text-muted-foreground mb-1">Est. Revenue</p>
              <p className="text-lg font-semibold text-foreground">
                {formatMoney(prediction.estimated_revenue)}
              </p>
            </div>
            <div className="bg-secondary/40 rounded-lg p-4 text-center">
              <Percent className="w-5 h-5 text-primary mx-auto mb-2" />
              <p className="text-xs text-muted-foreground mb-1">Confidence</p>
              <p className="text-lg font-semibold text-foreground">
                {prediction.confidence || "N/A"}%
              </p>
            </div>
          </div>

          {/* Reasoning */}
          {prediction.reasoning && (
            <div className="mt-6 p-4 bg-secondary/30 rounded-lg border border-border/40">
              <p className="text-sm text-muted-foreground leading-relaxed">
                <span className="font-semibold text-foreground">Analysis: </span>
                {prediction.reasoning}
              </p>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
}
