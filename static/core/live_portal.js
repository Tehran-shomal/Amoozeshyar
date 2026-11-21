/* پوستهٔ مشترک: منو، جستجو، خروج و پیام خطا. منطق هر گروه در پوشهٔ خودش است. */
window.PortalUI = {
    errorMessage(error) {
        const messages = {
            invalid_credentials: "نام کاربری یا گذرواژه نادرست است.",
            account_locked: "حساب به‌علت تلاش‌های ناموفق موقتاً قفل شده است.",
            account_inactive: "حساب غیرفعال است.",
            authentication_required: "نشست پایان یافته است؛ دوباره وارد شوید.",
            permission_denied: "حساب شما اجازهٔ انجام این عملیات را ندارد.",
            student_profile_not_found: "پروندهٔ دانشجویی پیدا نشد.",
            student_profile_ambiguous: "ابتدا پروندهٔ دانشجویی را انتخاب کنید.",
            registration_window_closed: "بازهٔ انتخاب واحد باز نیست.",
            drop_window_closed: "بازهٔ حذف درس باز نیست.",
            tuition_debt: "بدهی شهریه مانع انتخاب واحد است.",
            offering_full: "ظرفیت درس تکمیل شده است.",
            credit_limit_exceeded: "انتخاب این درس از سقف مجاز واحد بیشتر است.",
            schedule_conflict: "زمان درس با برنامهٔ شما تداخل دارد.",
            prerequisite_not_met: "پیش‌نیاز درس گذرانده نشده است.",
            term_not_active: "این نیمسال فعال نیست.",
            student_not_eligible: "وضعیت تحصیلی اجازهٔ انتخاب واحد نمی‌دهد.",
            enrollment_not_owned: "این ثبت‌نام متعلق به شما نیست."
        };
        return messages[error?.code] || (error instanceof TypeError
            ? "ارتباط با سامانه برقرار نشد؛ دوباره تلاش کنید."
            : "عملیات انجام نشد. " + (error?.message || "دوباره تلاش کنید."));
    },
    showStatus(message, selector = "[data-api-status]") {
        const node = document.querySelector(selector);
        if (!node) return;
        (node.querySelector("p") || node).textContent = message;
        node.hidden = false;
        node.scrollIntoView({block: "nearest", behavior: "smooth"});
    },
    profile() {
        return JSON.parse(document.getElementById("api-profile")?.textContent || "{}");
    }
};
document.addEventListener("DOMContentLoaded", () => {
    // Use the browser's native dialog behavior, including keyboard focus and Escape.
    const termDialog = document.querySelector("[data-term-dialog]");
    document.querySelector("[data-term-dialog-open]")?.addEventListener("click", () => {
        if (termDialog?.showModal) termDialog.showModal();
    });
    document.querySelector("[data-term-dialog-close]")?.addEventListener("click", () => termDialog?.close());
    termDialog?.addEventListener("click", event => {
        if (event.target === termDialog) termDialog.close();
    });

    const toggle = document.querySelector("[data-menu-toggle]");
    const close = () => { document.body.classList.remove("sidebar-open"); toggle?.setAttribute("aria-expanded", "false"); };
    toggle?.setAttribute("aria-expanded", "false");
    toggle?.addEventListener("click", () => {
        const open = document.body.classList.toggle("sidebar-open");
        toggle.setAttribute("aria-expanded", String(open));
    });
    document.querySelector("[data-sidebar-close]")?.addEventListener("click", close);
    document.addEventListener("keydown", event => { if (event.key === "Escape") close(); });
    document.querySelectorAll("[data-table-search]").forEach(input => input.addEventListener("input", () => {
        input.closest(".panel").querySelectorAll("tbody tr").forEach(row => {
            row.hidden = !row.textContent.toLocaleLowerCase().includes(input.value.trim().toLocaleLowerCase());
        });
    }));
    document.querySelector("[data-global-search]")?.addEventListener("input", event => {
        const needle = event.target.value.trim().toLocaleLowerCase();
        document.querySelectorAll(".sidebar-nav .nav-link").forEach(link => {
            link.hidden = !link.textContent.toLocaleLowerCase().includes(needle);
        });
        document.querySelectorAll(".nav-group").forEach(group => {
            group.hidden = ![...group.querySelectorAll(".nav-link")].some(link => !link.hidden);
            if (needle && !group.hidden) group.open = true;
        });
    });
    document.querySelectorAll("[data-api-logout-form]").forEach(form => form.addEventListener("submit", async event => {
        event.preventDefault();
        const button = form.querySelector("button");
        button.disabled = true;
        try { await window.PortalApi.logout(); window.location.assign(form.dataset.loginRedirect); }
        catch (error) { window.PortalUI.showStatus(window.PortalUI.errorMessage(error)); }
        finally { button.disabled = false; }
    }));
    document.querySelectorAll("[data-print]").forEach(button => button.addEventListener("click", () => window.print()));
    // Prevent repeated clicks while the native POST and redirect complete.
    document.querySelectorAll("form.live-form").forEach(form => form.addEventListener("submit", () => {
        form.querySelectorAll('[type="submit"]').forEach(button => button.disabled = true);
    }));
});
