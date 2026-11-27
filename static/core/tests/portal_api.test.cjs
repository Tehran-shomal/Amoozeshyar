const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

// Allow the first red run to report missing behavior as a normal assertion
// failure instead of a top-level MODULE_NOT_FOUND error.
let portalApi = null;
try {
    portalApi = require("../portal_api.js");
} catch (error) {
    if (error.code !== "MODULE_NOT_FOUND") throw error;
}

function apiModule() {
    assert.ok(portalApi, "static/core/portal_api.js has not been implemented");
    return portalApi;
}

function jsonResponse(value, status = 200) {
    return new Response(JSON.stringify(value), {
        status,
        headers: { "Content-Type": "application/json" },
    });
}

const sampleSelection = {
    lessonCode: "۱۱۲۰۸۴",
    groupTitle: "گروه ۰۱ • دکتر صادقی",
    schedule: "شنبه ۱۰:۰۰–۱۲:۰۰",
};

const matchingOffering = {
    id: 27,
    lesson_code: "112084",
    teacher: "علی صادقی",
    day_of_week: "saturday",
    start_time: "10:00:00",
    end_time: "12:00:00",
};

test("testUnsafeRequestsBootstrapCsrfAndSurfaceApiErrors", async () => {
    const calls = [];
    const fetchImpl = async (url, options = {}) => {
        calls.push({ url, options });
        if (url === "/api/accounts/csrf/") {
            return jsonResponse({ csrf_token: "csrf-token-1" });
        }
        if (url === "/api/accounts/login/" && options.body.includes('"blocked"')) {
            return jsonResponse(
                { error: { code: "invalid_credentials", message: "Invalid login" } },
                401,
            );
        }
        if (url === "/api/accounts/login/") {
            return jsonResponse({ user: { username: "sample" } });
        }
        throw new Error(`Unexpected request: ${url}`);
    };
    const client = apiModule().createPortalApi({
        fetchImpl,
        cookieReader: () => "csrftoken=csrf-token-1; sessionid=session-1",
    });

    await client.login({ username: "sample", password: "ok" });
    await assert.rejects(
        client.login({ username: "blocked", password: "bad" }),
        (error) => error.code === "invalid_credentials" && error.status === 401,
    );

    assert.equal(calls[0].url, "/api/accounts/csrf/");
    assert.equal(calls[0].options.credentials, "same-origin");
    const loginCalls = calls.filter((call) => call.url === "/api/accounts/login/");
    assert.equal(loginCalls.length, 2);
    for (const { options } of loginCalls) {
        assert.equal(options.method, "POST");
        assert.equal(options.credentials, "same-origin");
        assert.equal(options.headers["X-CSRFToken"], "csrf-token-1");
        assert.match(options.headers["Content-Type"], /application\/json/i);
    }
});

test("testExistingEndpointsUseTheirDocumentedPaths", async () => {
    const calls = [];
    const fetchImpl = async (url, options = {}) => {
        calls.push({ url, options });
        if (url === "/api/accounts/csrf/") {
            return jsonResponse({ csrf_token: "csrf-token-2" });
        }
        if (url === "/api/accounts/me/") return jsonResponse({ user: {} });
        if (url === "/api/accounts/logout/") return jsonResponse({ success: true });
        if (url === "/api/scheduling/active-term/") return jsonResponse({ term: null });
        if (url === "/api/scheduling/offerings/") return jsonResponse({ offerings: [] });
        if (url === "/api/enrollment/register/27/") {
            return jsonResponse({ enrollment: { id: 31 } }, 201);
        }
        if (url === "/api/enrollment/drop/31/") {
            return jsonResponse({ enrollment: { id: 31 } });
        }
        if (url === "/api/enrollment/emergency-drop/32/") {
            return jsonResponse({ enrollment: { id: 32 } });
        }
        throw new Error(`Unexpected request: ${url}`);
    };
    const client = apiModule().createPortalApi({ fetchImpl, cookieReader: () => "" });

    await client.me();
    await client.activeTerm();
    await client.offerings();
    await client.register(27, { student_code: "S-1" });
    await client.drop(31);
    await client.emergencyDrop(32);
    await client.logout();

    const byUrl = new Map(calls.map((call) => [call.url, call.options]));
    assert.equal(byUrl.get("/api/accounts/me/").method, "GET");
    assert.equal(byUrl.get("/api/scheduling/active-term/").method, "GET");
    assert.equal(byUrl.get("/api/scheduling/offerings/").method, "GET");
    for (const path of [
        "/api/enrollment/register/27/",
        "/api/enrollment/drop/31/",
        "/api/enrollment/emergency-drop/32/",
        "/api/accounts/logout/",
    ]) {
        assert.equal(byUrl.get(path).method, "POST");
        assert.equal(byUrl.get(path).credentials, "same-origin");
        assert.equal(byUrl.get(path).headers["X-CSRFToken"], "csrf-token-2");
    }
});

test("testPortalPagesUseJsonAndTermFilteredOfferingsUseSchedulingApi", async () => {
    const calls = [];
    const fetchImpl = async (url, options = {}) => {
        calls.push({ url, options });
        if (url === "/api/accounts/csrf/") return jsonResponse({ csrf_token: "csrf-page" });
        if (url === "/api/portal/pages/transcript/?student_code=S1") {
            return jsonResponse({ page: "transcript", html: "<main>page</main>" });
        }
        if (url === "/api/portal/pages/financial-aid/?student_code=S1") {
            return jsonResponse(
                { error: { code: "validation_error" }, html: "<main>bound form</main>" },
                400,
            );
        }
        if (url === "/api/scheduling/offerings/?term=T-1") {
            return jsonResponse({ offerings: [{ id: 27 }] });
        }
        throw new Error(`Unexpected request: ${url}`);
    };
    const client = apiModule().createPortalApi({ fetchImpl, cookieReader: () => "" });

    const page = await client.portalPage("/api/portal/pages/transcript/?student_code=S1");
    assert.equal(page.page, "transcript");
    await assert.rejects(
        client.submitPage("/api/portal/pages/financial-aid/?student_code=S1", { scholarship_type: "" }),
        (error) => error.payload.error.code === "validation_error"
            && error.payload.html.includes("bound form"),
    );
    const offerings = await client.offerings("T-1");
    assert.equal(offerings.offerings[0].id, 27);
    assert.equal(calls[1].options.method, "GET");
    assert.equal(calls[2].options.method, "POST");
    assert.equal(calls[2].options.headers["X-CSRFToken"], "csrf-page");
    assert.deepEqual(JSON.parse(calls[2].options.body), { scholarship_type: "" });
});

test("testNormalizeDigitsAndMatchCode", () => {
    const api = apiModule();
    assert.equal(api.normalizeDigits("۱۱۲٠۸۴"), "112084");
    assert.equal(api.matchOffering(sampleSelection, [matchingOffering])?.id, 27);
});

test("testMatchRequiresUniqueGroupOffering", () => {
    const { matchOffering } = apiModule();
    assert.equal(
        matchOffering(sampleSelection, [
            matchingOffering,
            { ...matchingOffering, id: 28 },
        ]),
        null,
    );
    assert.equal(
        matchOffering(sampleSelection, [
            { ...matchingOffering, teacher: "شخص دیگری", id: 29 },
        ]),
        null,
    );
});

test("testNoOfferingDoesNotRegister", async () => {
    const { matchOffering, registerMatchedOffering } = apiModule();
    const calls = [];
    const client = {
        register: async (offeringId) => calls.push(offeringId),
    };

    const result = await registerMatchedOffering(
        client,
        sampleSelection,
        [],
    );

    assert.equal(result, null);
    assert.deepEqual(calls, []);
    assert.equal(matchOffering(sampleSelection, []), null);
});

test("testAmbiguousOfferingDoesNotRegister", async () => {
    const { registerMatchedOffering } = apiModule();
    const calls = [];
    const client = {
        register: async (offeringId) => calls.push(offeringId),
    };

    const result = await registerMatchedOffering(
        client,
        sampleSelection,
        [matchingOffering, { ...matchingOffering, id: 28 }],
    );

    assert.equal(result, null);
    assert.deepEqual(calls, []);
});

test("testDropRejectsMissingEnrollmentIdWithoutFetching", async () => {
    let requestCount = 0;
    const client = apiModule().createPortalApi({
        fetchImpl: async () => {
            requestCount += 1;
            return jsonResponse({ success: true });
        },
        cookieReader: () => "",
    });

    await assert.rejects(client.drop(null), (error) => error.code === "invalid_enrollment_id");
    await assert.rejects(client.drop(0), (error) => error.code === "invalid_enrollment_id");
    assert.equal(requestCount, 0);
});

test("testBaseLoadsApiClientBeforePortalHandlers", () => {
    const basePath = path.join(__dirname, "../../../templates/base.html");
    const baseTemplate = fs.readFileSync(basePath, "utf8");
    const apiScript = baseTemplate.indexOf("core/portal_api.js");
    const portalScript = baseTemplate.indexOf("core/live_portal.js");

    assert.notEqual(apiScript, -1, "base template should load the API client");
    assert.notEqual(portalScript, -1, "base template should load the portal handlers");
    assert.ok(apiScript < portalScript, "API client must execute before portal handlers");
});

test("testRenderedPortalShellLoadsItsPageDataThroughThePageApi", async () => {
    const source = fs.readFileSync(path.join(__dirname, "../live_portal.js"), "utf8");
    const calls = [];
    let onReady;
    const shell = {
        dataset: { pageApiUrl: "/api/portal/pages/transcript/", portalLoading: "true" },
        setAttribute() {},
        querySelector() { return null; },
    };
    const document = {
        addEventListener(type, callback) {
            if (type === "DOMContentLoaded") onReady = callback;
        },
        querySelector(selector) {
            return selector === ".portal-shell[data-page-api-url]" ? shell : null;
        },
        body: { classList: { remove() {} } },
    };
    const window = {
        location: { search: "?student_code=S1", assign() {} },
        PortalApi: {
            async portalPage(url) {
                calls.push(url);
                throw new Error("Stop after observing the page API request.");
            },
        },
        PortalUI: {
            errorMessage: () => "Request observed",
            showStatus() {},
        },
    };

    vm.runInNewContext(source, { document, window, URLSearchParams });
    assert.equal(typeof onReady, "function");
    await onReady();

    assert.deepEqual(calls, ["/api/portal/pages/transcript/?student_code=S1"]);
});

test("testBrowserGlobalIsAReadyToUseApiClient", () => {
    const source = fs.readFileSync(path.join(__dirname, "../portal_api.js"), "utf8");
    const browserGlobal = {
        document: { cookie: "" },
        fetch: async () => jsonResponse({}),
    };

    vm.runInNewContext(source, browserGlobal);

    assert.equal(typeof browserGlobal.PortalApi.login, "function");
    assert.equal(typeof browserGlobal.PortalApi.me, "function");
    assert.equal(typeof browserGlobal.PortalApi.createPortalApi, "function");
});
