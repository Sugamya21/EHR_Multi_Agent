import { useEffect, useState } from "react";
import "./DoctorDashboard.css";
import {
  getPendingRequests,
  getActivePatients,
  acceptPatientRequest,
} from "../api/relationshipApi";

function DoctorDashboard() {
  const [patientId, setPatientId] = useState("");
  const [selectedPatient, setSelectedPatient] = useState(null);
  const [activeSection, setActiveSection] = useState("Overview");
  const [searchError, setSearchError] = useState("");

  const [pendingRequests, setPendingRequests] = useState([]);
  const [activePatients, setActivePatients] = useState([]);
  const [relationshipLoading, setRelationshipLoading] = useState(true);
  const [relationshipError, setRelationshipError] = useState("");
  const [acceptingPatient, setAcceptingPatient] = useState("");

  const loadRelationships = async () => {
    try {
      setRelationshipLoading(true);
      setRelationshipError("");

      const [pendingData, activeData] = await Promise.all([
        getPendingRequests(),
        getActivePatients(),
      ]);

      setPendingRequests(
        Array.isArray(pendingData)
          ? pendingData
          : pendingData.requests || pendingData.relationships || []
      );

      setActivePatients(
        Array.isArray(activeData)
          ? activeData
          : activeData.patients || []
      );
    } catch (error) {
      console.error("Failed to load doctor relationships:", error);

      setRelationshipError(
        error.response?.data?.detail ||
          "Unable to load patient relationships."
      );
    } finally {
      setRelationshipLoading(false);
    }
  };

  useEffect(() => {
    loadRelationships();
  }, []);

  const handleAcceptPatient = async (patientId) => {
    try {
      setAcceptingPatient(patientId);
      setRelationshipError("");

      await acceptPatientRequest(patientId);

      await loadRelationships();
    } catch (error) {
      console.error("Failed to accept patient:", error);

      setRelationshipError(
        error.response?.data?.detail ||
          "Unable to accept patient request."
      );
    } finally {
      setAcceptingPatient("");
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();

    const id = patientId.trim().toUpperCase();

    if (!id) {
      setSearchError("Please enter a Patient ID.");
      setSelectedPatient(null);
      return;
    }

    const patient = activePatients.find(
      (item) => item.patientId === id
    );

    if (!patient) {
      setSelectedPatient(null);
      setSearchError(
        "Patient not found or you are not authorized to access this patient."
      );
      return;
    }

    setSelectedPatient({
      patientId: patient.patientId,
      name: patient.name,
      gender: patient.gender,
      dateOfBirth: patient.birthDate,
      lastUpdate: "Available from EHR",
      reports: 0,
    });

    setSearchError("");
    setActiveSection("Overview");
  };

  const navigationItems = [
    { name: "Overview", icon: "⌂" },
    { name: "EHR", icon: "♧" },
    { name: "Reports", icon: "▤" },
    { name: "History", icon: "◷" },
    { name: "AI Summary", icon: "✦" },
  ];

  return (
    <div className="doctor-dashboard">

      <aside className="doctor-sidebar">

        <div className="doctor-brand">

          <div className="doctor-brand-icon">
            +
          </div>

          <div>
            <div className="doctor-brand-name">
              EHR<span>AI</span>
            </div>

            <div className="doctor-brand-tagline">
              Clinical Intelligence
            </div>
          </div>

        </div>

        <nav className="doctor-navigation">

          <p className="doctor-nav-label">
            PATIENTS
          </p>

          <button
            className="doctor-nav-item"
            onClick={() => {
              setSelectedPatient(null);
              setSearchError("");
              loadRelationships();
            }}
          >
            <span>◉</span>
            Patients
          </button>

          {selectedPatient && (
            <>
              <p className="doctor-nav-label">
                PATIENT RECORD
              </p>

              {navigationItems.map((item) => (
                <button
                  key={item.name}
                  className={`doctor-nav-item ${
                    activeSection === item.name
                      ? "active"
                      : ""
                  }`}
                  onClick={() => setActiveSection(item.name)}
                >
                  <span>{item.icon}</span>
                  {item.name}
                </button>
              ))}
            </>
          )}

        </nav>

        <div className="doctor-sidebar-bottom">

          <div className="doctor-security">
            <span></span>
            Secure clinical workspace
          </div>

          <button
            className="doctor-logout"
            onClick={() => {
              localStorage.removeItem("access_token");
              localStorage.removeItem("user");
              window.location.href = "/";
            }}
          >
            ← Sign out
          </button>

        </div>

      </aside>

      <main className="doctor-main">

        <header className="doctor-topbar">

          <div>

            <p className="doctor-eyebrow">
              DOCTOR WORKSPACE
            </p>

            <h1>
              Patient Records
            </h1>

            <p className="doctor-subtitle">
              Manage your connected patients and review their medical records.
            </p>

          </div>

          <div className="doctor-profile">

            <div className="doctor-avatar">
              DR
            </div>

            <div className="doctor-profile-info">
              <strong>Doctor</strong>
              <span>Clinical Workspace</span>
            </div>

          </div>

        </header>

        {relationshipError && (
          <div className="search-error">
            {relationshipError}
          </div>
        )}

        <section className="patient-search-card">

          <div className="search-heading">

            <div className="search-icon">
              🔎
            </div>

            <div>

              <p className="section-label">
                PATIENT SEARCH
              </p>

              <h2>
                Find a patient
              </h2>

              <p>
                Search only among patients who have an active connection with you.
              </p>

            </div>

          </div>

          <form
            className="patient-search-form"
            onSubmit={handleSearch}
          >

            <div className="search-input-wrapper">

              <span className="search-input-icon">
                #
              </span>

              <input
                type="text"
                value={patientId}
                onChange={(e) => setPatientId(e.target.value)}
                placeholder="Enter Patient ID"
              />

            </div>

            <button
              type="submit"
              className="patient-search-button"
            >
              Search Patient
              <span>→</span>
            </button>

          </form>

          {searchError && (
            <div className="search-error">
              {searchError}
            </div>
          )}

        </section>

        <section className="doctor-section relationship-section">

          <div className="doctor-section-heading">

            <div>

              <p className="section-label">
                PATIENT CONNECTIONS
              </p>

              <h2>
                Pending requests
              </h2>

            </div>

          </div>

          {relationshipLoading ? (
            <div className="doctor-empty-state">
              <p>Loading patient requests...</p>
            </div>
          ) : pendingRequests.length === 0 ? (
            <div className="doctor-empty-state">
              <div className="empty-state-icon">
                ✓
              </div>

              <h2>
                No pending requests
              </h2>

              <p>
                New patient consultation requests will appear here.
              </p>
            </div>
          ) : (
            <div className="relationship-list">

              {pendingRequests.map((request) => {
                const requestPatientId =
                  request.patientId ||
                  request.patient?.patientId;

                const requestPatient =
                  request.patient || {};

                return (
                  <div
                    className="relationship-card"
                    key={requestPatientId}
                  >

                    <div className="relationship-avatar">
                      {(
                        requestPatient.name ||
                        request.name ||
                        "P"
                      )
                        .charAt(0)
                        .toUpperCase()}
                    </div>

                    <div className="relationship-info">

                      <strong>
                        {requestPatient.name ||
                          request.name ||
                          requestPatientId}
                      </strong>

                      <span>
                        Patient ID: {requestPatientId}
                      </span>

                      <small>
                        Status: PENDING
                      </small>

                    </div>

                    <button
                      className="relationship-accept-button"
                      disabled={
                        acceptingPatient === requestPatientId
                      }
                      onClick={() =>
                        handleAcceptPatient(requestPatientId)
                      }
                    >
                      {acceptingPatient === requestPatientId
                        ? "Accepting..."
                        : "Accept"}
                    </button>

                  </div>
                );
              })}

            </div>
          )}

        </section>

        <section className="doctor-section relationship-section">

          <div className="doctor-section-heading">

            <div>

              <p className="section-label">
                ACTIVE PATIENTS
              </p>

              <h2>
                Connected patients
              </h2>

            </div>

            <span className="active-patient-count">
              {activePatients.length} connected
            </span>

          </div>

          {relationshipLoading ? (
            <div className="doctor-empty-state">
              <p>Loading connected patients...</p>
            </div>
          ) : activePatients.length === 0 ? (
            <div className="doctor-empty-state">
              <div className="empty-state-icon">
                👤
              </div>

              <h2>
                No connected patients
              </h2>

              <p>
                Patients you accept will appear here.
              </p>
            </div>
          ) : (
            <div className="active-patient-grid">

              {activePatients.map((patient) => (
                <button
                  className="active-patient-card"
                  key={patient.patientId}
                  onClick={() => {
                    setPatientId(patient.patientId);
                    setSelectedPatient({
                      patientId: patient.patientId,
                      name: patient.name,
                      gender: patient.gender,
                      dateOfBirth: patient.birthDate,
                      lastUpdate: "Available from EHR",
                      reports: 0,
                    });
                    setSearchError("");
                    setActiveSection("Overview");
                  }}
                >

                  <div className="active-patient-avatar">
                    {(patient.name || "P")
                      .charAt(0)
                      .toUpperCase()}
                  </div>

                  <div className="active-patient-info">

                    <strong>
                      {patient.name}
                    </strong>

                    <span>
                      {patient.patientId}
                    </span>

                    <small>
                      {patient.gender || "—"}
                      {patient.birthDate
                        ? ` • ${patient.birthDate}`
                        : ""}
                    </small>

                  </div>

                  <span className="active-patient-arrow">
                    →
                  </span>

                </button>
              ))}

            </div>
          )}

        </section>

        {!selectedPatient && !searchError && (
          <section className="doctor-empty-state">

            <div className="empty-state-icon">
              👤
            </div>

            <h2>
              Select a connected patient
            </h2>

            <p>
              Accept a patient request or select an active patient above to view their medical record.
            </p>

          </section>
        )}

        {selectedPatient && (
          <PatientWorkspace
            patient={selectedPatient}
            activeSection={activeSection}
            setActiveSection={setActiveSection}
          />
        )}

      </main>

    </div>
  );
}

function PatientWorkspace({
  patient,
  activeSection,
  setActiveSection,
}) {
  return (
    <div className="patient-workspace">

      <section className="patient-record-header">

        <div className="patient-record-identity">

          <div className="large-patient-avatar">
            {(patient.name || "P")
              .split(" ")
              .map((word) => word.charAt(0))
              .join("")
              .slice(0, 2)
              .toUpperCase()}
          </div>

          <div>

            <p className="section-label">
              PATIENT RECORD
            </p>

            <h2>
              {patient.name}
            </h2>

            <div className="patient-meta">

              <span>
                {patient.patientId}
              </span>

              <span>•</span>

              <span>
                {patient.gender}
              </span>

              <span>•</span>

              <span>
                DOB {patient.dateOfBirth}
              </span>

            </div>

          </div>

        </div>

        <button className="upload-report-button">
          <span>↑</span>
          Upload New Report
        </button>

      </section>

      <section className="doctor-stats">

        <div className="doctor-stat-card">

          <div className="doctor-stat-icon">
            ♧
          </div>

          <div>
            <span>Conditions</span>
            <strong>—</strong>
          </div>

        </div>

        <div className="doctor-stat-card">

          <div className="doctor-stat-icon blue">
            ◌
          </div>

          <div>
            <span>Observations</span>
            <strong>—</strong>
          </div>

        </div>

        <div className="doctor-stat-card">

          <div className="doctor-stat-icon purple">
            ✦
          </div>

          <div>
            <span>Medications</span>
            <strong>—</strong>
          </div>

        </div>

        <div className="doctor-stat-card">

          <div className="doctor-stat-icon gold">
            ▤
          </div>

          <div>
            <span>Reports</span>
            <strong>—</strong>
          </div>

        </div>

      </section>

      {activeSection === "Overview" && (
        <DoctorOverview
          patient={patient}
          setActiveSection={setActiveSection}
        />
      )}

      {activeSection === "EHR" && (
        <DoctorEHR />
      )}

      {activeSection === "Reports" && (
        <DoctorReports />
      )}

      {activeSection === "History" && (
        <DoctorHistory />
      )}

      {activeSection === "AI Summary" && (
        <DoctorAISummary />
      )}

    </div>
  );
}

function DoctorOverview({
  patient,
  setActiveSection,
}) {
  return (
    <>
      <section className="doctor-section">

        <div className="doctor-section-heading">

          <div>

            <p className="section-label">
              BASIC INFORMATION
            </p>

            <h2>
              Patient profile
            </h2>

          </div>

        </div>

        <div className="doctor-info-grid">

          <InfoField
            label="Patient Name"
            value={patient.name}
          />

          <InfoField
            label="Patient ID"
            value={patient.patientId}
          />

          <InfoField
            label="Gender"
            value={patient.gender}
          />

          <InfoField
            label="Date of Birth"
            value={patient.dateOfBirth}
          />

          <InfoField
            label="Last EHR Update"
            value={patient.lastUpdate}
          />

          <InfoField
            label="Medical Reports"
            value="Available through EHR"
          />

        </div>

      </section>

      <section className="doctor-section">

        <div className="doctor-section-heading">

          <div>

            <p className="section-label">
              CURRENT EHR
            </p>

            <h2>
              Medical record overview
            </h2>

          </div>

          <button
            className="doctor-view-button"
            onClick={() => setActiveSection("EHR")}
          >
            View full EHR →
          </button>

        </div>

        <div className="doctor-ehr-preview">

          <PreviewItem
            title="Conditions"
            value="View from EHR"
            icon="♧"
          />

          <PreviewItem
            title="Medications"
            value="View from EHR"
            icon="✚"
          />

          <PreviewItem
            title="Observations"
            value="View from EHR"
            icon="◌"
          />

          <PreviewItem
            title="Encounters"
            value="View from EHR"
            icon="▣"
          />

        </div>

      </section>

      <section className="doctor-actions">

        <div className="doctor-action-card">

          <div className="doctor-action-icon">
            ↑
          </div>

          <div>

            <h3>
              Add new medical report
            </h3>

            <p>
              Upload a PDF report to begin the EHR update process.
            </p>

          </div>

          <button className="action-button">
            Upload Report →
          </button>

        </div>

        <div className="doctor-action-card ai-action">

          <div className="doctor-action-icon ai-icon">
            ✦
          </div>

          <div>

            <h3>
              AI-generated summary
            </h3>

            <p>
              Generate a readable summary of the current EHR.
            </p>

          </div>

          <button
            className="action-button"
            onClick={() => setActiveSection("AI Summary")}
          >
            View Summary →
          </button>

        </div>

      </section>
    </>
  );
}

function DoctorEHR() {
  return (
    <section className="doctor-section">

      <div className="doctor-section-heading">

        <div>

          <p className="section-label">
            CURRENT EHR
          </p>

          <h2>
            Complete medical record
          </h2>

        </div>

      </div>

      <div className="doctor-ehr-grid">

        <EHRCard
          title="Conditions"
          count="—"
          description="Recorded medical conditions"
          icon="♧"
        />

        <EHRCard
          title="Medications"
          count="—"
          description="Current medications"
          icon="✚"
        />

        <EHRCard
          title="Observations"
          count="—"
          description="Clinical observations and lab results"
          icon="◌"
        />

        <EHRCard
          title="Encounters"
          count="—"
          description="Healthcare encounters"
          icon="▣"
        />

        <EHRCard
          title="Procedures"
          count="—"
          description="Recorded procedures"
          icon="⚕"
        />

        <EHRCard
          title="Care Plans"
          count="—"
          description="Active care plans"
          icon="▤"
        />

      </div>

    </section>
  );
}

function DoctorReports() {
  return (
    <section className="doctor-section">

      <div className="doctor-section-heading">

        <div>

          <p className="section-label">
            MEDICAL DOCUMENTS
          </p>

          <h2>
            Medical reports
          </h2>

        </div>

        <button className="upload-small-button">
          + Upload Report
        </button>

      </div>

      <div className="reports-list">

        <div className="doctor-empty-state">
          <div className="empty-state-icon">
            ▤
          </div>

          <h2>
            Reports will appear here
          </h2>

          <p>
            Uploaded medical reports for this patient will be displayed here.
          </p>
        </div>

      </div>

    </section>
  );
}

function DoctorHistory() {
  return (
    <section className="doctor-section">

      <div className="doctor-section-heading">

        <div>

          <p className="section-label">
            AUDIT TRAIL
          </p>

          <h2>
            EHR history
          </h2>

        </div>

      </div>

      <div className="doctor-empty-state">
        <div className="empty-state-icon">
          ◷
        </div>

        <h2>
          EHR history
        </h2>

        <p>
          Patient-specific EHR history will appear here.
        </p>
      </div>

    </section>
  );
}

function DoctorAISummary() {
  return (
    <section className="doctor-ai-summary">

      <div className="doctor-ai-icon">
        ✦
      </div>

      <p className="section-label">
        EHR ANALYSIS AGENT
      </p>

      <h2>
        AI-generated patient summary
      </h2>

      <p>
        Generate an understandable summary of the patient's
        current medical record, including relevant history,
        conditions, medications, observations, encounters
        and recent changes.
      </p>

      <div className="ai-disclaimer">
        <span>ⓘ</span>

        This summary is AI-generated for informational purposes
        and is not a medical diagnosis or treatment recommendation.
      </div>

      <button className="generate-doctor-summary">
        ✦ Generate AI Summary
      </button>

    </section>
  );
}

function InfoField({ label, value }) {
  return (
    <div className="doctor-info-field">

      <span>{label}</span>

      <strong>{value}</strong>

    </div>
  );
}

function PreviewItem({
  title,
  value,
  icon,
}) {
  return (
    <div className="preview-item">

      <div className="preview-icon">
        {icon}
      </div>

      <div>

        <strong>{title}</strong>

        <span>{value}</span>

      </div>

      <span className="preview-arrow">
        →
      </span>

    </div>
  );
}

function EHRCard({
  title,
  count,
  description,
  icon,
}) {
  return (
    <div className="doctor-ehr-card">

      <div className="doctor-ehr-icon">
        {icon}
      </div>

      <div>

        <span>{title}</span>

        <strong>{count}</strong>

        <p>{description}</p>

      </div>

    </div>
  );
}

export default DoctorDashboard;