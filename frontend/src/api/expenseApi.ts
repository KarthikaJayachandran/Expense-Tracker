import axios from "axios";
import type {
  Expense,
  ExpenseFormData,
  FilterParams,
  MonthlySummary,
} from "../types/expense";

const API = axios.create({
  baseURL: "http://localhost:8000",
  headers: {
    "Content-Type": "application/json",
  },
});

// Helper to extract clean error message from Axios errors
export const getErrorMessage = (error: any): string => {
  if (axios.isAxiosError(error)) {
    const data = error.response?.data;
    if (data) {
      if (typeof data.detail === "string") {
        return data.detail;
      }
      if (Array.isArray(data.detail)) {
        return data.detail.map((e: any) => e.msg).join(", ");
      }
      if (data.message) {
        return data.message;
      }
    }
    return error.message || "Network error occurred";
  }
  return error instanceof Error ? error.message : "An unexpected error occurred";
};

export const expenseApi = {
  /** Fetch all expenses with optional filters */
  async list(filters?: Partial<FilterParams>): Promise<Expense[]> {
    const params: Record<string, string> = {};
    if (filters) {
      if (filters.category) params.category = filters.category;
      if (filters.from_date) params.from_date = filters.from_date;
      if (filters.to_date) params.to_date = filters.to_date;
      if (filters.search?.trim()) params.search = filters.search.trim();
    }
    const response = await API.get<Expense[]>("/expenses", { params });
    return response.data;
  },

  /** Fetch single expense by id */
  async get(id: number): Promise<Expense> {
    const response = await API.get<Expense>(`/expenses/${id}`);
    return response.data;
  },

  /** Create a new expense */
  async create(data: ExpenseFormData): Promise<Expense> {
    const response = await API.post<Expense>("/expenses", {
      title: data.title.trim(),
      amount: parseFloat(data.amount),
      category: data.category,
      date: data.date,
      note: data.note.trim() || null,
    });
    return response.data;
  },

  /** Update (full replace) an expense */
  async update(id: number, data: ExpenseFormData): Promise<Expense> {
    const response = await API.put<Expense>(`/expenses/${id}`, {
      title: data.title.trim(),
      amount: parseFloat(data.amount),
      category: data.category,
      date: data.date,
      note: data.note.trim() || null,
    });
    return response.data;
  },

  /** Delete an expense */
  async delete(id: number): Promise<void> {
    await API.delete(`/expenses/${id}`);
  },

  /** Monthly summary */
  async monthlySummary(year?: number, month?: number): Promise<MonthlySummary> {
    const params: Record<string, number> = {};
    if (year) params.year = year;
    if (month) params.month = month;
    const response = await API.get<MonthlySummary>("/summary/current-month", { params });
    return response.data;
  },
};
