import { useState, useEffect } from "react";
import { expenseApi, getErrorMessage } from "../api/expenseApi";
import { CATEGORIES } from "../types/expense";
import type { Expense, ExpenseFormData } from "../types/expense";

interface Props {
  editingExpense?: Expense | null;
  onSuccess: () => void;
  onCancel: () => void;
}

const today = new Date().toISOString().split("T")[0];

const emptyForm: ExpenseFormData = {
  title: "",
  amount: "",
  category: "Food",
  date: today,
  note: "",
};

export function ExpenseForm({ editingExpense, onSuccess, onCancel }: Props) {
  const [form, setForm] = useState<ExpenseFormData>(emptyForm);
  const [errors, setErrors] = useState<Partial<Record<keyof ExpenseFormData, string>>>({});
  const [submitting, setSubmitting] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);

  // Populate form when editing
  useEffect(() => {
    if (editingExpense) {
      setForm({
        title: editingExpense.title,
        amount: String(editingExpense.amount),
        category: editingExpense.category,
        date: editingExpense.date,
        note: editingExpense.note ?? "",
      });
    } else {
      setForm(emptyForm);
    }
    setErrors({});
    setApiError(null);
  }, [editingExpense]);

  function validate(): boolean {
    const newErrors: Partial<Record<keyof ExpenseFormData, string>> = {};
    
    if (!form.title || !form.title.trim()) {
      newErrors.title = "Title is required and cannot be empty or only spaces";
    }

    const amt = parseFloat(form.amount);
    if (!form.amount || isNaN(amt) || amt <= 0) {
      newErrors.amount = "Amount must be a positive number greater than 0";
    }

    if (!form.date) {
      newErrors.date = "Date is required";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!validate()) return;
    setSubmitting(true);
    setApiError(null);
    try {
      if (editingExpense) {
        await expenseApi.update(editingExpense.id, form);
      } else {
        await expenseApi.create(form);
      }
      onSuccess();
      setForm(emptyForm);
    } catch (err) {
      setApiError(getErrorMessage(err));
    } finally {
      setSubmitting(false);
    }
  }

  function handleChange(
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
  ) {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
    if (errors[name as keyof ExpenseFormData]) {
      setErrors((prev) => ({ ...prev, [name]: undefined }));
    }
  }

  return (
    <div className="form-overlay" onClick={(e) => e.target === e.currentTarget && onCancel()}>
      <div className="form-modal">
        <div className="form-header">
          <h2>{editingExpense ? "✏️ Edit Expense" : "➕ Add Expense"}</h2>
          <button className="close-btn" onClick={onCancel} aria-label="Close">✕</button>
        </div>

        {apiError && <div className="alert alert-error">{apiError}</div>}

        <form onSubmit={handleSubmit} noValidate>
          <div className="form-group">
            <label htmlFor="title">Title *</label>
            <input
              id="title"
              name="title"
              type="text"
              value={form.title}
              onChange={handleChange}
              placeholder="e.g. Weekly groceries"
              maxLength={100}
              className={errors.title ? "input-error" : ""}
            />
            {errors.title && <span className="field-error">{errors.title}</span>}
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="amount">Amount (₹) *</label>
              <input
                id="amount"
                name="amount"
                type="number"
                value={form.amount}
                onChange={handleChange}
                placeholder="0.00"
                min="0.01"
                step="0.01"
                className={errors.amount ? "input-error" : ""}
              />
              {errors.amount && <span className="field-error">{errors.amount}</span>}
            </div>

            <div className="form-group">
              <label htmlFor="date">Date *</label>
              <input
                id="date"
                name="date"
                type="date"
                value={form.date}
                onChange={handleChange}
                className={errors.date ? "input-error" : ""}
              />
              {errors.date && <span className="field-error">{errors.date}</span>}
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="category">Category *</label>
            <select
              id="category"
              name="category"
              value={form.category}
              onChange={handleChange}
            >
              {CATEGORIES.map((cat) => (
                <option key={cat} value={cat}>{cat}</option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="note">Note <span className="optional">(optional)</span></label>
            <textarea
              id="note"
              name="note"
              value={form.note}
              onChange={handleChange}
              placeholder="Any additional details..."
              rows={3}
              maxLength={500}
            />
          </div>

          <div className="form-actions">
            <button type="button" className="btn btn-ghost" onClick={onCancel}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary" disabled={submitting}>
              {submitting ? "Saving…" : editingExpense ? "Update" : "Add Expense"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
