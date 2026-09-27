import React, { useState } from 'react';
import {
  User,
  School,
  GraduationCap,
  Briefcase,
  MapPin,
  Sparkles,
  ArrowRight,
  Upload,
  FileText,
  CheckCircle2,
  Calendar,
  Plus,
  X,
  Layers,
  FileCheck
} from 'lucide-react';
import { ResumeIQLogo } from '../CompanyLogos';
import { CandidateAvatar } from '../BrandIllustrations';

export default function BasicDetailsScreen({ currentUser, setCurrentUser, onComplete }) {
  // All fields blank by default so the candidate writes their own information
  const [fullName, setFullName] = useState(currentUser?.full_name || '');
  const [college, setCollege] = useState(currentUser?.college || '');
  const [degree, setDegree] = useState(currentUser?.degree || '');
  const [gradYear, setGradYear] = useState(currentUser?.gradYear || '');
  const [cgpa, setCgpa] = useState(currentUser?.cgpa || '');
  const [targetRole, setTargetRole] = useState(currentUser?.targetRole || '');
  const [preferredLocation, setPreferredLocation] = useState(currentUser?.preferredLocation || '');
  const [workMode, setWorkMode] = useState(currentUser?.workMode || 'Full-time');
  const [selectedSkills, setSelectedSkills] = useState(currentUser?.skills || []);
  const [customSkillInput, setCustomSkillInput] = useState('');
  const [uploadedFile, setUploadedFile] = useState(null);

  const suggestedSkills = [
    'Python', 'Java', 'C++', 'JavaScript', 'React', 'Node.js',
    'Data Structures & Algorithms', 'Machine Learning', 'Deep Learning',
    'SQL', 'FastAPI', 'System Design', 'Docker', 'AWS'
  ];

  const toggleSkill = (skill) => {
    if (selectedSkills.includes(skill)) {
      setSelectedSkills(selectedSkills.filter((s) => s !== skill));
    } else {
      setSelectedSkills([...selectedSkills, skill]);
    }
  };

  const handleAddCustomSkill = (e) => {
    e.preventDefault();
    const trimmed = customSkillInput.trim();
    if (trimmed && !selectedSkills.includes(trimmed)) {
      setSelectedSkills([...selectedSkills, trimmed]);
      setCustomSkillInput('');
    }
  };

  const handleRemoveSkill = (skillToRemove) => {
    setSelectedSkills(selectedSkills.filter((s) => s !== skillToRemove));
  };

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      setUploadedFile({
        name: file.name,
        size: (file.size / 1024).toFixed(1) + ' KB'
      });
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const updatedUser = {
      ...currentUser,
      full_name: fullName.trim() || 'Candidate',
      college: college.trim(),
      degree: degree.trim(),
      gradYear: gradYear.trim(),
      cgpa: cgpa.trim(),
      targetRole: targetRole.trim(),
      preferredLocation: preferredLocation.trim(),
      workMode: workMode,
      skills: selectedSkills,
      resumeFileName: uploadedFile?.name || null,
      profileCompleted: true
    };
    if (setCurrentUser) setCurrentUser(updatedUser);
    if (onComplete) onComplete(updatedUser);
  };

  return (
    <div className="min-h-screen bg-[#F4F7FC] py-10 px-4 sm:px-6 flex items-center justify-center animate-fadeIn">
      <div className="w-full max-w-3xl space-y-6">
        {/* Step Progress Header */}
        <div className="flex items-center justify-between px-2">
          <div className="flex items-center space-x-3">
            <ResumeIQLogo className="w-8 h-8" />
            <div>
              <h1 className="text-lg font-bold text-slate-900 font-display">ResumeIQ</h1>
              <p className="text-[11px] text-slate-500">Candidate Onboarding Journey</p>
            </div>
          </div>

          <div className="flex items-center space-x-2 text-xs font-semibold">
            <span className="px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200">
              ✓ Step 1: Login Complete
            </span>
            <span className="text-slate-400">&rarr;</span>
            <span className="px-3 py-1 rounded-full bg-[#3B49DF] text-white shadow-xs">
              Step 2: Basic Details
            </span>
            <span className="text-slate-400">&rarr;</span>
            <span className="px-2.5 py-1 rounded-full bg-slate-100 text-slate-500">
              Step 3: Dashboard
            </span>
          </div>
        </div>

        {/* Form Container Card */}
        <div className="bg-white rounded-3xl border border-slate-200/90 shadow-xl overflow-hidden p-6 sm:p-10 space-y-8">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-6 border-b border-slate-100">
            <div className="space-y-1">
              <h2 className="text-2xl font-bold font-display text-slate-900">
                Setup Your Candidate Profile
              </h2>
              <p className="text-xs text-slate-500 max-w-lg">
                Enter your real academic details and career interests so our AI engine can accurately calibrate matching opportunities.
              </p>
            </div>

            {/* Live Profile Snippet */}
            <div className="flex items-center space-x-3 p-2.5 bg-slate-50 rounded-2xl border border-slate-200/80 min-w-[200px]">
              <CandidateAvatar className="w-11 h-11 flex-shrink-0" />
              <div className="text-xs pr-1">
                <p className="font-bold text-slate-800 truncate max-w-[130px]">
                  {fullName.trim() || 'Your Name'}
                </p>
                <p className="text-[11px] text-indigo-600 font-semibold truncate max-w-[130px]">
                  {degree.trim() || 'Degree / Branch'}
                </p>
                <p className="text-[10px] text-slate-400 truncate max-w-[130px]">
                  {college.trim() || 'College / Institute'}
                </p>
              </div>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* 1. Academic Information */}
            <div className="space-y-4">
              <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider font-mono flex items-center space-x-1.5">
                <School className="w-4 h-4 text-indigo-600" />
                <span>1. Academic Information</span>
              </h3>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-slate-700 flex items-center space-x-1">
                    <User className="w-3.5 h-3.5 text-slate-400" />
                    <span>Candidate Full Name</span>
                  </label>
                  <input
                    type="text"
                    required
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    placeholder="e.g. Rahul Sharma"
                    className="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-900 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 font-medium transition-colors"
                  />
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-slate-700 flex items-center space-x-1">
                    <School className="w-3.5 h-3.5 text-slate-400" />
                    <span>College / Institute</span>
                  </label>
                  <input
                    type="text"
                    required
                    value={college}
                    onChange={(e) => setCollege(e.target.value)}
                    placeholder="e.g. IIT Bombay, Delhi University, etc."
                    className="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-900 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 font-medium transition-colors"
                  />
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-slate-700 flex items-center space-x-1">
                    <GraduationCap className="w-3.5 h-3.5 text-slate-400" />
                    <span>Degree &amp; Specialization</span>
                  </label>
                  <input
                    type="text"
                    required
                    value={degree}
                    onChange={(e) => setDegree(e.target.value)}
                    placeholder="e.g. B.Tech Computer Science, BCA, MCA"
                    className="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-900 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 font-medium transition-colors"
                  />
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div className="space-y-1.5">
                    <label className="text-xs font-semibold text-slate-700 flex items-center space-x-1">
                      <Calendar className="w-3.5 h-3.5 text-slate-400" />
                      <span>Graduation Year</span>
                    </label>
                    <input
                      type="text"
                      value={gradYear}
                      onChange={(e) => setGradYear(e.target.value)}
                      placeholder="e.g. 2026"
                      className="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-900 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 font-medium transition-colors font-mono"
                    />
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-xs font-semibold text-slate-700">
                      <span>CGPA / Grade</span>
                    </label>
                    <input
                      type="text"
                      value={cgpa}
                      onChange={(e) => setCgpa(e.target.value)}
                      placeholder="e.g. 8.5 / 10.0"
                      className="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-900 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 font-medium transition-colors font-mono"
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* 2. Target Role & Job Preferences */}
            <div className="space-y-4 pt-4 border-t border-slate-100">
              <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider font-mono flex items-center space-x-1.5">
                <Briefcase className="w-4 h-4 text-indigo-600" />
                <span>2. Career Aspirations &amp; Work Preferences</span>
              </h3>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-slate-700">Target Role Title</label>
                  <input
                    type="text"
                    value={targetRole}
                    onChange={(e) => setTargetRole(e.target.value)}
                    placeholder="e.g. Software Engineer, AI/ML, Full Stack..."
                    className="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-900 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 font-medium transition-colors"
                  />
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-slate-700 flex items-center space-x-1">
                    <MapPin className="w-3.5 h-3.5 text-slate-400" />
                    <span>Preferred Location</span>
                  </label>
                  <input
                    type="text"
                    value={preferredLocation}
                    onChange={(e) => setPreferredLocation(e.target.value)}
                    placeholder="e.g. Bangalore, Hyderabad, Remote..."
                    className="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-900 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 font-medium transition-colors"
                  />
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-slate-700">Job Arrangement</label>
                  <select
                    value={workMode}
                    onChange={(e) => setWorkMode(e.target.value)}
                    className="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-900 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 font-medium cursor-pointer"
                  >
                    <option value="Full-time">Full-time</option>
                    <option value="Internship">Internship</option>
                    <option value="Part-time">Part-time</option>
                    <option value="Remote">Remote</option>
                  </select>
                </div>
              </div>
            </div>

            {/* 3. Verified Technical Skills */}
            <div className="space-y-3 pt-4 border-t border-slate-100">
              <div className="flex items-center justify-between">
                <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider font-mono flex items-center space-x-1.5">
                  <Sparkles className="w-4 h-4 text-indigo-600" />
                  <span>3. Verified Technical Skills</span>
                </h3>
                <span className="text-[11px] text-slate-500 font-mono">
                  {selectedSkills.length} skills added
                </span>
              </div>

              {/* Custom Skill Input */}
              <div className="flex items-center space-x-2">
                <input
                  type="text"
                  value={customSkillInput}
                  onChange={(e) => setCustomSkillInput(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault();
                      handleAddCustomSkill(e);
                    }
                  }}
                  placeholder="Type any skill you know (e.g. C++, PyTorch, React, SQL)..."
                  className="flex-1 px-3.5 py-2 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500"
                />
                <button
                  type="button"
                  onClick={handleAddCustomSkill}
                  className="px-3.5 py-2 rounded-xl bg-[#3B49DF] text-white text-xs font-bold hover:bg-[#313ec0] flex items-center space-x-1 cursor-pointer"
                >
                  <Plus className="w-3.5 h-3.5" />
                  <span>Add Skill</span>
                </button>
              </div>

              {/* Selected Skills Chips */}
              {selectedSkills.length > 0 && (
                <div className="p-3 bg-indigo-50/40 rounded-2xl border border-indigo-100/70 space-y-1.5">
                  <span className="text-[10px] font-bold text-indigo-800 uppercase tracking-wider font-mono">
                    Your Profile Skills:
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {selectedSkills.map((skill) => (
                      <span
                        key={skill}
                        className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-lg bg-[#3B49DF] text-white text-xs font-medium shadow-xs"
                      >
                        <span>{skill}</span>
                        <button
                          type="button"
                          onClick={() => handleRemoveSkill(skill)}
                          className="hover:text-red-200 cursor-pointer ml-1"
                        >
                          <X className="w-3 h-3" />
                        </button>
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Quick Select Suggestions */}
              <div className="space-y-1.5 pt-1">
                <span className="text-[11px] text-slate-400 font-medium">Quick suggestions (click to toggle):</span>
                <div className="flex flex-wrap gap-1.5">
                  {suggestedSkills.map((skill) => {
                    const isSelected = selectedSkills.includes(skill);
                    return (
                      <button
                        type="button"
                        key={skill}
                        onClick={() => toggleSkill(skill)}
                        className={`px-2.5 py-1 rounded-lg text-xs font-medium transition-all cursor-pointer ${
                          isSelected
                            ? 'bg-[#3B49DF] text-white shadow-xs'
                            : 'bg-slate-100 hover:bg-slate-200 text-slate-700'
                        }`}
                      >
                        {isSelected ? '✓ ' : '+ '}
                        {skill}
                      </button>
                    );
                  })}
                </div>
              </div>
            </div>

            {/* 4. Resume Attachment (Real File Selector) */}
            <div className="space-y-2 pt-4 border-t border-slate-100">
              <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider font-mono flex items-center space-x-1.5">
                <FileText className="w-4 h-4 text-indigo-600" />
                <span>4. Resume Attachment (Optional)</span>
              </h3>

              <label className="p-4 rounded-2xl border-2 border-dashed border-slate-200 hover:border-indigo-400 bg-slate-50/50 hover:bg-indigo-50/30 flex items-center justify-between flex-wrap gap-3 cursor-pointer transition-colors">
                <input
                  type="file"
                  accept=".pdf,.docx,.doc,.txt"
                  onChange={handleFileChange}
                  className="hidden"
                />
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 rounded-xl bg-white border border-slate-200 flex items-center justify-center text-indigo-600 shadow-xs">
                    {uploadedFile ? <FileCheck className="w-5 h-5 text-emerald-600" /> : <Upload className="w-5 h-5" />}
                  </div>
                  <div>
                    <p className="text-xs font-bold text-slate-800">
                      {uploadedFile ? uploadedFile.name : 'Upload your resume (PDF, DOCX)'}
                    </p>
                    <p className="text-[11px] text-slate-400">
                      {uploadedFile ? `Size: ${uploadedFile.size} • Ready for analysis` : 'Click to browse files on your computer'}
                    </p>
                  </div>
                </div>

                <span className="px-3 py-1.5 rounded-xl bg-white border border-slate-200 text-slate-700 text-xs font-semibold shadow-xs hover:bg-slate-50">
                  {uploadedFile ? 'Change File' : 'Browse File'}
                </span>
              </label>
            </div>

            {/* Submit Action */}
            <div className="pt-4 flex items-center justify-end">
              <button
                type="submit"
                className="w-full sm:w-auto px-8 py-3.5 rounded-xl bg-[#3B49DF] hover:bg-[#313ec0] text-white font-bold text-xs transition-all shadow-md shadow-indigo-600/30 flex items-center justify-center space-x-2 cursor-pointer"
              >
                <span>Save Profile &amp; Explore Matching Jobs</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
