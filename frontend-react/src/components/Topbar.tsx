import { useState } from "react";
import type { PortalShellData } from "../api/types";
import { TermPicker } from "./TermPicker";

interface TopbarProps {
  shell: PortalShellData;
  onMenuToggle: () => void;
}

export function Topbar({ shell, onMenuToggle }: TopbarProps) {
  const [profile, setProfile] = useState(shell.current_profile?.student_code || "");
  const reactPreview = new URLSearchParams(window.location.search).get("react") === "1";
  const legacyPreview = new URLSearchParams(window.location.search).get("legacy") === "1";
  const term = new URLSearchParams(window.location.search).get("term");

  function submitProfile() {
    const url = new URL(window.location.href);
    if (profile) url.searchParams.set("student_code", profile);
    else url.searchParams.delete("student_code");
    if (term) url.searchParams.set("term", term);
    if (reactPreview) url.searchParams.set("react", "1");
    if (legacyPreview) url.searchParams.set("legacy", "1");
    window.location.assign(`${url.pathname}${url.search}`);
  }

  return (
    <header className="topbar">
      <div className="topbar-profile">
        <span className="avatar" aria-hidden="true">{shell.student.avatar_initials || "د"}</span>
        <div className="topbar-title">
          <strong>دانشجوی گرامی، خوش آمدید</strong>
          <small>{shell.student.name || "پنل کاربری دانشجو"}</small>
        </div>
        <button className="icon-button menu-toggle" type="button" onClick={onMenuToggle} aria-label="باز کردن منو">☰</button>
      </div>
      <label className="global-search">
        <span aria-hidden="true">⌕</span>
        <input type="search" placeholder="جستجو در منو..." aria-label="جستجو در منو" data-global-search />
      </label>
      {shell.profiles.length > 1 && (
        <form className="profile-picker" onSubmit={(event) => { event.preventDefault(); submitProfile(); }} aria-label="انتخاب پرونده دانشجویی">
          <label htmlFor="student-profile-select">پرونده دانشجویی</label>
          <select id="student-profile-select" value={profile} onChange={(event) => setProfile(event.target.value)} required>
            <option value="" disabled>انتخاب پرونده</option>
            {shell.profiles.map((item) => <option value={item.student_code} key={item.student_code}>{item.student_code} · {item.educational_level}</option>)}
          </select>
          <button type="submit">نمایش</button>
        </form>
      )}
      <TermPicker shell={shell} termLabel={shell.student.term || ""} />
    </header>
  );
}
