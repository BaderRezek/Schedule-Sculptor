import React from "react";

export default function RemainingView({ data }) {
    const remaining = data?.remainingRequirements || [];

    if (remaining.length === 0)
        return <p className="text-gray-500 text-center">All requirements complete — great job!</p>;

    return (
    <div>
        <h3 className="text-xl font-semibold mb-4 text-gray-600">Remaining Requirements</h3>
        <ul className="space-y-4">
            {remaining.map((req, i) => (
                <li key={i} className="border p-3 rounded-lg bg-gray-50">
                <p className="font-medium">{req.category}</p>
                <p className="text-sm text-gray-600">
                    Courses needed: {req.coursesNeeded}
                </p>
                {req.courses?.length > 0 && (
                    <ul className="ml-4 mt-2 list-disc text-gray-700 text-sm">
                    {req.courses.map((course, j) => (
                        <li key={j}>
                        {course.code} — {course.title} ({course.credits} cr)
                        </li>
                    ))}
                    </ul>
                )}
                </li>
            ))}
        </ul>
    </div>
    );
}
