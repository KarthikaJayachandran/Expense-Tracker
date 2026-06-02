import { useState, useEffect } from "react";
import { expenseApi } from "../api/expenseApi";
import type { MonthlySummary } from "../types/expense";

export function useSummary(year?: number, month?: number) {
  const [summary, setSummary] = useState<MonthlySummary | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    expenseApi
      .monthlySummary(year, month)
      .then(setSummary)
      .catch((err) =>
        setError(err instanceof Error ? err.message : "Failed to load summary")
      )
      .finally(() => setLoading(false));
  }, [year, month]);

  return { summary, loading, error };
}
