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
    assert.match(registration, /api\.register\(Number\(button\.dataset\.recordId\)/);
    assert.match(drop, /api\.drop\(Number\(activeButton\.dataset\.recordId\)/);
    assert.match(drop, /data-confirm-drop/);
    assert.doesNotMatch(drop, /window\.confirm/);
});
