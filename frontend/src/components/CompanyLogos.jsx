import React from 'react';

export function ResumeIQLogo({ className = "w-9 h-9" }) {
  return (
    <div className={`relative flex items-center justify-center ${className}`}>
      {/* Subtle cyan glow */}
      <div className="absolute inset-0 rounded-xl bg-cyan-400/20 blur-md" />
      <svg
        className="w-full h-full relative z-10"
        viewBox="0 0 48 48"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <rect width="48" height="48" rx="12" fill="#0B132B" />
        <path
          d="M24 10C16.82 10 11 15.82 11 23C11 27.28 13.06 31.08 16.24 33.48L17.5 38.5C17.7 39.38 18.5 40 19.4 40H28.6C29.5 40 30.3 39.38 30.5 38.5L31.76 33.48C34.94 31.08 37 27.28 37 23C37 15.82 31.18 10 24 10Z"
          stroke="url(#brain_grad)"
          strokeWidth="2.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        {/* Brain sulci / neural network circuitry */}
        <path
          d="M24 14V22M18 18C19 20 21 21 24 21M30 18C29 20 27 21 24 21M16 26C18 26 21 27 24 29M32 26C30 26 27 27 24 29M20 34H28"
          stroke="#00D2FF"
          strokeWidth="2"
          strokeLinecap="round"
        />
        {/* Glowing Neural Dots */}
        <circle cx="24" cy="14" r="1.5" fill="#38BDF8" />
        <circle cx="18" cy="18" r="1.5" fill="#38BDF8" />
        <circle cx="30" cy="18" r="1.5" fill="#38BDF8" />
        <circle cx="16" cy="26" r="1.5" fill="#38BDF8" />
        <circle cx="32" cy="26" r="1.5" fill="#38BDF8" />
        <circle cx="24" cy="29" r="1.5" fill="#38BDF8" />
        <defs>
          <linearGradient id="brain_grad" x1="11" y1="10" x2="37" y2="40" gradientUnits="userSpaceOnUse">
            <stop stopColor="#00F2FE" />
            <stop offset="0.5" stopColor="#38BDF8" />
            <stop offset="1" stopColor="#6366F1" />
          </linearGradient>
        </defs>
      </svg>
    </div>
  );
}

export function GoogleLogo({ className = "w-9 h-9" }) {
  return (
    <div className={`p-1.5 bg-white rounded-xl shadow-sm border border-slate-100 flex items-center justify-center ${className}`}>
      <svg className="w-full h-full" viewBox="0 0 24 24">
        <path
          fill="#4285F4"
          d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
        />
        <path
          fill="#34A853"
          d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
        />
        <path
          fill="#FBBC05"
          d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"
        />
        <path
          fill="#EA4335"
          d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"
        />
      </svg>
    </div>
  );
}

export function MicrosoftLogo({ className = "w-9 h-9" }) {
  return (
    <div className={`p-1.5 bg-white rounded-xl shadow-sm border border-slate-100 flex items-center justify-center ${className}`}>
      <svg className="w-full h-full" viewBox="0 0 24 24">
        <rect x="2" y="2" width="9.5" height="9.5" fill="#F25022" rx="1.5" />
        <rect x="12.5" y="2" width="9.5" height="9.5" fill="#7FBA00" rx="1.5" />
        <rect x="2" y="12.5" width="9.5" height="9.5" fill="#00A4EF" rx="1.5" />
        <rect x="12.5" y="12.5" width="9.5" height="9.5" fill="#FFB900" rx="1.5" />
      </svg>
    </div>
  );
}

export function AmazonLogo({ className = "w-9 h-9" }) {
  return (
    <div className={`p-1.5 bg-white rounded-xl shadow-sm border border-slate-100 flex items-center justify-center ${className}`}>
      <svg className="w-full h-full" viewBox="0 0 24 24">
        <path
          fill="#111827"
          d="M13.5 13.2c0-1.8-1.1-2.9-2.7-2.9-1.3 0-2.2.8-2.6 1.8l1.6.8c.2-.5.6-.8 1-.8.7 0 1.1.5 1.1 1.2v.2c-.4-.2-1-.4-1.7-.4-1.8 0-3 1-3 2.5 0 1.5 1.1 2.4 2.5 2.4 1.1 0 1.9-.5 2.3-1.3h.1v1.1h1.7v-4.5zm-1.6 2.8c-.3.5-.8.8-1.4.8-.7 0-1.2-.5-1.2-1.3 0-.9.6-1.3 1.5-1.3.4 0 .8.1 1.1.2v1.6z"
        />
        <path
          fill="#FF9900"
          d="M18.8 17.5c-2.4 1.8-6.1 2.7-9.1 1.7-1.4-.5-2.6-1.3-3.7-2.3-.2-.2-.2-.5 0-.7.2-.2.5-.1.7.1.9.9 2 1.6 3.2 2 2.6.9 5.9.1 8-1.5.3-.2.6 0 .7.3.1.2 0 .3-.1.4z"
        />
        <path
          fill="#FF9900"
          d="M19.7 15.9c-.3-.3-1.6-.2-2.3 0-.2.1-.2-.2-.1-.3.8-.7 2.1-.7 2.6-.2.5.5.1 1.9-.6 2.6-.2.2-.4.1-.3-.1.3-.7.7-1.7.7-2z"
        />
      </svg>
    </div>
  );
}

export function TcsLogo({ className = "w-9 h-9" }) {
  return (
    <div className={`p-1 bg-white rounded-xl shadow-sm border border-slate-100 flex items-center justify-center ${className}`}>
      <span className="font-extrabold text-[12px] tracking-tight bg-gradient-to-r from-pink-600 via-purple-600 to-indigo-600 bg-clip-text text-transparent">
        tcs
      </span>
    </div>
  );
}

export function AccentureLogo({ className = "w-9 h-9" }) {
  return (
    <div className={`px-2 py-1 bg-white rounded-xl shadow-sm border border-slate-100 flex items-center justify-center ${className}`}>
      <span className="font-bold text-[11px] tracking-tighter text-slate-800 flex items-center">
        accenture<span className="text-purple-600 font-black ml-0.5">&gt;</span>
      </span>
    </div>
  );
}

export function CompanyLogo({ company, className = "w-10 h-10" }) {
  const norm = (company || '').toLowerCase();
  if (norm.includes('google')) return <GoogleLogo className={className} />;
  if (norm.includes('microsoft')) return <MicrosoftLogo className={className} />;
  if (norm.includes('amazon')) return <AmazonLogo className={className} />;
  if (norm.includes('tcs') || norm.includes('tata')) return <TcsLogo className={className} />;
  if (norm.includes('accenture')) return <AccentureLogo className={className} />;

  // Default fallback company badge
  const initials = company ? company.substring(0, 2).toUpperCase() : 'CO';
  return (
    <div className={`p-1.5 bg-gradient-to-tr from-slate-100 to-slate-200 rounded-xl shadow-sm border border-slate-200/80 flex items-center justify-center font-bold text-slate-700 text-xs ${className}`}>
      {initials}
    </div>
  );
}
