interface Fact {
  label: string;
  value: unknown;
  note?: string;
}

function asFacts(value: unknown): Fact[] {
  if (!Array.isArray(value)) return [];
  return value.flatMap((item): Fact[] => {
    if (Array.isArray(item) && item.length >= 2) {
      return [{ label: String(item[0] ?? ""), value: item[1] }];
    }
    if (typeof item === "object" && item !== null && "label" in item && "value" in item) {
      const fact = item as Record<string, unknown>;
      return [{
        label: String(fact.label ?? ""),
        value: fact.value,
        note: typeof fact.note === "string" ? fact.note : undefined,
      }];
    }
    return [];
  });
}

export function isFactList(value: unknown): boolean {
  return asFacts(value).length > 0;
}

export function FactList({ title, facts }: { title: string; facts: unknown }) {
  const items = asFacts(facts);
  if (!items.length) return null;
  return (
    <section className="panel side-info-panel" aria-label={title || undefined}>
      {title && <div className="panel-heading"><h2>{title}</h2></div>}
      <dl className="key-value-list">
        {items.map((fact, index) => (
          <div key={`${fact.label}-${index}`}>
            <dt>{fact.label}</dt>
            <dd>{typeof fact.value === "string" || typeof fact.value === "number" ? fact.value : JSON.stringify(fact.value)}</dd>
            {fact.note && <small>{fact.note}</small>}
          </div>
        ))}
      </dl>
    </section>
  );
}
