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
    document.querySelectorAll('[data-enrollment-action="register"]').forEach(button => {
        button.addEventListener("click", async () => {
            button.disabled = true;
            try { await api.register(Number(button.dataset.recordId), ui.profile()); window.location.reload(); }
            catch (error) { ui.showStatus(ui.errorMessage(error)); button.disabled = false; }
        });
    });
});
