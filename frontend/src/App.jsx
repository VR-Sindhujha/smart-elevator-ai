import { useState } from "react";
import "./App.css";

const requests = [
  { floor: 3, pcs: 0.97, qfi: 0.2, dbos: 0.55, action: "WAIT" },
  { floor: 5, pcs: 0.82, qfi: 0.6, dbos: 0.59, action: "WAIT" },
  { floor: 7, pcs: 0.45, qfi: 0.8, dbos: 0.39, action: "STOP" },
];

function App() {
  const [currentFloor, setCurrentFloor] = useState(1);
  const [selectedFloor] = useState(5);
  const [running, setRunning] = useState(false);
  const [status, setStatus] = useState("READY");

  const runSimulation = () => {
    setRunning(true);
    setStatus("🧠 AI DECISION → FLOOR 5");

    let floor = 1;
    const target = 5;

    const interval = setInterval(() => {
      floor++;

      setCurrentFloor(floor);
      setStatus(`🛗 ELEVATOR MOVING → FLOOR ${floor}`);

      if (floor >= target) {
        clearInterval(interval);

        setTimeout(() => {
          setRunning(false);
          setStatus("✓ REQUEST SERVED");
        }, 800);
      }
    }, 500);
  };

  return (
    <div className="app">

      {/* HEADER */}
      <header className="header">
        <div>
          <div className="logo">
            🛗 <span>ADAPTIVE AI ELEVATOR</span>
          </div>

          <p className="subtitle">
            Intent-Aware Smart Elevator Dispatch System
          </p>
        </div>

        <div className="status">
          <span className="status-dot"></span>
          SYSTEM ONLINE
        </div>
      </header>


      {/* MAIN DASHBOARD */}
      <main className="dashboard">

        {/* LEFT — ELEVATOR SIMULATION */}
        <section className="card elevator-card">

          <div className="card-title">
            <span>🛗</span>
            LIVE ELEVATOR SIMULATION
          </div>

          <div className="elevator-area">

            <div className="floors">

              {[10, 9, 8, 7, 6, 5, 4, 3, 2, 1].map((floor) => (

                <div
                  key={floor}
                  className={`floor ${
                    currentFloor === floor ? "active-floor" : ""
                  }`}
                >

                  <span>FLOOR {floor}</span>

                  {/* PASSENGERS */}
                  {floor === 3 && (
                    <span className="passengers">
                      👤 →
                    </span>
                  )}

                  {floor === 5 && (
                    <span className="passengers">
                      👤 →
                    </span>
                  )}

                  {floor === 7 && (
                    <span className="passengers">
                      👥
                    </span>
                  )}

                  {/* ELEVATOR */}
                  {currentFloor === floor && (
                    <div className="lift">

                      <div className="lift-door left"></div>

                      <div className="lift-door right"></div>

                      <span>🛗</span>

                    </div>
                  )}

                </div>

              ))}

            </div>

          </div>


          {/* ELEVATOR INFORMATION */}
          <div className="elevator-info">

            <div>
              <span>Current Floor</span>
              <strong>{currentFloor}</strong>
            </div>

            <div>
              <span>Target Floor</span>
              <strong>{selectedFloor}</strong>
            </div>

            <div>
              <span>Capacity</span>
              <strong>6 / 12</strong>
            </div>

          </div>

        </section>


        {/* RIGHT SIDE */}
        <section className="right-column">


          {/* AI DECISION ENGINE */}
          <div className="card decision-card">

            <div className="card-title">
              <span>🧠</span>
              AI DECISION ENGINE
            </div>


            <div className="decision-main">

              <div className="selected-floor">

                <span>SELECTED FLOOR</span>

                <strong>{selectedFloor}</strong>

              </div>

              <div className="action-badge">
                WAIT
              </div>

            </div>


            {/* METRICS */}
            <div className="metrics">

              {/* PCS */}
              <div className="metric">

                <span>PCS</span>

                <strong>0.82</strong>

                <div className="bar">
                  <div style={{ width: "82%" }}></div>
                </div>

              </div>


              {/* QFI */}
              <div className="metric">

                <span>QFI</span>

                <strong>0.60</strong>

                <div className="bar">
                  <div style={{ width: "60%" }}></div>
                </div>

              </div>


              {/* DBOS */}
              <div className="metric">

                <span>DBOS</span>

                <strong>0.59</strong>

                <div className="bar">
                  <div style={{ width: "59%" }}></div>
                </div>

              </div>


              {/* MWW */}
              <div className="metric">

                <span>MWW</span>

                <strong>2.0 sec</strong>

                <div className="bar">
                  <div style={{ width: "70%" }}></div>
                </div>

              </div>

            </div>

          </div>


          {/* REQUEST TABLE */}
          <div className="card">

            <div className="card-title">
              <span>📊</span>
              PENDING FLOOR REQUESTS
            </div>


            <table>

              <thead>

                <tr>
                  <th>FLOOR</th>
                  <th>PCS</th>
                  <th>QFI</th>
                  <th>DBOS</th>
                  <th>ACTION</th>
                </tr>

              </thead>


              <tbody>

                {requests.map((request) => (

                  <tr
                    key={request.floor}
                    className={
                      request.floor === selectedFloor
                        ? "selected-row"
                        : ""
                    }
                  >

                    <td>
                      <strong>{request.floor}</strong>
                    </td>

                    <td>
                      {request.pcs.toFixed(2)}
                    </td>

                    <td>
                      {request.qfi.toFixed(2)}
                    </td>

                    <td>
                      <strong>
                        {request.dbos.toFixed(2)}
                      </strong>
                    </td>

                    <td>

                      <span
                        className={`action ${request.action.toLowerCase()}`}
                      >
                        {request.action}
                      </span>

                    </td>

                  </tr>

                ))}

              </tbody>

            </table>

          </div>


          {/* MICRO WAIT WINDOW */}
          <div className="card mww-card">

            <div className="card-title">
              <span>⏳</span>
              MICRO-WAIT WINDOW
            </div>


            <div className="mww-content">

              <div className="passenger-visual">
                👤 ─────────→ 🛗
              </div>


              <div>

                <p>
                  High-commitment passenger approaching
                </p>

                <strong>
                  Estimated arrival: 2.0 seconds
                </strong>

              </div>


              <div className="wait-badge">
                WAIT 2 SEC
              </div>

            </div>

          </div>


          {/* SIMULATION BUTTON */}
          <button
            className="run-button"
            onClick={runSimulation}
            disabled={running}
          >
            {status}
          </button>

        </section>

      </main>


      {/* FOOTER */}
      <footer>

        <div>

          <strong>AI MODULES</strong>

          <span>PCS</span>
          <span>QFI</span>
          <span>DBOS</span>
          <span>MWW</span>

        </div>


        <div>
          REVIEW 1 • SOFTWARE PROTOTYPE
        </div>

      </footer>

    </div>
  );
}

export default App;