import React, { useState } from "react";
import CustomPrediction from "../components/movies/CustomPrediction";

export default function CustomPredictionPage() {
  const [selectedModel, setSelectedModel] = useState("logistic");

  return (
    <div className="min-h-screen bg-background text-foreground">
      <div className="max-w-5xl mx-auto px-4 py-12">
        <button
          type="button"
          onClick={() => {
            window.location.href = "/";
          }}
          className="mb-8 text-sm text-muted-foreground hover:text-primary underline underline-offset-4 transition"
        >
          ← Back to Database Search
        </button>

        <div className="text-center mb-10">
          <h1 className="text-4xl sm:text-5xl font-display font-bold">
            Custom Movie Prediction
          </h1>

          <p className="text-muted-foreground mt-3 max-w-2xl mx-auto">
            Enter previous movie data from a franchise that is not in the
            database. Then choose a model to predict whether the next movie may
            be profitable.
          </p>
        </div>

        <div className="flex justify-center mb-6">
          <div className="inline-flex p-1 rounded-xl bg-secondary/60 border border-border/40">
            <button
              type="button"
              onClick={() => setSelectedModel("logistic")}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                selectedModel === "logistic"
                  ? "bg-primary text-primary-foreground shadow-sm"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              Logistic Regression
            </button>

            <button
              type="button"
              onClick={() => setSelectedModel("xgboost")}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                selectedModel === "xgboost"
                  ? "bg-primary text-primary-foreground shadow-sm"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              XGBoost
            </button>
          </div>
        </div>

        <div className="mb-8 grid grid-cols-1 md:grid-cols-2 gap-4">
          <div
            className={`rounded-2xl border p-5 transition ${
              selectedModel === "logistic"
                ? "border-primary/50 bg-primary/10"
                : "border-border/50 bg-card/60"
            }`}
          >
            <h3 className="font-semibold mb-2">Logistic Regression</h3>
            <p className="text-sm text-muted-foreground">
              More careful with risk, but it may miss some profit opportunities.
            </p>
          </div>

          <div
            className={`rounded-2xl border p-5 transition ${
              selectedModel === "xgboost"
                ? "border-primary/50 bg-primary/10"
                : "border-border/50 bg-card/60"
            }`}
          >
            <h3 className="font-semibold mb-2">XGBoost</h3>
            <p className="text-sm text-muted-foreground">
              Better at finding possible profit opportunities, but it may also
              approve some movies that become losses.
            </p>
          </div>
        </div>

        <CustomPrediction selectedModel={selectedModel} />
      </div>
    </div>
  );
}