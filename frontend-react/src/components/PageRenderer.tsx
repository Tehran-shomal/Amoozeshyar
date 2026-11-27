import type { ReactNode } from "react";
import type { PagePayload } from "../api/types";
import type { PortalBootstrap } from "../types";
import { portalPageHref } from "../app/navigation";
import { DataTable, isTableData } from "./DataTable";
import { DynamicForm } from "./DynamicForm";
import { EmptyState } from "./EmptyState";
import { FactList, isFactList } from "./FactList";
import { OperationResult } from "./OperationResult";
import { PageHeading } from "./PageHeading";
import { AnnouncementsPage } from "../pages/miri/AnnouncementsPage";
import { NotificationsPage } from "../pages/miri/NotificationsPage";
import { DashboardPage } from "../pages/mobina/DashboardPage";
import { StudentCardPage } from "../pages/mobina/StudentCardPage";
import { SettingsPage } from "../pages/mobina/SettingsPage";
import { FinancePage } from "../pages/parsa/FinancePage";
import { GuidePage } from "../pages/miri/GuidePage";
import { MessagesPage } from "../pages/miri/MessagesPage";
import { SupportPage } from "../pages/miri/SupportPage";
import { AcademicPage } from "../pages/omid/AcademicPage";
import { AttendancePage } from "../pages/niousha/AttendancePage";
import { CalendarPage } from "../pages/niousha/CalendarPage";
import { ExamCardPage } from "../pages/niousha/ExamCardPage";
import { SchedulePage } from "../pages/niousha/SchedulePage";
import { EvaluationPage } from "../pages/miri/EvaluationPage";
import { EvaluationFormPage } from "../pages/miri/EvaluationFormPage";
import { GradeAppealPage } from "../pages/omid/GradeAppealPage";
import { EnrollmentPage } from "../pages/shaghayegh/EnrollmentPage";
import { SelectedCoursesPage } from "../pages/shaghayegh/SelectedCoursesPage";
import { CourseChangesPage } from "../pages/shaghayegh/CourseChangesPage";
import { RegistrationStatusPage } from "../pages/shaghayegh/RegistrationStatusPage";
import { StudentServicePage } from "../pages/shahsvand/StudentServicePage";

interface PageRendererProps {
  payload: PagePayload;
  bootstrap: PortalBootstrap;
}

export function PageRenderer({ payload, bootstrap }: PageRendererProps) {
  const specialPages = new Set([
    "home", "student-card", "announcements", "notifications", "payments", "secure-payment", "tuition",
    "settings", "guide", "messages", "support", "academic-activities", "transcript", "curriculum",
    "attendance", "calendar", "exam-card", "schedule",
    "evaluation", "evaluation-form", "grade-appeal",
    "enrollment", "selected-courses", "add-drop", "emergency-drop", "registration-status",
    "financial-aid", "internship", "guest-request", "graduation", "graduation-certificate", "requests", "education-certificate",
  ]);
  if (specialPages.has(payload.page)) {
    return (
      <>
        {payload.page !== "home" && <PageHeading title={payload.title} subtitle={payload.subtitle} groups={payload.shell.nav_groups} slug={payload.page} homeUrl={bootstrap.homeUrl} />}
        {payload.page === "home" && <DashboardPage payload={payload} bootstrap={bootstrap} />}
        {payload.page === "student-card" && <StudentCardPage payload={payload} bootstrap={bootstrap} />}
        {payload.page === "announcements" && <AnnouncementsPage payload={payload} bootstrap={bootstrap} />}
        {payload.page === "notifications" && <NotificationsPage payload={payload} bootstrap={bootstrap} />}
        {payload.page === "settings" && <SettingsPage payload={payload} bootstrap={bootstrap} />}
        {payload.page === "guide" && <GuidePage payload={payload} bootstrap={bootstrap} />}
        {payload.page === "messages" && <MessagesPage payload={payload} bootstrap={bootstrap} />}
        {payload.page === "support" && <SupportPage payload={payload} bootstrap={bootstrap} />}
        {payload.page === "attendance" && <AttendancePage payload={payload} bootstrap={bootstrap} />}
        {payload.page === "calendar" && <CalendarPage payload={payload} />}
        {payload.page === "exam-card" && <ExamCardPage payload={payload} bootstrap={bootstrap} />}
        {payload.page === "schedule" && <SchedulePage payload={payload} bootstrap={bootstrap} />}
        {payload.page === "evaluation" && <EvaluationPage payload={payload} bootstrap={bootstrap} />}
        {payload.page === "evaluation-form" && <EvaluationFormPage payload={payload} bootstrap={bootstrap} />}
        {payload.page === "grade-appeal" && <GradeAppealPage payload={payload} bootstrap={bootstrap} />}
        {payload.page === "enrollment" && <EnrollmentPage payload={payload} bootstrap={bootstrap} />}
        {payload.page === "selected-courses" && <SelectedCoursesPage payload={payload} bootstrap={bootstrap} />}
        {["add-drop", "emergency-drop"].includes(payload.page) && <CourseChangesPage payload={payload} bootstrap={bootstrap} />}
        {payload.page === "registration-status" && <RegistrationStatusPage payload={payload} bootstrap={bootstrap} />}
        {["financial-aid", "internship", "guest-request", "graduation", "graduation-certificate", "requests", "education-certificate"].includes(payload.page) && <StudentServicePage payload={payload} bootstrap={bootstrap} />}
        {["academic-activities", "transcript", "curriculum"].includes(payload.page) && <AcademicPage payload={payload} bootstrap={bootstrap} />}
        {["payments", "secure-payment", "tuition"].includes(payload.page) && <FinancePage payload={payload} bootstrap={bootstrap} />}
      </>
    );
  }

  // An unknown backend slug must never fall through to a generic renderer:
  // that can make a page appear migrated while silently dropping its workflow.
  if (!specialPages.has(payload.page)) {
    return <main className="portal-page-loading" role="alert">این صفحه هنوز در نسخهٔ React نگاشت نشده است.</main>;
  }

  const data = payload.data;
  const known = new Set(["notice", "facts", "tables", "form_title", "operation_result", "links", "printable"]);
  const extraEntries = Object.entries(data).filter(([key]) => !known.has(key));
  const hasBody = Boolean(
    data.facts || data.tables || payload.form || data.operation_result || data.notice ||
      data.links || data.printable || extraEntries.length,
  );

  return (
    <>
      <PageHeading title={payload.title} subtitle={payload.subtitle} groups={payload.shell.nav_groups} slug={payload.page} homeUrl={bootstrap.homeUrl} />
      {typeof data.notice === "string" && <div className="inline-notice" role="status"><p>{data.notice}</p></div>}
      {isFactList(data.facts) && <FactList title="" facts={data.facts} />}
      {data.operation_result && typeof data.operation_result === "object" && (
        <OperationResult result={data.operation_result as { heading?: string; message?: string; status?: string; created_at?: string; note?: string }} />
      )}
      {Array.isArray(data.tables) && data.tables.filter(isTableData).map((table, index) => <DataTable table={table} key={`${table.title || "table"}-${index}`} />)}
      {payload.form && <DynamicForm schema={payload.form} title={stringValue(data.form_title)} submitUrl={bootstrap.submitUrl} />}
      {Array.isArray(data.links) && <nav className="page-actions" aria-label="پیوندهای مرتبط">{data.links.map((item, index) => {
        const link = Array.isArray(item)
          ? { slug: item[0], label: item[1] }
          : (typeof item === "object" && item !== null ? item as Record<string, unknown> : {});
        if (typeof link.slug !== "string" || typeof link.label !== "string") return null;
        return <a className="button button--soft" href={portalPageHref(link.slug, bootstrap)} key={`${link.slug}-${index}`}>{link.label}</a>;
      })}</nav>}
      {data.printable === true && <div className="page-actions"><button className="button button--soft" type="button" onClick={() => window.print()}>چاپ</button></div>}
      {extraEntries.map(([key, value]) => <StructuredBlock key={key} title={key} value={value} />)}
      {!hasBody && <EmptyState />}
    </>
  );
}

function stringValue(value: unknown): string | undefined {
  return typeof value === "string" && value ? value : undefined;
}

function StructuredBlock({ title, value }: { title: string; value: unknown }) {
  if (value === null || value === undefined || value === false || value === "") return null;
  if (isTableData(value)) return <DataTable table={value} />;
  if (isFactList(value)) return <FactList title={title} facts={value} />;
  if (typeof value === "string" || typeof value === "number") {
    return <section className="panel"><div className="panel-heading"><h2>{title}</h2></div><p>{value}</p></section>;
  }
  if (Array.isArray(value)) {
    if (!value.length) return null;
    return (
      <section className="panel">
        <div className="panel-heading"><h2>{title}</h2></div>
        <div className="portal-card-list">
          {value.map((item, index) => (
            <div className="portal-card-row" key={index}><div className="portal-card-copy"><StructuredValue value={item} /></div></div>
          ))}
        </div>
      </section>
    );
  }
  if (typeof value === "object") {
    const entries = Object.entries(value as Record<string, unknown>);
    if (!entries.length) return null;
    return (
      <section className="panel">
        <div className="panel-heading"><h2>{title}</h2></div>
        <dl className="key-value-list">
          {entries.map(([key, child]) => <div key={key}><dt>{key}</dt><dd><StructuredValue value={child} /></dd></div>)}
        </dl>
      </section>
    );
  }
  return null;
}

function StructuredValue({ value }: { value: unknown }): ReactNode {
  if (value === null || value === undefined || value === "") return "—";
  if (typeof value === "string" || typeof value === "number") return value;
  if (typeof value === "boolean") return value ? "بله" : "خیر";
  if (Array.isArray(value)) return value.map((item, index) => <span key={index}>{index > 0 ? "، " : ""}<StructuredValue value={item} /></span>);
  if (isTableData(value)) return <DataTable table={value} />;
  if (typeof value === "object") {
    return Object.entries(value as Record<string, unknown>).map(([key, child]) => (
      <span key={key}>{key}: <StructuredValue value={child} /> </span>
    ));
  }
  return null;
}
