async function apiFetch(url, options = {}) {
  const isFormData = options.body instanceof FormData;

  const res = await fetch(url, {
    credentials: "include", // 쿠키 포함
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
  return data;
}

document.addEventListener("DOMContentLoaded", () => {
  // 요소 참조
  const loginForm = document.getElementById("login-form");
  const loginResult = document.getElementById("login-result");
  const meSection = document.getElementById("me-section");
  const meInfo = document.getElementById("me-info");
  const logoutBtn = document.getElementById("logout-btn");

  const createAdSection = document.getElementById("create-ad-section");
  const createAdForm = document.getElementById("create-ad-form");
  const createAdResult = document.getElementById("create-ad-result");

  const adsSection = document.getElementById("ads-section");
  const loadAdsBtn = document.getElementById("load-ads-btn");
  const adsList = document.getElementById("ads-list");
    
  const adDetailSection = document.getElementById("ad-detail-section");
  const detailAdIdInput = document.getElementById("detail-ad-id");
  const loadAdDetailBtn = document.getElementById("load-ad-detail-btn");
  const deleteAdBtn = document.getElementById("delete-ad-btn");
  const adDetailView = document.getElementById("ad-detail-view");

  const updateAdForm = document.getElementById("update-ad-form");
  const updateAdResult = document.getElementById("update-ad-result");

  // ----------------------------
  // 로그인 처리
  // ----------------------------
  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const formData = new FormData(loginForm);

    const body = {
      loginId: formData.get("loginId"),
      password: formData.get("password"),
    };

    try {
      const res = await apiFetch("/api/admin/login", {
        method: "POST",
        body: JSON.stringify(body),
      });

      loginResult.textContent = res.message;

      meSection.style.display = "block";
      createAdSection.style.display = "block";
      adsSection.style.display = "block";
      adDetailSection.style.display = "block";

      await loadMe();
    } catch (err) {
      loginResult.textContent = err.message;
    }
  });

  // 관리자 정보 조회
  async function loadMe() {
    try {
      const res = await apiFetch("/api/admin/me");
      meInfo.textContent = JSON.stringify(res.result, null, 2);
    } catch (err) {
      meInfo.textContent = "로그인 필요: " + err.message;
    }
  }

  // ----------------------------
  // 로그아웃
  // ----------------------------
  logoutBtn.addEventListener("click", async () => {
    try {
      await apiFetch("/api/auth/logout", { method: "POST" });

      meInfo.textContent = "";
      adsList.innerHTML = "";
      adDetailView.textContent = "";
      createAdResult.textContent = "";
      updateAdResult.textContent = "";
    } catch (err) {
      console.error(err);
    }
  });

  // ----------------------------
  // 광고 등록
  // ----------------------------
  createAdForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const formData = new FormData(createAdForm);

    try {
      const res = await apiFetch("/api/admin/ads", {
        method: "POST",
        body: formData,
      });

      createAdResult.textContent =
        "등록 완료:\n" + JSON.stringify(res.result, null, 2);

      await loadAds();
    } catch (err) {
      createAdResult.textContent = "등록 실패: " + err.message;
    }
  });

  // ----------------------------
  // 광고 목록 조회 (이미지 카드 렌더링)
  // ----------------------------
  async function loadAds() {
    try {
        const res = await apiFetch("/api/admin/ads?page=0&size=20");
        const ads = res.result?.content ?? [];

        // 기존 카드 초기화
        adsList.innerHTML = "";

        if (ads.length === 0) {
        adsList.textContent = "등록된 광고가 없습니다.";
        return;
        }

        ads.forEach((ad) => {
        const card = document.createElement("div");
        card.className = "ad-card";

        const imgHtml = ad.image_url
            ? `<img src="${ad.image_url}" alt="${ad.title ?? ""}">`
            : "";

        const shortUrlText =
            ad.target_url && ad.target_url.length > 30
            ? ad.target_url.substring(0, 30) + "..."
            : ad.target_url || "";

        card.innerHTML = `
            ${imgHtml}
            <div class="ad-title">[${ad.id}] ${ad.title ?? ""}</div>
            <div class="ad-desc">${ad.description ?? ""}</div>
            <div class="ad-url">
            ${
                ad.target_url
                ? `<a href="${ad.target_url}" target="_blank" rel="noreferrer noopener">${shortUrlText}</a>`
                : ""
            }
            </div>
        `;

        adsList.appendChild(card);
        });
    } catch (err) {
        adsList.innerHTML = "";
        const errorDiv = document.createElement("div");
        errorDiv.textContent = "목록 조회 실패: " + err.message;
        adsList.appendChild(errorDiv);
    }
}

loadAdsBtn.addEventListener("click", loadAds);

  // ----------------------------
  // 광고 단건 조회
  // ----------------------------
  loadAdDetailBtn.addEventListener("click", async () => {
    const adId = detailAdIdInput.value;
    if (!adId) return alert("ID를 입력해줘.");

    try {
      const res = await apiFetch(`/api/admin/ads/${adId}`);
      adDetailView.textContent = JSON.stringify(res.result, null, 2);

      fillUpdateForm(res.result);
    } catch (err) {
      adDetailView.textContent = "조회 실패: " + err.message;
    }
  });

  function fillUpdateForm(ad) {
    updateAdForm.elements["title"].value = ad.title || "";
    updateAdForm.elements["description"].value = ad.description || "";
    updateAdForm.elements["target_url"].value = ad.target_url || "";
  }

  // ----------------------------
  // 광고 수정 (PATCH)
  // ----------------------------
  updateAdForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const adId = detailAdIdInput.value;
    if (!adId) return alert("광고 ID를 먼저 입력하고 조회해줘.");

    const form = updateAdForm;
    const body = {};

    const title = form.elements["title"].value;
    const desc = form.elements["description"].value;
    const targetUrl = form.elements["target_url"].value;

    if (title) body.title = title;
    if (desc) body.description = desc;
    if (targetUrl) body.target_url = targetUrl;

    try {
      const res = await apiFetch(`/api/admin/ads/${adId}`, {
        method: "PATCH",
        body: JSON.stringify(body),
      });

      updateAdResult.textContent =
        "수정 완료:\n" + JSON.stringify(res.result, null, 2);

      adDetailView.textContent = JSON.stringify(res.result, null, 2);
      await loadAds();
    } catch (err) {
      updateAdResult.textContent = "수정 실패: " + err.message;
    }
  });

  // ----------------------------
  // 광고 삭제
  // ----------------------------
  deleteAdBtn.addEventListener("click", async () => {
    const adId = detailAdIdInput.value;
    if (!adId) return alert("삭제할 광고 ID를 입력해줘.");
    if (!confirm(`정말 광고 ID ${adId} 을 삭제할까?`)) return;

    try {
      await apiFetch(`/api/admin/ads/${adId}`, {
        method: "DELETE",
      });

      updateAdResult.textContent = "삭제 완료";
      adDetailView.textContent = "";

      await loadAds();
    } catch (err) {
      updateAdResult.textContent = "삭제 실패: " + err.message;
    }
  });

  // ----------------------------
  // 최초 페이지 로딩 시 세션 체크
  // ----------------------------
  loadMe()
    .then(() => {
      meSection.style.display = "block";
      createAdSection.style.display = "block";
      adsSection.style.display = "block";
      adDetailSection.style.display = "block";
    })
    .catch(() => {});
});
