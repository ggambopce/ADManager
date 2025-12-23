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

  return data?.result ?? data;
}

function truncate(text, n) {
  if (!text) return "";
  return text.length > n ? text.substring(0, n) + "..." : text;
}

document.addEventListener("DOMContentLoaded", () => {
  const adId = document.getElementById("ad-id").value;

  const idEl = document.getElementById("detail-id");
  const typeEl = document.getElementById("detail-type");        // (추가된 요소)
  const titleEl = document.getElementById("detail-title");
  const descEl = document.getElementById("detail-description");
  const urlEl = document.getElementById("detail-url");
  const previewEl = document.getElementById("detail-preview");  // (detail-image → detail-preview)
  const createdEl = document.getElementById("detail-created");
  const msg = document.getElementById("detail-message");

  const btnBack = document.getElementById("btn-back");
  const btnEdit = document.getElementById("btn-edit");
  const btnDelete = document.getElementById("btn-delete");

  btnBack.addEventListener("click", () => (window.location.href = "/ads"));
  btnEdit.addEventListener("click", () => (window.location.href = `/ads/${adId}/edit`));

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
      typeEl.textContent = ad.ad_type || "IMAGE";
      titleEl.textContent = ad.title ?? "";
      descEl.textContent = ad.description ?? "";
      createdEl.textContent = ad.created_at || ad.createdAt || ad.created || "";

      urlEl.textContent = "";
      previewEl.innerHTML = "";

      const adType = ad.ad_type || "IMAGE";

      if (adType === "IFRAME") {
        const src = ad.embed_src || "";
        if (src) {
          urlEl.innerHTML = `<a href="${src}" target="_blank" rel="noreferrer noopener">${truncate(src, 60)}</a>`;
          const w = ad.embed_width || 300;
          const h = ad.embed_height || 250;

          previewEl.innerHTML = `
            <iframe
              scrolling="no"
              src="${src}"
              width="${w}"
              height="${h}"
              frameborder="0"
              marginwidth="0"
              marginheight="0"
              style="border:0; overflow:hidden;"
            ></iframe>
          `;
        }
      } else {
        const clickUrl = ad.short_url || ad.target_url || "";
        if (clickUrl) {
          urlEl.innerHTML = `<a href="${clickUrl}" target="_blank" rel="noreferrer noopener">${truncate(clickUrl, 60)}</a>`;
        }

        if (ad.image_url) {
          previewEl.innerHTML = `
            <img src="${ad.image_url}" alt="${ad.title ?? ""}"
              style="max-width:300px;border-radius:8px;" />
          `;
        }
      }
    } catch (e) {
      msg.textContent = "상세 조회 실패: " + e.message;
    }
  }
});
