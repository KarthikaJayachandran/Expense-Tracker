import type { Expense } from "../types/expense";

/**
 * Escapes a CSV field to handle commas, newlines, and quotes.
 */
function escapeCSV(field: string | number | null | undefined): string {
  if (field === null || field === undefined) return "";
  const str = String(field);
  // If the field contains quotes, commas, or newlines, wrap in quotes and escape internal quotes
  if (/[",\n]/.test(str)) {
    return `"${str.replace(/"/g, '""')}"`;
  }
  return str;
}

/**
 * Exports a list of expenses to a CSV file and triggers download.
 */
export function exportExpensesToCSV(expenses: Expense[]) {
  if (expenses.length === 0) return;

  const headers = ["Title", "Amount", "Category", "Date", "Note"];
  
  const csvRows = [headers.join(",")];
  
  for (const expense of expenses) {
    const row = [
      escapeCSV(expense.title),
      escapeCSV(expense.amount),
      escapeCSV(expense.category),
      escapeCSV(expense.date),
      escapeCSV(expense.note)
    ];
    csvRows.push(row.join(","));
  }
  
  const csvContent = csvRows.join("\n");
  const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  
  // Format YYYY-MM-DD using local time
  const date = new Date();
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  const dateStr = `${year}-${month}-${day}`;
  
  const fileName = `expenses-${dateStr}.csv`;
  
  const link = document.createElement("a");
  link.setAttribute("href", url);
  link.setAttribute("download", fileName);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}
