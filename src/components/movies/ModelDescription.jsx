import React from "react";

export default function ModelDescription() {
  return (
    <div className="mt-5 mb-8 max-w-3xl mx-auto">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        <div className="rounded-2xl border border-border/60 bg-card/40 px-5 py-4 text-left">
          <h3 className="text-sm font-semibold text-foreground mb-1">
            Logistic Regression
          </h3>
          <p className="text-sm text-muted-foreground leading-relaxed">
            More careful with risk, but it may miss some profit opportunities.
          </p>
        </div>

        <div className="rounded-2xl border border-border/60 bg-card/40 px-5 py-4 text-left">
          <h3 className="text-sm font-semibold text-foreground mb-1">
            XGBoost
          </h3>
          <p className="text-sm text-muted-foreground leading-relaxed">
            Better at finding possible profit opportunities, but it may also
            approve some movies that become losses.
          </p>
        </div>
      </div>
    </div>
  );
}