import { useAuth0 } from "@auth0/auth0-react";
import { useEffect, useMemo, useState } from "react";
import type { FormEvent } from "react";
import { CandidateJobsTile } from "../../components/ui/CandidateJobsTile";
import { useEnsureUser } from "../../hooks/useEnsureUser";
import { applyToJob } from "../../services/jobService";
import type { Job } from "../../types/job";

export default function CandidateDashboard() {
  const { user, getAccessTokenSilently, logout: auth0Logout } = useAuth0();
  const { error: upsertError } = useEnsureUser();
  const [isApplyModalOpen, setIsApplyModalOpen] = useState(false);
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [cvFile, setCvFile] = useState<File | undefined>(undefined);
  const [applyingJobId, setApplyingJobId] = useState<string | null>(null);
  const [appliedJobIds, setAppliedJobIds] = useState<string[]>([]);
  const [applyError, setApplyError] = useState<string | null>(null);
  const [applySuccess, setApplySuccess] = useState<string | null>(null);

  const canApply = useMemo(
    () => fullName.trim() !== "" && email.trim() !== "",
    [email, fullName]
  );

  useEffect(() => {
    if (user?.name) {
      setFullName(user.name);
    }
    if (user?.email) {
      setEmail(user.email);
    }
  }, [user?.email, user?.name]);

  const printAccessToken = async () => {
    const token = await getAccessTokenSilently();
    console.log("ACCESS TOKEN:", token);
  };

  const openApplyModal = (job?: Job) => {
    if (job) {
      setSelectedJob(job);
    }
    setApplyError(null);
    setApplySuccess(null);
    setIsApplyModalOpen(true);
  };
  const closeApplyModal = () => {
    setIsApplyModalOpen(false);
    setApplyError(null);
  };

  const handleApplySubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!selectedJob) {
      setApplyError("Please select a job to apply.");
      return;
    }
    if (!canApply) {
      setApplyError("Full name and email are required.");
      return;
    }

    setApplyingJobId(selectedJob.id);
    setApplyError(null);
    setApplySuccess(null);
    try {
      const token = await getAccessTokenSilently();
      const result = await applyToJob(token, selectedJob.id, {
        full_name: fullName.trim(),
        email: email.trim(),
        phone: phone.trim() || undefined,
        cv_file: cvFile,
      });
      setAppliedJobIds((prev) =>
        prev.includes(selectedJob.id) ? prev : [...prev, selectedJob.id]
      );
      setApplySuccess(result.message);
      setIsApplyModalOpen(false);
    } catch (e) {
      setApplyError(e instanceof Error ? e.message : "Failed to apply");
    } finally {
      setApplyingJobId(null);
    }
  };

  return (
    <main className="flex min-h-0 flex-1 flex-col overflow-auto p-8 lg:p-16">
      <div className="mx-auto w-full max-w-2xl">
        {upsertError && (
          <p className="mb-4 rounded-lg bg-red-500/20 p-3 text-sm text-red-100">
            Could not sync user: {upsertError.message}
          </p>
        )}
        <h1 className="text-3xl font-bold text-white">Candidate Dashboard</h1>
        <p className="mt-2 text-white/90">Logged in as {user?.email}</p>
        <button
          type="button"
          onClick={() => openApplyModal()}
          className="mt-6 rounded-xl border-2 border-white/50 bg-white/10 py-2 px-4 font-medium text-white transition-colors hover:bg-white/20"
        >
          Open Apply Form
        </button>

        <CandidateJobsTile
          getToken={getAccessTokenSilently}
          onApplyJob={(job) => openApplyModal(job)}
          applyingJobId={applyingJobId}
          appliedJobIds={appliedJobIds}
        />

        {applySuccess && (
          <p className="mt-4 rounded-lg bg-emerald-500/20 p-2 text-sm text-emerald-100">
            {applySuccess}
          </p>
        )}

        {isApplyModalOpen && (
          <div
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4"
            onClick={closeApplyModal}
          >
            <div
              className="w-full max-w-2xl rounded-xl border border-white/20 bg-white/10 p-6 backdrop-blur-sm"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold text-white">Apply for Job</h2>
                <button
                  type="button"
                  onClick={closeApplyModal}
                  className="rounded-md border border-white/30 bg-white/10 px-2 py-1 text-sm text-white hover:bg-white/20"
                >
                  Close
                </button>
              </div>
              {selectedJob && (
                <p className="mt-2 text-sm text-accent">
                  Applying to: {selectedJob.title}
                </p>
              )}
              <form className="mt-2" onSubmit={handleApplySubmit}>
                <p className="text-sm text-white/80">
                  Fill required details and upload your CV.
                </p>
                <div className="mt-4 grid gap-3 md:grid-cols-2">
                  <input
                    type="text"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    placeholder="Full name *"
                    className="w-full rounded-lg border border-white/30 bg-black/30 px-3 py-2 text-sm text-white placeholder-white/50"
                  />
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="Email *"
                    className="w-full rounded-lg border border-white/30 bg-black/30 px-3 py-2 text-sm text-white placeholder-white/50"
                  />
                  <input
                    type="text"
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    placeholder="Phone (optional)"
                    className="w-full rounded-lg border border-white/30 bg-black/30 px-3 py-2 text-sm text-white placeholder-white/50"
                  />
                  <input
                    type="file"
                    accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    onChange={(e) => {
                      const next = e.target.files?.[0];
                      setCvFile(next);
                    }}
                    className="w-full rounded-lg border border-white/30 bg-black/30 px-3 py-2 text-sm text-white file:mr-3 file:rounded-md file:border-0 file:bg-accent file:px-3 file:py-1 file:text-white hover:file:bg-accent-hover"
                  />
                </div>
                {!canApply && (
                  <p className="mt-3 rounded-lg bg-red-500/20 p-2 text-sm text-red-100">
                    Full name and email are required.
                  </p>
                )}
                {applyError && (
                  <p className="mt-3 rounded-lg bg-red-500/20 p-2 text-sm text-red-100">
                    {applyError}
                  </p>
                )}
                {cvFile && (
                  <p className="mt-3 text-sm text-white/80">Selected CV: {cvFile.name}</p>
                )}
                <div className="mt-4 flex justify-end gap-2">
                  <button
                    type="button"
                    onClick={closeApplyModal}
                    className="rounded-lg border border-white/40 bg-white/10 px-4 py-2 text-sm font-medium text-white hover:bg-white/20"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={!selectedJob || applyingJobId === selectedJob.id}
                    className="rounded-lg bg-accent px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-accent-hover disabled:cursor-not-allowed disabled:opacity-60"
                  >
                    {selectedJob && applyingJobId === selectedJob.id
                      ? "Submitting..."
                      : "Submit Application"}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        <div className="mt-8 rounded-xl border border-white/20 bg-white/10 p-6 backdrop-blur-sm">
          <h2 className="text-lg font-semibold text-white">Debug</h2>
          <button
            type="button"
            onClick={printAccessToken}
            className="mt-4 rounded-xl bg-accent py-2 px-4 font-medium text-white transition-colors hover:bg-accent-hover"
          >
            Print Access Token
          </button>

          <pre className="mt-4 overflow-auto rounded-lg bg-black/30 p-4 text-sm text-white/90">
            {JSON.stringify(user, null, 2)}
          </pre>

          <button
            type="button"
            onClick={() => auth0Logout({ logoutParams: { returnTo: window.location.origin } })}
            className="mt-4 rounded-xl border-2 border-white/50 bg-white/10 py-2 px-4 font-medium text-white transition-colors hover:bg-white/20"
          >
            Logout
          </button>
        </div>
      </div>
    </main>
  );
}
