// static/js/admin_auth.js
(function () {
  // 페이지 공통 로그인/로그아웃 관리 스크립트
  document.addEventListener("DOMContentLoaded", () => {
    const loginForm = document.getElementById("login-form");
    const loginResult = document.getElementById("login-result");
    const topbarUser = document.getElementById("topbar-user");
    const adminNameSpan = document.getElementById("admin-name");
    const logoutBtn = document.getElementById("logout-btn");

    if (!loginForm || !topbarUser) {
      return;
    }

    // ---------- 공통 fetch (Auth 용) ----------
    async function authFetch(url, options = {}) {
      const isFormData = options.body instanceof FormData;

      const res = await fetch(url, {
        credentials: "include", // 세션 쿠키 포함
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
      return data; // 여기서는 ApiResponse 전체 그대로
    }

    // ---------- 로그인 ----------
    loginForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      loginResult.textContent = "";

      const formData = new FormData(loginForm);
      const body = {
        loginId: formData.get("loginId"),
        password: formData.get("password"),
      };

      try {
        const res = await authFetch("/api/admin/login", {
          method: "POST",
          body: JSON.stringify(body),
        });

        loginResult.textContent = res.message || "로그인 성공";

        // 폼 숨기고, 사용자 영역 표시
        loginForm.style.display = "none";
        topbarUser.style.display = "flex";

        // 관리자 정보 다시 조회
        await loadMe();
      } catch (err) {
        loginResult.textContent = err.message;
      }
    });

    // ---------- 현재 관리자 정보 조회 ----------
    async function loadMe() {
      try {
        const res = await authFetch("/api/admin/me");
        const admin = res.result;

        if (admin && admin.loginId) {
          adminNameSpan.textContent = admin.loginId;
        } else if (admin && admin.username) {
          adminNameSpan.textContent = admin.username;
        } else {
          adminNameSpan.textContent = "관리자";
        }

        // 로그인 상태 UI
        loginForm.style.display = "none";
        topbarUser.style.display = "flex";
      } catch (err) {
        // 미로그인 상태면 폼만 보이게
        adminNameSpan.textContent = "";
        loginForm.style.display = "flex";
        topbarUser.style.display = "none";
      }
    }

    // ---------- 로그아웃 ----------
    logoutBtn.addEventListener("click", async () => {
      try {
        await authFetch("/api/auth/logout", { method: "POST" });

        adminNameSpan.textContent = "";
        loginResult.textContent = "";

        // 폼은 다시 보이게, 사용자 영역 숨기기
        loginForm.style.display = "flex";
        topbarUser.style.display = "none";

        // 비밀번호는 비워둔다
        loginForm.elements["password"].value = "";
      } catch (err) {
        console.error(err);
      }
    });

    // 페이지 진입 시 세션 체크 (새로고침해도 로그인 유지)
    loadMe();
  });
})();
