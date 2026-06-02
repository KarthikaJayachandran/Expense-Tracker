import { useState } from "react";
import { expenseApi } from "../api/expenseApi";
import { CATEGORY_ICONS } from "../types/expense";
import type { Expense } from "../types/expense";

interface Props {
  expenses: Expense[];
  onEdit: (expense: Expense) => void;
  onRefetch: () => void;
}

function formatDate(dateStr: string): string {
  const [year, month, day] = dateStr.split("-");
  return new Date(Number(year), Number(month) - 1, Number(day)).toLocaleDateString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

function formatAmount(amount: number): string {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    minimumFractionDigits: 2,
  }).format(amount);
}

export function ExpenseTable({ expenses, onEdit, onRefetch }: Props) {
  const [deletingId, setDeletingId] = useState<number | null>(null);
  const [confirmId, setConfirmId] = useState<number | null>(null);
  const [deleteError, setDeleteError] = useState<string | null>(null);

  async function handleDelete(id: number) {
    setDeletingId(id);
    setDeleteError(null);
    try {
      await expenseApi.delete(id);
      onRefetch();
    } catch (err) {
      setDeleteError(err instanceof Error ? err.message : "Delete failed");
    } finally {
      setDeletingId(null);
      setConfirmId(null);
    }
  }

  if (expenses.length === 0) {
    return (
      <div className="empty-state">
        <div className="empty-icon">💸</div>
        <h3>No expenses found</h3>
        <p>Add your first expense or adjust your filters.</p>
      </div>
    );
  }

  return (
    <div className="table-wrapper">
      {deleteError && <div className="alert alert-error">{deleteError}</div>}
      <table className="expense-table">
        <thead>
          <tr>
            <th>Date</th>
            <th>Title</th>
            <th>Category</th>
            <th>Amount</th>
            <th>Note</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {expenses.map((expense) => (
            <tr key={expense.id} className="expense-row">
              <td className="col-date">{formatDate(expense.date)}</td>
              <td className="col-title">{expense.title}</td>
              <td className="col-category">
                <span className={`badge badge-${expense.category.toLowerCase()}`}>
                  {CATEGORY_ICONS[expense.category]} {expense.category}
                </span>
              </td>
              <td className="col-amount">{formatAmount(expense.amount)}</td>
              <td className="col-note" title={expense.note ?? ""}>
                {expense.note
                  ? expense.note.length > 40
                    ? expense.note.slice(0, 40) + "…"
                    : expense.note
                  : <span className="muted">—</span>}
              </td>
              <td className="col-actions">
                {confirmId === expense.id ? (
                  <div className="confirm-delete">
                    <span>Delete?</span>
                    <button
                      className="btn btn-danger btn-xs"
                      onClick={() => handleDelete(expense.id)}
                      disabled={deletingId === expense.id}
                      id={`confirm-delete-${expense.id}`}
                    >
                      {deletingId === expense.id ? "…" : "Yes"}
                    </button>
                    <button
                      className="btn btn-ghost btn-xs"
                      onClick={() => setConfirmId(null)}
                      id={`cancel-delete-${expense.id}`}
                    >
                      No
                    </button>
                  </div>
                ) : (
                  <>
                    <button
                      className="btn btn-icon"
                      onClick={() => onEdit(expense)}
                      title="Edit"
                      id={`edit-btn-${expense.id}`}
                    >
                      ✏️
                    </button>
                    <button
                      className="btn btn-icon btn-danger-icon"
                      onClick={() => setConfirmId(expense.id)}
                      title="Delete"
                      id={`delete-btn-${expense.id}`}
                    >
                      🗑️
                    </button>
                  </>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
