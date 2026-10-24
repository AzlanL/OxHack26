
import { useState } from "react";
import "./App.css";

const INITIAL_ROBOTS = [
  { id: 1, x: 1, y: 2, color: "#3b82f6" },
  { id: 2, x: 6, y: 2, color: "#22c55e" },
  { id: 3, x: 8, y: 7, color: "#f59e0b" },
];

const API_URL = "http://localhost:8000";

export default function App() {
  const [robots, setRobots] = useState(INITIAL_ROBOTS);
  const [messes, setMesses] = useState([]);
  const [totalCost, setTotalCost] = useState(0);
  const [offlineCost, setOfflineCost] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleMapClick(event) {
    if (loading) return;

    // Convert mouse position to coordinates in [0, 10].
    const rect = event.currentTarget.getBoundingClientRect();

    const x = ((event.clientX - rect.left) / rect.width) * 10;
    const y = ((event.clientY - rect.top) / rect.height) * 10;

    const mess = { x, y };

    setLoading(true);
    setError("");
    setMesses((previous) => [...previous, mess]);

    try {
      const response = await fetch(`${API_URL}/mess`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(mess),
      });

      if (!response.ok) {
        throw new Error(`Backend returned ${response.status}`);
      }

      const step = await response.json();

      console.log("WFA decision:", step);

      // Move the robot selected by WFA.
      if (step.moved_from !== null) {
        setRobots((previous) =>
          previous.map((robot) => {
            const isSelected =
              robot.x === step.moved_from[0] &&
              robot.y === step.moved_from[1];

            if (!isSelected) return robot;

            return {
              ...robot,
              x: step.moved_to[0],
              y: step.moved_to[1],
            };
          })
        );
      }

      setTotalCost(step.total_cost);
      setOfflineCost(step.offline_optimum_so_far);

      // Allow the robot animation to finish.
      await new Promise((resolve) => setTimeout(resolve, 650));

      // Remove the cleaned mess.
      setMesses((previous) =>
        previous.filter((item) => item !== mess)
      );
    } catch (err) {
      console.error(err);
      setError(err.message);
      setMesses((previous) =>
        previous.filter((item) => item !== mess)
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app">
      <header>
        <h1>Airport Robovac</h1>
        <p>Online k-server optimisation using WFA</p>
      </header>

      <div className="dashboard">
        <div className="stat">
          <span>WFA Travel Distance</span>
          <strong>{totalCost.toFixed(2)}</strong>
        </div>

        <div className="stat">
          <span>Offline Optimum</span>
          <strong>{offlineCost.toFixed(2)}</strong>
        </div>
      </div>

      <div className="map" onClick={handleMapClick}>
        <span className="map-label">AIRPORT TERMINAL</span>

        {robots.map((robot) => (
          <div
            key={robot.id}
            className="robot"
            style={{
              left: `${robot.x * 10}%`,
              top: `${robot.y * 10}%`,
              backgroundColor: robot.color,
            }}
          >
            {robot.id}
          </div>
        ))}

        {messes.map((mess, index) => (
          <div
            key={index}
            className="mess"
            style={{
              left: `${mess.x * 10}%`,
              top: `${mess.y * 10}%`,
            }}
          >
            ✕
          </div>
        ))}
      </div>

      <p className="instructions">
        {loading
          ? "Robot is cleaning..."
          : "Click anywhere on the map to generate a mess."}
      </p>

      {error && <p className="error">{error}</p>}
    </div>
  );
}

