import 'dotenv/config'; 
import express from 'express';
import { PrismaClient } from '@prisma/client';
import jwt from 'jsonwebtoken';

import dotenv from 'dotenv';
dotenv.config();

console.log("ENV:", process.env.DATABASE_URL);

const app = express();
// Pass the URL explicitly to the constructor to be 100% sure it's loaded
const prisma = new PrismaClient();
const PORT = process.env.PORT || 3001;
const JWT_SECRET = process.env.JWT_SECRET || 'change_this_in_production';

app.use(express.json());

// --- 1. Public Route: Login ---
app.post('/api/auth/login', async (req, res) => {
    const { password } = req.body;
    if (password === process.env.ADMIN_PASSWORD) {
        const token = jwt.sign({ role: 'admin' }, JWT_SECRET, { expiresIn: '7d' });
        return res.json({ token });
    }
    res.status(401).json({ message: 'Unauthorized' });
});

// --- 2. Middleware ---
const authenticateJWT = (req: any, res: any, next: any) => {
    const token = req.headers.authorization?.split(' ')[1];
    if (!token) return res.status(401).send('Missing token');

    jwt.verify(token, JWT_SECRET, (err: any, user: any) => {
        if (err) return res.status(403).send('Invalid token');
        req.user = user;
        next();
    });
};

// --- 3. Protected Route ---
app.get('/api/parking/latest', authenticateJWT, async (req, res) => {
    try {
        const latest = await prisma.messages.findFirst({
            orderBy: { timestamp: 'desc' },
        });
        res.json(latest);
    } catch (error) {
        console.error("DB Error:", error);
        res.status(500).json({ error: "Failed to fetch data" });
    }
});

app.listen(PORT, () => {
    console.log(`🚀 API running on http://localhost:${PORT}`);
});