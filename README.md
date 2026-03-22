# PTA Simulator

A high-fidelity Pure Tone Audiometry (PTA) simulator for audiology students and researchers.

## Features

- **Virtual Patient Generator**: Generates patients based on real clinical hearing patterns.
- **Realistic Response Engine**: Simulates human-like responses with variability and clinical masking requirements (Interaural Attenuation, Cross-over).
- **Interactive Simulator Interface**: Professional UI matching standard clinical audiometers.
- **Dynamic Audiogram Charting**: Real-time plotting of clinical symbols (O, X, <, >, etc.).
- **Automated Evaluation**: Assesses threshold accuracy and adherence to testing protocols (e.g., "Up 5, Down 10").

## Setup and Running

### Backend (FastAPI)

1. **Install Dependencies**:
   ```bash
   pip install -r backend/requirements.txt
   ```

2. **Initialize and Seed Database**:
   ```bash
   PYTHONPATH=. python3 -m backend.init_db
   PYTHONPATH=. python3 -m backend.seed_data
   ```

3. **Run the Server**:
   ```bash
   uvicorn backend.main:app --reload --port 8000
   ```

### Frontend (React + Vite)

1. **Install Dependencies**:
   ```bash
   cd frontend
   npm install
   ```

2. **Run Development Server**:
   ```bash
   npm run dev
   ```

3. Access the application at `http://localhost:5173`.

## Utility Scripts

- **View All Patients**:
  ```bash
  PYTHONPATH=. python3 -m backend.show_patients
  ```
- **Run Backend Tests**:
  ```bash
  PYTHONPATH=. python3 -m backend.tests
  ```
