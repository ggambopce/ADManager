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

  return data?.result ?? data;
}

document.addEventListener("DOMContentLoaded", () => {
  const mode = document.getElementById("form-mode").value;
  const adId = document.getElementById("ad-id").value || null;

  const form = document.getElementById("ad-form");

  const typeSelect = document.getElementById("ad_type");
  const titleInput = document.getElementById("title");
  const descInput = document.getElementById("description");

  const urlInput = document.getElementById("target_url");
  const imageInput = document.getElementById("image");
  const currentImageDiv = document.getElementById("current-image");

  const embedSrcInput = document.getElementById("embed_src");
  const embedWInput = document.getElementById("embed_width");
  const embedHInput = document.getElementById("embed_height");

  const targetRow = document.getElementById("target-row");
  const imageRow = document.getElementById("image-row");
  const iframeRow = document.getElementById("iframe-row");
  const iframeSizeRow = document.getElementById("iframe-size-row");

  const msg = document.getElementById("form-message");
  const btnCancel = document.getElementById("btn-cancel");

  function toggleFields() {
    const t = typeSelect.value;
    if (t === "IMAGE") {
      targetRow.style.display = "";
      imageRow.style.display = "";
      iframeRow.style.display = "none";
      iframeSizeRow.style.display = "none";
    } else {
      targetRow.style.display = "none";
      imageRow.style.display = "none";
      iframeRow.style.display = "";
      iframeSizeRow.style.display = "";
    }
  }

  typeSelect.addEventListener("change", toggleFields);
  toggleFields();

  if (mode === "edit" && adId) loadExisting();

  btnCancel.addEventListener("click", () => {
    window.location.href = adId ? `/ads/${adId}` : "/ads";
  });

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    msg.textContent = "";

    const adType = typeSelect.value;

    try {
      if (mode === "edit" && adId) {
        // 수정은 PATCH 하나로 통일 (서버 update_ad에서 타입별 허용 필드 제한)
        const body =
          adType === "IFRAME"
            ? {
                title: titleInput.value,
                description: descInput.value,
                embed_src: embedSrcInput.value,
                embed_width: Number(embedWInput.value || 300),
                embed_height: Number(embedHInput.value || 250),
              }
            : {
                title: titleInput.value,
                description: descInput.value,
                target_url: urlInput.value,
              };

        await apiFetch(`/api/admin/ads/${adId}`, {
          method: "PATCH",
          body: JSON.stringify(body),
        });

        window.location.href = `/ads/${adId}`;
        return;
      }

      // 등록
      if (adType === "IFRAME") {
        // JSON 등록 엔드포인트 필요: POST /api/admin/ads/iframe
        const body = {
          ad_type: "IFRAME",
          title: titleInput.value,
          description: descInput.value,
          embed_src: embedSrcInput.value,
          embed_width: Number(embedWInput.value || 300),
          embed_height: Number(embedHInput.value || 250),
        };

        const created = await apiFetch("/api/admin/ads/iframe", {
          method: "POST",
          body: JSON.stringify(body),
        });

        window.location.href = created?.id ? `/ads/${created.id}` : "/ads";
      } else {
        // 기존 IMAGE 등록 (multipart)
        const fd = new FormData();
        fd.append("ad_type", "IMAGE");
        fd.append("title", titleInput.value);
        fd.append("description", descInput.value);
        fd.append("target_url", urlInput.value);

        if (!imageInput.files[0]) throw new Error("이미지를 선택해줘.");
        fd.append("image", imageInput.files[0]);

        const created = await apiFetch("/api/admin/ads", {
          method: "POST",
          body: fd,
        });

        window.location.href = created?.id ? `/ads/${created.id}` : "/ads";
      }
    } catch (e2) {
      msg.textContent = (mode === "edit" ? "수정 실패: " : "등록 실패: ") + e2.message;
    }
  });

  async function loadExisting() {
    try {
      const ad = await apiFetch(`/api/admin/ads/${adId}`);

      const t = ad.ad_type || "IMAGE";
      typeSelect.value = t;
      toggleFields();

      titleInput.value = ad.title ?? "";
      descInput.value = ad.description ?? "";

      if (t === "IFRAME") {
        embedSrcInput.value = ad.embed_src ?? "";
        embedWInput.value = ad.embed_width ?? 300;
        embedHInput.value = ad.embed_height ?? 250;
      } else {
        urlInput.value = ad.target_url ?? "";
        if (ad.image_url) {
          currentImageDiv.innerHTML = `현재 이미지: <br><img src="${ad.image_url}" alt="${ad.title ?? ""}" style="max-width:200px;border-radius:6px;" />`;
        } else {
          currentImageDiv.textContent = "등록된 이미지 없음";
        }
      }
    } catch (e) {
      msg.textContent = "기존 광고 로딩 실패: " + e.message;
    }
  }
});
