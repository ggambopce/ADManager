// static/ads_api.js
export async function apiFetch(url, options = {}) {
  const isFormData = options.body instanceof FormData;

  const res = await fetch(url, {
    credentials: "include", // 관리자 세션 쿠키 포함
    ...options,
    headers: {
      ...(isFormData ? {} : { "Content-Type": "application/json" }),
      ...(options.headers || {}),
    },
  });

  const data = await res.json().catch(() => null);

  if (!res.ok) {
    const msg = data?.message || data?.detail || "API error";
    throw new Error(msg);
  }

  // ApiResponse 래퍼를 쓰므로 result만 꺼내서 반환
  return data?.result ?? data;
}
