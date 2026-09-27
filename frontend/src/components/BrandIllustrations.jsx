import React from 'react';
import { ArrowRight, Sparkles } from 'lucide-react';

export function CandidateAvatar({ className = "w-11 h-11" }) {
  return (
    <div className={`relative rounded-full overflow-hidden border-2 border-indigo-400/30 shadow-sm flex items-center justify-center bg-gradient-to-tr from-indigo-100 via-sky-50 to-purple-100 ${className}`}>
      <svg viewBox="0 0 120 120" className="w-full h-full">
        {/* Soft pastel background */}
        <circle cx="60" cy="60" r="60" fill="#E0F2FE" />
        {/* Hair back */}
        <path d="M25 65 C20 40, 30 15, 60 15 C90 15, 100 40, 95 65 C95 85, 90 100, 90 100 L30 100 C30 100, 25 85, 25 65 Z" fill="#1E293B" />
        {/* Neck */}
        <rect x="52" y="75" width="16" height="20" rx="6" fill="#FBD3B6" />
        {/* Shoulders / Shirt */}
        <path d="M25 120 C25 96, 40 90, 60 90 C80 90, 95 96, 95 120 Z" fill="#3B82F6" />
        <path d="M48 90 L60 102 L72 90 Z" fill="#FFFFFF" />
        {/* Face */}
        <ellipse cx="60" cy="58" rx="24" ry="26" fill="#FDE2D0" />
        {/* Bangs / Hair front */}
        <path d="M36 46 C42 36, 56 32, 60 38 C64 32, 78 36, 84 46 C80 44, 72 40, 60 43 C48 40, 40 44, 36 46 Z" fill="#1E293B" />
        <path d="M33 50 C32 60, 35 70, 38 78 C35 70, 35 56, 38 48 Z" fill="#1E293B" />
        <path d="M87 50 C88 60, 85 70, 82 78 C85 70, 85 56, 82 48 Z" fill="#1E293B" />
        {/* Eyes */}
        <ellipse cx="50" cy="58" rx="2.5" ry="3.5" fill="#1E293B" />
        <ellipse cx="70" cy="58" rx="2.5" ry="3.5" fill="#1E293B" />
        <circle cx="51" cy="56.5" r="1" fill="#FFFFFF" />
        <circle cx="71" cy="56.5" r="1" fill="#FFFFFF" />
        {/* Eyebrows */}
        <path d="M46 51 Q50 49 54 51" stroke="#1E293B" strokeWidth="1.5" strokeLinecap="round" fill="none" />
        <path d="M66 51 Q70 49 74 51" stroke="#1E293B" strokeWidth="1.5" strokeLinecap="round" fill="none" />
        {/* Cheeks */}
        <circle cx="45" cy="65" r="4" fill="#FDA4AF" opacity="0.6" />
        <circle cx="75" cy="65" r="4" fill="#FDA4AF" opacity="0.6" />
        {/* Smile */}
        <path d="M54 67 Q60 73 66 67" stroke="#E11D48" strokeWidth="1.8" strokeLinecap="round" fill="none" />
      </svg>
    </div>
  );
}

export function HeroRobotIllustration({ className = "w-64 h-48" }) {
  return (
    <div className={`relative flex items-center justify-center select-none ${className}`}>
      {/* Speech bubble */}
      <div className="absolute -top-3 right-2 sm:right-6 bg-white/95 backdrop-blur-sm border border-indigo-200/80 rounded-2xl px-3 py-1.5 shadow-md z-20 text-center animate-bounce duration-1000">
        <span className="text-[11px] font-bold text-slate-800 tracking-tight block">
          Better Skills
        </span>
        <span className="text-[10px] font-semibold text-indigo-600 block">
          Bigger Opportunities! 🚀
        </span>
        <div className="absolute -bottom-1.5 right-6 w-3 h-3 bg-white rotate-45 border-r border-b border-indigo-200" />
      </div>

      <svg viewBox="0 0 320 220" className="w-full h-full drop-shadow-lg">
        <defs>
          <linearGradient id="laptopGrad" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="#1E293B" />
            <stop offset="100%" stopColor="#0F172A" />
          </linearGradient>
          <linearGradient id="screenGrad" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="#1E3A8A" />
            <stop offset="100%" stopColor="#3B82F6" />
          </linearGradient>
          <linearGradient id="botGrad" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="#FFFFFF" />
            <stop offset="100%" stopColor="#E2E8F0" />
          </linearGradient>
          <linearGradient id="glowCyan" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="#00F2FE" />
            <stop offset="100%" stopColor="#38BDF8" />
          </linearGradient>
        </defs>

        {/* Ambient shadow underneath */}
        <ellipse cx="160" cy="205" rx="130" ry="12" fill="#CBD5E1" opacity="0.45" />

        {/* Laptop Base */}
        <path d="M40 185 L180 185 L195 198 L25 198 Z" fill="#94A3B8" />
        <rect x="95" y="196" width="30" height="2" rx="1" fill="#64748B" />

        {/* Laptop Screen / Display Lid */}
        <path d="M45 80 L175 80 L180 185 L40 185 Z" fill="url(#laptopGrad)" rx="8" />
        {/* Inside Screen Glowing Display */}
        <rect x="52" y="88" width="116" height="90" rx="5" fill="url(#screenGrad)" />

        {/* Brain network visual on laptop screen */}
        <circle cx="110" cy="130" r="18" fill="#1D4ED8" stroke="#38BDF8" strokeWidth="2" />
        <path d="M102 124 C106 120 114 120 118 124 C116 128 114 132 110 134 C106 132 104 128 102 124 Z" fill="#60A5FA" />
        <circle cx="100" cy="120" r="2.5" fill="#FFFFFF" />
        <circle cx="120" cy="120" r="2.5" fill="#FFFFFF" />
        <circle cx="110" cy="142" r="2.5" fill="#38BDF8" />
        <line x1="100" y1="120" x2="110" y2="130" stroke="#93C5FD" strokeWidth="1.5" />
        <line x1="120" y1="120" x2="110" y2="130" stroke="#93C5FD" strokeWidth="1.5" />
        <line x1="110" y1="130" x2="110" y2="142" stroke="#93C5FD" strokeWidth="1.5" />

        {/* Floating Sparks */}
        <circle cx="70" cy="105" r="2" fill="#FDE047" />
        <circle cx="145" cy="115" r="2.5" fill="#FDE047" />
        <circle cx="80" cy="160" r="1.5" fill="#6EE7B7" />

        {/* AI Robot Companion */}
        {/* Antenna */}
        <rect x="228" y="70" width="4" height="15" rx="2" fill="#94A3B8" />
        <circle cx="230" cy="67" r="5" fill="#00D2FF" />

        {/* Robot Head */}
        <rect x="205" y="82" width="50" height="42" rx="14" fill="url(#botGrad)" stroke="#CBD5E1" strokeWidth="1.5" />
        {/* Visor Screen */}
        <rect x="212" y="90" width="36" height="24" rx="8" fill="#0F172A" />
        {/* Glowing Eyes (Happy curved arcs) */}
        <path d="M218 102 Q222 98 226 102" stroke="#00F2FE" strokeWidth="2.5" strokeLinecap="round" fill="none" />
        <path d="M234 102 Q238 98 242 102" stroke="#00F2FE" strokeWidth="2.5" strokeLinecap="round" fill="none" />
        {/* Rosy cheeks */}
        <circle cx="216" cy="106" r="2" fill="#F43F5E" opacity="0.8" />
        <circle cx="244" cy="106" r="2" fill="#F43F5E" opacity="0.8" />

        {/* Robot Body */}
        <rect x="208" y="128" width="44" height="46" rx="12" fill="url(#botGrad)" stroke="#CBD5E1" strokeWidth="1.5" />
        {/* Chest core badge (glowing brain or heart) */}
        <circle cx="230" cy="148" r="9" fill="#EEF2F6" stroke="#93C5FD" strokeWidth="1" />
        <path d="M226 148 L230 144 L234 148 L230 152 Z" fill="#3B82F6" />

        {/* Left Arm (Resting on table/laptop) */}
        <path d="M208 138 C198 142, 192 155, 190 170" stroke="#94A3B8" strokeWidth="8" strokeLinecap="round" fill="none" />
        <circle cx="190" cy="170" r="5" fill="#64748B" />

        {/* Right Arm (Waving enthusiastically!) */}
        <path d="M252 138 C265 130, 275 110, 270 95" stroke="#94A3B8" strokeWidth="8" strokeLinecap="round" fill="none" />
        <circle cx="270" cy="95" r="5" fill="#64748B" />
        {/* Wave motion lines */}
        <path d="M278 88 Q282 92 284 98" stroke="#3B82F6" strokeWidth="2" strokeLinecap="round" fill="none" />
        <path d="M282 82 Q288 88 290 96" stroke="#3B82F6" strokeWidth="2" strokeLinecap="round" fill="none" />
      </svg>
    </div>
  );
}

export function SidebarCareerCard({ onNavigate }) {
  return (
    <div className="relative overflow-hidden rounded-2xl p-4 bg-gradient-to-br from-[#1E295D] via-[#1A214D] to-[#161B40] border border-indigo-500/20 text-white shadow-lg group">
      {/* Decorative leaf / foliage background */}
      <div className="absolute right-0 bottom-0 opacity-25 pointer-events-none transform translate-x-2 translate-y-2">
        <svg width="120" height="120" viewBox="0 0 100 100" fill="none">
          <path
            d="M80 90 C80 50, 40 40, 20 20 C40 20, 60 30, 70 50 C80 30, 95 20, 95 20 C95 40, 90 70, 80 90 Z"
            fill="url(#foliageGrad)"
          />
          <path
            d="M60 85 C60 65, 45 55, 35 45 C45 45, 55 52, 60 65 Z"
            fill="#818CF8"
          />
          <defs>
            <linearGradient id="foliageGrad" x1="20" y1="20" x2="95" y2="90">
              <stop stopColor="#818CF8" />
              <stop offset="100%" stopColor="#C084FC" />
            </linearGradient>
          </defs>
        </svg>
      </div>

      <div className="relative z-10 space-y-2">
        <h4 className="text-sm font-extrabold leading-snug tracking-tight text-white pr-4">
          Your Dream Career is Closer Than You Think!
        </h4>
        <p className="text-[11px] text-slate-300 leading-relaxed font-sans pr-6">
          Right skills. Right opportunities. A brighter future.
        </p>

        <div className="pt-2">
          <button
            type="button"
            onClick={() => onNavigate && onNavigate('search')}
            className="w-8 h-8 rounded-full bg-gradient-to-tr from-indigo-500 to-purple-500 hover:from-indigo-400 hover:to-purple-400 text-white flex items-center justify-center shadow-md shadow-indigo-500/30 transition-transform group-hover:translate-x-1 cursor-pointer"
            title="Explore Opportunities"
          >
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
