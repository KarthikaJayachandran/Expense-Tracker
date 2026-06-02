import { CATEGORIES } from "../types/expense";
import type { FilterParams } from "../types/expense";

interface Props {
  filters: FilterParams;
  onChange: (filters: FilterParams) => void;
  onReset: () => void;
}

export function Filters({ filters, onChange, onReset }: Props) {
  function handleChange(
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) {
    const { name, value } = e.target;
    onChange({ ...filters, [name]: value });
  }

  const hasActiveFilters =
    !!(filters.category || filters.from_date || filters.to_date || filters.search);

  const isDateRangeInvalid =
    !!(filters.from_date && filters.to_date && filters.from_date > filters.to_date);

  return (
    <div className="filters-container">
      <div className="filter-bar">
        <div className="filter-group">
          <label htmlFor="filter-search">🔍 Search</label>
          <input
            id="filter-search"
            name="search"
            type="text"
            placeholder="Search by title..."
            value={filters.search}
            onChange={handleChange}
          />
        </div>

        <div className="filter-group">
          <label htmlFor="filter-category">📂 Category</label>
          <select
            id="filter-category"
            name="category"
            value={filters.category}
            onChange={handleChange}
          >
            <option value="">All Categories</option>
            {CATEGORIES.map((cat) => (
              <option key={cat} value={cat}>{cat}</option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label htmlFor="filter-from-date">📅 From</label>
          <input
            id="filter-from-date"
            name="from_date"
            type="date"
            value={filters.from_date}
            onChange={handleChange}
            className={isDateRangeInvalid ? "input-error" : ""}
          />
        </div>

        <div className="filter-group">
          <label htmlFor="filter-to-date">📅 To</label>
          <input
            id="filter-to-date"
            name="to_date"
            type="date"
            value={filters.to_date}
            onChange={handleChange}
            className={isDateRangeInvalid ? "input-error" : ""}
          />
        </div>

        {hasActiveFilters && (
          <button className="btn btn-ghost btn-sm" onClick={onReset} id="clear-filters-btn">
            ✕ Clear Filters
          </button>
        )}
      </div>

      {isDateRangeInvalid && (
        <div className="alert alert-error" style={{ marginTop: "10px", display: "block" }}>
          ⚠️ <strong>Invalid Date Range:</strong> The "From" date cannot be after the "To" date.
        </div>
      )}
    </div>
  );
}
