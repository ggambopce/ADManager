// static/ads_list.js

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

  // ApiResponse<AdPageResponse>
  return data?.result ?? data;
}

document.addEventListener("DOMContentLoaded", () => {
  const tbody = document.querySelector("#ads-table tbody");
  const btnNew = document.getElementById("btn-new");
  const msg = document.getElementById("list-message");

  btnNew.addEventListener("click", () => {
    window.location.href = "/ads/new";
  });

  loadAds();

  async function loadAds() {
    msg.textContent = "";
    try {
      // page, size 는 필요에 맞게
      const pageRes = await apiFetch("/api/admin/ads?page=0&size=20");
      const ads = pageRes.content ?? [];

      tbody.innerHTML = "";

      if (ads.length === 0) {
        tbody.innerHTML =
          '<tr><td colspan="4">등록된 광고가 없다.</td></tr>';
        return;
      }

      ads.forEach((ad) => {
        const tr = document.createElement("tr");

        const created =
          ad.created_at || ad.createdAt || ad.created || "";

        const urlText =
          ad.target_url && ad.target_url.length > 25
            ? ad.target_url.substring(0, 25) + "..."
            : ad.target_url || "";

        tr.innerHTML = `
          <td>${ad.id}</td>
          <td><a href="/ads/${ad.id}">${ad.title ?? ""}</a></td>
          <td>
            ${
              ad.target_url
                ? `<a href="${ad.target_url}" target="_blank" rel="noreferrer noopener">${urlText}</a>`
                : ""
            }
          </td>
          <td>${created}</td>
        `;

        tbody.appendChild(tr);
      });
    } catch (e) {
      msg.textContent = "목록 조회 실패: " + e.message;
    }
  }
});
