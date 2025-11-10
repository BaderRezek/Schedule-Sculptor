import React from "react";
import { CourseItem, CourseListHeader } from "./CourseComponents";

export default function InProgressView({ data }) {
    const courses = data?.inProgressCourses || [];

    if (courses.length === 0)
        return <p className="text-gray-500 text-center">No courses in progress.</p>;

    return (
    <div className="w-full">
        <h3 className="text-xl font-semibold mb-4 text-[#9A8FB8]">In Progress</h3>
        
        {/* Add the header */}
        <CourseListHeader />

        {/* Map over the courses and render a CourseItem for each one */}
        <div className="space-y-1 mt-2">
            {courses.map((course, i) => (
            <CourseItem
                key={i}
                term={course.semester || "N/A"}
                code={course.code || "N/A"}
                credits={parseFloat(course.credits) || 0}
                grade="IP" // Hardcode "IP" for "In Progress"
                title={course.title || ""}
            />
            ))}
        </div>
    </div>
    );
}
