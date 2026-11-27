export function EmptyState({ children = "اطلاعاتی برای نمایش وجود ندارد." }: { children?: string }) {
  return <div className="empty-state" role="status">{children}</div>;
}
