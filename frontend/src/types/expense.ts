export type Category =
  | "Food"
  | "Transport"
  | "Shopping"
  | "Bills"
  | "Entertainment"
  | "Other";

export const CATEGORIES: Category[] = [
  "Food",
  "Transport",
  "Shopping",
  "Bills",
  "Entertainment",
  "Other",
];

export const CATEGORY_ICONS: Record<Category, string> = {
  Food: "🍔",
  Transport: "🚗",
  Shopping: "🛍️",
  Bills: "💡",
  Entertainment: "🎬",
  Other: "📦",
};

export interface Expense {
  id: number;
  title: string;
  amount: number;
  category: Category;
  date: string; // ISO date string "YYYY-MM-DD"
  note?: string | null;
  created_at: string;
  updated_at: string;
}

export interface ExpenseFormData {
  title: string;
  amount: string;
  category: Category;
  date: string;
  note: string;
}

export interface MonthlySummary {
  year: number;
  month: number;
  total_spent: number;
  category_breakdown: Record<Category, number>;
}

export interface FilterParams {
  category: Category | "";
  from_date: string;
  to_date: string;
  search: string;
}
