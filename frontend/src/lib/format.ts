export function formatDateTime(value: string | null | undefined) {
  if (!value) return "—";
  return new Intl.DateTimeFormat(undefined, { dateStyle: "medium", timeStyle: "short" }).format(new Date(value));
}

export function shortId(value: string) {
  return value.slice(0, 8).toUpperCase();
}

export const formatDate = formatDateTime;
