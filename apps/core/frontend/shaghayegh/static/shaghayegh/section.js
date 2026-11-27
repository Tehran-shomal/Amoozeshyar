/* شقایق: جزئیات حذف در مودال PDF نشان داده می‌شود؛ API مالکیت و بازه را کنترل می‌کند. */
let activeDropButton = null;
let activeRegistrationButton = null;
let courseModalOpener = null;
const dayLabels = {
    saturday: "شنبه", sunday: "یکشنبه", monday: "دوشنبه", tuesday: "سه‌شنبه",
    wednesday: "چهارشنبه", thursday: "پنجشنبه", friday: "جمعه",
};

function offeringUnits(offering) {
    const total = Number(offering?.total_units);
    if (offering?.total_units != null && Number.isFinite(total)) return total;
    return Number(offering?.theory_units || 0) + Number(offering?.practical_units || 0);
}

function lessonKey(offering) {
    return `${offering?.lesson_code || ""}\u0000${offering?.title || ""}`;
}

function courseGroups(offerings) {
    const grouped = new Map();
    for (const offering of offerings) {
        if (!Number.isInteger(Number(offering?.id)) || Number(offering.id) <= 0) continue;
        const key = lessonKey(offering);
        if (!grouped.has(key)) grouped.set(key, []);
        grouped.get(key).push(offering);
    }
    return [...grouped.values()];
}

function renderCourseChoices(offerings) {
    const modal = document.querySelector("[data-course-modal]");
    const container = modal?.querySelector("[data-course-modal-courses]");
    if (!container) return;

    const groups = courseGroups(offerings);
    modal._courseOfferingGroups = groups;
    if (!groups.length) {
        const empty = document.createElement("p");
        empty.className = "empty-state";
        empty.textContent = "برای این نیمسال درسی ارائه نشده است.";
        container.replaceChildren(empty);
        return;
    }

    const fragment = document.createDocumentFragment();
    groups.forEach((offeringsForCourse, index) => {
        const first = offeringsForCourse[0];
        const card = document.createElement("article");
        card.className = "course-choice";
        const details = document.createElement("div");
        const title = document.createElement("h3");
        title.textContent = first.title || "عنوان درس ثبت نشده";
        const metadata = document.createElement("p");
        const units = offeringUnits(first);
        metadata.textContent = `کد ${first.lesson_code || "—"} · ${units} واحد`;
        const count = document.createElement("small");
        count.textContent = `${offeringsForCourse.length} ارائهٔ فعال`;
        details.append(title, metadata, count);

        const button = document.createElement("button");
        button.type = "button";
        button.className = "button button--primary";
        button.dataset.showCourseGroups = String(index);
        button.textContent = "انتخاب گروه";
        card.append(details, button);
        fragment.append(card);
    });
    container.replaceChildren(fragment);
}

function setCourseModalStatus(message = "") {
    const status = document.querySelector("[data-course-modal-status]");
    if (!status) return;
    status.textContent = message;
    status.hidden = !message;
}

function selectCourseOffering(modal, offering) {
    const button = modal?.querySelector('[data-enrollment-action="register"]');
    if (!button || !offering) return;
    modal._courseSelectedOfferings ||= new Map();
    modal._courseSelectedOfferings.set(lessonKey(offering), String(offering.id));
    button.dataset.recordId = String(offering.id);
    const capacity = Number(offering.remaining_capacity);
    button.disabled = Number.isFinite(capacity) && capacity <= 0;
    const exam = modal.querySelector("[data-course-modal-exam]");
    if (exam) {
        const examDate = String(offering.exam_date || "");
        const examTime = String(offering.exam_time || "").slice(0, 5);
        exam.textContent = examDate && examTime
            ? `زمان امتحان: ${examDate} · ${examTime}`
            : "زمان امتحان در داده‌های سامانه ثبت نشده است.";
    }
    setCourseModalStatus(button.disabled ? "ظرفیت این ارائه تکمیل است؛ ارائهٔ دیگری را انتخاب کنید." : "");
}

function showCourseGroups(index) {
    const modal = document.querySelector("[data-course-modal]");
    const offerings = modal?._courseOfferingGroups?.[index];
    if (!modal || !offerings?.length) return;

    const first = offerings[0];
    const selectedId = modal._courseSelectedOfferings?.get(lessonKey(first));
    const selectedOffering = offerings.find(item => String(item.id) === selectedId) || first;
    modal.querySelector("[data-course-modal-list]").hidden = true;
    const detail = modal.querySelector("[data-course-detail]");
    detail.hidden = false;
    modal.querySelector('[role="dialog"]')?.setAttribute("aria-labelledby", "course-detail-title");
    modal.querySelector("[data-course-modal-title]").textContent = first.title || "عنوان درس ثبت نشده";
    modal.querySelector("[data-course-modal-code]").textContent = first.lesson_code || "—";
    modal.querySelector("[data-course-modal-units]").textContent = String(offeringUnits(first));

    const options = modal.querySelector("[data-course-modal-groups]");
    const fragment = document.createDocumentFragment();
    offerings.forEach((offering, optionIndex) => {
        const label = document.createElement("label");
        label.className = "course-group-option";
        const radio = document.createElement("input");
        radio.type = "radio";
        radio.name = "course-offering-choice";
        radio.value = String(offering.id);
        radio.dataset.courseGroupChoice = "";
        radio.checked = String(offering.id) === String(selectedOffering.id);
        const text = document.createElement("span");
        const teacher = document.createElement("strong");
        teacher.textContent = `ارائه با ${offering.teacher || "استاد ثبت‌نشده"}`;
        const schedule = document.createElement("small");
        const dayCode = String(offering.day_of_week || "").toLocaleLowerCase();
        const day = dayLabels[dayCode] || "روز نامشخص";
        const start = String(offering.start_time || "").slice(0, 5);
        const end = String(offering.end_time || "").slice(0, 5);
        const remaining = offering.remaining_capacity == null ? "—" : offering.remaining_capacity;
        schedule.textContent = `${day} ${start}–${end} · ظرفیت باقی‌مانده: ${remaining} نفر`;
        text.append(teacher, schedule);
        label.append(radio, text);
        fragment.append(label);
    });
    options.replaceChildren(fragment);
    selectCourseOffering(modal, selectedOffering);
    modal.querySelector("[data-enrollment-action=\"register\"]")?.focus();
}

function closeCourseModal(modal) {
    if (!modal) return;
    modal.hidden = true;
    modal.querySelector("[data-course-modal-list]").hidden = false;
    modal.querySelector("[data-course-detail]").hidden = true;
    modal.querySelector('[data-enrollment-action="register"]').disabled = true;
    courseModalOpener?.setAttribute("aria-expanded", "false");
    courseModalOpener?.focus();
    courseModalOpener = null;
    document.body.classList.remove("modal-open");
}

document.addEventListener("portal:offerings-loaded", event => {
    renderCourseChoices(event.detail?.offerings || []);
});

document.addEventListener("portal:offerings-error", event => {
    const container = document.querySelector("[data-course-modal-courses]");
    if (!container) return;
    const message = document.createElement("p");
    message.className = "empty-state";
    message.textContent = window.PortalUI.errorMessage(event.detail?.error);
    container.replaceChildren(message);
});

document.addEventListener("change", event => {
    const choice = event.target.closest("[data-course-group-choice]");
    if (!choice) return;
    const modal = choice.closest("[data-course-modal]");
    const offering = modal?._courseOfferingGroups?.flat().find(
        item => String(item.id) === choice.value
    );
    selectCourseOffering(modal, offering);
});

function closeTuitionDebtModal(modal) {
    if (!modal) return;
    modal.hidden = true;
    activeRegistrationButton?.focus();
    activeRegistrationButton = null;
}

function closeDropModal(modal) {
    if (!modal) return;
    modal.hidden = true;
    activeDropButton?.focus();
    activeDropButton = null;
}

document.addEventListener("click", async event => {
    const offeringsButton = event.target.closest("[data-open-course-offerings]");
    if (offeringsButton) {
        const courseModal = document.querySelector("[data-course-modal]");
        if (courseModal && offeringsButton.hasAttribute("data-course-modal-opener")) {
            courseModalOpener = offeringsButton;
            courseModal.hidden = false;
            document.body.classList.add("modal-open");
            offeringsButton.setAttribute("aria-expanded", "true");
            courseModal.querySelector("[data-course-modal-close]")?.focus();
            return;
        }
        const offeringsPanel = document.getElementById("course-offerings-panel");
        if (!offeringsPanel) return;
        const shouldOpen = offeringsPanel.hidden;
        offeringsPanel.hidden = !shouldOpen;
        offeringsButton.setAttribute("aria-expanded", String(shouldOpen));
        offeringsButton.textContent = shouldOpen ? "بستن فهرست درس‌ها" : "انتخاب درس‌ها";
        if (shouldOpen) offeringsPanel.scrollIntoView({ block: "start", behavior: "smooth" });
        return;
    }

    const groupButton = event.target.closest("[data-show-course-groups]");
    if (groupButton) {
        showCourseGroups(Number(groupButton.dataset.showCourseGroups));
        return;
    }

    const backToCourses = event.target.closest("[data-course-modal-back]");
    if (backToCourses) {
        const modal = backToCourses.closest("[data-course-modal]");
        modal.querySelector("[data-course-detail]").hidden = true;
        modal.querySelector("[data-course-modal-list]").hidden = false;
        modal.querySelector('[role="dialog"]')?.setAttribute("aria-labelledby", "course-modal-title");
        setCourseModalStatus("");
        modal.querySelector("[data-show-course-groups]")?.focus();
        return;
    }

    const closeCourseButton = event.target.closest("[data-course-modal-close]");
    const courseBackdrop = event.target.matches("[data-course-modal]") ? event.target : null;
    if (closeCourseButton || courseBackdrop) {
        closeCourseModal(closeCourseButton?.closest("[data-course-modal]") || courseBackdrop);
        return;
    }

    const registerButton = event.target.closest('[data-enrollment-action="register"]');
    if (registerButton && !registerButton.disabled) {
        registerButton.disabled = true;
        try {
            const result = await window.PortalApi.register(
                Number(registerButton.dataset.recordId), window.PortalUI.profile()
            );
            if (result.created) {
                const params = new URLSearchParams(window.location.search);
                const profile = window.PortalUI.profile();
                if (profile.student_code) params.set("student_code", profile.student_code);
                params.delete("dropped_enrollment_id");
                params.set("registration_id", String(result.enrollment.id));
                const query = params.toString();
                window.location.assign(`/portal/add-drop/${query ? `?${query}` : ""}`);
            } else {
                const message = "این درس از قبل در برنامهٔ شما ثبت فعال دارد.";
                if (document.querySelector("[data-course-modal]:not([hidden])")) setCourseModalStatus(message);
                else window.PortalUI.showStatus(message);
                registerButton.disabled = false;
            }
        } catch (error) {
            if (error.code === "tuition_debt") {
                const debtModal = document.querySelector("[data-tuition-debt-modal]");
                if (debtModal) {
                    activeRegistrationButton = registerButton;
                    debtModal.hidden = false;
                    debtModal.querySelector("[data-close-tuition-debt]")?.focus();
                    registerButton.disabled = false;
                    return;
                }
            }
            const message = window.PortalUI.errorMessage(error);
            if (document.querySelector("[data-course-modal]:not([hidden])")) setCourseModalStatus(message);
            else window.PortalUI.showStatus(message);
            registerButton.disabled = false;
        }
        return;
    }

    const closeDebtButton = event.target.closest("[data-close-tuition-debt]");
    const debtBackdrop = event.target.matches("[data-tuition-debt-modal]")
        ? event.target
        : null;
    if (closeDebtButton || debtBackdrop) {
        closeTuitionDebtModal(closeDebtButton?.closest("[data-tuition-debt-modal]") || debtBackdrop);
        return;
    }

    const dropButton = event.target.closest(
        '[data-enrollment-action="drop"], [data-enrollment-action="emergency-drop"]'
    );
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
        const drop = activeDropButton.dataset.enrollmentAction === "emergency-drop"
            ? window.PortalApi.emergencyDrop
            : window.PortalApi.drop;
        const result = await drop(Number(activeDropButton.dataset.recordId), window.PortalUI.profile());
        const droppedEnrollment = result?.enrollment;
        if (!droppedEnrollment?.id) throw new Error("Drop response did not include the saved enrollment.");
        const params = new URLSearchParams(window.location.search);
        const profile = window.PortalUI.profile();
        if (profile.student_code) params.set("student_code", profile.student_code);
        params.delete("registration_id");
        params.set("dropped_enrollment_id", String(droppedEnrollment.id));
        window.location.assign(`${window.location.pathname}?${params.toString()}`);
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
        const debtModal = document.querySelector("[data-tuition-debt-modal]:not([hidden])");
        if (debtModal) {
            closeTuitionDebtModal(debtModal);
            return;
        }
        const courseModal = document.querySelector("[data-course-modal]:not([hidden])");
        if (courseModal) {
            closeCourseModal(courseModal);
            return;
        }
        const modal = document.querySelector("[data-drop-modal]:not([hidden])");
        if (modal) closeDropModal(modal);
    }
});
