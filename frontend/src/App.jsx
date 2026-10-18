import { useEffect, useState } from "react";

import "./App.css";

const API_URL = "http://127.0.0.1:8000";

const initialRequests = [];

const demoPerformance = {

  waitingTime: 0.47,

  travelDistance: 5,

  serviceRate: 100,

  utilization: 12.5,

  fairness: 50,

  emergencyResponse: 2.0,

};



function AIExplanationPanel({ active, displayedMww, showEmergency, selectedElevator }) {

  const [selectedMechanism, setSelectedMechanism] = useState("PCS");



  const mechanisms = {

    PCS: {

      title: "Passenger Commitment Score",

      question: "What does this score tell us?",

      steps: [

        "The backend receives the selected floor request and its passenger-related inputs.",

        "The backend calculates PCS using the formula implemented in the Python code.",

        "The returned score is displayed here and can be compared with the dispatch decision."

      ],

      note: "The exact formula and weights are not shown until they are verified against the backend implementation."

    },

    QFI: {

      title: "Queue Fairness Index",

      question: "Has this request been skipped repeatedly?",

      steps: [

        `Skip count provided for this request: ${active?.input?.skipped ?? "not available"}.`,

        "Recorded project rule: QFI = min(skip count / 5, 1.0).",

        "At QFI ≥ 0.80, the recorded fairness rule selects STOP."

      ],

      note: "This explanation reflects the recorded project rule. The live score shown above comes from the selected request's available result."

    },

    DBOS: {

      title: "Dynamic Boarding Opportunity Score",

      question: "Is stopping at this floor worthwhile?",

      steps: [

        "The backend evaluates the request using its implemented DBOS calculation.",

        "The score returned by the backend is displayed below.",

        "The dispatch logic applies the project's decision thresholds and fairness override."

      ],

      note: "Exact DBOS weights and contributions must be read from the backend implementation; this panel does not invent them."

    },

    MWW: {

      title: "Micro-Wait Window",

      question: "Should the elevator briefly wait for the passenger?",

      steps: [

        `Estimated passenger arrival: ${Number(displayedMww?.arrival_time ?? 0).toFixed(2)} seconds.`,

        `Recommendation returned by the available result: ${displayedMww?.recommendation ?? "not available"}.`,

        `Wait duration: ${Number(displayedMww?.wait_duration ?? 0).toFixed(2)} seconds.`

      ],

      note: "These values are taken from the selected request's available API result. They are not a separate prediction made by the frontend."

    },

    EMERGENCY: {

      title: "Emergency Dispatch",

      question: "How does the software respond to an emergency request?",

      steps: [

        "The frontend sends an emergency request to the emergency-dispatch API.",

        `Elevator selected in the current dashboard: ${selectedElevator}.`,

        "The twin animates the selected elevator toward the emergency floor after the API responds."

      ],

      note: "This is a software simulation. It does not control a physical elevator. The actual selection rule should be explained from the emergency endpoint's implementation."

    }

  };



  const current = mechanisms[selectedMechanism];



  return (

    <section className="card ai-explainer">

      <div className="card-title">

        <span>🧠</span>

        UNDERSTAND THE AI

      </div>

      <p className="explainer-intro">

        Select a mechanism to learn what it does, what information it uses,

        and how its result relates to the elevator decision.

      </p>

      <div className="explainer-tabs">

        {Object.keys(mechanisms).map((key) => (

          <button

            key={key}

            type="button"

            className={`explainer-tab ${selectedMechanism === key ? "explainer-tab-active" : ""}`}

            onClick={() => setSelectedMechanism(key)}

          >

            {key}

          </button>

        ))}

      </div>

      <div className="explainer-content">

        <h3>{current.title}</h3>

        <p className="explainer-question">{current.question}</p>

        <h4>How it works</h4>

        <ol>

          {current.steps.map((step, index) => (

            <li key={`${selectedMechanism}-${index}`}>{step}</li>

          ))}

        </ol>

        <div className="explainer-result">

          <span>Selected request · Floor {active?.floor ?? "—"}</span>

          <strong>

            {selectedMechanism === "PCS" &&

              (typeof active?.pcs === "number" ? active.pcs.toFixed(2) : "Not available")}

            {selectedMechanism === "QFI" &&

              (typeof active?.qfi === "number" ? active.qfi.toFixed(2) : "Not available")}

            {selectedMechanism === "DBOS" &&

              (typeof active?.dbos === "number" ? active.dbos.toFixed(2) : "Not available")}

            {selectedMechanism === "MWW" && (displayedMww?.recommendation ?? "Not available")}

            {selectedMechanism === "EMERGENCY" && (showEmergency ? "EMERGENCY ACTIVE" : "Emergency demo")}

          </strong>

        </div>

        <p className="explainer-note">{current.note}</p>

      </div>

    </section>

  );

}



const sleep = (ms) =>

  new Promise((resolve) => setTimeout(resolve, ms));

function App() {

  const [currentFloor, setCurrentFloor] = useState(1);

  // Elevator positions are initialized from the live backend state.

  const [elevatorFloors, setElevatorFloors] = useState({ E1: 1, E2: 1 });

  const [elevatorStates, setElevatorStates] = useState({});



  // Load both elevator states from FastAPI when the dashboard opens.

  const refreshElevatorState = async () => {

    try {

      const response = await fetch(`${API_URL}/elevators`, {

        headers: { Accept: "application/json" },

      });

      if (!response.ok) throw new Error(`Elevator state API returned HTTP ${response.status}`);

      const data = await response.json();

      const elevators = data.elevators;

      if (!elevators?.E1 || !elevators?.E2) {

        throw new Error("The elevator API did not return both E1 and E2.");

      }

      setElevatorStates(elevators);

      setElevatorFloors({

        E1: Number(elevators.E1.current_floor),

        E2: Number(elevators.E2.current_floor),

      });

      setApiConnected(true);

      setApiError("");

      return elevators;

    } catch (error) {

      setApiError(`${error.message}. Check that FastAPI is running at ${API_URL}.`);

      return null;

    }

  };



  useEffect(() => {

    refreshElevatorState();

    // Refresh only on mount; movement also updates state during animation.

    // eslint-disable-next-line react-hooks/exhaustive-deps

  }, []);

  const [selectedFloor, setSelectedFloor] = useState(3);

  const [selectedElevator, setSelectedElevator] = useState("E1");

  const [running, setRunning] = useState(false);

  const [status, setStatus] = useState("READY");

  const [activeRequest, setActiveRequest] = useState(0);

  const [showEmergency, setShowEmergency] = useState(false);

  const [requestResults, setRequestResults] =

    useState(initialRequests);

  const [apiLoading, setApiLoading] = useState(false);

  const [apiError, setApiError] = useState("");

  const [apiConnected, setApiConnected] = useState(false);

  const [mwwResult, setMwwResult] = useState(null);

  const [scenarioName, setScenarioName] = useState("Ready to demonstrate");

  const [scenarioExplanation, setScenarioExplanation] = useState("Choose a scenario to watch the digital twin respond.");

  // Call the real Python AI API for a normal floor request.

  const evaluateFloor = async (request) => {

    setApiLoading(true);

    setApiError("");

    try {

      const response = await fetch(`${API_URL}/evaluate`, {

        method: "POST",

        headers: {

          "Content-Type": "application/json",

          Accept: "application/json",

        },

        body: JSON.stringify({

          floor: request.floor,

          ...request.input,

        }),

      });

      if (!response.ok) {

        throw new Error(`API returned HTTP ${response.status}`);

      }

      const data = await response.json();

      setApiConnected(true);

      setRequestResults((previous) =>

        previous.map((item) =>

          item.floor === request.floor

            ? {

                ...item,

                pcs: data.pcs,

                qfi: data.qfi,

                dbos: data.dbos,

                action: data.decision,

                apiData: data,

              }

            : item

        )

      );

      setMwwResult(data.mww);

      return data;

    } catch (error) {

      setApiConnected(false);

      setApiError(

        `${error.message}. Check that FastAPI is running at ${API_URL}.`

      );

      return null;

    } finally {

      setApiLoading(false);

    }

  };

  // Ask FastAPI to update the shared elevator state, then animate the UI.

  const animateElevator = async (

    startFloor,

    targetFloor,

    elevatorId,

    emergency = false

  ) => {

    const response = await fetch(`${API_URL}/elevators/move`, {

      method: "POST",

      headers: {

        "Content-Type": "application/json",

        Accept: "application/json",

      },

      body: JSON.stringify({

        elevator_id: elevatorId,

        target_floor: targetFloor,

      }),

    });

    if (!response.ok) {

      throw new Error(`Elevator movement API returned HTTP ${response.status}`);

    }

    const movementData = await response.json();

    if (movementData.status !== "success") {

      throw new Error(movementData.message || "Elevator movement failed.");

    }

    const actualStartFloor = Number(

      startFloor ?? elevatorStates[elevatorId]?.current_floor

    );

    const step = targetFloor >= actualStartFloor ? 1 : -1;

    setCurrentFloor(actualStartFloor);

    setElevatorFloors((previous) => ({ ...previous, [elevatorId]: actualStartFloor }));

    for (let floor = actualStartFloor; floor !== targetFloor; floor += step) {

      await sleep(450);

      const nextFloor = floor + step;

      setCurrentFloor(nextFloor);

      setElevatorFloors((previous) => ({ ...previous, [elevatorId]: nextFloor }));

      setStatus(

        emergency

          ? `🚨 ${elevatorId} EMERGENCY → FLOOR ${nextFloor}`

          : `🛗 ${elevatorId} MOVING → FLOOR ${nextFloor}`

      );

    }

    setCurrentFloor(targetFloor);

    setElevatorFloors((previous) => ({ ...previous, [elevatorId]: targetFloor }));

    await sleep(250);

    // Re-read the backend after movement so the twin reflects the API state.

    await refreshElevatorState();

    return movementData.state;

  };

  // Emergency is a standalone scenario. Normal traffic scenarios never invoke it.
  const runSimulation = async () => {
    if (running) return;
    setRunning(true);
    setApiLoading(true);
    setApiError("");
    setApiConnected(false);
    setShowEmergency(false);
    setMwwResult(null);
    setRequestResults([]);
    setActiveRequest(0);
    setStatus("🚨 RUNNING EMERGENCY-ONLY SCENARIO...");
    setScenarioName("EMERGENCY (F9)");
    setScenarioExplanation("Standalone emergency test: normal PCS/QFI/DBOS dispatch is bypassed; the nearest available elevator is selected for Floor 9.");

    try {
      const stateResponse = await fetch(`${API_URL}/elevators`, {
        headers: { Accept: "application/json" },
      });
      if (!stateResponse.ok) throw new Error(`Elevator state API returned HTTP ${stateResponse.status}`);
      const stateData = await stateResponse.json();
      const live = stateData.elevators;

      const emergencyResponse = await fetch(`${API_URL}/emergency-dispatch`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify({
          emergency_floor: 9,
          elevators: ["E1", "E2"].map((id) => ({
            elevator_id: id,
            current_floor: Number(live[id].current_floor),
            available: !live[id].is_moving && Number(live[id].available_capacity ?? 1) > 0,
          })),
        }),
      });
      if (!emergencyResponse.ok) throw new Error(`Emergency API returned HTTP ${emergencyResponse.status}`);
      const result = await emergencyResponse.json();
      if (result.status !== "success" || !result.selected_elevator) {
        throw new Error(result.message || "No available elevator for emergency dispatch.");
      }

      const id = result.selected_elevator;
      const emergencyFloor = Number(result.emergency_floor);
      const emergencyRow = {
        floor: emergencyFloor, type: "EMERGENCY", pcs: null, qfi: null,
        dbos: null, action: "PRIORITY", elevator: id, input: {},
      };
      // Keep emergency as its own scenario: remove every normal request row.
      setRequestResults([emergencyRow]);
      setActiveRequest(0);
      setSelectedFloor(emergencyFloor);
      setSelectedElevator(id);
      setShowEmergency(true);
      setApiConnected(true);
      setStatus(`🚨 EMERGENCY FLOOR ${emergencyFloor} → ${id} SELECTED (${result.distance} floors away)`);

      await animateElevator(Number(result.elevator_current_floor), emergencyFloor, id, true);
      setStatus(`✓ EMERGENCY SERVED BY ${id} — STANDALONE SCENARIO`);
    } catch (error) {
      setApiError(`${error.message}. Check that FastAPI is running at ${API_URL}.`);
      setStatus("⚠ EMERGENCY SCENARIO ERROR");
    } finally {
      setApiLoading(false);
      setRunning(false);
    }
  };

  const runScenario = async (scenario) => {
    if (running) return;
    const request = (floor, input) => ({ floor, input });
    const common = {
      button: true, walking_speed: 1.0, facing: 0.8,
      speed: 0.7, direction: 0.7, distance: 0.7,
      waiting: 0.5, capacity: 0.7, skipped: 1, energy: 0.3, door: 0.1,
    };
    const scenarios = {
      low: {
        name: "LOW TRAFFIC",
        explanation: "A small number of floor requests are evaluated. The twin serves the requests that the API marks STOP or WAIT.",
        requests: [
          request(3, { ...common, distance: 0.8, waiting: 0.4, skipped: 1 }),
          request(5, { ...common, distance: 0.5, waiting: 0.3, skipped: 1 }),
        ],
      },
      up_peak: {
        name: "UP-PEAK TRAFFIC",
        explanation: "Several upward-demand requests originate near the lobby. Watch the system evaluate upper-floor requests and move the cars.",
        requests: [
          request(4, { ...common, distance: 0.9, direction: 1, waiting: 0.7, skipped: 2 }),
          request(7, { ...common, distance: 0.8, direction: 1, waiting: 0.8, skipped: 3 }),
          request(8, { ...common, distance: 0.7, direction: 1, waiting: 0.6, skipped: 4 }),
        ],
      },
      down_peak: {
        name: "DOWN-PEAK TRAFFIC",
        explanation: "Requests are concentrated at upper floors with downward demand toward lower floors. Each request is evaluated by the Python API.",
        requests: [
          request(8, { ...common, distance: 0.9, direction: 0.2, waiting: 0.7, skipped: 2 }),
          request(6, { ...common, distance: 0.7, direction: 0.2, waiting: 0.8, skipped: 3 }),
          request(3, { ...common, distance: 0.5, direction: 0.2, waiting: 0.6, skipped: 4 }),
        ],
      },
      interfloor: {
        name: "INTERFLOOR TRAFFIC",
        explanation: "Requests occur at different floors rather than being concentrated at the lobby. The twin processes the requests in sequence.",
        requests: [
          request(2, { ...common, distance: 0.4, direction: 0.5, waiting: 0.4, skipped: 1 }),
          request(6, { ...common, distance: 0.7, direction: 0.5, waiting: 0.7, skipped: 2 }),
          request(4, { ...common, distance: 0.6, direction: 0.5, waiting: 0.9, skipped: 4 }),
        ],
      },
      multiple: {
        name: "MULTIPLE REQUESTS",
        explanation: "Several floors compete for service. Live PCS, QFI, DBOS and the backend action are displayed for every evaluated request.",
        requests: [
          request(3, { ...common, skipped: 1, waiting: 0.4 }),
          request(5, { ...common, skipped: 2, waiting: 0.6 }),
          request(7, { ...common, skipped: 4, waiting: 0.9 }),
        ],
      },
    };
    const plan = scenarios[scenario];
    if (!plan) return;
    setRunning(true);
    setApiLoading(true);
    setApiError("");
    setShowEmergency(false);
    setMwwResult(null);
    setRequestResults([]);
    setActiveRequest(0);
    setStatus(`🧠 STARTING ${plan.name} — NORMAL TRAFFIC ONLY`);
    try {
      setScenarioName(plan.name);
      setScenarioExplanation(plan.explanation);
      setStatus(`🧠 EVALUATING ${plan.name} REQUESTS...`);
      const evaluated = [];
      for (const item of plan.requests) {
        const response = await fetch(`${API_URL}/evaluate`, {
          method: "POST",
          headers: { "Content-Type": "application/json", Accept: "application/json" },
          body: JSON.stringify({ floor: item.floor, ...item.input }),
        });
        if (!response.ok) throw new Error(`Evaluation API returned HTTP ${response.status}`);
        const data = await response.json();
        evaluated.push({
          ...item,
          pcs: Number(data.pcs),
          qfi: Number(data.qfi),
          dbos: Number(data.dbos),
          action: data.decision,
          apiData: {
            ...data,
            mww: typeof data.mww === "string"
              ? { arrival_time: 0, recommendation: data.mww, wait_duration: 0 }
              : (data.mww ?? { arrival_time: 0, recommendation: "NO WAIT", wait_duration: 0 }),
          },
          type: "NORMAL",
        });
      }
      setApiConnected(true);
      setRequestResults(evaluated);
      setActiveRequest(0);
      setSelectedFloor(evaluated[0].floor);
      setMwwResult(evaluated[0].apiData.mww);
      setStatus(`✓ ${evaluated.length} REQUESTS EVALUATED`);
      setApiLoading(false);

      // Normal scenarios ONLY: dispatch normal requests and animate the assigned car.
      // Rebalance slightly after each assignment so both cars can participate in a
      // multi-request scenario, while still accounting for current distance.
      const assignments = { E1: 0, E2: 0 };
      for (let index = 0; index < evaluated.length; index += 1) {
        const item = evaluated[index];
        setActiveRequest(index);
        setSelectedFloor(item.floor);
        setMwwResult(item.apiData.mww);
        const live = await refreshElevatorState();
        if (!live) throw new Error("Could not read live elevator positions.");
        const candidates = ["E1", "E2"].map((id) => ({
          id,
          distance: Math.abs(Number(live[id].current_floor) - item.floor),
          busy: Boolean(live[id].is_moving),
          available: Number(live[id].available_capacity ?? 1) > 0,
        })).filter((candidate) => !candidate.busy && candidate.available);
        if (!candidates.length) throw new Error("No available elevator for this normal request.");
        candidates.sort((a, b) => {
          const aCost = a.distance + assignments[a.id] * 2;
          const bCost = b.distance + assignments[b.id] * 2;
          return aCost - bCost || a.id.localeCompare(b.id);
        });
        const elevatorId = candidates[0].id;
        setSelectedElevator(elevatorId);
        setStatus(`${plan.name}: FLOOR ${item.floor} → ${item.action} (${elevatorId})`);
        if (item.action === "WAIT") await sleep(500);
        if (item.action === "STOP" || item.action === "WAIT") {
          assignments[elevatorId] += 1;
          await animateElevator(Number(live[elevatorId].current_floor), item.floor, elevatorId, false);
        } else {
          await sleep(700);
        }
      }
      setStatus(`✓ ${plan.name} COMPLETE — ${evaluated.length} REQUESTS EVALUATED`);
    } catch (error) {
      setApiError(`${error.message}. Check that FastAPI is running at ${API_URL}.`);
      setStatus("⚠ SCENARIO ERROR");
    } finally {
      setApiLoading(false);
      setRunning(false);
    }
  };

  const active = requestResults[activeRequest];

  const displayedMww =

    active?.apiData?.mww ??

    (active?.action === "WAIT"

      ? { arrival_time: 0.95, recommendation: "WAIT", wait_duration: 0.95 }

      : { arrival_time: 0, recommendation: "NO WAIT", wait_duration: 0 });

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

          {apiLoading

            ? "API PROCESSING"

            : apiConnected

              ? "PYTHON API CONNECTED"

              : "SYSTEM ONLINE"}

        </div>

      </header>

      {/* MAIN DASHBOARD */}

      <main className="dashboard">

        <section className="card scenario-card">

          <div className="card-title"><span>🎬</span> SCENARIO DEMONSTRATION MODE</div>

          <p className="scenario-intro">Choose a NORMAL traffic situation to evaluate floor requests and animate elevator service. Emergency dispatch is a separate scenario and is never run automatically by these buttons.</p>

          <div className="scenario-buttons">

            <button disabled={running} onClick={() => runScenario("low")}>LOW TRAFFIC</button>

            <button disabled={running} onClick={() => runScenario("up_peak")}>UP-PEAK</button>

            <button disabled={running} onClick={() => runScenario("down_peak")}>DOWN-PEAK</button>

            <button disabled={running} onClick={() => runScenario("interfloor")}>INTERFLOOR</button>

            <button disabled={running} onClick={() => runScenario("multiple")}>MULTIPLE REQUESTS</button>

            <button disabled={running} onClick={runSimulation}>🚨 EMERGENCY (F9)</button>

          </div>

          <div className="scenario-explanation"><strong>{scenarioName}</strong><p>{scenarioExplanation}</p><span>Live positions: E1 Floor {elevatorFloors.E1} · E2 Floor {elevatorFloors.E2}</span></div>

        </section>

        {/* LEFT: ELEVATOR SIMULATION */}

        <section className="card elevator-card">

          <div className="card-title">

            <span>🛗</span>

            LIVE ELEVATOR SIMULATION

          </div>

          <div className="elevator-area twin-building">

            <div className="twin-heading">

              <span>BUILDING ELEVATION · 10 FLOORS</span>

              <span className="twin-live-dot">● SIMULATION VIEW</span>

            </div>

            <div className="twin-grid">

              <div className="floor-label-column">

                {[10, 9, 8, 7, 6, 5, 4, 3, 2, 1].map((floor) => (

                  <div className={`twin-floor-label ${selectedFloor === floor ? "requested-floor-label" : ""}`} key={floor}>F{floor}</div>

                ))}

              </div>

              {["E1", "E2"].map((id) => (

                <div className="shaft-column" key={id}>

                  <div className="shaft-title">

                    {id}

                    {selectedElevator === id && <span className="shaft-selected">ACTIVE</span>}

                  </div>

                  <div className="shaft">

                    {[10, 9, 8, 7, 6, 5, 4, 3, 2, 1].map((floor) => {

                      const isCarHere = elevatorFloors[id] === floor;

                      const hasRequest = requestResults.some((request) => request.floor === floor);

                      return (

                        <div className={`shaft-floor ${selectedFloor === floor ? "shaft-target-floor" : ""}`} key={floor}>

                          <span className="shaft-floor-line" />

                          {hasRequest && <span className={`twin-request ${requestResults.some((request) => request.floor === floor && request.type === "EMERGENCY") ? "emergency-marker" : ""}`} title={requestResults.some((request) => request.floor === floor && request.type === "EMERGENCY") ? "Emergency request" : `Request at floor ${floor}`}>{requestResults.some((request) => request.floor === floor && request.type === "EMERGENCY") ? "🚨" : "●"}</span>}

                          {isCarHere && <div className={`twin-car ${selectedElevator === id ? "car-active" : ""}`} title={`${id} at floor ${floor}`}><span>▥</span><small>{id}</small></div>}

                        </div>

                      );

                    })}

                  </div>

                  <div className="shaft-current">Current floor: <strong>{elevatorFloors[id]}</strong></div>

                  <div className="shaft-target">

                    Target: {selectedElevator === id ? selectedFloor : (elevatorStates[id]?.destinations?.[0] ?? "—")}

                  </div>

                  <div className="shaft-target">

                    {elevatorStates[id]?.is_moving ? `MOVING ${elevatorStates[id]?.direction ?? ""}` : (elevatorStates[id]?.direction ?? "IDLE")}

                    {` · ${elevatorStates[id]?.available_capacity ?? 12}/${elevatorStates[id]?.capacity ?? 12} free`}

                  </div>

                </div>

              ))}

            </div>

            <div className="twin-legend">

              <span><i className="legend-car" /> Elevator car</span>

              <span><i className="legend-request" /> Floor request</span>

              <span>🚨 Emergency floor</span>

            </div>

          </div>

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

              <span>Selected Elevator</span>

              <strong>{selectedElevator}</strong>

            </div>

          </div>

          <div className="elevator-info">

            <div>

              <span>E1 Status</span>

              <strong>

                {selectedElevator === "E1" ? "ACTIVE" : "STANDBY"}

              </strong>

            </div>

            <div>

              <span>E2 Status</span>

              <strong>

                {selectedElevator === "E2" ? "ACTIVE" : "STANDBY"}

              </strong>

            </div>

            <div>

              <span>Capacity</span>

              <strong>12</strong>

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

              <div

                className={`action-badge ${

                  active?.type === "EMERGENCY"

                    ? "emergency-action"

                    : ""

                }`}

              >

                {active?.action ?? "READY"}

              </div>

            </div>

            {showEmergency || active?.type === "EMERGENCY" ? (

              <div className="emergency-panel">

                <strong>🚨 EMERGENCY PRIORITY OVERRIDE</strong>

                <p>Normal DBOS prioritization bypassed.</p>

                <p>

                  Nearest available elevator: <strong>E2</strong>

                </p>

                <p>

                  Demonstration response:{" "}

                  <strong>{demoPerformance.emergencyResponse.toFixed(1)} sec</strong>

                </p>

                <p>

                  Emergency dispatch is connected to the FastAPI endpoint.

                </p>

              </div>

            ) : (

              <div className="metrics">

                <div className="metric">

                  <span>PCS</span>

                  <strong>

                    {active?.pcs?.toFixed(2) ?? "—"}

                  </strong>

                  <div className="bar">

                    <div

                      style={{

                        width: `${(active?.pcs ?? 0) * 100}%`,

                      }}

                    ></div>

                  </div>

                </div>

                <div className="metric">

                  <span>QFI</span>

                  <strong>

                    {active?.qfi?.toFixed(2) ?? "—"}

                  </strong>

                  <div className="bar">

                    <div

                      style={{

                        width: `${(active?.qfi ?? 0) * 100}%`,

                      }}

                    ></div>

                  </div>

                </div>

                <div className="metric">

                  <span>DBOS</span>

                  <strong>

                    {active?.dbos?.toFixed(2) ?? "—"}

                  </strong>

                  <div className="bar">

                    <div

                      style={{

                        width: `${(active?.dbos ?? 0) * 100}%`,

                      }}

                    ></div>

                  </div>

                </div>

                <div className="metric">

                  <span>MWW</span>

                  <strong>

                    {displayedMww.recommendation === "WAIT"

                      ? `${Number(displayedMww.wait_duration).toFixed(2)} sec`

                      : "NO WAIT"}

                  </strong>

                  <div className="bar">

                    <div

                      style={{

                        width:

                          displayedMww.recommendation === "WAIT"

                            ? "70%"

                            : "0%",

                      }}

                    ></div>

                  </div>

                </div>

              </div>

            )}

            {apiError && (

              <div className="emergency-panel" role="alert">

                <strong>⚠ API CONNECTION ERROR</strong>

                <p>{apiError}</p>

                <p>

                  The dashboard still shows demo values where available.

                </p>

              </div>

            )}

          </div>

          {/* REQUEST TABLE */}

          <div className="card">

            <div className="card-title">

              <span>📊</span>

              FLOOR REQUESTS

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

                {requestResults.map((request, index) => (

                  <tr

                    key={request.floor}

                    className={

                      index === activeRequest ? "selected-row" : ""

                    }

                  >

                    <td>

                      <strong>{request.floor}</strong>

                      {request.type === "EMERGENCY" && " 🚨"}

                    </td>

                    <td>

                      {typeof request.pcs === "number"

                        ? request.pcs.toFixed(2)

                        : "—"}

                    </td>

                    <td>

                      {typeof request.qfi === "number"

                        ? request.qfi.toFixed(2)

                        : "—"}

                    </td>

                    <td>

                      <strong>

                        {typeof request.dbos === "number"

                          ? request.dbos.toFixed(2)

                          : "—"}

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

          {/* MICRO-WAIT WINDOW */}

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

                <p>Passenger arrival estimate</p>

                <strong>

                  {Number(displayedMww.arrival_time).toFixed(2)} seconds

                </strong>

                <p>

                  Recommendation: {displayedMww.recommendation}

                </p>

              </div>

              <div className="wait-badge">

                {displayedMww.recommendation === "WAIT"

                  ? `WAIT ${Number(displayedMww.wait_duration).toFixed(2)} SEC`

                  : "NO WAIT"}

              </div>

            </div>

          </div>

          <AIExplanationPanel

            active={active}

            displayedMww={displayedMww}

            showEmergency={showEmergency}

            selectedElevator={selectedElevator}

          />



          {/* PERFORMANCE */}

          <div className="card">

            <div className="card-title">

              <span>📈</span>

              PERFORMANCE EVALUATION

            </div>

            <div className="metrics">

              <div className="metric">

                <span>AVG WAIT</span>

                <strong>{demoPerformance.waitingTime} sec</strong>

              </div>

              <div className="metric">

                <span>TRAVEL</span>

                <strong>{demoPerformance.travelDistance} floors</strong>

              </div>

              <div className="metric">

                <span>SERVICE RATE</span>

                <strong>{demoPerformance.serviceRate}%</strong>

              </div>

              <div className="metric">

                <span>UTILIZATION</span>

                <strong>{demoPerformance.utilization}%</strong>

              </div>

              <div className="metric">

                <span>FAIRNESS</span>

                <strong>{demoPerformance.fairness}%</strong>

              </div>

              <div className="metric">

                <span>EMERGENCY RESPONSE</span>

                <strong>{demoPerformance.emergencyResponse} sec</strong>

              </div>

            </div>

            <p style={{ padding: "0 22px 18px", color: "#8993b5", fontSize: "11px" }}>

              Demonstration metrics from the current evaluation scenario;

              not calculated by the live API.

            </p>

          </div>

          {/* RUN BUTTON */}

          <button

            className="run-button"

            onClick={runSimulation}

            disabled={running || apiLoading}

          >

            {running

              ? status

              : apiLoading

                ? "CONNECTING TO PYTHON..."

                : "🚨 RUN EMERGENCY SCENARIO"}

          </button>

          <div className="simulation-status">

            {status}

          </div>

          <div className="simulation-status">

            {apiConnected

              ? "✓ Python API connected successfully"

              : "Python API connection will be tested when simulation starts"}

          </div>

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

          <span>EMERGENCY</span>

        </div>

        <div>REVIEW 1 • AI ELEVATOR PROTOTYPE</div>

      </footer>

    </div>

  );

}

export default App;
