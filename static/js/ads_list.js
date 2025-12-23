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

  return data?.result ?? data;
}

function truncate(text, n) {
  if (!text) return "";
  return text.length > n ? text.substring(0, n) + "..." : text;
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
      const pageRes = await apiFetch("/api/admin/ads?page=0&size=20");
      const ads = pageRes.content ?? [];

      tbody.innerHTML = "";

      if (ads.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5">등록된 광고가 없다.</td></tr>';
        return;
      }

      ads.forEach((ad) => {
        const tr = document.createElement("tr");
        const created = ad.created_at || ad.createdAt || ad.created || "";
        const type = ad.ad_type || "IMAGE";

        let link = "";
        let href = "";

        if (type === "IFRAME") {
          href = ad.embed_src || "";
          link = href ? `<a href="${href}" target="_blank" rel="noreferrer noopener">${truncate(href, 35)}</a>` : "";
        } else {
          href = ad.short_url || ad.target_url || "";
          link = href ? `<a href="${href}" target="_blank" rel="noreferrer noopener">${truncate(href, 35)}</a>` : "";
        }

        tr.innerHTML = `
          <td>${ad.id}</td>
          <td>${type}</td>
          <td><a href="/ads/${ad.id}">${ad.title ?? ""}</a></td>
          <td>${link}</td>
          <td>${created}</td>
        `;

        tbody.appendChild(tr);
      });
    } catch (e) {
      msg.textContent = "목록 조회 실패: " + e.message;
    }
  }
});
