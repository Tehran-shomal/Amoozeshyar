/* Same-origin Django API helpers shared by the portal and Node tests. */
(function exposePortalApi(root, factory) {
    const api = factory(root);
    if (typeof module === "object" && module.exports) {
        module.exports = api;
    } else {
        root.PortalApi = Object.assign(api.createPortalApi(), api);
    }
})(typeof globalThis === "undefined" ? this : globalThis, function createApiModule(root) {
    const DAY_CODES = {
        شنبه: "saturday",
        یکشنبه: "sunday",
        دوشنبه: "monday",
        سهشنبه: "tuesday",
        چهارشنبه: "wednesday",
        پنجشنبه: "thursday",
        جمعه: "friday",
    };

    // Convert localized numerals only for comparisons and request IDs.
    function normalizeDigits(value) {
        return String(value ?? "").replace(/[۰-۹٠-٩]/g, (digit) => {
            const code = digit.charCodeAt(0);
            const zero = code >= 0x06f0 ? 0x06f0 : 0x0660;
            return String(code - zero);
        });
    }

    function normalizePersianText(value) {
        return normalizeDigits(value)
            .normalize("NFKC")
            .replace(/[يى]/g, "ی")
            .replace(/ك/g, "ک")
            .replace(/[\u200c\u200f\u200e]/g, "")
            .trim()
            .toLocaleLowerCase("fa-IR");
    }

    function teacherTokens(value) {
        const personName = normalizePersianText(value)
            .split(/[•·]/)
            .pop()
            .trim()
            .replace(/^(?:دکتر|استاد)\s*/u, "")
            .replace(/^(?:گروه)\s*\d*\s*/u, "")
            .replace(/[^\p{L}\p{N}\s]/gu, " ");
        return personName.split(/\s+/u).filter(Boolean);
    }

    function parseSchedule(value) {
        const normalized = normalizePersianText(value).replace(/[–—]/g, "-");
        const match = normalized.match(/^([^\s]+)\s+(\d{1,2}:\d{2})\s*-\s*(\d{1,2}:\d{2})$/u);
        if (!match) return null;

        const day = DAY_CODES[match[1]];
        if (!day) return null;
        return {
            day,
            start: normalizeTime(match[2]),
            end: normalizeTime(match[3]),
        };
    }

    function normalizeTime(value) {
        const match = normalizeDigits(value).match(/^(\d{1,2}):(\d{2})/);
        if (!match) return "";
        return `${match[1].padStart(2, "0")}:${match[2]}`;
    }

    // Return an offering only when code, group teacher, day, and time identify it uniquely.
    function matchOffering(selection, offerings) {
        if (!selection || !Array.isArray(offerings)) return null;
        const lessonCode = normalizeDigits(selection.lessonCode).replace(/\s+/g, "");
        const selectedTeacher = teacherTokens(selection.groupTitle);
        const selectedSchedule = parseSchedule(selection.schedule);
        if (!lessonCode || !selectedTeacher.length || !selectedSchedule) return null;

        const matches = offerings.filter((offering) => {
            if (normalizeDigits(offering.lesson_code).replace(/\s+/g, "") !== lessonCode) return false;

            const offeredTeacher = new Set(teacherTokens(offering.teacher));
            if (!selectedTeacher.every((token) => offeredTeacher.has(token))) return false;

            const offeredDay = normalizePersianText(offering.day_of_week)
                .replace(/[\s_-]/g, "");
            if (offeredDay !== selectedSchedule.day) return false;
            return normalizeTime(offering.start_time) === selectedSchedule.start
                && normalizeTime(offering.end_time) === selectedSchedule.end;
        });

        return matches.length === 1 ? matches[0] : null;
    }

    async function registerMatchedOffering(api, selection, offerings, payload) {
        const offering = matchOffering(selection, offerings);
        if (!offering || !Number.isInteger(Number(offering.id)) || Number(offering.id) <= 0) {
            return null;
        }
        return api.register(Number(offering.id), payload);
    }

    function parseCookie(cookieString, cookieName) {
        const prefix = `${cookieName}=`;
        const item = String(cookieString || "")
            .split(";")
            .map((cookie) => cookie.trim())
            .find((cookie) => cookie.startsWith(prefix));
        return item ? decodeURIComponent(item.slice(prefix.length)) : "";
    }

    async function responseJson(response) {
        try {
            return await response.json();
        } catch (_error) {
            return {};
        }
    }

    function apiError(payload, status) {
        const detail = payload?.error || {};
        const error = new Error(detail.message || `API request failed (${status})`);
        error.code = detail.code || "api_error";
        error.status = status;
        error.payload = payload;
        return error;
    }

    function createPortalApi({ fetchImpl, cookieReader } = {}) {
        const fetchRequest = fetchImpl || root.fetch.bind(root);
        const readCookie = cookieReader || (() => root.document?.cookie || "");
        let csrfRequest = null;

        function clearCsrf() {
            csrfRequest = null;
        }

        async function csrfToken() {
            if (!csrfRequest) {
                csrfRequest = (async () => {
                    const response = await fetchRequest("/api/accounts/csrf/", {
                        method: "GET",
                        credentials: "same-origin",
                        headers: { Accept: "application/json" },
                    });
                    const payload = await responseJson(response);
                    if (!response.ok) throw apiError(payload, response.status);

                    const token = payload.csrf_token || parseCookie(readCookie(), "csrftoken");
                    if (!token) {
                        const error = new Error("CSRF token was not returned by the server.");
                        error.code = "csrf_token_missing";
                        error.status = response.status;
                        throw error;
                    }
                    return token;
                })().catch((error) => {
                    clearCsrf();
                    throw error;
                });
            }
            return csrfRequest;
        }

        async function request(path, { method = "GET", payload } = {}) {
            const verb = method.toUpperCase();
            const headers = { Accept: "application/json" };
            const options = {
                method: verb,
                credentials: "same-origin",
                headers,
            };
            if (payload !== undefined) {
                headers["Content-Type"] = "application/json";
                options.body = JSON.stringify(payload);
            }
            if (!["GET", "HEAD", "OPTIONS"].includes(verb)) {
                headers["X-CSRFToken"] = await csrfToken();
            }

            const response = await fetchRequest(path, options);
            const data = await responseJson(response);
            if (!response.ok) throw apiError(data, response.status);
            return data;
        }

        return {
            csrfToken,
            login: async (credentials) => {
                const result = await request("/api/accounts/login/", {
                    method: "POST",
                    payload: credentials,
                });
                // Django rotates CSRF on login, so the next write bootstraps the new token.
                clearCsrf();
                return result;
            },
            me: () => request("/api/accounts/me/"),
            logout: async () => {
                const result = await request("/api/accounts/logout/", { method: "POST" });
                clearCsrf();
                return result;
            },
            activeTerm: () => request("/api/scheduling/active-term/"),
            offerings: (termCode) => {
                const query = termCode
                    ? `?term=${encodeURIComponent(String(termCode))}`
                    : "";
                return request(`/api/scheduling/offerings/${query}`);
            },
            portalPage: (url) => request(url),
            submitPage: (url, payload) => request(url, { method: "POST", payload }),
            register: (offeringId, payload = {}) => {
                const id = Number(offeringId);
                if (!Number.isInteger(id) || id <= 0) {
                    const error = new Error("A valid offering ID is required.");
                    error.code = "invalid_offering_id";
                    error.status = 400;
                    throw error;
                }
                return request(`/api/enrollment/register/${id}/`, {
                    method: "POST",
                    payload,
                });
            },
            drop: (enrollmentId, payload = {}) => {
                const id = Number(enrollmentId);
                if (!Number.isInteger(id) || id <= 0) {
                    const error = new Error("A valid enrollment ID is required.");
                    error.code = "invalid_enrollment_id";
                    error.status = 400;
                    return Promise.reject(error);
                }
                return request(`/api/enrollment/drop/${id}/`, {
                    method: "POST",
                    payload,
                });
            },
            emergencyDrop: (enrollmentId, payload = {}) => {
                const id = Number(enrollmentId);
                if (!Number.isInteger(id) || id <= 0) {
                    const error = new Error("A valid enrollment ID is required.");
                    error.code = "invalid_enrollment_id";
                    error.status = 400;
                    return Promise.reject(error);
                }
                return request(`/api/enrollment/emergency-drop/${id}/`, {
                    method: "POST",
                    payload,
                });
            },
        };
    }

    return {
        createPortalApi,
        normalizeDigits,
        matchOffering,
        registerMatchedOffering,
    };
});
