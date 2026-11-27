/* پوستهٔ مشترک: منو، جستجو، خروج و پیام خطا. منطق هر گروه در پوشهٔ خودش است. */
window.PortalUI = {
    errorMessage(error) {
        const messages = {
            invalid_credentials: "نام کاربری یا گذرواژه نادرست است.",
            account_locked: "حساب به‌علت تلاش‌های ناموفق موقتاً قفل شده است.",
            account_inactive: "حساب غیرفعال است.",
            authentication_required: "نشست پایان یافته است؛ دوباره وارد شوید.",
            permission_denied: "حساب شما اجازهٔ انجام این عملیات را ندارد.",
            page_not_found: "صفحهٔ درخواستی پیدا نشد.",
            page_data_not_found: "اطلاعات این صفحه پیدا نشد.",
            term_not_found: "نیمسال انتخاب‌شده پیدا نشد.",
            database_unavailable: "پایگاه داده در دسترس نیست.",
            invalid_form_payload: "اطلاعات فرم معتبر نیست.",
            validation_error: "فرم را بررسی و خطاها را اصلاح کنید.",
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
function pageApiUrl(shell) {
    return shell.dataset.pageApiUrl + window.location.search;
}

function formPayload(form) {
    const payload = {};
    for (const [name, value] of new FormData(form).entries()) {
        if (name === "csrfmiddlewaretoken") continue;
        if (value instanceof File) continue;
        if (Object.prototype.hasOwnProperty.call(payload, name)) {
            payload[name] = Array.isArray(payload[name]) ? [...payload[name], value] : [payload[name], value];
        } else {
            payload[name] = value;
        }
    }
    return payload;
}

function replacePortalShell(html) {
    const parsed = new DOMParser().parseFromString(html, "text/html");
    const currentShell = document.querySelector(".portal-shell");
    const nextShell = parsed.querySelector(".portal-shell");
    if (!currentShell || !nextShell) throw new Error("The page API did not return a portal shell.");

    const importedShell = document.importNode(nextShell, true);
    currentShell.replaceWith(importedShell);
    const currentProfile = document.getElementById("api-profile");
    const nextProfile = parsed.getElementById("api-profile");
    if (currentProfile && nextProfile) {
        currentProfile.replaceWith(document.importNode(nextProfile, true));
    }
    document.body.className = parsed.body.className;
    document.title = parsed.title;
    document.dispatchEvent(new CustomEvent("portal:content-loaded", {
        detail: { page: importedShell.dataset.portalPage },
    }));
    return importedShell;
}

function showLoadFailure(shell, error) {
    shell.dataset.portalLoading = "false";
    shell.setAttribute("aria-busy", "false");
    shell.querySelector("[data-page-loading]")?.remove();
    if (error.code === "authentication_required") {
        window.location.assign("/login/");
        return;
    }
    window.PortalUI.showStatus(window.PortalUI.errorMessage(error));
}

function renderOfferings(shell, offerings) {
    const table = shell.querySelector("[data-offerings-api-table]");
    const body = table?.querySelector("tbody");
    if (!body) return;

    const fragment = document.createDocumentFragment();
    const dayLabels = {
        saturday: "شنبه", sunday: "یکشنبه", monday: "دوشنبه", tuesday: "سه‌شنبه",
        wednesday: "چهارشنبه", thursday: "پنجشنبه", friday: "جمعه",
    };
    for (const offering of offerings) {
        const row = document.createElement("tr");
        const day = dayLabels[String(offering.day_of_week || "").toLowerCase()] || "";
        const start = String(offering.start_time || "").slice(0, 5);
        const end = String(offering.end_time || "").slice(0, 5);
        const units = Number(offering.total_units || 0);
        const cells = [
            offering.lesson_code,
            offering.title,
            offering.teacher,
            units,
            `${day} ${start}–${end}`.trim(),
            offering.remaining_capacity,
        ];
        for (const value of cells) {
            const cell = document.createElement("td");
            cell.textContent = value == null ? "—" : String(value);
            row.append(cell);
        }
        const actionCell = document.createElement("td");
        const button = document.createElement("button");
        button.type = "button";
        button.className = "table-action";
        button.dataset.enrollmentAction = "register";
        button.dataset.recordId = String(offering.id);
        button.textContent = "انتخاب درس";
        actionCell.append(button);
        row.append(actionCell);
        fragment.append(row);
    }

    if (!offerings.length) {
        const row = document.createElement("tr");
        const cell = document.createElement("td");
        cell.colSpan = 7;
        cell.className = "empty-state";
        cell.textContent = "برای این نیمسال درسی ارائه نشده است.";
        row.append(cell);
        fragment.append(row);
    }
    body.replaceChildren(fragment);
}

async function loadActiveTerm(shell) {
    try {
        const { term } = await window.PortalApi.activeTerm();
        if (!term) return;
        shell.dataset.activeTermCode = term.term_code;
        const button = shell.querySelector("[data-term-dialog-open]");
        if (button) button.title = `نیمسال فعال: ${term.term_code}`;
    } catch (error) {
        window.PortalUI.showStatus(window.PortalUI.errorMessage(error));
    }
}

async function loadCourseOfferings(shell) {
    const table = shell.querySelector("[data-offerings-api-table]");
    const courseModal = shell.querySelector("[data-course-modal]");
    if (!table && !courseModal) return;
    const selectedTerm = shell.dataset.selectedTermCode || new URLSearchParams(window.location.search).get("term");
    try {
        const payload = await window.PortalApi.offerings(selectedTerm || undefined);
        const offerings = payload.offerings || [];
        if (table) renderOfferings(shell, offerings);
        document.dispatchEvent(new CustomEvent("portal:offerings-loaded", {
            detail: { offerings, termCode: selectedTerm || "" },
        }));
    } catch (error) {
        document.dispatchEvent(new CustomEvent("portal:offerings-error", { detail: { error } }));
        window.PortalUI.showStatus(window.PortalUI.errorMessage(error));
    }
}

function bindPortalShell(shell) {
    const closeSidebar = () => {
        document.body.classList.remove("sidebar-open");
        shell.querySelector("[data-menu-toggle]")?.setAttribute("aria-expanded", "false");
    };
    shell.querySelector("[data-menu-toggle]")?.addEventListener("click", event => {
        const open = document.body.classList.toggle("sidebar-open");
        event.currentTarget.setAttribute("aria-expanded", String(open));
    });
    shell.querySelector("[data-sidebar-close]")?.addEventListener("click", closeSidebar);

    const dialog = shell.querySelector("[data-term-dialog]");
    shell.querySelector("[data-term-dialog-open]")?.addEventListener("click", () => dialog?.showModal?.());
    shell.querySelector("[data-term-dialog-close]")?.addEventListener("click", () => dialog?.close());
    dialog?.addEventListener("click", event => { if (event.target === dialog) dialog.close(); });

    shell.querySelectorAll("[data-table-search]").forEach(input => input.addEventListener("input", () => {
        input.closest(".panel")?.querySelectorAll("tbody tr").forEach(row => {
            row.hidden = !row.textContent.toLocaleLowerCase().includes(input.value.trim().toLocaleLowerCase());
        });
    }));
    shell.querySelector("[data-global-search]")?.addEventListener("input", event => {
        const needle = event.target.value.trim().toLocaleLowerCase();
        shell.querySelectorAll(".sidebar-nav .nav-link").forEach(link => {
            link.hidden = !link.textContent.toLocaleLowerCase().includes(needle);
        });
        shell.querySelectorAll(".nav-group").forEach(group => {
            group.hidden = ![...group.querySelectorAll(".nav-link")].some(link => !link.hidden);
            if (needle && !group.hidden) group.open = true;
        });
    });
    shell.querySelectorAll("[data-print]").forEach(button => button.addEventListener("click", () => window.print()));

    shell.addEventListener("submit", async event => {
        const form = event.target.closest("form");
        if (!form) return;
        if (form.matches("[data-api-logout-form]")) {
            event.preventDefault();
            const button = form.querySelector("button");
            button.disabled = true;
            try {
                await window.PortalApi.logout();
                window.location.assign(form.dataset.loginRedirect);
            } catch (error) {
                window.PortalUI.showStatus(window.PortalUI.errorMessage(error));
                button.disabled = false;
            }
            return;
        }
        if (!form.matches("form.live-form")) return;
        event.preventDefault();
        const buttons = [...form.querySelectorAll('[type="submit"]')];
        buttons.forEach(button => { button.disabled = true; });
        try {
            const result = await window.PortalApi.submitPage(pageApiUrl(shell), formPayload(form));
            if (result.redirect) window.location.assign(result.redirect);
        } catch (error) {
            if (error.payload?.html) {
                const replacement = replacePortalShell(error.payload.html);
                bindPortalShell(replacement);
                void loadActiveTerm(replacement);
                void loadCourseOfferings(replacement);
            }
            window.PortalUI.showStatus(window.PortalUI.errorMessage(error));
            buttons.forEach(button => { button.disabled = false; });
        }
    });
}

async function loadPortalPage() {
    const shell = document.querySelector(".portal-shell[data-page-api-url]");
    if (!shell) return;
    try {
        const page = await window.PortalApi.portalPage(pageApiUrl(shell));
        const loadedShell = replacePortalShell(page.html);
        bindPortalShell(loadedShell);
        void loadActiveTerm(loadedShell);
        void loadCourseOfferings(loadedShell);
    } catch (error) {
        showLoadFailure(shell, error);
    }
}

document.addEventListener("keydown", event => {
    if (event.key === "Escape") document.body.classList.remove("sidebar-open");
});
document.addEventListener("DOMContentLoaded", loadPortalPage);
