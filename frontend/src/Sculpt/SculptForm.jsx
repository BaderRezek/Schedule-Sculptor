import React, { useState } from 'react';

// Reusable Checkbox component
const RequirementCheckbox = ({ id, label, isChecked, onChange, disabled }) => (
  <label 
    htmlFor={id} 
    className={`flex items-center space-x-3 ${disabled ? 'cursor-not-allowed' : 'cursor-pointer'}`}
  >
    <input 
      id={id}
      type="checkbox"
      className="h-5 w-5 text-purple-600 border-gray-300 rounded focus:ring-purple-500"
      checked={isChecked}
      onChange={onChange}
      disabled={disabled}
    />
    <span className={`text-sm ${disabled ? 'text-gray-400' : 'text-gray-700'}`}>{label}</span>
  </label>
);

// Reusable Star Rating component
const StarRating = ({ selected, onChange }) => {
  const stars = [
    { label: "Very Easy", value: "Very Easy" },
    { label: "Easy", value: "Easy" },
    { label: "Moderate", value: "Moderate" },
    { label: "Challenging", value: "Challenging" },
    { label: "Intensive", value: "Intensive" },
  ];

  return (
    <div className="flex items-center justify-center space-x-4">
      {stars.map((star) => (
        <label key={star.value} className="flex flex-col items-center cursor-pointer">
          <svg 
            className={`w-8 h-8 ${selected === star.value ? 'text-yellow-400' : 'text-gray-300'}`} 
            fill="currentColor" 
            viewBox="0 0 20 20"
            onClick={() => onChange(star.value)}
          >
            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
          </svg>
          <span className={`text-xs font-medium mt-1 ${selected === star.value ? 'text-[#4C3B6F]' : 'text-gray-500'}`}>
            {star.label}
          </span>
        </label>
      ))}
    </div>
  );
};

export default function SculptForm({ remainingRequirements, initialPrefs, onSubmit, isGenerating, hasAuditData }) {
  const [reqs, setReqs] = useState(initialPrefs.requirements);
  const [credits, setCredits] = useState(initialPrefs.creditLoad);
  const [difficulty, setDifficulty] = useState(initialPrefs.difficulty);

  const handleReqToggle = (category) => {
    setReqs(prev => prev.includes(category) ? prev.filter(c => c !== category) : [...prev, category]);
  };
  
  const handleCreditToggle = (creditVal) => {
     setCredits(prev => prev.includes(creditVal) ? prev.filter(c => c !== creditVal) : [...prev, creditVal]);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({ requirements: reqs, creditLoad: credits, difficulty });
  };
  
  // Combine requirements from audit with placeholders
  const allReqs = React.useMemo(() => {
    const auditReqs = remainingRequirements.map(r => r.category);
    const placeholders = ["General Education", "Major Core", "Technical Electives", "Free Electives", "Concentration Courses"];
    // Use a Set to ensure requirements are unique
    return [...new Set([...auditReqs, ...placeholders])];
  }, [remainingRequirements]);

  return (
    <div className="w-full max-w-3xl text-center">
      <h2 className="serif-title text-2xl lg:text-5xl font-bold brand-purple leading-tight mb-4">
        Sculpt your Semester
      </h2>
      <p className="text-lg text-gray-500 mb-6">
        Let's plan your next semester based off of your needs.
      </p>

      <form onSubmit={handleSubmit} className="space-y-12">
        <div className="flex flex-col md:flex-row justify-around">
          
          {/* --- Step 1: Requirements --- */}
          <div className="flex-1">
            <h3 className="serif-title text-2xl brand-purple mb-4">Step 1: Requirements to fulfill</h3>
            <div className="flex flex-col items-start space-y-4 max-w-xs mx-auto">
              {!hasAuditData && <p className="text-red-500 text-sm">Upload your audit to see remaining requirements.</p>}
              {allReqs.map((req, i) => (
                <RequirementCheckbox 
                  key={i}
                  id={`req-${i}`}
                  label={req}
                  isChecked={reqs.includes(req)}
                  onChange={() => handleReqToggle(req)}
                  disabled={!hasAuditData} // Disable if no audit is loaded
                />
              ))}
            </div>
          </div>

          {/* --- Step 2: Preferences --- */}
          <div className="flex-1 md:mt-0">
            <h3 className="serif-title text-2xl brand-purple mb-4">Step 2: Your Preferences</h3>
            <h4 className="font-semibold text-gray-700 mb-3">Credit Load:</h4>
            <div className="flex flex-col items-start space-y-3 max-w-xs mx-auto">
              {[
                {label: "12 Credits", value: 12}, // Use a single value for simplicity
                {label: "13 Credits", value: 13},
                {label: "14 Credits", value: 14},
                {label: "15 Credits", value: 15},
                {label: "16 Credits", value: 16},
                {label: "17 Credits", value: 17},
                {label: "< 18 Credits (Overload)", value: 18}
              ].map((item, i) => (
                  <RequirementCheckbox 
                    key={item.value}
                    id={`credit-${i}`}
                    label={item.label}
                    isChecked={credits.includes(item.value)}
                    onChange={() => handleCreditToggle(item.value)}
                  />
                )
              )}
            </div>
            
            <h4 className="font-semibold text-gray-700 mt-8 mb-3">Course Difficulty:</h4>
            <StarRating selected={difficulty} onChange={setDifficulty} />
          </div>

        </div>

        {/* --- Step 3: Generate --- */}
        <div>
          <h3 className="serif-title text-2xl brand-purple mb-4">Step 3: Generate your Schedule!</h3>
          <button
            type="submit"
            disabled={isGenerating || !hasAuditData || reqs.length === 0 || credits.length === 0}
            className="px-8 py-3 bg-[#4C3B6F] text-white font-bold rounded-full hover:bg-[#392d57] disabled:bg-gray-300 transition-all transform hover:scale-105"
          >
            {isGenerating ? "Generating..." : "Generate My Semester Plan"}
          </button>
        </div>
      </form>
    </div>
  );
}