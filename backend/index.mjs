import express from "express";
import cors from "cors";
import dotenv from "dotenv";
import { sophosChat} from "./sophosChatHandler.js";

dotenv.config();

const app = express();
app.use(cors());
app.use(express.json());

app.get("/", (req, res) => {
    res.json({ message: "Welcome to the Sophos Chat API" });
});

app.post("/sophos-chat", async (req, res) => {
    try {
        const { query } = req.body;
        if (!query) {
            return res.status(400).json({ error: "Query is required" });
        }

        const response = await sophosChat(query);
        res.json({ response });
    } catch (error) {
        console.error("Error handling /sophos-chat:", error);
        res.status(500).json({ error: "Internal Server Error" });
    }
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});