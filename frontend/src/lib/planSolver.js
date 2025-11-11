/**
 * A simple, synchronous plan generator.
 * It finds courses that match the criteria and haven't been taken.
 */
export function generatePlan(preferences, parsedAudit, courseCatalog) {
  const { requirements, creditLoad, difficulty } = preferences;
  
  // 1. Get lists of courses the user has already taken or is taking.
  const completedCodes = (parsedAudit?.completedCourses || []).map(c => c.code);
  const inProgressCodes = (parsedAudit?.inProgressCourses || []).map(c => c.code);
  const takenCodes = new Set([...completedCodes, ...inProgressCodes]);

  // 2. Get the specific course codes from the user's remaining requirements
  // that match the categories they selected.
  const requiredCourseCodes = new Set();
  (parsedAudit?.remainingRequirements || []).forEach(req => {
    if (requirements.includes(req.category)) {
      (req.courses || []).forEach(course => {
        requiredCourseCodes.add(course.code);
      });
    }
  });

  // 3. Filter the master course catalog to find all possible courses
  const allPossibleCourses = (courseCatalog || []).filter(course => {
    // Check if the course is one of the ones that can fulfill a selected requirement
    const fulfillsRequirement = requiredCourseCodes.has(course.code);
    
    // Check if the course has already been taken
    const hasBeenTaken = takenCodes.has(course.code);

    const hasPrereqs = checkPrerequisites(course.prereqs, completedCodes);
    
    return fulfillsRequirement && !hasBeenTaken && hasPrereqs;
  });
  
  // For now, we just shuffle the array to give a different result each time
  const shuffledCourses = allPossibleCourses.sort(() => 0.5 - Math.random());

  // 4. Build the plan
  const suggestedPlan = [];
  let currentCredits = 0;
  
  // Get the credit load target (e.g., the max of [15])
  const maxCredits = Math.max(...creditLoad);

  for (const course of shuffledCourses) {
    if (currentCredits + course.credits <= maxCredits) {
      suggestedPlan.push(course);
      currentCredits += course.credits;
    }
    
    // Stop if we have a reasonable number of courses
    if (suggestedPlan.length >= 5 || currentCredits >= maxCredits) {
      break;
    }
  }

  return {
    plan: suggestedPlan,
    totalCredits: currentCredits,
    criteria: {
    selectedRequirements: requirements,
    creditLoad: maxCredits,
    excludedCourses: [...takenCodes],
    }
  };
}


// Checks whether the user has completed all prerequisites for a given course.
function checkPrerequisites(prereqCodes, completedCodes) {
  if (!prereqCodes || prereqCodes.length === 0) {
    return true; // No prerequisites
  }

  return prereqCodes.every(code => completedCodes.includes(code));
}