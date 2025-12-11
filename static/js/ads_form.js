// static/ads_form.js

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

  // ApiResponse 래퍼
  return data?.result ?? data;
}

document.addEventListener("DOMContentLoaded", () => {
  const mode = document.getElementById("form-mode").value; // "create" | "edit"
  const adId = document.getElementById("ad-id").value || null;

  const form = document.getElementById("ad-form");
  const titleInput = document.getElementById("title");
  const descInput = document.getElementById("description");
  const urlInput = document.getElementById("target_url");
  const imageInput = document.getElementById("image");
  const currentImageDiv = document.getElementById("current-image");
  const msg = document.getElementById("form-message");
  const btnCancel = document.getElementById("btn-cancel");

  if (mode === "edit" && adId) {
    // 수정 모드에서는 기존 데이터 로딩
    loadExisting();
  }

  btnCancel.addEventListener("click", () => {
    if (adId) {
      window.location.href = `/ads/${adId}`;
    } else {
      window.location.href = "/ads";
    }
  });

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    msg.textContent = "";

    try {
      if (mode === "edit" && adId) {
        // 수정: JSON PATCH (이미지 제외)
        const body = {
          title: titleInput.value,
          description: descInput.value,
          target_url: urlInput.value,
        };

        await apiFetch(`/api/admin/ads/${adId}`, {
          method: "PATCH",
          body: JSON.stringify(body),
        });

        window.location.href = `/ads/${adId}`;
      } else {
        // 등록: multipart/form-data (이미지 포함)
        const fd = new FormData();
        fd.append("title", titleInput.value);
        fd.append("description", descInput.value);
        fd.append("target_url", urlInput.value);

        if (!imageInput.files[0]) {
          throw new Error("이미지를 선택해줘.");
        }
        fd.append("image", imageInput.files[0]);

        const created = await apiFetch("/api/admin/ads", {
          method: "POST",
          body: fd,
        });

        if (created && created.id) {
          window.location.href = `/ads/${created.id}`;
        } else {
          window.location.href = "/ads";
        }
      }
    } catch (e2) {
      msg.textContent =
        (mode === "edit" ? "수정 실패: " : "등록 실패: ") + e2.message;
    }
  });

  async function loadExisting() {
    try {
      const ad = await apiFetch(`/api/admin/ads/${adId}`);

      titleInput.value = ad.title ?? "";
      descInput.value = ad.description ?? "";
      urlInput.value = ad.target_url ?? "";

      if (ad.image_url) {
        currentImageDiv.innerHTML = `현재 이미지: <br><img src="${ad.image_url}" alt="${ad.title ?? ""}" style="max-width:200px;border-radius:6px;" />`;
      } else {
        currentImageDiv.textContent = "등록된 이미지 없음";
      }
    } catch (e) {
      msg.textContent = "기존 광고 로딩 실패: " + e.message;
    }
  }
});
