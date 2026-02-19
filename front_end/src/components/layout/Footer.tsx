export function Footer() {
  return (
    <footer className="shrink-0 border-t border-white/10 bg-black/20 backdrop-blur-sm">
      <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
        <p className="text-center text-sm text-white/80">
          © {new Date().getFullYear()} HireSight. All rights reserved.
        </p>
      </div>
    </footer>
  );
}
