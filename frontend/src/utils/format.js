export function formatDate(value) {
  if (!value) {
    return "—";
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return String(value);
  }
  return date.toLocaleString(undefined, { hour12: false });
}

export function formatDuration(ms) {
  if (ms == null || ms === "") {
    return "—";
  }
  const n = Number(ms);
  if (Number.isNaN(n)) {
    return "—";
  }
  if (n < 1000) {
    return `${Math.round(n)} ms`;
  }
  return `${(n / 1000).toFixed(2)} s`;
}

export function shortId(id) {
  if (!id) {
    return "—";
  }
  const s = String(id);
  return s.length > 12 ? `${s.slice(0, 8)}…` : s;
}

export function unwrapList(data) {
  if (Array.isArray(data)) {
    return { items: data, total: data.length, page: 1, limit: data.length || 20 };
  }
  const items = data?.items || data?.results || [];
  return {
    items,
    total: data?.total ?? data?.count ?? items.length,
    page: data?.page ?? 1,
    limit: data?.limit ?? 20,
  };
}

export function buildJobQuery(filters) {
  const params = {};
  const keys = [
    "status",
    "queue_id",
    "priority",
    "worker_id",
    "created_after",
    "created_before",
    "q",
    "sort",
    "order",
    "page",
    "limit",
  ];
  keys.forEach((key) => {
    const value = filters[key];
    if (value !== undefined && value !== null && value !== "") {
      params[key] = value;
    }
  });
  return params;
}
