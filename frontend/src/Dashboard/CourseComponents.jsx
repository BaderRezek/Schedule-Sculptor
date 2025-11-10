import React from "react";

export const CourseItem = React.memo(({ term, code, credits, grade, title }) => (
    <div className="flex justify-between items-center text-center border-b border-gray-200 py-3 text-gray-800 text-sm">
        <div className="flex space-x-8 items-center">
            {/* Term */}
            <span className="w-16 font-medium">{term}</span>
            {/* Code */}
            <span className="w-20 font-medium">{code}</span>
            {/* Credits */}
            <span className="w-12">{credits.toFixed(2)}</span>
            {/* Grade */}
            <span
            className={`w-8 font-semibold ${
                grade === "IP" ? "text-blue-500" : "text-gray-700"
            }`}
            >
            {grade}
            </span>
        </div>
        {/* Title */}
        <span className="flex-1 italic truncate ml-4">{title}</span>
    </div>
));

export const CourseListHeader = () => (
    <div className="flex justify-between items-center text-center border-b-2 border-gray-400 pb-2 text-gray-500 text-xs font-bold uppercase tracking-wider">
        <div className="flex space-x-8 items-center">
            <span className="w-16">Term</span>
            <span className="w-20">Code</span>
            <span className="w-12">Credits</span>
            <span className="w-8">Grade</span>
        </div>
        <span className="flex-1 text-center italic truncate ml-4">Title</span>
    </div>
);