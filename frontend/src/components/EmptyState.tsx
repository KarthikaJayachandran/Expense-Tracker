interface EmptyStateProps {
  hasActiveFilters: boolean;
}

export function EmptyState({ hasActiveFilters }: EmptyStateProps) {
  if (hasActiveFilters) {
    return (
      <div className="empty-state">
        <div className="empty-icon">🔍</div>
        <h3>No matching expenses</h3>
        <p>
          No expenses match the selected filters.<br />
          Try adjusting the search term, category, or date range.
        </p>
      </div>
    );
  }

  return (
    <div className="empty-state">
      <div className="empty-icon">💸</div>
      <h3>No expenses found</h3>
      <p>Add your first expense to get started.</p>
    </div>
  );
}
