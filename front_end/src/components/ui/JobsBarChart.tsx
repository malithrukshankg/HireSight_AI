type ChartDataItem = { month: string; count: number };

type JobsBarChartProps = {
  data: ChartDataItem[];
  maxBars?: number;
};

const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

export function JobsBarChart({ data, maxBars = 12 }: JobsBarChartProps) {
  const maxCount = Math.max(1, ...data.map((d) => d.count));
  const bars = data.slice(0, maxBars);

  return (
    <div className="flex h-56 items-end gap-1">
      {bars.map((item) => (
        <div key={item.month} className="flex flex-1 flex-col items-center gap-1">
          <div className="w-full flex-1 overflow-hidden rounded-t-md bg-white/10" style={{ minHeight: 120 }}>
            <div
              className="w-full rounded-t-md bg-accent transition-all duration-500"
              style={{
                height: `${(item.count / maxCount) * 100}%`,
                minHeight: item.count > 0 ? "4px" : 0,
              }}
            />
          </div>
          <span className="text-xs text-white/80">{item.month}</span>
        </div>
      ))}
    </div>
  );
}

export function jobsToBarChartData(jobs: { created_at: string }[]): ChartDataItem[] {
  const now = new Date();
  const result: ChartDataItem[] = [];
  for (let i = 11; i >= 0; i--) {
    const d = new Date(now.getFullYear(), now.getMonth() - i, 1);
    const count = jobs.filter((j) => {
      const jd = new Date(j.created_at);
      return jd.getMonth() === d.getMonth() && jd.getFullYear() === d.getFullYear();
    }).length;
    result.push({ month: `${MONTHS[d.getMonth()]}`, count });
  }
  return result;
}
