type StatusCount = { status: string; count: number; color: string };

type JobStatusDonutProps = {
  data: StatusCount[];
};

const STATUS_COLORS: Record<string, string> = {
  open: "#22c55e",
  draft: "#eab308",
  closed: "#ef4444",
};

export function JobStatusDonut({ data }: JobStatusDonutProps) {
  const total = data.reduce((s, d) => s + d.count, 0);

  if (total === 0) {
    return (
      <div className="flex h-48 items-center justify-center">
        <p className="text-white/70">No jobs yet</p>
      </div>
    );
  }

  let acc = 0;
  const conicParts = data
    .map((d) => {
      const pct = (d.count / total) * 100;
      const part = `${d.color} ${acc}% ${acc + pct}%`;
      acc += pct;
      return part;
    })
    .join(", ");

  return (
    <div className="flex flex-col items-center gap-4">
      <div
        className="h-40 w-40 rounded-full border-4 border-white/10"
        style={{
          background: `conic-gradient(from 0deg, ${conicParts})`,
        }}
      />
      <div className="flex flex-wrap justify-center gap-4">
        {data.map((d) => (
          <div key={d.status} className="flex items-center gap-2">
            <div
              className="h-3 w-3 rounded-full"
              style={{ backgroundColor: d.color }}
            />
            <span className="text-sm text-white/90">
              {d.status}: {d.count}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

export function jobsToStatusData(
  jobs: { status: string }[]
): StatusCount[] {
  const counts: Record<string, number> = { draft: 0, open: 0, closed: 0 };
  jobs.forEach((j) => {
    counts[j.status] = (counts[j.status] ?? 0) + 1;
  });
  return Object.entries(counts).map(([status, count]) => ({
    status: status.charAt(0).toUpperCase() + status.slice(1),
    count,
    color: STATUS_COLORS[status] ?? "#64748b",
  }));
}
