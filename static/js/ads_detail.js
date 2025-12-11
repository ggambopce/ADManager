// static/ads_detail.js

async function apiFetch(url, options = {}) {
  const isFormData = options.body instanceof FormData;

  const res = await fetch(url, {
    credentials: "include",
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

  // ApiResponse<AdResponse>
  return data?.result ?? data;
}

document.addEventListener("DOMContentLoaded", () => {
  const adId = document.getElementById("ad-id").value;

  const idEl = document.getElementById("detail-id");
  const titleEl = document.getElementById("detail-title");
  const descEl = document.getElementById("detail-description");
  const urlEl = document.getElementById("detail-url");
  const imageEl = document.getElementById("detail-image");
  const createdEl = document.getElementById("detail-created");
  const msg = document.getElementById("detail-message");

  const btnBack = document.getElementById("btn-back");
  const btnEdit = document.getElementById("btn-edit");
  const btnDelete = document.getElementById("btn-delete");

  btnBack.addEventListener("click", () => {
    window.location.href = "/ads";
  });

  btnEdit.addEventListener("click", () => {
    window.location.href = `/ads/${adId}/edit`;
  });

  btnDelete.addEventListener("click", async () => {
    if (!confirm("정말 삭제할까?")) return;

    try {
      await apiFetch(`/api/admin/ads/${adId}`, { method: "DELETE" });
      window.location.href = "/ads";
    } catch (e) {
      msg.textContent = "삭제 실패: " + e.message;
    }
  });

  loadDetail();

  async function loadDetail() {
    msg.textContent = "";
    try {
      const ad = await apiFetch(`/api/admin/ads/${adId}`);

      idEl.textContent = ad.id;
      titleEl.textContent = ad.title ?? "";
      descEl.textContent = ad.description ?? "";

      if (ad.target_url) {
        const urlText =
          ad.target_url.length > 40
            ? ad.target_url.substring(0, 40) + "..."
            : ad.target_url;
        urlEl.innerHTML = `<a href="${ad.target_url}" target="_blank" rel="noreferrer noopener">${urlText}</a>`;
      } else {
        urlEl.textContent = "";
      }

      if (ad.image_url) {
        imageEl.innerHTML = `<img src="${ad.image_url}" alt="${ad.title ?? ""}" style="max-width:300px;border-radius:8px;" />`;
      } else {
        imageEl.textContent = "";
      }

      createdEl.textContent =
        ad.created_at || ad.createdAt || ad.created || "";
    } catch (e) {
      msg.textContent = "상세 조회 실패: " + e.message;
    }
  }
});
