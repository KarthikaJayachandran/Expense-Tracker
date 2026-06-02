import { useState, useEffect } from "react";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts";
import { expenseApi, getErrorMessage } from "../api/expenseApi";
import { CATEGORIES, CATEGORY_ICONS } from "../types/expense";
import type { Category, MonthlySummary } from "../types/expense";

interface Props {
  refreshTrigger: number;
}

const MONTH_NAMES = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December",
];

const CATEGORY_COLORS: Record<Category, string> = {
  Food: "#f97316",
  Transport: "#3b82f6",
  Shopping: "#a855f7",
  Bills: "#ef4444",
  Entertainment: "#ec4899",
  Other: "#6b7280",
};

function formatAmount(amount: number): string {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    minimumFractionDigits: 2,
  }).format(amount);
}

export function Summary({ refreshTrigger }: Props) {
  const currentDate = new Date();
  const [year, setYear] = useState<number>(currentDate.getFullYear());
  const [month, setMonth] = useState<number>(currentDate.getMonth() + 1);
  const [summary, setSummary] = useState<MonthlySummary | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Generate lists of months and last 5 years for dropdowns
  const months = MONTH_NAMES.map((name, index) => ({ name, value: index + 1 }));
  const currentYear = currentDate.getFullYear();
  const years = Array.from({ length: 5 }, (_, i) => currentYear - i);

  useEffect(() => {
    let active = true;

    async function fetchSummary() {
      setLoading(true);
      setError(null);
      try {
        const data = await expenseApi.monthlySummary(year, month);
        if (active) {
          setSummary(data);
        }
      } catch (err) {
        if (active) {
          setError(getErrorMessage(err));
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    fetchSummary();

    return () => {
      active = false;
    };
  }, [year, month, refreshTrigger]);

  const total = summary ? summary.total_spent : 0;
  const breakdown: Record<Category, number> = summary ? summary.category_breakdown : {
    Food: 0,
    Transport: 0,
    Shopping: 0,
    Bills: 0,
    Entertainment: 0,
    Other: 0,
  };

  // Sort categories by expenditure amount descending
  const sortedBreakdown = CATEGORIES.map((cat) => ({
    cat,
    amount: breakdown[cat] ?? 0,
    pct: total > 0 ? ((breakdown[cat] ?? 0) / total) * 100 : 0,
  })).sort((a, b) => b.amount - a.amount);

  return (
    <div className="summary-section">
      <div className="summary-header">
        <h3>📊 Monthly Summary</h3>
        <div className="summary-selectors">
          <select
            value={month}
            onChange={(e) => setMonth(Number(e.target.value))}
            aria-label="Select Month"
            id="summary-month-select"
          >
            {months.map((m) => (
              <option key={m.value} value={m.value}>
                {m.name}
              </option>
            ))}
          </select>
          <select
            value={year}
            onChange={(e) => setYear(Number(e.target.value))}
            aria-label="Select Year"
            id="summary-year-select"
          >
            {years.map((y) => (
              <option key={y} value={y}>
                {y}
              </option>
            ))}
          </select>
        </div>
      </div>

      {loading && <div className="summary-loading">Loading summary...</div>}
      {error && <div className="alert alert-error">{error}</div>}

      {!loading && !error && summary && (
        <div className="summary-panel card">
          <div className="summary-total-section">
            <div className="summary-label">Total Spent</div>
            <div className="summary-period">
              {MONTH_NAMES[month - 1]} {year}
            </div>
            <div className="summary-amount">{formatAmount(total)}</div>
          </div>

          <div className="summary-chart-section">
            <ResponsiveContainer width="100%" height={160}>
              <PieChart>
                <Pie
                  data={sortedBreakdown.filter(d => d.amount > 0)}
                  dataKey="amount"
                  nameKey="cat"
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={70}
                  paddingAngle={5}
                  stroke="none"
                >
                  {sortedBreakdown.filter(d => d.amount > 0).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={CATEGORY_COLORS[entry.cat]} />
                  ))}
                </Pie>
                <Tooltip 
                  formatter={(value: number) => formatAmount(value)}
                  contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px rgba(0,0,0,0.1)' }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="summary-breakdown-section">
            {total === 0 ? (
              <div className="empty-state small">
                <span>No spending recorded for this period.</span>
              </div>
            ) : (
              <div className="breakdown-list compact">
                {sortedBreakdown.map(({ cat, amount, pct }) => (
                  <div key={cat} className="breakdown-item compact">
                    <div className="breakdown-meta">
                      <span className="breakdown-icon">{CATEGORY_ICONS[cat]}</span>
                      <span className="breakdown-cat">{cat}</span>
                      <span className="breakdown-pct">{pct.toFixed(1)}%</span>
                      <span className="breakdown-amt">{formatAmount(amount)}</span>
                    </div>
                    <div className="breakdown-bar-bg">
                      <div
                        className="breakdown-bar-fill"
                        style={{
                          width: `${pct}%`,
                          backgroundColor: CATEGORY_COLORS[cat],
                        }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
