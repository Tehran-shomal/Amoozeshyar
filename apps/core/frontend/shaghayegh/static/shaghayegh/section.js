/* شقایق: جزئیات حذف در مودال PDF نشان داده می‌شود؛ API مالکیت و بازه را کنترل می‌کند. */
document.addEventListener("DOMContentLoaded", () => {
    const api = window.PortalApi, ui = window.PortalUI;
    const modal = document.querySelector("[data-drop-modal]");
    const confirmButton = modal?.querySelector("[data-confirm-drop]");
    const status = modal?.querySelector("[data-drop-api-status]");
    let activeButton = null;

    const closeModal = () => {
        if (!modal) return;
        modal.hidden = true;
        activeButton?.focus();
        activeButton = null;
    };

    document.querySelectorAll('[data-enrollment-action="drop"]').forEach(button => {
        button.addEventListener("click", () => {
            if (!modal) return;
            activeButton = button;
            modal.querySelector("[data-drop-course-name]").textContent = button.dataset.courseName || "";
            modal.querySelector("[data-drop-course-code]").textContent = button.dataset.courseCode || "";
            modal.querySelector("[data-drop-course-units]").textContent = button.dataset.courseUnits || "";
            if (status) { status.hidden = true; status.textContent = ""; }
            modal.hidden = false;
            confirmButton?.focus();
        });
    });

    modal?.querySelector("[data-close-drop]")?.addEventListener("click", closeModal);
    modal?.addEventListener("click", event => { if (event.target === modal) closeModal(); });
    document.addEventListener("keydown", event => {
        if (event.key === "Escape" && modal && !modal.hidden) closeModal();
    });

    confirmButton?.addEventListener("click", async () => {
        if (!activeButton) return;
        confirmButton.disabled = true;
        try {
            await api.drop(Number(activeButton.dataset.recordId), ui.profile());
            window.location.reload();
        } catch (error) {
            ui.showStatus(ui.errorMessage(error), "[data-drop-api-status]");
            confirmButton.disabled = false;
        }
    });

});
