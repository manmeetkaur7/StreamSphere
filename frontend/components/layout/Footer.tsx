const footerLinks = ["About", "Privacy", "Contact"];

export default function Footer() {
  return (
    <footer className="border-t border-white/10 bg-black px-6 py-8 sm:px-8 lg:px-10">
      <div className="mx-auto flex w-full max-w-7xl flex-col items-center justify-between gap-5 text-sm text-white/50 sm:flex-row">
        <p>© {new Date().getFullYear()} StreamSphere</p>
        <nav aria-label="Footer navigation" className="flex items-center gap-6">
          {footerLinks.map((item) => (
            <a
              key={item}
              href={`#${item.toLowerCase()}`}
              className="transition-colors hover:text-white"
            >
              {item}
            </a>
          ))}
          <a
            href="https://github.com"
            target="_blank"
            rel="noreferrer"
            className="transition-colors hover:text-white"
          >
            GitHub
          </a>
        </nav>
      </div>
    </footer>
  );
}
