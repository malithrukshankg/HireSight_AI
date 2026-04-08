import { useAuth0 } from "@auth0/auth0-react";
import { useCallback, useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { getCvProfile, openCvPdfInNewTab } from "../../services/cvService";
import { getJobApplications, getJobById } from "../../services/jobService";
import type { JobApplication } from "../../types/application";
import type { CVProfile } from "../../types/cv";
import type { Job } from "../../types/job";

function formatAppliedDate(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return "Unknown";
  }
  return date.toLocaleString();
}

function ParsedCvView({ profile }: { profile: CVProfile | null }) {
  if (!profile) {
    return <p className="text-sm text-white/80">No CV profile loaded.</p>;
  }
  const parsed = profile.parsed_profile_json;
  if (!parsed) {
    return (
      <p className="text-sm text-white/80">
        Parsed CV data is not available for this application.
      </p>
    );
  }

  const skills = Array.isArray(parsed.skills) ? parsed.skills : [];
  const experience = Array.isArray(parsed.experience) ? parsed.experience : [];
  const education = Array.isArray(parsed.education) ? parsed.education : [];
  const projects = Array.isArray(parsed.projects) ? parsed.projects : [];

  return (
    <div className="space-y-4">
      <div className="rounded-lg border border-white/20 bg-white/5 p-3">
        <h4 className="text-sm font-semibold text-white">Summary</h4>
        <p className="mt-2 text-sm text-white/90">
          {(typeof parsed.full_name === "string" && parsed.full_name) || "N/A"}
        </p>
        <p className="text-sm text-white/80">
          {(typeof parsed.email === "string" && parsed.email) || "N/A"}
        </p>
        <p className="text-sm text-white/80">
          {(typeof parsed.phone === "string" && parsed.phone) || "N/A"}
        </p>
      </div>

      <div className="rounded-lg border border-white/20 bg-white/5 p-3">
        <h4 className="text-sm font-semibold text-white">Skills</h4>
        {skills.length === 0 ? (
          <p className="mt-2 text-sm text-white/80">No skills listed.</p>
        ) : (
          <div className="mt-2 flex flex-wrap gap-2">
            {skills.map((skill, idx) => (
              <span
                key={`${String(skill)}-${idx}`}
                className="rounded-md bg-white/15 px-2 py-1 text-xs text-white"
              >
                {String(skill)}
              </span>
            ))}
          </div>
        )}
      </div>

      <div className="rounded-lg border border-white/20 bg-white/5 p-3">
        <h4 className="text-sm font-semibold text-white">Experience</h4>
        {experience.length === 0 ? (
          <p className="mt-2 text-sm text-white/80">No experience listed.</p>
        ) : (
          <div className="mt-2 space-y-2">
            {experience.map((item, idx) => {
              const record = item as Record<string, unknown>;
              return (
                <div key={idx} className="rounded-md border border-white/10 bg-black/20 p-2">
                  <p className="text-sm text-white">
                    {String(record.title ?? "Role")} at {String(record.company ?? "Company")}
                  </p>
                  <p className="text-xs text-white/70">
                    {String(record.start_date ?? "")} - {String(record.end_date ?? "")}
                  </p>
                  <p className="mt-1 text-xs text-white/80">
                    {String(record.description ?? "")}
                  </p>
                </div>
              );
            })}
          </div>
        )}
      </div>

      <div className="rounded-lg border border-white/20 bg-white/5 p-3">
        <h4 className="text-sm font-semibold text-white">Education</h4>
        {education.length === 0 ? (
          <p className="mt-2 text-sm text-white/80">No education listed.</p>
        ) : (
          <div className="mt-2 space-y-2">
            {education.map((item, idx) => {
              const record = item as Record<string, unknown>;
              return (
                <div key={idx} className="rounded-md border border-white/10 bg-black/20 p-2">
                  <p className="text-sm text-white">
                    {String(record.degree ?? "Degree")} -{" "}
                    {String(record.institution ?? "Institution")}
                  </p>
                  <p className="text-xs text-white/70">
                    {String(record.start_date ?? "")} - {String(record.end_date ?? "")}
                  </p>
                </div>
              );
            })}
          </div>
        )}
      </div>

      <div className="rounded-lg border border-white/20 bg-white/5 p-3">
        <h4 className="text-sm font-semibold text-white">Projects</h4>
        {projects.length === 0 ? (
          <p className="mt-2 text-sm text-white/80">No projects listed.</p>
        ) : (
          <ul className="mt-2 list-disc pl-5 text-sm text-white/90">
            {projects.map((project, idx) => (
              <li key={`${String(project)}-${idx}`}>{String(project)}</li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

export default function JobApplicationsPage() {
  const { getAccessTokenSilently } = useAuth0();
  const navigate = useNavigate();
  const { jobId } = useParams<{ jobId: string }>();

  const [job, setJob] = useState<Job | null>(null);
  const [applications, setApplications] = useState<JobApplication[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [selectedApplication, setSelectedApplication] = useState<JobApplication | null>(null);
  const [cvProfile, setCvProfile] = useState<CVProfile | null>(null);
  const [cvLoading, setCvLoading] = useState(false);
  const [cvError, setCvError] = useState<string | null>(null);

  const pageTitle = useMemo(() => {
    if (!job) return "Job Applications";
    return `${job.title} - Applications`;
  }, [job]);

  const fetchPageData = useCallback(async () => {
    if (!jobId) {
      setError("Job ID is missing.");
      setLoading(false);
      return;
    }
    try {
      setError(null);
      const token = await getAccessTokenSilently();
      const [jobData, appData] = await Promise.all([
        getJobById(token, jobId),
        getJobApplications(token, jobId),
      ]);
      setJob(jobData);
      setApplications(appData);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load applications");
    } finally {
      setLoading(false);
    }
  }, [getAccessTokenSilently, jobId]);

  useEffect(() => {
    fetchPageData();
  }, [fetchPageData]);

  const handleViewParsedCv = async (application: JobApplication) => {
    if (!application.cv_id) {
      setCvError("CV is not available for this application.");
      setSelectedApplication(application);
      setCvProfile(null);
      return;
    }
    try {
      setCvLoading(true);
      setCvError(null);
      setSelectedApplication(application);
      const token = await getAccessTokenSilently();
      const profile = await getCvProfile(token, application.cv_id);
      setCvProfile(profile);
    } catch (e) {
      setCvProfile(null);
      setCvError(e instanceof Error ? e.message : "Failed to load parsed CV");
    } finally {
      setCvLoading(false);
    }
  };

  const handleViewPdfCv = async (application: JobApplication) => {
    if (!application.cv_id) {
      setError("CV is not available for this application.");
      return;
    }
    try {
      const token = await getAccessTokenSilently();
      await openCvPdfInNewTab(token, application.cv_id);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to open PDF CV");
    }
  };

  return (
    <main className="flex min-h-0 flex-1 flex-col p-6 lg:p-8">
      <div className="w-full">
        <div className="mb-6 flex items-center justify-between gap-3">
          <div>
            <h1 className="text-2xl font-bold text-white">{pageTitle}</h1>
            {job && (
              <p className="mt-1 text-sm text-white/80">
                {job.location} · {job.employment_type} · {job.status}
              </p>
            )}
          </div>
          <button
            type="button"
            onClick={() => navigate("/recruiter")}
            className="rounded-xl border-2 border-white/50 bg-white/10 py-2 px-4 text-sm font-medium text-white transition-colors hover:bg-white/20"
          >
            Back to Jobs
          </button>
        </div>

        <div className="rounded-xl border border-white/20 bg-white/10 p-6 backdrop-blur-sm">
          {loading ? (
            <p className="text-white/80">Loading applications...</p>
          ) : error ? (
            <p className="rounded-lg bg-red-500/20 p-3 text-sm text-red-100">{error}</p>
          ) : applications.length === 0 ? (
            <p className="text-white/80">No applications found for this job.</p>
          ) : (
            <div className="flex flex-col gap-3">
              {applications.map((application) => (
                <div
                  key={application.candidate_id}
                  className="rounded-xl border border-white/20 bg-white/5 p-4"
                >
                  <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
                    <div>
                      <p className="font-medium text-white">{application.full_name}</p>
                      <p className="text-sm text-white/80">{application.email}</p>
                      <p className="text-sm text-white/70">
                        Status: {application.status} · Applied:{" "}
                        {formatAppliedDate(application.applied_at)}
                      </p>
                    </div>
                    <div className="flex gap-2">
                      <button
                        type="button"
                        onClick={() => handleViewParsedCv(application)}
                        className="rounded-lg bg-accent px-3 py-2 text-sm font-medium text-white transition-colors hover:bg-accent-hover"
                      >
                        View AI Parsed CV
                      </button>
                      <button
                        type="button"
                        onClick={() => handleViewPdfCv(application)}
                        className="rounded-lg border border-white/40 bg-white/10 px-3 py-2 text-sm font-medium text-white transition-colors hover:bg-white/20"
                      >
                        View PDF CV
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {selectedApplication && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4"
          onClick={() => {
            setSelectedApplication(null);
            setCvProfile(null);
            setCvError(null);
          }}
        >
          <div
            className="max-h-[90vh] w-full max-w-3xl overflow-auto rounded-xl border border-white/20 bg-white/10 p-6 backdrop-blur-sm"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="mb-3 flex items-center justify-between">
              <h3 className="text-lg font-semibold text-white">
                Parsed CV - {selectedApplication.full_name}
              </h3>
              <button
                type="button"
                onClick={() => {
                  setSelectedApplication(null);
                  setCvProfile(null);
                  setCvError(null);
                }}
                className="rounded-md border border-white/30 bg-white/10 px-2 py-1 text-sm text-white hover:bg-white/20"
              >
                Close
              </button>
            </div>

            {cvLoading ? (
              <p className="text-white/80">Loading parsed CV...</p>
            ) : cvError ? (
              <p className="rounded-lg bg-red-500/20 p-3 text-sm text-red-100">{cvError}</p>
            ) : (
              <ParsedCvView profile={cvProfile} />
            )}
          </div>
        </div>
      )}
    </main>
  );
}

