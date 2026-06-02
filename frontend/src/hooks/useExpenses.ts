import { useState, useCallback, useEffect } from "react";
import { expenseApi } from "../api/expenseApi";
import type { Expense, FilterParams } from "../types/expense";

export function useExpenses() {
  const [expenses, setExpenses] = useState<Expense[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchExpenses = useCallback(async (filters?: Partial<FilterParams>) => {
    setLoading(true);
    setError(null);
    try {
      const data = await expenseApi.list(filters);
      setExpenses(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load expenses");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchExpenses();
  }, [fetchExpenses]);

  return { expenses, loading, error, refetch: fetchExpenses };
}
