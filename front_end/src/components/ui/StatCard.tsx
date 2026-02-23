type StatCardProps = {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  iconBgClass?: string;
};

export function StatCard({ title, value, icon, iconBgClass = "bg-accent/80" }: StatCardProps) {
  return (
    <div className="rounded-xl border border-white/20 bg-white/10 p-5 backdrop-blur-sm">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-white/80">{title}</p>
          <p className="mt-2 text-2xl font-bold text-white">{value}</p>
        </div>
        <div className={`flex h-12 w-12 shrink-0 items-center justify-center rounded-lg ${iconBgClass}`}>
          {icon}
        </div>
      </div>
    </div>
  );
}
