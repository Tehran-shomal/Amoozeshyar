import type { PagePayload } from "../../api/types";
import type { PortalBootstrap } from "../../types";
import { portalPageHref } from "../../app/navigation";

type Row = Record<string, unknown>;
function object(value: unknown): Row { return typeof value === "object" && value !== null ? value as Row : {}; }
function list(value: unknown): Row[] { return Array.isArray(value) ? value.map(object) : []; }
function text(value: unknown, fallback = "—"): string { return value === null || value === undefined || value === "" ? fallback : String(value); }

export function GuidePage({ payload, bootstrap }: { payload: PagePayload; bootstrap: PortalBootstrap }) {
  const topics = list(payload.data.guide_topics);
  return topics.length ? (
    <section className="portal-card-list-panel portal-card-list-panel--guide" aria-label="راهنمای خدمات پرتال">
      <div className="portal-card-list">
        {topics.map((topic, index) => (
          <article className="portal-card-row guide-topic" key={`${topic.slug}-${index}`}>
            <div className="portal-card-copy">
              <strong>{text(topic.title)}</strong>
              <p>{text(topic.description, "")}</p>
              {typeof topic.implementation_note === "string" && topic.implementation_note && <small className="guide-topic-note">{topic.implementation_note}</small>}
            </div>
            <a className="button button--soft" href={portalPageHref(text(topic.slug, ""), bootstrap)}>{text(topic.link_label, "ورود به بخش")}</a>
          </article>
        ))}
      </div>
      <div className="portal-card-list-actions">
        <a className="button button--primary" href={portalPageHref(text(payload.data.guide_support_slug, "support"), bootstrap)}>تماس با پشتیبانی</a>
      </div>
    </section>
  ) : <section className="panel"><p className="empty-state">راهنمایی برای نمایش ثبت نشده است.</p></section>;
}
