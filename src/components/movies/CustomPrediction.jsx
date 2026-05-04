import React, { useState } from "react";
import { Plus, Trash2, Loader2 } from "lucide-react";

const API_URL = "https://predict-movie-profit-backend.onrender.com";
// Later for deployed version, change to:
// const API_URL = "https://predict-movie-profit-backend.onrender.com";

export default function CustomPrediction({ selectedModel = "logistic" }) {
  const [movies, setMovies] = useState([
    { budget: "", gross: "", imdb: "" },
    { budget: "", gross: "", imdb: "" },
  ]);

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  const updateMovie = (index, field, value) => {
    const updated = [...movies];
    updated[index][field] = value;
    setMovies(updated);
  };

  const addMovie = () => {
    setMovies([...movies, { budget: "", gross: "", imdb: "" }]);
  };

  const removeMovie = (index) => {
    if (movies.length <= 2) return;
    setMovies(movies.filter((_, i) => i !== index));
  };

  const handlePredict = async () => {
    setLoading(true);
    setResult(null);
    setError("");

    try {
      const response = await fetch(`${API_URL}/api/custom-predict`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          model: selectedModel,
          movies: movies.map((m) => ({
            budget: Number(m.budget),
            gross: Number(m.gross),
            imdb: Number(m.imdb),
          })),
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Prediction failed");
      }

      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="mt-10 rounded-2xl border bg-card p-6 shadow-sm">
      <div className="mb-6">
        <h2 className="text-xl font-semibold">Custom Prediction</h2>
        <p className="text-sm text-muted-foreground mt-1">
          Enter previous movie data from a franchise that is not in the database.
          Sentiment is automatically set to the dataset median value.
        </p>
      </div>

      <div className="space-y-5">
        {movies.map((movie, index) => (
          <div
            key={index}
            className="rounded-xl border bg-background p-4 space-y-3"
          >
            <div className="flex items-center justify-between">
              <h3 className="font-medium">Previous Movie {index + 1}</h3>

              {movies.length > 2 && (
                <button
                  type="button"
                  onClick={() => removeMovie(index)}
                  className="text-sm text-red-500 flex items-center gap-1"
                >
                  <Trash2 className="w-4 h-4" />
                  Remove
                </button>
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              <input
                type="number"
                placeholder="Budget"
                value={movie.budget}
                onChange={(e) =>
                  updateMovie(index, "budget", e.target.value)
                }
                className="rounded-lg border px-3 py-2 bg-background"
              />

              <input
                type="number"
                placeholder="Gross / Revenue"
                value={movie.gross}
                onChange={(e) =>
                  updateMovie(index, "gross", e.target.value)
                }
                className="rounded-lg border px-3 py-2 bg-background"
              />

              <input
                type="number"
                step="0.1"
                placeholder="IMDb score"
                value={movie.imdb}
                onChange={(e) =>
                  updateMovie(index, "imdb", e.target.value)
                }
                className="rounded-lg border px-3 py-2 bg-background"
              />
            </div>
          </div>
        ))}
      </div>

      <div className="flex flex-col sm:flex-row gap-3 mt-6">
        <button
          type="button"
          onClick={addMovie}
          className="rounded-lg border px-4 py-2 flex items-center justify-center gap-2"
        >
          <Plus className="w-4 h-4" />
          Add Previous Movie
        </button>

        <button
          type="button"
          onClick={handlePredict}
          disabled={loading}
          className="rounded-lg bg-primary text-primary-foreground px-4 py-2 flex items-center justify-center gap-2"
        >
          {loading && <Loader2 className="w-4 h-4 animate-spin" />}
          Predict Next Movie
        </button>
      </div>

      {error && (
        <div className="mt-5 rounded-lg border border-red-300 bg-red-50 p-4 text-red-600 text-sm">
          {error}
        </div>
      )}

      {result && (
        <div className="mt-5 rounded-xl border bg-background p-5">
          <p className="text-sm text-muted-foreground">Prediction Result</p>

          <h3 className="text-2xl font-semibold mt-1">
            {result.prediction}
          </h3>

          <p className="text-sm text-muted-foreground mt-2">
            Model used:{" "}
            <span className="font-medium text-foreground">
              {result.model === "xgboost"
                ? "XGBoost"
                : "Logistic Regression"}
            </span>
          </p>

          <p className="text-sm text-muted-foreground">
            Profit probability:{" "}
            <span className="font-medium text-foreground">
              {(result.probability * 100).toFixed(1)}%
            </span>
          </p>

          <p className="text-xs text-muted-foreground mt-3">
            Sentiment score was automatically set to {result.sentiment_used}.
          </p>
        </div>
      )}
    </section>
  );
}