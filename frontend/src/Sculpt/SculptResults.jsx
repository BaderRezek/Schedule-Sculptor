import React from 'react';

// A single row for a suggested course
const SuggestedCourseItem = ({ term, code, credits, title, category }) => {
  // Simple mapping for the key/legend
  const categoryColors = {
    "Tech Elective": "bg-gray-800",
    "Gen Ed": "bg-green-500",
    "Major": "bg-red-500",
    "Minor": "bg-purple-500",
    "Concentration": "bg-yellow-500",
    "Free Elective": "bg-blue-500",
  };
  const categoryColor = categoryColors[category] || "bg-gray-400";

  return (
    <div className="flex items-center space-x-4 py-3 border-b border-gray-200">
      <div className={`${categoryColor} w-2 h-2 rounded-full`}></div>
      <span className="w-16 font-medium text-gray-500">{term}</span>
      <span className="w-20 font-bold text-gray-800">{code}</span>
      <span className="w-16 text-gray-600">{credits.toFixed(2)}</span>
      <span className="flex-1 text-gray-800">{title}</span>
    </div>
  );
};

// The legend component
const Legend = () => (
  <div className="flex flex-wrap justify-center gap-x-4 gap-y-1 text-xs text-gray-600 mb-6">
    <span className="flex items-center"><div className="w-2 h-2 rounded-full bg-gray-800 mr-1"></div>Tech Elective</span>
    <span className="flex items-center"><div className="w-2 h-2 rounded-full bg-green-500 mr-1"></div>Gen Ed</span>
    <span className="flex items-center"><div className="w-2 h-2 rounded-full bg-red-500 mr-1"></div>Major</span>
    <span className="flex items-center"><div className="w-2 h-2 rounded-full bg-purple-500 mr-1"></div>Minor</span>
    <span className="flex items-center"><div className="w-2 h-2 rounded-full bg-yellow-500 mr-1"></div>Concentration</span>
    <span className="flex items-center"><div className="w-2 h-2 rounded-full bg-blue-500 mr-1"></div>Free Elective</span>
  </div>
);

export default function SculptResults({ plan, preferences, onGenerateNew }) {
  
  if (!plan) {
    return (
      <div className="text-center">
        <p className="text-gray-500">Generating your plan...</p>
      </div>
    );
  }
  
  // Simple function to determine a "placeholder" category for the demo
  const getCategory = (course) => {
    if (preferences.requirements.includes("Technical Electives") && course.subject === "CS") return "Tech Elective";
    if (preferences.requirements.includes("General Education")) return "Gen Ed";
    if (preferences.requirements.includes("Major Core")) return "Major";
    return "Free Elective";
  }

  return (
    <div className="w-full max-w-3xl">
      <div className="text-center mb-6">
        <h2 className="serif-title text-5xl lg:text-7xl font-bold brand-purple leading-tight mb-3">
          Suggested Courses
        </h2>
        <p className="text-lg text-gray-500">
          Based off of your requirements and priorities
        </p>
      </div>

      {/* Course List */}
      <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
        {plan.plan.length > 0 ? (
          plan.plan.map(course => (
            <SuggestedCourseItem
              key={course.code}
              term="SP26" // Placeholder term
              code={course.code}
              credits={course.credits}
              title={course.title}
              category={getCategory(course)} // Use placeholder logic
            />
          ))
        ) : (
          <p className="text-gray-500 text-center py-4">No courses found matching all your criteria. Try adjusting your preferences.</p>
        )}
      </div>

      {/* Info Button */}
      <div className="text-center mb-6">
        <button className="bg-white text-[#4C3B6F] font-semibold py-2 px-5 rounded-full border-2 border-[#4C3B6F] hover:bg-gray-50">
          Why Were These Courses Chosen?
        </button>
      </div>

      {/* Summary and Actions */}
      <div className="flex justify-between items-center mb-4">
        <div>
          <p className="text-lg font-bold text-gray-800">
            Credit Load: <span className="font-normal text-gray-600">{plan.totalCredits} Credit Hours</span>
          </p>
          <p className="text-lg font-bold text-gray-800">
            Semester Difficulty: <span className="font-normal text-gray-600">{preferences.difficulty}</span>
          </p>
        </div>
        <div className="flex flex-col space-y-3">
          <button className="px-6 py-3 bg-[#4C3B6F] text-white font-bold rounded-full hover:bg-[#392d57] transition-all">
            Confirm Semester Plan
          </button>
          <button 
            onClick={onGenerateNew}
            className="px-6 py-3 bg-gray-200 text-gray-700 font-bold rounded-full hover:bg-gray-300 transition-all"
          >
            Generate New Plan
          </button>
        </div>
      </div>
    </div>
  );
}