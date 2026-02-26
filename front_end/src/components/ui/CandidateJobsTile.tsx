import { useEffect, useMemo, useState } from "react";
import { getJobs } from "../../services/jobService";
import type { Job } from "../../types/job";

const DEBOUNCE_MS = 400;
const MIN_QUERY_LENGTH = 2;
const PAGE_SIZE = 20;

export type CandidateJobsTileProps = {
  getToken: () => Promise<string>;
  onSelectJob?: (job: Job) => void;
};

export function CandidateJobsTile({ getToken, onSelectJob }: CandidateJobsTileProps) {
  const [queryInput, setQueryInput] = useState("");
  const [locationInput, setLocationInput] = useState("");
  const [debouncedQuery, setDebouncedQuery] = useState("");
  const [debouncedLocation, setDebouncedLocation] = useState("");
  const [page, setPage] = useState(1);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const timeout = window.setTimeout(() => {
      setDebouncedQuery(queryInput);
      setDebouncedLocation(locationInput);
    }, DEBOUNCE_MS);
    return () => window.clearTimeout(timeout);
  }, [queryInput, locationInput]);

  useEffect(() => {
    setPage(1);
  }, [debouncedQuery, debouncedLocation]);

  const normalizedQuery = debouncedQuery.trim();
  const normalizedLocation = debouncedLocation.trim();
  const isQueryTooShort =
    normalizedQuery.length > 0 && normalizedQuery.length < MIN_QUERY_LENGTH;

  useEffect(() => {
    let cancelled = false;

    if (isQueryTooShort) {
      setJobs([]);
      setLoading(false);
      setError(null);
      return;
    }

    const loadJobs = async () => {
      setLoading(true);
      setError(null);
      try {
        const token = await getToken();
        const data = await getJobs(token, {
          query: normalizedQuery || undefined,
          location: normalizedLocation || undefined,
          page,
          page_size: PAGE_SIZE,
          sort: "recent",
        });
        if (!cancelled) {
          setJobs(data);
        }
      } catch (e) {
        if (!cancelled) {
          setError(e instanceof Error ? e.message : String(e));
          setJobs([]);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    loadJobs();
    return () => {
      cancelled = true;
    };
  }, [getToken, isQueryTooShort, normalizedLocation, normalizedQuery, page]);

  const canGoPrev = page > 1;
  const canGoNext = jobs.length === PAGE_SIZE && !loading && !isQueryTooShort;
  const activeFilters = useMemo(
    () => [normalizedQuery, normalizedLocation].filter((value) => value !== "").length,
    [normalizedLocation, normalizedQuery]
  );

  return (
    <section className="mt-8 rounded-xl border border-white/20 bg-white/10 p-6 backdrop-blur-sm">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <h2 className="text-lg font-semibold text-white">Available Jobs</h2>
        <p className="text-sm text-white/75">
          Debounced search ({DEBOUNCE_MS}ms) · Page {page}
        </p>
      </div>

      <div className="mt-4 grid gap-3 md:grid-cols-2">
        <input
          type="text"
          value={queryInput}
          onChange={(e) => setQueryInput(e.target.value)}
          placeholder="Search jobs (title or description)"
          className="w-full rounded-lg border border-white/30 bg-black/30 px-3 py-2 text-sm text-white placeholder-white/50"
        />
        <input
          type="text"
          value={locationInput}
          onChange={(e) => setLocationInput(e.target.value)}
          placeholder="Filter by location"
          className="w-full rounded-lg border border-white/30 bg-black/30 px-3 py-2 text-sm text-white placeholder-white/50"
        />
      </div>

      {isQueryTooShort && (
        <p className="mt-3 rounded-lg bg-red-500/20 p-2 text-sm text-red-100">
          Enter at least {MIN_QUERY_LENGTH} characters for keyword search.
        </p>
      )}

      <div className="mt-4 flex items-center justify-between">
        <p className="text-sm text-white/75">
          {activeFilters > 0 ? `${activeFilters} filter(s) active` : "Showing latest open jobs"}
        </p>
        <div className="flex gap-2">
          <button
            type="button"
            disabled={!canGoPrev}
            onClick={() => setPage((prev) => Math.max(1, prev - 1))}
            className="rounded-lg border border-white/30 bg-white/10 px-3 py-1.5 text-sm text-white transition-colors hover:bg-white/20 disabled:opacity-40"
          >
            Prev
          </button>
          <button
            type="button"
            disabled={!canGoNext}
            onClick={() => setPage((prev) => prev + 1)}
            className="rounded-lg border border-white/30 bg-white/10 px-3 py-1.5 text-sm text-white transition-colors hover:bg-white/20 disabled:opacity-40"
          >
            Next
          </button>
        </div>
      </div>

      {loading ? (
        <p className="mt-4 text-white/80">Loading jobs...</p>
      ) : error ? (
        <p className="mt-4 rounded-lg bg-red-500/20 p-3 text-sm text-red-100">{error}</p>
      ) : jobs.length === 0 ? (
        <p className="mt-4 text-white/80">No jobs found for the current filters.</p>
      ) : (
        <div className="mt-4 flex flex-col gap-3">
          {jobs.map((job) => (
            <article
              key={job.id}
              className="rounded-xl border border-white/20 bg-white/10 p-4 backdrop-blur-sm"
            >
              <div className="flex items-start justify-between gap-3">
                <div>
                  <h3 className="text-base font-semibold text-white">{job.title}</h3>
                  <p className="mt-1 text-sm text-white/80">
                    {job.location} · {job.employment_type}
                  </p>
                </div>
                {onSelectJob && (
                  <button
                    type="button"
                    onClick={() => onSelectJob(job)}
                    className="rounded-lg bg-accent px-3 py-1.5 text-sm font-medium text-white transition-colors hover:bg-accent-hover"
                  >
                    View Details
                  </button>
                )}
              </div>
              <p className="mt-3 line-clamp-3 text-sm text-white/85">{job.description}</p>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
