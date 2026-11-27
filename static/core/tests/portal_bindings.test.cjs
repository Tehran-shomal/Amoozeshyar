const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const root = path.join(__dirname, "../../../apps/core/frontend");

test("every team declares real page ownership without placeholder assets", () => {
    for (const owner of ["mobina", "shaghayegh", "parsa", "omid", "niousha", "shahsvand", "miri"]) {
        assert.ok(fs.existsSync(path.join(root, owner, "pages.py")), `${owner} page manifest`);
        assert.ok(fs.existsSync(path.join(root, owner, "selectors.py")), `${owner} selectors`);
        assert.ok(fs.existsSync(path.join(root, owner, "README.md")), `${owner} ownership`);
        assert.ok(!fs.existsSync(path.join(root, owner, "templates", owner, "content.html")), `${owner} shared wrapper`);
        assert.ok(!fs.existsSync(path.join(root, owner, "static", owner, "section.css")), `${owner} placeholder CSS`);
    }
    assert.ok(fs.existsSync(path.join(root, "niousha", "pages.py")), "Niousha owns schedule pages and the term picker");
});

test("login, registration, and drop flows call the APIs with database record IDs", () => {
    const login = fs.readFileSync(path.join(root, "mobina/static/mobina/login.js"), "utf8");
    const registration = fs.readFileSync(path.join(root, "shaghayegh/static/shaghayegh/section.js"), "utf8");
    const drop = fs.readFileSync(path.join(root, "shaghayegh/static/shaghayegh/section.js"), "utf8");
    assert.match(login, /api\.login\(/);
    assert.match(registration, /PortalApi\.register\(/);
    assert.match(drop, /PortalApi\.drop\(\s*Number\(activeDropButton\.dataset\.recordId\)/);
    assert.match(drop, /data-confirm-drop/);
    assert.match(drop, /dropped_enrollment_id/);
    assert.match(drop, /window\.location\.assign/);
    assert.doesNotMatch(drop, /window\.confirm/);
});

test("tuition debt registration errors open the debt blocker with a real finance route", () => {
    const registration = fs.readFileSync(path.join(root, "shaghayegh/static/shaghayegh/section.js"), "utf8");
    const courses = fs.readFileSync(path.join(root, "shaghayegh/templates/shaghayegh/selected_courses.html"), "utf8");
    assert.match(registration, /error\.code\s*===\s*["']tuition_debt["']/);
    assert.match(registration, /data-tuition-debt-modal/);
    assert.match(registration, /data-close-tuition-debt/);
    assert.match(courses, /data-tuition-debt-modal/);
    assert.match(courses, /core:section' 'secure-payment/);
});

test("selected-course modal renders API offerings and registers the chosen real group", () => {
    const selection = fs.readFileSync(path.join(root, "shaghayegh/static/shaghayegh/section.js"), "utf8");
    const loader = fs.readFileSync(path.join(__dirname, "../live_portal.js"), "utf8");
    const courses = fs.readFileSync(path.join(root, "shaghayegh/templates/shaghayegh/selected_courses.html"), "utf8");
    assert.match(courses, /data-course-modal/);
    assert.match(courses, /data-course-modal-close/);
    assert.match(courses, /data-enrollment-action="register"/);
    assert.match(selection, /portal:offerings-loaded/);
    assert.match(selection, /data-course-modal-groups/);
    assert.match(selection, /data-show-course-groups/);
    assert.match(selection, /PortalApi\.register\(/);
    assert.match(loader, /portal:offerings-loaded/);
});

test("responsive table search keeps a single border around the control", () => {
    const portalCss = fs.readFileSync(path.join(__dirname, "../portal.css"), "utf8");
    const responsiveCss = fs.readFileSync(path.join(__dirname, "../responsive.css"), "utf8");
    const wrapper = portalCss.match(/\.table-search\s*\{([^}]+)\}/);
    const input = responsiveCss.match(/\.table-search\s+input\s*\{([^}]+)\}/);

    assert.ok(wrapper, "table search wrapper must remain visibly framed");
    assert.ok(input, "responsive table search input rule must exist");
    assert.match(wrapper[1], /\bborder\s*:/);
    assert.doesNotMatch(input[1], /\bborder(?:-\w+)?\s*:/);
});

test("selected-course page keeps navigation group headings at full sidebar width", () => {
    const responsiveCss = fs.readFileSync(path.join(__dirname, "../responsive.css"), "utf8");

    assert.match(
        responsiveCss,
        /body\.portal-body--selected-courses\s+\.nav-group\s+summary\s*\{[^}]*\bwidth\s*:\s*100%\s*;/s,
    );
});

test("selected-course desktop controls and cards match the PDF frame", () => {
    const responsiveCss = fs.readFileSync(path.join(__dirname, "../responsive.css"), "utf8");

    assert.match(
        responsiveCss,
        /body\.portal-body--selected-courses\s+\.course-warning-panel\s+\.button\s*\{[^}]*\bwidth\s*:\s*160px\s*;/s,
    );
    assert.match(
        responsiveCss,
        /body\.portal-body--selected-courses\s+\.course-page-actions\s+\.button\s*\{[^}]*\bwidth\s*:\s*180px\s*;/s,
    );
    assert.match(
        responsiveCss,
        /body\.portal-body--selected-courses\s+\.student-course-summary,\s*body\.portal-body--selected-courses\s+\.course-current-panel,\s*body\.portal-body--selected-courses\s+\.course-totals\s*\{[^}]*\bbox-shadow\s*:\s*none\s*;/s,
    );
});
