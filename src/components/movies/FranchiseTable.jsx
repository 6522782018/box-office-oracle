import React from "react";
import MovieRow from "./MovieRow";
import { Film } from "lucide-react";

export default function FranchiseTable({ movies, franchiseName }) {
  if (!movies || movies.length === 0) return null;

  return (
    <div className="w-full">
      <div className="flex items-center gap-3 mb-6">
        <div className="p-2.5 rounded-lg bg-primary/10 border border-primary/20">
          <Film className="w-5 h-5 text-primary" />
        </div>
        <div>
          <h2 className="text-xl font-display font-semibold text-foreground">
            {franchiseName} Franchise
          </h2>
          <p className="text-sm text-muted-foreground">
            {movies.length} movie{movies.length !== 1 ? "s" : ""} in the franchise
          </p>
        </div>
      </div>

      <div className="rounded-xl border border-border/60 overflow-hidden bg-card/50 backdrop-blur-sm">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-border/60 bg-secondary/30">
                <th className="text-left py-3.5 px-4 text-xs font-semibold uppercase tracking-wider text-muted-foreground">#</th>
                <th className="text-left py-3.5 px-4 text-xs font-semibold uppercase tracking-wider text-muted-foreground">Title</th>
                <th className="text-left py-3.5 px-4 text-xs font-semibold uppercase tracking-wider text-muted-foreground">Year</th>
                <th className="text-left py-3.5 px-4 text-xs font-semibold uppercase tracking-wider text-muted-foreground">Budget</th>
                <th className="text-left py-3.5 px-4 text-xs font-semibold uppercase tracking-wider text-muted-foreground">Revenue</th>
                <th className="text-left py-3.5 px-4 text-xs font-semibold uppercase tracking-wider text-muted-foreground">Profit / Loss</th>
                <th className="text-left py-3.5 px-4 text-xs font-semibold uppercase tracking-wider text-muted-foreground">ROI</th>
              </tr>
            </thead>
            <tbody>
              {movies.map((movie, i) => (
                <MovieRow key={i} movie={movie} index={i} />
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}