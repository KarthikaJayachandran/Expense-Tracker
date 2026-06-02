import { useMemo } from "react";
import type { Expense } from "../types/expense";

interface DashboardStatsProps {
  expenses: Expense[];
}

function formatAmount(amount: number): string {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    minimumFractionDigits: 2,
  }).format(amount);
}

export function DashboardStats({ expenses }: DashboardStatsProps) {
  const { totalCount, totalSpent, highestExpense } = useMemo(() => {
    if (expenses.length === 0) {
      return { totalCount: 0, totalSpent: 0, highestExpense: 0 };
    }

    const count = expenses.length;
    let sum = 0;
    let max = 0;

    for (const expense of expenses) {
      sum += expense.amount;
      if (expense.amount > max) {
        max = expense.amount;
      }
    }

    return {
      totalCount: count,
      totalSpent: sum,
      highestExpense: max,
    };
  }, [expenses]);

  return (
    <div className="stats-grid">
      <div className="stat-card">
        <span className="stat-icon">📄</span>
        <div className="stat-info">
          <div className="stat-label">Total Expenses</div>
          <div className="stat-value">{totalCount}</div>
        </div>
      </div>

      <div className="stat-card">
        <span className="stat-icon">💰</span>
        <div className="stat-info">
          <div className="stat-label">Total Spent</div>
          <div className="stat-value">{formatAmount(totalSpent)}</div>
        </div>
      </div>

      <div className="stat-card">
        <span className="stat-icon">🔥</span>
        <div className="stat-info">
          <div className="stat-label">Highest Expense</div>
          <div className="stat-value">{formatAmount(highestExpense)}</div>
        </div>
      </div>
    </div>
  );
}
