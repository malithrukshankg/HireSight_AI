export function Footer() {
  return (
    <footer className="shrink-0 border-t border-neutral-200 bg-neutral-50">
      <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
        <p className="text-center text-sm text-neutral-500">
          © {new Date().getFullYear()} HireSight. All rights reserved.
        </p>
      </div>
    </footer>
  );
}
