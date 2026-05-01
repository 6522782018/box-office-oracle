import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Clapperboard } from "lucide-react";

import SearchBar from "../components/movies/SearchBar";
import FranchiseTable from "../components/movies/FranchiseTable";
import PredictionCard from "../components/movies/PredictionCard";
import RevenueChart from "../components/movies/RevenueChart";
import ModelDescription from "../components/movies/ModelDescription";

export default function Home() {
  const [isLoading, setIsLoading] = useState(false);
  const [franchiseName, setFranchiseName] = useState("");
  const [movies, setMovies] = useState([]);
  const [prediction, setPrediction] = useState(null);
  const [notFound, setNotFound] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  const [selectedModel, setSelectedModel] = useState("logistic");

  const handleSearch = async (query) => {
    const cleanQuery = query.trim();

    if (!cleanQuery) return;

    setIsLoading(true);
    setMovies([]);
    setPrediction(null);
    setNotFound(false);
    setErrorMessage("");
    setFranchiseName(cleanQuery);

    try {
      const response = await fetch("https://predict-movie-profit-backend.onrender.com/api/predict", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          query: cleanQuery,
          model: selectedModel,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        setMovies([]);
        setPrediction(null);

        if (response.status === 404) {
          setNotFound(true);
          setErrorMessage("");
        } else {
          setNotFound(false);
          setErrorMessage(data.details || data.error || "Backend error");
        }

        setIsLoading(false);
        return;
      }

      setFranchiseName(data.franchiseName || cleanQuery);
      setMovies(data.movies || []);
      setPrediction(data.prediction || null);
      setNotFound(false);
      setErrorMessage("");
    } catch (error) {
      console.error("Prediction API error:", error);
      setNotFound(false);
      setMovies([]);
      setPrediction(null);
      setErrorMessage(
        "Cannot connect to backend. Make sure Flask is running on port 5001."
      );
    }

    setIsLoading(false);
  };

  return (
    <div className="min-h-screen bg-background">
      <div className="relative overflow-hidden">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-[400px] bg-primary/8 rounded-full blur-3xl" />

        <div className="relative max-w-5xl mx-auto px-4 pt-16 pb-12 sm:pt-24 sm:pb-16">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center mb-12"
          >
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 border border-primary/20 mb-6">
              <Clapperboard className="w-4 h-4 text-primary" />
              <span className="text-sm font-medium text-primary">
                ML-Powered Predictions
              </span>
            </div>

            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-display font-bold text-foreground mb-4 leading-tight">
              Will the Next Movie
              <br />
              <span className="text-primary">Profit or Flop?</span>
            </h1>

            <p className="text-lg text-muted-foreground max-w-xl mx-auto">
              Search any movie franchise and our ML model will analyze the
              financial history to predict the next installment&apos;s box
              office performance.
            </p>
          </motion.div>

          {/* Model selector */}
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

          <ModelDescription />

          <div className="mt-8">
            <SearchBar onSearch={handleSearch} isLoading={isLoading} />

            <div className="w-full max-w-[760px] mx-auto mt-4">
              <button
                type="button"
                onClick={() => {
                  window.location.href = "/custom-prediction";
                }}
                className="block text-left text-sm text-muted-foreground hover:text-primary underline underline-offset-4 transition"
              >
                Cannot find your franchise? Try Custom Prediction
              </button>
            </div>
          </div>
        </div>
      </div>

      <AnimatePresence>
        {isLoading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="max-w-5xl mx-auto px-4 py-16"
          >
            <div className="flex flex-col items-center gap-4">
              <div className="relative">
                <div className="w-16 h-16 rounded-full border-4 border-secondary border-t-primary animate-spin" />
              </div>

              <p className="text-muted-foreground text-sm animate-pulse">
                Analyzing {franchiseName} franchise data with{" "}
                {selectedModel === "xgboost"
                  ? "XGBoost"
                  : "Logistic Regression"}
                …
              </p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {!isLoading && movies.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="max-w-5xl mx-auto px-4 pb-20 space-y-10"
          >
            <FranchiseTable movies={movies} franchiseName={franchiseName} />

            <RevenueChart movies={movies} />

            {prediction && <PredictionCard prediction={prediction} />}
          </motion.div>
        )}
      </AnimatePresence>

      {!isLoading && notFound && (
        <div className="max-w-5xl mx-auto px-4 pb-20">
          <div className="text-center py-12 rounded-2xl border border-border/40 bg-secondary/30">
            <p className="text-foreground font-medium">Franchise not found</p>
            <p className="text-sm text-muted-foreground mt-2">
              Try searching a movie title that exists in your dataset, such as
              Harry Potter, Star Wars, Fast, Dune, or The Godfather.
            </p>

            <button
              type="button"
              onClick={() => {
                window.location.href = "/custom-prediction";
              }}
              className="mt-5 inline-flex rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition"
            >
              Use Custom Prediction
            </button>
          </div>
        </div>
      )}

      {!isLoading && errorMessage && (
        <div className="max-w-5xl mx-auto px-4 pb-20">
          <div className="text-center py-12 rounded-2xl border border-red-500/30 bg-red-500/10">
            <p className="text-red-400 font-medium">Backend error</p>
            <p className="text-sm text-muted-foreground mt-2">
              {errorMessage}
            </p>
          </div>
        </div>
      )}

      {!isLoading && movies.length === 0 && !notFound && !errorMessage && (
        <div className="max-w-5xl mx-auto px-4 pb-20">
          <div className="text-center py-16">
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 max-w-lg mx-auto">
              {["Harry Potter", "Star Wars", "Fast", "Dune"].map((name) => (
                <button
                  key={name}
                  onClick={() => handleSearch(name)}
                  className="px-4 py-3 rounded-xl bg-secondary/60 border border-border/40 text-sm text-muted-foreground hover:text-foreground hover:border-primary/30 hover:bg-secondary transition-all"
                >
                  {name}
                </button>
              ))}
            </div>

            <p className="text-xs text-muted-foreground/60 mt-4">
              Try one of these available movie franchises
            </p>
          </div>
        </div>
      )}
    </div>
  );
}