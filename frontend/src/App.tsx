import { useState, useEffect, useCallback } from "react";
import { expenseApi, getErrorMessage } from "./api/expenseApi";
import { ExpenseForm } from "./components/ExpenseForm";
import { ExpenseList } from "./components/ExpenseList";
import { Filters } from "./components/Filters";
import { Summary } from "./components/Summary";
import { DashboardStats } from "./components/DashboardStats";
import { exportExpensesToCSV } from "./utils/csvExport";
import type { Expense, FilterParams } from "./types/expense";

const defaultFilters: FilterParams = {
  category: "",
  from_date: "",
  to_date: "",
  search: "",
};

export default function App() {
  const [expenses, setExpenses] = useState<Expense[]>([]);
  const [filters, setFilters] = useState<FilterParams>(defaultFilters);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Refresh trigger for Summary component
  const [refreshSummaryTrigger, setRefreshSummaryTrigger] = useState(0);

  // Form modal state
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingExpense, setEditingExpense] = useState<Expense | null>(null);

  const fetchExpenses = useCallback(async () => {
    // Prevent fetching if from_date > to_date (Filters component displays user error)
    if (filters.from_date && filters.to_date && filters.from_date > filters.to_date) {
      return;
    }
    
    setLoading(true);
    setError(null);
    try {
      const data = await expenseApi.list(filters);
      setExpenses(data);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    fetchExpenses();
  }, [fetchExpenses]);

  const handleRefreshAll = () => {
    fetchExpenses();
    setRefreshSummaryTrigger((prev) => prev + 1);
  };

  const handleEditClick = (expense: Expense) => {
    setEditingExpense(expense);
    setIsFormOpen(true);
  };

  const handleAddClick = () => {
    setEditingExpense(null);
    setIsFormOpen(true);
  };

  const handleFormSuccess = () => {
    setIsFormOpen(false);
    setEditingExpense(null);
    setFilters(defaultFilters);
    handleRefreshAll();
  };

  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="header-brand">
          <span className="brand-icon">💰</span>
          <span className="brand-name">PocketLens</span>
        </div>
        <button className="btn btn-primary" onClick={handleAddClick} id="add-expense-btn">
          ➕ Add Expense
        </button>
      </header>

      <main className="app-main">
        {/* Monthly Summary Component */}
        <Summary refreshTrigger={refreshSummaryTrigger} />

        {/* Filters Section */}
        <div className="card">
          <Filters
            filters={filters}
            onChange={setFilters}
            onReset={() => setFilters(defaultFilters)}
          />
        </div>

        {/* Expenses List Section */}
        <div className="card list-card">
          <div className="list-header">
            <h3>📋 Expense List</h3>
            <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
              {loading && <span className="spinner" title="Syncing..." />}
              <button 
                className="btn btn-ghost btn-sm" 
                onClick={() => exportExpensesToCSV(expenses)}
                disabled={expenses.length === 0}
              >
                📥 Export CSV
              </button>
            </div>
          </div>

          {error && <div className="alert alert-error">{error}</div>}

          {!error && (
            <>
              <DashboardStats expenses={expenses} />
              <ExpenseList
                expenses={expenses}
                onEdit={handleEditClick}
                onRefetch={handleRefreshAll}
              />
            </>
          )}
        </div>
      </main>

      {isFormOpen && (
        <ExpenseForm
          editingExpense={editingExpense}
          onSuccess={handleFormSuccess}
          onCancel={() => {
            setIsFormOpen(false);
            setEditingExpense(null);
          }}
        />
      )}

      <footer className="app-footer">
        <span>Personal Expense Tracker • {new Date().getFullYear()}</span>
      </footer>
    </div>
  );
}
