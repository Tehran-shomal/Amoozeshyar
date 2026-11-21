/* مبینا: ورود واقعی و انتخاب درس با شناسهٔ قطعی ارائه. */
document.addEventListener("DOMContentLoaded", () => {
    const api = window.PortalApi, ui = window.PortalUI;
    const form = document.querySelector("[data-login-form]");
    form?.addEventListener("submit", async event => {
        event.preventDefault();
        const button = form.querySelector('[type="submit"]');
        button.disabled = true;
        const values = new FormData(form);
        try {
            await api.login({
                username: values.get("username"),
                password: values.get("password"),
                remember_me: values.get("remember_me") === "on",
            });
            const session = await api.me();
            if (!session.user) throw new Error("نشست تأیید نشد.");
            window.location.assign(form.dataset.loginRedirect);
        } catch (error) { ui.showStatus(ui.errorMessage(error), "[data-login-status]"); }
        finally { button.disabled = false; }
    });
});

// Course rows arrive from the scheduling API after this script has loaded.
document.addEventListener("click", async event => {
    const button = event.target.closest('[data-enrollment-action="register"]');
    if (!button || button.disabled) return;
    button.disabled = true;
    try {
        await window.PortalApi.register(Number(button.dataset.recordId), window.PortalUI.profile());
        window.location.reload();
    } catch (error) {
        window.PortalUI.showStatus(window.PortalUI.errorMessage(error));
        button.disabled = false;
    }
});
