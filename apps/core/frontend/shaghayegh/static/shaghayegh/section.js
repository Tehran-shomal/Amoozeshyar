/* شقایق: جزئیات حذف در مودال PDF نشان داده می‌شود؛ API مالکیت و بازه را کنترل می‌کند. */
let activeDropButton = null;

function closeDropModal(modal) {
    if (!modal) return;
    modal.hidden = true;
    activeDropButton?.focus();
    activeDropButton = null;
}

document.addEventListener("click", async event => {
    const dropButton = event.target.closest('[data-enrollment-action="drop"]');
    if (dropButton) {
        const modal = document.querySelector("[data-drop-modal]");
        if (!modal) return;
        activeDropButton = dropButton;
        modal.querySelector("[data-drop-course-name]").textContent = dropButton.dataset.courseName || "";
        modal.querySelector("[data-drop-course-code]").textContent = dropButton.dataset.courseCode || "";
        modal.querySelector("[data-drop-course-units]").textContent = dropButton.dataset.courseUnits || "";
        const status = modal.querySelector("[data-drop-api-status]");
        if (status) { status.hidden = true; status.textContent = ""; }
        modal.hidden = false;
        modal.querySelector("[data-confirm-drop]")?.focus();
        return;
    }

    const closeButton = event.target.closest("[data-close-drop]");
    const backdrop = event.target.matches("[data-drop-modal]") ? event.target : null;
    if (closeButton || backdrop) {
        closeDropModal(closeButton?.closest("[data-drop-modal]") || backdrop);
        return;
    }

    const confirmButton = event.target.closest("[data-confirm-drop]");
    if (!confirmButton || !activeDropButton) return;
    confirmButton.disabled = true;
    try {
        await window.PortalApi.drop(
            Number(activeDropButton.dataset.recordId),
            window.PortalUI.profile(),
        );
        window.location.reload();
    } catch (error) {
        window.PortalUI.showStatus(
            window.PortalUI.errorMessage(error),
            "[data-drop-api-status]",
        );
        confirmButton.disabled = false;
    }
});

document.addEventListener("keydown", event => {
    if (event.key === "Escape") {
        const modal = document.querySelector("[data-drop-modal]:not([hidden])");
        if (modal) closeDropModal(modal);
    }
});
