# Digital Twins Platform - Frontend

A modern React frontend for the Digital Twins Industrial IoT Platform.

## Tech Stack

- **React 18** - UI Framework
- **TypeScript** - Type Safety
- **Vite** - Build Tool & Dev Server
- **Three.js / React Three Fiber** - 3D Visualization
- **Recharts** - Data Visualization
- **Tailwind CSS** - Styling
- **React Router** - Routing

## Prerequisites

- Node.js 18+ 
- npm or yarn

## Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Environment Variables

Create a `.env` file in the root directory:

```env
VITE_API_URL=http://localhost:8000/api
VITE_WS_URL=ws://localhost:8000/ws
VITE_USE_MOCK=true
```

## Project Structure

```
src/
├── components/        # Reusable UI components
│   ├── Layout.tsx     # Main layout with sidebar
│   ├── StatusBadge.tsx
│   └── TwinCard.tsx
├── data/              # Mock data for development
│   └── mockData.ts
├── hooks/             # Custom React hooks
│   └── index.ts
├── pages/             # Page components
│   ├── Dashboard.tsx  # Main dashboard with KPIs
│   ├── TwinList.tsx   # List/grid of twins
│   ├── TwinDetail.tsx # 3D viewer + sensors
│   └── Analytics.tsx  # AI-powered insights
├── services/          # API and WebSocket services
│   └── api.ts
├── types/             # TypeScript type definitions
│   └── index.ts
├── utils/             # Utility functions
│   └── index.ts
├── App.tsx            # Main app component
├── main.tsx           # Entry point
└── index.css          # Global styles
```

## Features

- **Real-time Monitoring**: Live sensor data updates via WebSocket
- **3D Visualization**: Interactive 3D models of industrial equipment
- **AI Analytics**: Predictive maintenance and anomaly detection insights
- **Responsive Design**: Mobile-first approach with dark theme
- **Industrial Aesthetic**: Professional UI with technical look

## API Integration

The frontend connects to a FastAPI backend at `/api`. When the backend is not available, it uses mock data for development.

### WebSocket Events

- `sensor_update` - Real-time sensor values
- `status_change` - Twin status changes
- `alert` - New alerts

## Pages

1. **Dashboard** (`/`) - Overview with KPIs, charts, twin list
2. **Twin List** (`/twins`) - Searchable/filterable list of twins
3. **Twin Detail** (`/twins/:id`) - 3D viewer, sensors, controls
4. **Analytics** (`/analytics`) - AI insights, predictions, maintenance schedule

## License

MIT
