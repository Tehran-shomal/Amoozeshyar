const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const root = path.join(__dirname, "../../../apps/core/frontend");

test("every team declares real page ownership without placeholder assets", () => {
    for (const owner of ["mobina", "shaghayegh", "academic_services", "parsa", "neyousha_pouya"]) {
        assert.ok(fs.existsSync(path.join(root, owner, "pages.py")), `${owner} page manifest`);
        assert.ok(fs.existsSync(path.join(root, owner, "selectors.py")), `${owner} selectors`);
        assert.ok(fs.existsSync(path.join(root, owner, "README.md")), `${owner} ownership`);
        assert.ok(!fs.existsSync(path.join(root, owner, "templates", owner, "content.html")), `${owner} shared wrapper`);
        assert.ok(!fs.existsSync(path.join(root, owner, "static", owner, "section.css")), `${owner} placeholder CSS`);
    }
    assert.ok(!fs.existsSync(path.join(root, "omid")), "Omid's page ownership is represented inside the academic services group");
    assert.ok(!fs.existsSync(path.join(root, "shahsavand")), "Shahsavand's page ownership is represented inside the academic services group");
});

test("registration and drop flows call the APIs with database record IDs", () => {
    const registration = fs.readFileSync(path.join(root, "mobina/static/mobina/section.js"), "utf8");
    const drop = fs.readFileSync(path.join(root, "shaghayegh/static/shaghayegh/section.js"), "utf8");
    assert.match(registration, /PortalApi\.register\(Number\(button\.dataset\.recordId\)/);
    assert.match(drop, /PortalApi\.drop\(\s*Number\(activeDropButton\.dataset\.recordId\)/);
    assert.match(drop, /data-confirm-drop/);
    assert.doesNotMatch(drop, /window\.confirm/);
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
