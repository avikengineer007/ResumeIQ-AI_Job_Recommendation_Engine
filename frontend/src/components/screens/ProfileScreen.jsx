import React from 'react';
import {
  User,
  School,
  GraduationCap,
  Mail,
  MapPin,
  Calendar,
  CheckCircle2,
  Star,
  Send,
  Heart,
  FileText,
  Sparkles,
  ExternalLink,
  Edit3,
  Award
} from 'lucide-react';
import { CandidateAvatar } from '../BrandIllustrations';

export default function ProfileScreen({ currentUser, activeResume, onNavigate }) {
  const candidate = {
    name: currentUser?.full_name || 'Candidate',
    degree: currentUser?.degree || 'B.Tech CSE (AI & ML)',
    college: currentUser?.college || 'Sunrise College of Technology',
    email: currentUser?.email || 'candidate@sunrise.edu.in',
    location: 'Bangalore, India',
    graduationYear: '2026',
    gpa: '8.9 / 10.0',
    skills: [
      'Python', 'Machine Learning', 'Data Analysis', 'Deep Learning',
      'SQL', 'Java', 'DSA', 'FastAPI', 'PyTorch', 'TensorFlow', 'PostgreSQL'
    ],
    verifiedCertifications: [
      'Deep Learning Specialization (Coursera)',
      'AWS Certified Cloud Practitioner',
      'Data Structures & Algorithms in Java'
    ]
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto py-4 animate-fadeIn">
      {/* Top Banner */}
      <div className="relative rounded-3xl bg-gradient-to-r from-[#0B112C] via-[#151D42] to-[#1E2B63] p-8 text-white overflow-hidden shadow-xl border border-indigo-500/20">
        <div className="absolute right-0 top-0 w-80 h-80 rounded-full bg-indigo-500/10 blur-3xl pointer-events-none" />

        <div className="flex flex-col sm:flex-row items-center sm:items-start gap-6 relative z-10">
          <CandidateAvatar className="w-24 h-24 ring-4 ring-indigo-400/30 shadow-2xl" />

          <div className="flex-1 text-center sm:text-left space-y-2">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div>
                <h2 className="text-2xl font-bold font-display text-white">
                  {candidate.name}
                </h2>
                <p className="text-sm text-cyan-300 font-medium">
                  {candidate.degree}
                </p>
              </div>

              <button
                onClick={() => onNavigate && onNavigate('builder')}
                className="px-4 py-2 rounded-xl bg-white/10 hover:bg-white/20 text-white text-xs font-semibold border border-white/20 flex items-center space-x-2 self-center sm:self-auto cursor-pointer transition-all"
              >
                <Edit3 className="w-3.5 h-3.5 text-cyan-300" />
                <span>Update Resume</span>
              </button>
            </div>

            <div className="flex flex-wrap items-center justify-center sm:justify-start gap-y-1 gap-x-4 text-xs text-slate-300 pt-1">
              <span className="flex items-center space-x-1.5">
                <School className="w-4 h-4 text-indigo-400" />
                <span>{candidate.college}</span>
              </span>
              <span>•</span>
              <span className="flex items-center space-x-1">
                <MapPin className="w-4 h-4 text-slate-400" />
                <span>{candidate.location}</span>
              </span>
              <span>•</span>
              <span className="flex items-center space-x-1">
                <Mail className="w-4 h-4 text-slate-400" />
                <span>{candidate.email}</span>
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* 4 Metrics Strip */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="p-4 rounded-2xl bg-white border border-slate-200/80 shadow-sm flex items-center space-x-3.5">
          <div className="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center flex-shrink-0">
            <CheckCircle2 className="w-5 h-5" />
          </div>
          <div>
            <p className="text-[11px] font-medium text-slate-500">Profile Status</p>
            <p className="text-lg font-extrabold text-slate-900">100% Done</p>
          </div>
        </div>

        <div className="p-4 rounded-2xl bg-white border border-slate-200/80 shadow-sm flex items-center space-x-3.5">
          <div className="w-10 h-10 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center flex-shrink-0">
            <Star className="w-5 h-5" />
          </div>
          <div>
            <p className="text-[11px] font-medium text-slate-500">Skills Matched</p>
            <p className="text-lg font-extrabold text-slate-900">8 / 10</p>
          </div>
        </div>

        <div className="p-4 rounded-2xl bg-white border border-slate-200/80 shadow-sm flex items-center space-x-3.5">
          <div className="w-10 h-10 rounded-xl bg-sky-50 text-sky-600 flex items-center justify-center flex-shrink-0">
            <Send className="w-5 h-5" />
          </div>
          <div>
            <p className="text-[11px] font-medium text-slate-500">Applications</p>
            <p className="text-lg font-extrabold text-slate-900">7 This Month</p>
          </div>
        </div>

        <div className="p-4 rounded-2xl bg-white border border-slate-200/80 shadow-sm flex items-center space-x-3.5">
          <div className="w-10 h-10 rounded-xl bg-rose-50 text-rose-600 flex items-center justify-center flex-shrink-0">
            <Heart className="w-5 h-5" />
          </div>
          <div>
            <p className="text-[11px] font-medium text-slate-500">Saved Jobs</p>
            <p className="text-lg font-extrabold text-slate-900">12 Positions</p>
          </div>
        </div>
      </div>

      {/* Main Details Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Left Column: Academic & Verifications (1 col) */}
        <div className="space-y-6">
          <div className="p-5 rounded-2xl bg-white border border-slate-200/80 shadow-sm space-y-4">
            <div className="flex items-center space-x-2 text-slate-900 font-bold text-sm">
              <GraduationCap className="w-4 h-4 text-indigo-600" />
              <span>Academic Background</span>
            </div>

            <div className="space-y-3 text-xs">
              <div className="p-3 rounded-xl bg-slate-50 border border-slate-100 space-y-1">
                <p className="font-bold text-slate-800">{candidate.degree}</p>
                <p className="text-slate-600">{candidate.college}</p>
                <div className="flex justify-between text-[11px] text-slate-500 pt-1">
                  <span>Graduation: {candidate.graduationYear}</span>
                  <span className="font-semibold text-emerald-600">CGPA: {candidate.gpa}</span>
                </div>
              </div>
            </div>
          </div>

          <div className="p-5 rounded-2xl bg-white border border-slate-200/80 shadow-sm space-y-3">
            <div className="flex items-center space-x-2 text-slate-900 font-bold text-sm">
              <Award className="w-4 h-4 text-amber-500" />
              <span>Certifications</span>
            </div>
            <div className="space-y-2 text-xs">
              {candidate.verifiedCertifications.map((cert) => (
                <div key={cert} className="flex items-center space-x-2 text-slate-700">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500 flex-shrink-0" />
                  <span className="font-medium">{cert}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column: Skills Matrix & Active Resume (2 cols) */}
        <div className="md:col-span-2 space-y-6">
          {/* Skills Matrix */}
          <div className="p-5 rounded-2xl bg-white border border-slate-200/80 shadow-sm space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2 text-slate-900 font-bold text-sm">
                <Sparkles className="w-4 h-4 text-indigo-600" />
                <span>Extracted &amp; Verified Skills</span>
              </div>
              <span className="text-[11px] text-indigo-600 font-semibold cursor-pointer" onClick={() => onNavigate && onNavigate('skills')}>
                Analyze Skill Gap &rarr;
              </span>
            </div>

            <div className="flex flex-wrap gap-2">
              {candidate.skills.map((skill) => (
                <span
                  key={skill}
                  className="px-3 py-1 rounded-lg bg-sky-50 text-sky-800 text-xs font-semibold border border-sky-100"
                >
                  {skill}
                </span>
              ))}
            </div>
          </div>

          {/* Active Resume Summary */}
          <div className="p-5 rounded-2xl bg-white border border-slate-200/80 shadow-sm space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2 text-slate-900 font-bold text-sm">
                <FileText className="w-4 h-4 text-indigo-600" />
                <span>Active Resume Overview</span>
              </div>
              <button
                onClick={() => onNavigate && onNavigate('resume_analysis')}
                className="text-xs font-bold text-indigo-600 hover:text-indigo-800 cursor-pointer"
              >
                Deep Analysis &rarr;
              </button>
            </div>

            <div className="p-4 rounded-xl bg-slate-50 border border-slate-100 text-xs text-slate-600 leading-relaxed font-sans">
              {activeResume?.summary ||
                'Computer Science candidate specializing in Artificial Intelligence & Machine Learning with demonstrated expertise in predictive modeling, deep learning architectures, Python algorithms, and SQL data analytics.'}
            </div>

            <div className="flex flex-wrap items-center gap-3 pt-2">
              <button
                onClick={() => onNavigate && onNavigate('recommendations')}
                className="px-4 py-2 rounded-xl bg-[#3B49DF] text-white text-xs font-bold shadow-sm shadow-indigo-600/20 cursor-pointer"
              >
                Find Matching Jobs
              </button>
              <button
                onClick={() => onNavigate && onNavigate('builder')}
                className="px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-800 text-xs font-semibold cursor-pointer"
              >
                Upload New Version
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
