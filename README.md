# NFL Fantasy Project

This project is a full-stack web application for managing NFL fantasy teams. It uses FastAPI (Python) for the backend and React (TypeScript, Vite) for the frontend.

---

## Backend Setup (FastAPI)

1. **Install Python dependencies**

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

2. **Run the backend server**

```powershell
uvicorn src.main:app --reload --host localhost
```

- The API will be available at: `http://localhost:8000`
- Hot-reload is enabled for development.

---

## Frontend Setup (React + Vite)

1. **Install Node dependencies**

```powershell
cd frontend\nfl_fantasy_frontend
npm install
```

2. **Run the frontend dev server**

```powershell
npm run dev
```

- The app will be available at: `http://localhost:5173`
- The frontend is configured to communicate with the backend at `http://localhost:8000`.

---

## Build Frontend for Production

```powershell
npm run build
```
- Output will be in the `dist/` folder.

---

## Project Structure

```
backend/
	src/
		main.py
		config/
		core/
		modules/
			users/
			teams/
frontend/
	nfl_fantasy_frontend/
		src/
			features/
			shared/
			services/
			...
```

---

## Common Issues
- If you see `ModuleNotFoundError` in backend, ensure you run `uvicorn src.main:app` from the `backend` folder and all imports use package-relative paths.
- If frontend cannot reach backend, check that `src/services/apiService.ts` uses the correct baseURL (`http://localhost:8000`).
- For CORS errors, ensure backend allows `http://localhost:5173` in `CORSMiddleware`.

---

## Environment Variables
- For production, use `.env` files to store secrets and API URLs.

