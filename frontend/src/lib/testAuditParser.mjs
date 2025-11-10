// frontend/src/lib/testAuditParser.mjs

import 'dotenv/config';
import { parseAuditPDF } from "./auditParser.js";

async function main() {
    try {
        const pdfPath = "./test_audit.pdf"; // Path to a sample degree audit PDF
        console.log("Extracting and parsing audit...");
        const result = await parseAuditPDF(pdfPath);
        console.log("✅ Parsed audit result:");
        console.dir(result, { depth: null });
    } catch (err) {
        console.error("❌ Test failed:", err);
    }
}

main();