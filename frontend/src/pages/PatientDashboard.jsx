import {
  NavLink,
  Routes,
  Route,
  Link,
  useLocation,
} from "react-router-dom";

import {
  getDoctors,
  requestDoctorConnection,
} from "../api/relationshipApi";

import { useEffect, useState } from "react";
import jsPDF from "jspdf";

import { getPatientEHR } from "../api/patientApi";
import { generatePatientSummary } from "../api/summaryApi";

import "./PatientDashboard.css";


function PatientDashboard() {

   const storedUser = JSON.parse(
    localStorage.getItem("user") || "{}"
  );

  const patientId = storedUser.patientId;

  const [ehrData, setEhrData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);


  // =====================================================
  // LOAD PATIENT EHR
  // =====================================================

  useEffect(() => {

    const loadEHR = async () => {

      try {

        setLoading(true);

        const data = await getPatientEHR(patientId);

        console.log(
          "EHR DATA FROM BACKEND:",
          data
        );

        setEhrData(data);

      } catch (err) {

        console.error(
          "EHR API ERROR:",
          err
        );

        setError(
          err.message || "Failed to load patient EHR."
        );

      } finally {

        setLoading(false);

      }

    };


    loadEHR();

  }, []);


  // =====================================================
  // NAVIGATION
  // =====================================================

  const navigationItems = [

    {
      name: "Overview",
      path: "/patient",
      icon: "⌂",
      end: true,
    },

    {
      name: "Conditions",
      path: "/patient/conditions",
      icon: "♧",
    },

    {
      name: "Observations",
      path: "/patient/observations",
      icon: "◌",
    },

    {
      name: "Medications",
      path: "/patient/medications",
      icon: "✚",
    },

    {
      name: "Encounters",
      path: "/patient/encounters",
      icon: "▣",
    },

    {
      name: "Procedures",
      path: "/patient/procedures",
      icon: "⚕",
    },

    {
      name: "Care Plans",
      path: "/patient/care-plans",
      icon: "▤",
    },

    {
      name: "Timeline",
      path: "/patient/timeline",
      icon: "◷",
    },

    {
      name: "AI Summary",
      path: "/patient/ai-summary",
      icon: "✦",
      ai: true,
    },
    {
      name: "Find a Doctor",
      path: "/patient/doctors",
      icon: "⚕",
    }
  ];


  // =====================================================
  // PATIENT INFORMATION
  // =====================================================

  const patientResource =
    ehrData?.sections?.patient?.[0];

  const patientName =
    getPatientName(patientResource);

  const patientGender =
    patientResource?.gender || "Not available";

  const patientBirthDate =
    patientResource?.birthDate || "Not available";


  // =====================================================
  // MAIN UI
  // =====================================================

  return (

    <div className="patient-dashboard">


      {/* =================================================
          SIDEBAR
      ================================================= */}

      <aside className="patient-sidebar">

        <div className="dashboard-brand">

          <div className="dashboard-brand-icon">
            +
          </div>

          <div>

            <div className="dashboard-brand-name">
              EHR<span>AI</span>
            </div>

            <div className="dashboard-brand-tagline">
              Intelligent Health Records
            </div>

          </div>

        </div>


        <nav className="sidebar-navigation">

          {navigationItems.map((item) => (

            <NavLink
              key={item.name}
              to={item.path}
              end={item.end}
              className={({ isActive }) =>
                `sidebar-item ${
                  isActive ? "active" : ""
                } ${item.ai ? "ai-item" : ""}`
              }
            >

              <span>
                {item.icon}
              </span>

              {item.name}

            </NavLink>

          ))}

        </nav>


        <div className="sidebar-bottom">

          <div className="privacy-small">

            <span className="privacy-dot"></span>

            Secure healthcare workspace

          </div>


          <Link
            to="/"
            className="logout-button"
          >
            ← Sign out
          </Link>

        </div>

      </aside>


      {/* =================================================
          MAIN
      ================================================= */}

      <main className="patient-main">


        {/* =================================================
            TOP BAR
        ================================================= */}

        <header className="dashboard-topbar">

          <div>

            {window.location.pathname === "/patient" && (
              <p className="dashboard-eyebrow">
                PATIENT DASHBOARD
              </p>
            )}

            <h1>
              <PageTitle />
            </h1>

            <p className="dashboard-subtitle">
              <PageDescription />
            </p>

          </div>


          <div className="patient-profile">

            <div className="patient-avatar">
              {getInitials(patientName)}
            </div>

            <div className="patient-profile-info">

              <strong>
                {patientName}
              </strong>

              <span>
                {patientId}
              </span>

            </div>

          </div>

        </header>


        {/* =================================================
            ROUTES
        ================================================= */}

        <Routes>

          <Route
            index
            element={
              <OverviewSection
                ehrData={ehrData}
                loading={loading}
                error={error}
                patientName={patientName}
                patientGender={patientGender}
                patientBirthDate={patientBirthDate}
                patientId={patientId}
              />
            }
          />


          <Route
            path="conditions"
            element={
              <ConditionsSection
                ehrData={ehrData}
                loading={loading}
                error={error}
              />
            }
          />


          <Route
            path="observations"
            element={
              <ObservationsSection
                ehrData={ehrData}
                loading={loading}
                error={error}
              />
            }
          />


          <Route
            path="medications"
            element={
              <MedicationsSection
                ehrData={ehrData}
                loading={loading}
                error={error}
              />
            }
          />


          <Route
            path="encounters"
            element={
              <EncountersSection
                ehrData={ehrData}
                loading={loading}
                error={error}
              />
            }
          />


          <Route
            path="procedures"
            element={
              <ProceduresSection
                ehrData={ehrData}
                loading={loading}
                error={error}
              />
            }
          />


          <Route
            path="care-plans"
            element={
              <CarePlansSection
                ehrData={ehrData}
                loading={loading}
                error={error}
              />
            }
          />


          <Route
            path="timeline"
            element={
              <TimelineSection
                ehrData={ehrData}
                loading={loading}
                error={error}
              />
            }
          />


          <Route
  path="ai-summary"
  element={
    <AISummarySection
      patientId={patientId}
      patientName={patientName}
      patientGender={patientGender}
      patientBirthDate={patientBirthDate}
      ehrData={ehrData}
    />
  }
/>

          <Route
            path="doctors"
            element={
            <DoctorsSection />
             }
          />

        </Routes>

      </main>

    </div>

  );

}


/* =====================================================
   PAGE TITLE
===================================================== */

function PageTitle() {

  const { pathname: currentPath } = useLocation();

  if (currentPath.endsWith("/conditions")) {
    return "Conditions";
  }

  if (currentPath.endsWith("/observations")) {
    return "Observations";
  }

  if (currentPath.endsWith("/medications")) {
    return "Medications";
  }

  if (currentPath.endsWith("/encounters")) {
    return "Encounters";
  }

  if (currentPath.endsWith("/procedures")) {
    return "Procedures";
  }

  if (currentPath.endsWith("/care-plans")) {
    return "Care Plans";
  }

  if (currentPath.endsWith("/timeline")) {
    return "Timeline";
  }

  if (currentPath.endsWith("/ai-summary")) {
    return "";
  }

  if (currentPath.endsWith("/doctors")) {
  return "Find a Doctor";
  }

  return "Overview";

}


/* =====================================================
   PAGE DESCRIPTION
===================================================== */

function PageDescription() {

  const { pathname: currentPath } = useLocation();

  if (currentPath.endsWith("/conditions")) {
    return "Review your recorded medical conditions.";
  }

  if (currentPath.endsWith("/observations")) {
    return "Review your laboratory and clinical observations.";
  }

  if (currentPath.endsWith("/medications")) {
    return "Review your current and previous medications.";
  }

  if (currentPath.endsWith("/encounters")) {
    return "View your recorded healthcare encounters.";
  }

  if (currentPath.endsWith("/procedures")) {
    return "View procedures recorded in your medical history.";
  }

  if (currentPath.endsWith("/care-plans")) {
    return "Review your recorded care plans.";
  }

  if (currentPath.endsWith("/timeline")) {
    return "View your medical history chronologically.";
  }

  if (currentPath.endsWith("/ai-summary")) {
    return "";
  }

  if (currentPath.endsWith("/doctors")) {
  return "Find and connect with doctors who can access your authorized medical record.";
  }

  return "Here's an overview of your medical history.";

}


/* =====================================================
   OVERVIEW
===================================================== */

function OverviewSection({
  ehrData,
  loading,
  error,
  patientName,
  patientGender,
  patientBirthDate,
  patientId,
}) {


  if (loading) {

    return (
      <section className="dashboard-section">

        <p>
          Loading patient data...
        </p>

      </section>
    );

  }


  if (error) {

    return (
      <section className="dashboard-section">

        <p>
          Failed to load patient data.
        </p>

        <p>
          {error}
        </p>

      </section>
    );

  }


  if (!ehrData) {

    return (
      <section className="dashboard-section">

        <p>
          No patient data found.
        </p>

      </section>
    );

  }


  const sections =
    ehrData.sections || {};

  const conditions =
    sections.conditions || [];

  const observations =
    sections.observations || [];

  const medications =
    sections.medications || [];

  const encounters =
    sections.encounters || [];


  return (

    <>


      {/* =================================================
          STATISTICS
      ================================================= */}

      <section className="dashboard-stats">


        <div className="stat-card">

          <div className="stat-icon condition-stat">
            ✚
          </div>

          <div>

            <span>
              Conditions
            </span>

            <strong>
              {conditions.length}
            </strong>

          </div>

        </div>


        <div className="stat-card">

          <div className="stat-icon observation-stat">
            ◌
          </div>

          <div>

            <span>
              Observations
            </span>

            <strong>
              {observations.length}
            </strong>

          </div>

        </div>


        <div className="stat-card">

          <div className="stat-icon medication-stat">
            ✦
          </div>

          <div>

            <span>
              Medications
            </span>

            <strong>
              {medications.length}
            </strong>

          </div>

        </div>


        <div className="stat-card">

          <div className="stat-icon encounter-stat">
            ▣
          </div>

          <div>

            <span>
              Encounters
            </span>

            <strong>
              {encounters.length}
            </strong>

          </div>

        </div>


      </section>


      {/* =================================================
          PATIENT INFORMATION
      ================================================= */}

      <section className="dashboard-section">

        <div className="section-heading">

          <div>

            <p className="section-label">
              PATIENT INFORMATION
            </p>

            <h2>
              Personal details
            </h2>

          </div>

        </div>


        <div className="patient-info-card">

          <div className="info-field">

            <span>
              Patient Name
            </span>

            <strong>
              {patientName}
            </strong>

          </div>


          <div className="info-field">

            <span>
              Patient ID
            </span>

            <strong>
              {patientId}
            </strong>

          </div>


          <div className="info-field">

            <span>
              Gender
            </span>

            <strong>
              {patientGender}
            </strong>

          </div>


          <div className="info-field">

            <span>
              Date of Birth
            </span>

            <strong>
              {patientBirthDate}
            </strong>

          </div>

        </div>

      </section>


      {/* =================================================
          CONDITIONS PREVIEW
      ================================================= */}

      <section className="dashboard-section">

        <div className="section-heading">

          <div>

            <p className="section-label">
              MEDICAL HISTORY
            </p>

            <h2>
              Current conditions
            </h2>

          </div>


          <Link
            to="/patient/conditions"
            className="view-all-button"
          >
            View all →
          </Link>

        </div>


        <div className="condition-grid">

          {conditions
            .filter(
              (condition) =>
                condition.status === "active"
            )
            .slice(0, 2)
            .map((condition) => (

              <Link
                key={condition.id}
                to="/patient/conditions"
                className="condition-card-link"
              >

                <ConditionCard
                  name={condition.name}
                  status={condition.status}
                  date={formatDate(condition.onset)}
                />

              </Link>

            ))}

        </div>

      </section>


      <AISummaryPreview />

    </>

  );

}


/* =====================================================
   CONDITIONS
===================================================== */

function ConditionsSection({
  ehrData,
  loading,
  error,
}) {

  if (loading) {
    return <LoadingMessage />;
  }

  if (error) {
    return <ErrorMessage message={error} />;
  }


  const conditions =
    ehrData?.sections?.conditions || [];


  return (

    <section className="dashboard-section">

      <div className="section-heading">

        <div>

          {/* <p className="section-label">
            MEDICAL RECORD
          </p> */}

          {/* <h2>
            Conditions
          </h2> */}

        </div>

      </div>


      <div className="condition-grid">

        {conditions.map((condition) => (

          <ConditionCard
            key={condition.id}
            name={condition.name}
            status={condition.status}
            date={formatDate(condition.onset)}
          />

        ))}

      </div>

    </section>

  );

}


/* =====================================================
   OBSERVATIONS
===================================================== */

function ObservationsSection({
  ehrData,
  loading,
  error,
}) {

  if (loading) {
    return <LoadingMessage />;
  }

  if (error) {
    return <ErrorMessage message={error} />;
  }


  const observations =
    ehrData?.sections?.observations || [];


  return (

    <section className="dashboard-section">

      <div className="section-heading">

        <div>

          {/* <p className="section-label">
            CLINICAL DATA
          </p> */}

          {/* <h2>
            Observations & Lab Results
          </h2> */}

        </div>

      </div>


      <div className="record-table">


        <div className="record-table-header">

          <span>
            Observation
          </span>

          <span>
            Value
          </span>

          <span>
            Status
          </span>

          <span>
            Date
          </span>

        </div>


        {observations.map((observation) => (

          <ObservationRow
            key={observation.id}
            name={observation.name}
            value={formatObservationValue(
              observation
            )}
            status={observation.status}
            date={formatDate(
              observation.date
            )}
          />

        ))}

      </div>

    </section>

  );

}


/* =====================================================
   MEDICATIONS
===================================================== */

function MedicationsSection({
  ehrData,
  loading,
  error,
}) {

  if (loading) {
    return <LoadingMessage />;
  }

  if (error) {
    return <ErrorMessage message={error} />;
  }


  const medications =
    ehrData?.sections?.medications || [];


  return (

    <section className="dashboard-section">

      <div className="section-heading">

        <div>

          {/* <p className="section-label">
            MEDICATION RECORD
          </p> */}

          {/* <h2>
            Medications
          </h2> */}

        </div>

      </div>


      <div className="record-list">

        {medications.map((medication) => (

          <MedicationCard
            key={medication.id}
            name={medication.name}
            status={
              medication.status || "Recorded"
            }
            dosage={
              medication.dosage || "Not available"
            }
            date={
              medication.startDate
                ? `Started ${formatDate(
                    medication.startDate
                  )}`
                : "Start date not available"
            }
          />

        ))}

      </div>

    </section>

  );

}


/* =====================================================
   ENCOUNTERS
===================================================== */

function EncountersSection({
  ehrData,
  loading,
  error,
}) {

  if (loading) {
    return <LoadingMessage />;
  }

  if (error) {
    return <ErrorMessage message={error} />;
  }


  const encounters =
    ehrData?.sections?.encounters || [];


  return (

    <section className="dashboard-section">

      <div className="section-heading">

        <div>

          {/* <p className="section-label">
            HEALTHCARE ACTIVITY
          </p> */}

          {/* <h2>
            Encounters
          </h2> */}

        </div>

      </div>


      <div className="record-list">

        {encounters.map((encounter) => (

          <EncounterCard
            key={encounter.id}
            type={encounter.type || "Encounter"}
            reason={
              encounter.reason ||
              "No reason recorded"
            }
            date={formatDate(
              encounter.startDate
            )}
          />

        ))}

      </div>

    </section>

  );

}


/* =====================================================
   PROCEDURES
===================================================== */

function ProceduresSection({
  ehrData,
  loading,
  error,
}) {

  if (loading) {
    return <LoadingMessage />;
  }

  if (error) {
    return <ErrorMessage message={error} />;
  }


  const procedures =
    ehrData?.sections?.procedures || [];


  return (

    <section className="dashboard-section">

      <div className="section-heading">

        <div>

          {/* <p className="section-label">
            MEDICAL HISTORY
          </p> */}

          {/* <h2>
            Procedures
          </h2> */}

        </div>

      </div>


      <div className="record-list">

        {procedures.map((procedure) => (

          <SimpleRecordCard
            key={procedure.id}
            title={procedure.name}
            status={procedure.status}
            date={formatDate(
              procedure.startDate
            )}
          />

        ))}

      </div>

    </section>

  );

}


/* =====================================================
   CARE PLANS
===================================================== */

function CarePlansSection({
  ehrData,
  loading,
  error,
}) {

  if (loading) {
    return <LoadingMessage />;
  }

  if (error) {
    return <ErrorMessage message={error} />;
  }


  const carePlans =
    ehrData?.sections?.carePlans || [];


  return (

    <section className="dashboard-section">

      <div className="section-heading">

        <div>

          {/* <p className="section-label">
            CARE MANAGEMENT
          </p> */}

          {/* <h2>
            Care Plans
          </h2> */}

        </div>

      </div>


      <div className="record-list">

        {carePlans.map((plan) => (

          <SimpleRecordCard
            key={plan.id}
            title={
              plan.description ||
              plan.title ||
              "Care Plan"
            }
            status={plan.status}
            date={
              plan.startDate
                ? formatDate(plan.startDate)
                : "Date not available"
            }
          />

        ))}

      </div>

    </section>

  );

}


/* =====================================================
   TIMELINE
===================================================== */

function TimelineSection({
  ehrData,
  loading,
  error,
}) {

  if (loading) {
    return <LoadingMessage />;
  }

  if (error) {
    return <ErrorMessage message={error} />;
  }


  const sections =
    ehrData?.sections || {};


  const events = [];


  // Conditions

  (sections.conditions || []).forEach(
    (condition) => {

      if (condition.onset) {

        events.push({

          date: condition.onset,

          title: condition.name,

          description:
            `Condition recorded with status: ${
              condition.status
            }.`,

        });

      }

    }
  );


  // Encounters

  (sections.encounters || []).forEach(
    (encounter) => {

      if (encounter.startDate) {

        events.push({

          date: encounter.startDate,

          title:
            encounter.type ||
            "Healthcare encounter",

          description:
            encounter.reason ||
            `Encounter status: ${
              encounter.status || "recorded"
            }.`,

        });

      }

    }
  );


  // Procedures

  (sections.procedures || []).forEach(
    (procedure) => {

      if (procedure.startDate) {

        events.push({

          date: procedure.startDate,

          title:
            procedure.name ||
            "Procedure",

          description:
            `Procedure status: ${
              procedure.status || "recorded"
            }.`,

        });

      }

    }
  );


  // Sort newest first

  events.sort(
    (a, b) =>
      new Date(b.date) -
      new Date(a.date)
  );


  return (

    <section className="dashboard-section">

      <div className="section-heading">

        <div>

          {/* <p className="section-label">
            MEDICAL HISTORY
          </p> */}

          {/* <h2>
            Medical Timeline
          </h2> */}

        </div>

      </div>


      <div className="timeline">

        {events.map(
          (event, index) => (

            <TimelineItem
              key={`${event.title}-${index}`}
              date={formatDate(event.date)}
              title={event.title}
              description={event.description}
            />

          )
        )}

      </div>

    </section>

  );

}

function DoctorsSection() {

  const [doctors, setDoctors] = useState([]);
  const [loadingDoctors, setLoadingDoctors] = useState(true);
  const [doctorError, setDoctorError] = useState("");
  const [requestingDoctor, setRequestingDoctor] = useState(null);

  const loadDoctors = async () => {

    try {

      setLoadingDoctors(true);
      setDoctorError("");

      const data = await getDoctors();

      setDoctors(data.doctors || []);

    } catch (error) {

      console.error(
        "DOCTOR DISCOVERY ERROR:",
        error
      );

      setDoctorError(
        error.response?.data?.detail ||
        "Failed to load doctors."
      );

    } finally {

      setLoadingDoctors(false);

    }

  };


  useEffect(() => {

    loadDoctors();

  }, []);


  const handleRequest = async (doctorId) => {

    try {

      setRequestingDoctor(doctorId);
      setDoctorError("");

      await requestDoctorConnection(doctorId);

      await loadDoctors();

    } catch (error) {

      console.error(
        "DOCTOR REQUEST ERROR:",
        error
      );

      setDoctorError(
        error.response?.data?.detail ||
        "Failed to send doctor request."
      );

    } finally {

      setRequestingDoctor(null);

    }

  };


  if (loadingDoctors) {

    return (
      <section className="dashboard-section">

        <div className="section-heading">

          <div>

            <p className="section-label">
              CARE TEAM
            </p>

            <h2>
              Find a Doctor
            </h2>

          </div>

        </div>

        <p>
          Loading available doctors...
        </p>

      </section>
    );

  }


  if (doctorError && doctors.length === 0) {

    return (
      <section className="dashboard-section">

        <div className="section-heading">

          <div>

            <p className="section-label">
              CARE TEAM
            </p>

            <h2>
              Find a Doctor
            </h2>

          </div>

        </div>

        <div className="doctor-discovery-error">
          {doctorError}
        </div>

      </section>
    );

  }


  return (

    <section className="dashboard-section">

      <div className="section-heading">

        <div>

          {/* <p className="section-label">
            CARE TEAM
          </p> */}

          {/* <h2>
            Find a Doctor
          </h2> */}

        </div>

      </div>


      {/* <p className="doctor-discovery-description">
        Browse available doctors and request a connection
        with a healthcare professional.
      </p> */}


      {doctorError && (
        <div className="doctor-discovery-error">
          {doctorError}
        </div>
      )}


      <div className="doctor-discovery-grid">

        {doctors.map((doctor) => (

          <div
            className="doctor-discovery-card"
            key={doctor.doctorId}
          >

            <div className="doctor-discovery-avatar">
              {getInitials(doctor.name)}
            </div>


            <div className="doctor-discovery-info">

              <h3>
                {doctor.name}
              </h3>

              <p>
                {doctor.specialization}
              </p>

              <span>
                {doctor.doctorId}
              </span>

            </div>


            <div className="doctor-discovery-action">

              {doctor.status === "ACTIVE" && (

                <span className="doctor-status active">
                  Connected
                </span>

              )}


              {doctor.status === "PENDING" && (

                <span className="doctor-status pending">
                  Request Pending
                </span>

              )}


              {doctor.status === "NOT_CONNECTED" && (

                <button
                  className="doctor-connect-button"
                  onClick={() =>
                    handleRequest(
                      doctor.doctorId
                    )
                  }
                  disabled={
                    requestingDoctor ===
                    doctor.doctorId
                  }
                >

                  {requestingDoctor ===
                  doctor.doctorId
                    ? "Sending..."
                    : "Connect"}

                </button>

              )}

            </div>

          </div>

        ))}

      </div>


      {doctors.length === 0 && (

        <div className="doctor-discovery-empty">

          <h3>
            No doctors available
          </h3>

          <p>
            There are currently no doctors available
            for connection.
          </p>

        </div>

      )}

    </section>

  );

}

/* =====================================================
   AI SUMMARY
===================================================== */

function AISummarySection({
  patientId,
  patientName,
  patientGender,
  patientBirthDate,
  ehrData,
}) {
  const [summary, setSummary] = useState(null);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState(null);

  const generateSummary = async () => {
    try {
      setGenerating(true);
      setError(null);

      const data = await generatePatientSummary(patientId);

      setSummary(data);
    } catch (err) {
      console.error("AI SUMMARY ERROR:", err);

      setError(
        err.response?.data?.detail ||
        err.message ||
        "Failed to generate AI summary."
      );
    } finally {
      setGenerating(false);
    }
  };

  if (generating && !summary) {
    return (
      <section className="ai-summary-loading">
        <div className="ai-loading-icon">
          ✦
        </div>

        <p className="section-label">
          EHR ANALYSIS AGENT
        </p>

        <h2>
          Generating Clinical Summary
        </h2>

        <p>
          The EHR Analysis Agent is analyzing the patient's
          medical records and identifying relevant clinical information.
        </p>

        <div className="ai-loading-bar">
          <div></div>
        </div>

        <span>
          Analyzing EHR records...
        </span>
      </section>
    );
  }

  if (error) {
    return (
      <section className="ai-summary-error">
        <div className="ai-error-icon">
          !
        </div>

        <h2>
          Unable to generate summary
        </h2>

        <p>
          {error}
        </p>

        <button
          type="button"
          className="clinical-primary-button"
          onClick={generateSummary}
        >
          Try Again
        </button>
      </section>
    );
  }

  if (!summary) {
    return (
      <section className="ai-summary-large">
        <div className="ai-summary-large-icon">
          ✦
        </div>

        <p className="section-label">
          EHR ANALYSIS AGENT
        </p>

        <h2>
          Generate Clinical Summary
        </h2>

        <p>
          Generate an AI-powered summary of the patient's
          medical record, including current conditions,
          medications, important observations, recent events,
          and documented care plans.
        </p>

        <button
          type="button"
          className="generate-summary-button"
          onClick={generateSummary}
        >
          ✦ Generate Summary
        </button>
      </section>
    );
  }

  return (
    <ClinicalSummary
      summary={summary}
      ehrData={ehrData}
      patientId={patientId}
      patientName={patientName}
      patientGender={patientGender}
      patientBirthDate={patientBirthDate}
      onRegenerate={generateSummary}
      generating={generating}
    />
  );
}

function ClinicalSummary({
  summary,
  patientId,
  patientName,
  patientGender,
  patientBirthDate,
  onRegenerate,
  generating,
}) {
  const age = calculateAge(patientBirthDate);

  const hasValue = (value) =>
    value !== undefined &&
    value !== null &&
    String(value).trim() !== "";

  const hasItems = (value) =>
    Array.isArray(value) && value.length > 0;

  const formatReportItem = (item) => {
    if (typeof item === "string") {
      return item;
    }

    if (typeof item === "object" && item !== null) {
      return Object.entries(item)
        .filter(
          ([, value]) =>
            value !== undefined &&
            value !== null &&
            String(value).trim() !== ""
        )
        .map(([key, value]) => {
          const label = key
            .replace(/([A-Z])/g, " $1")
            .replace(/^./, (char) => char.toUpperCase());

          return `${label}: ${value}`;
        })
        .join(" • ");
    }

    return String(item);
  };

  const reportSections = [
    {
      key: "reasonForVisit",
      title: "REASON FOR VISIT",
      value: summary?.reasonForVisit,
      type: "text",
    },
    {
      key: "clinicalFindings",
      title: "CLINICAL OBSERVATIONS",
      value: summary?.clinicalFindings,
      type: "list",
    },
    {
      key: "assessment",
      title: "CLINICAL ASSESSMENT",
      value: summary?.assessment,
      type: "list",
    },
    {
      key: "investigations",
      title: "RESULTS",
      value: summary?.investigations,
      type: "list",
    },
    {
      key: "medications",
      title: "MEDICATIONS",
      value: summary?.medications,
      type: "list",
    },
    {
      key: "procedures",
      title: "PROCEDURES",
      value: summary?.procedures,
      type: "list",
    },
    {
      key: "clinicalImpression",
      title: "CLINICAL IMPRESSION",
      value: summary?.clinicalImpression,
      type: "text",
    },
    {
      key: "plan",
      title: "PLAN",
      value: summary?.plan,
      type: "list",
    },
    {
      key: "importantNotes",
      title: "IMPORTANT NOTES",
      value: summary?.importantNotes,
      type: "list",
    },
  ];

  const visibleSections = reportSections.filter((section) => {
    if (section.type === "list") {
      return hasItems(section.value);
    }

    return hasValue(section.value);
  });

  const downloadSummary = () => {
    const doc = new jsPDF();

    const pageWidth = doc.internal.pageSize.getWidth();
    const pageHeight = doc.internal.pageSize.getHeight();

    const left = 18;
    const right = pageWidth - 18;
    const contentWidth = right - left;

    let y = 20;

    const ensureSpace = (height = 10) => {
      if (y + height > pageHeight - 20) {
        doc.addPage();
        y = 20;
      }
    };

    const addText = (
      text,
      size = 9.5,
      bold = false,
      gap = 4
    ) => {
      const value = String(text || "");

      if (!value.trim()) {
        return;
      }

      doc.setFontSize(size);
      doc.setFont(undefined, bold ? "bold" : "normal");

      const lines = doc.splitTextToSize(
        value,
        contentWidth
      );

      const lineHeight = size <= 9 ? 4.2 : 4.8;

      ensureSpace(
        lines.length * lineHeight + gap
      );

      doc.text(lines, left, y);

      y +=
        lines.length * lineHeight +
        gap;

      doc.setFont(undefined, "normal");
    };

    const addSectionHeading = (title) => {
      ensureSpace(18);

      y += 4;

      doc.setFontSize(11);

      doc.setFont(undefined, "bold");

      doc.text(title, left, y);

      y += 6;

      doc.setDrawColor(210, 225, 227);

      doc.line(
        left,
        y,
        right,
        y
      );

      y += 7;

      doc.setFont(undefined, "normal");
    };

    const addBullet = (text) => {
      const value = String(text || "");

      if (!value.trim()) {
        return;
      }

      doc.setFontSize(9);

      doc.setFont(undefined, "normal");

      const lines = doc.splitTextToSize(
        value,
        contentWidth - 8
      );

      const lineHeight = 4.4;

      ensureSpace(
        lines.length * lineHeight + 3
      );

      doc.text(
        "•",
        left,
        y
      );

      doc.text(
        lines,
        left + 5,
        y
      );

      y +=
        lines.length * lineHeight +
        3;
    };

    doc.setFontSize(19);

    doc.setFont(undefined, "bold");

    doc.text(
      "PATIENT CLINICAL REPORT",
      left,
      y
    );

    y += 7;

    doc.setFontSize(8.5);

    doc.setFont(undefined, "normal");

    doc.text(
      "Generated from the patient's documented EHR information",
      left,
      y
    );

    y += 10;

    addSectionHeading(
      "PATIENT INFORMATION"
    );

    addText(
      `Name: ${patientName}`,
      9.5,
      true,
      2
    );

    addText(
      `Patient ID: ${patientId}`,
      9,
      false,
      2
    );

    if (hasValue(patientBirthDate)) {
      addText(
        `Date of Birth: ${formatDate(patientBirthDate)}`,
        9,
        false,
        2
      );
    }

    if (
      hasValue(patientGender) &&
      patientGender !== "Not available"
    ) {
      addText(
        `Sex: ${patientGender}`,
        9,
        false,
        2
      );
    }

    if (
      age !== undefined &&
      age !== null &&
      !Number.isNaN(age)
    ) {
      addText(
        `Age: ${age}`,
        9,
        false,
        2
      );
    }

    visibleSections.forEach(
      (section) => {
        addSectionHeading(
          section.title
        );

        if (section.type === "text") {
          addText(
            section.value,
            9.5,
            false,
            2
          );
        }

        if (section.type === "list") {
          section.value.forEach(
            (item) => {
              addBullet(
                formatReportItem(item)
              );
            }
          );
        }
      }
    );

    ensureSpace(15);

    doc.setFontSize(7.5);

    doc.setFont(undefined, "italic");

    doc.text(
      "This report reflects information documented in the patient's EHR and does not constitute an independent medical diagnosis or treatment recommendation.",
      left,
      pageHeight - 10,
      {
        maxWidth: contentWidth,
      }
    );

    doc.setFont(undefined, "normal");

    doc.save(
      `${patientId}_Clinical_Report.pdf`
    );
  };

  return (
    <section className="clinical-report-page">

      <div className="clinical-report-header">

        <div>
          {/* <p className="section-label">
            EHR ANALYSIS AGENT
          </p> */}

          <h2>
            PATIENT CLINICAL REPORT
          </h2>

          <p>
            Concise clinical information generated from the documented patient record.
          </p>
        </div>

        <div className="clinical-report-actions">

          <button
            type="button"
            className="clinical-secondary-button"
            onClick={onRegenerate}
            disabled={generating}
          >
            ↻{" "}
            {generating
              ? "Generating..."
              : "Regenerate"}
          </button>

          <button
            type="button"
            className="clinical-primary-button"
            onClick={downloadSummary}
          >
            ↓ Download PDF
          </button>

        </div>

      </div>

      <div className="clinical-report-patient">

        <div className="clinical-avatar">
          {getInitials(patientName)}
        </div>

        <div className="clinical-report-patient-main">

          <span>
            PATIENT
          </span>

          <h3>
            {patientName}
          </h3>

          <p>
            {patientId}
          </p>

        </div>

        <div className="clinical-report-patient-meta">

          {hasValue(patientGender) &&
            patientGender !== "Not available" && (
              <div>
                <span>SEX</span>
                <strong>
                  {patientGender}
                </strong>
              </div>
            )}

          {hasValue(patientBirthDate) &&
            patientBirthDate !== "Not available" && (
              <div>
                <span>DATE OF BIRTH</span>
                <strong>
                  {formatDate(
                    patientBirthDate
                  )}
                </strong>
              </div>
            )}

          {age !== undefined &&
            age !== null &&
            !Number.isNaN(age) && (
              <div>
                <span>AGE</span>
                <strong>
                  {age}
                </strong>
              </div>
            )}

          <div>
            <span>REPORT DATE</span>
            <strong>
              {new Date().toLocaleDateString()}
            </strong>
          </div>

        </div>

      </div>

      <div className="clinical-report-body">

        {visibleSections.map(
          (section) => (
            <section
              className="clinical-report-section"
              key={section.key}
            >

              <div className="clinical-report-section-heading">
                <span></span>

                <h3>
                  {section.title}
                </h3>
              </div>

              {section.type === "text" && (
                <p className="clinical-report-text">
                  {section.value}
                </p>
              )}

              {section.type === "list" && (
                <div className="clinical-report-list">

                  {section.value.map(
                    (item, index) => (
                      <div
                        className="clinical-report-list-item"
                        key={`${section.key}-${index}`}
                      >
                        <span className="clinical-report-bullet">
                          •
                        </span>

                        <p>
                          {formatReportItem(
                            item
                          )}
                        </p>
                      </div>
                    )
                  )}

                </div>
              )}

            </section>
          )
        )}

      </div>

    </section>
  );
}

function ClinicalSummaryCard({
  label,
  title,
  icon,
  children,
  className = "",
}) {
  return (
    <section
      className={`clinical-summary-card ${className}`}
    >
      <div className="clinical-card-header">

        <div className="clinical-card-icon">
          {icon}
        </div>

        <div>
          <p className="section-label">
            {label}
          </p>

          <h3>
            {title}
          </h3>
        </div>

      </div>

      <div className="clinical-card-body">
        {children}
      </div>
    </section>
  );
}


function ClinicalEmptyState({ text }) {
  return (
    <div className="clinical-empty">
      <span>—</span>
      {text}
    </div>
  );
}


function calculateAge(birthDate) {
  if (!birthDate) {
    return "Not available";
  }

  const birth = new Date(birthDate);

  if (Number.isNaN(birth.getTime())) {
    return "Not available";
  }

  const today = new Date();

  let age =
    today.getFullYear() -
    birth.getFullYear();

  const monthDifference =
    today.getMonth() -
    birth.getMonth();

  if (
    monthDifference < 0 ||
    (
      monthDifference === 0 &&
      today.getDate() < birth.getDate()
    )
  ) {
    age--;
  }

  return age;
}

function ClinicalInfo({
  label,
  value,
}) {

  return (

    <div className="clinical-info">

      <span>
        {label}
      </span>

      <strong>
        {value || "Not available"}
      </strong>

    </div>

  );

}


/* =====================================================
   CONDITION CARD
===================================================== */

function ConditionCard({
  name,
  status,
  date,
}) {

  return (

    <div className="condition-card">

      <div className="condition-card-top">

        <span className="condition-status">
          {status || "Recorded"}
        </span>

      </div>


      <h3>
        {name}
      </h3>


      <p>
        Recorded medical condition
      </p>


      <div className="condition-date">

        Onset · {date || "Not available"}

      </div>

    </div>

  );

}


/* =====================================================
   OBSERVATION ROW
===================================================== */

function ObservationRow({
  name,
  value,
  status,
  date,
}) {

  return (

    <div className="record-table-row">

      <strong>
        {name}
      </strong>

      <span>
        {value}
      </span>

      <span className="table-status">
        {status || "Recorded"}
      </span>

      <span>
        {date || "Not available"}
      </span>

    </div>

  );

}


/* =====================================================
   MEDICATION CARD
===================================================== */

function MedicationCard({
  name,
  status,
  dosage,
  date,
}) {

  return (

    <div className="record-card">

      <div className="record-card-icon">
        ✚
      </div>


      <div className="record-card-content">

        <h3>
          {name}
        </h3>

        <p>
          Dosage: {dosage}
        </p>

        <span>
          {date}
        </span>

      </div>


      <span className="record-status">
        {status}
      </span>

    </div>

  );

}


/* =====================================================
   ENCOUNTER CARD
===================================================== */

function EncounterCard({
  type,
  reason,
  date,
}) {

  return (

    <div className="record-card">

      <div className="record-card-icon encounter-icon">
        ▣
      </div>


      <div className="record-card-content">

        <h3>
          {type}
        </h3>

        <p>
          {reason}
        </p>

        <span>
          {date}
        </span>

      </div>


      <span className="record-status">
        Recorded
      </span>

    </div>

  );

}


/* =====================================================
   SIMPLE RECORD CARD
===================================================== */

function SimpleRecordCard({
  title,
  status,
  date,
}) {

  return (

    <div className="record-card">

      <div className="record-card-icon">
        ✦
      </div>


      <div className="record-card-content">

        <h3>
          {title}
        </h3>

        <p>
          Medical record entry
        </p>

        <span>
          {date}
        </span>

      </div>


      <span className="record-status">
        {status || "Recorded"}
      </span>

    </div>

  );

}


/* =====================================================
   TIMELINE ITEM
===================================================== */

function TimelineItem({
  date,
  title,
  description,
}) {

  return (

    <div className="timeline-item">

      <div className="timeline-dot"></div>


      <div className="timeline-content">

        <span>
          {date}
        </span>

        <h3>
          {title}
        </h3>

        <p>
          {description}
        </p>

      </div>

    </div>

  );

}


/* =====================================================
   AI SUMMARY PREVIEW
===================================================== */

function AISummaryPreview() {

  return (

    <section className="ai-summary-card">

      <div className="ai-summary-icon">
        ✦
      </div>


      <div className="ai-summary-content">

        <p className="section-label">
          AI-POWERED ANALYSIS
        </p>

        <h2>
          Understand your medical history
        </h2>

        <p>
          Generate an AI-powered summary of your
          complete medical record using the EHR
          Analysis Agent.
        </p>

      </div>


      <Link
        to="/patient/ai-summary"
        className="generate-summary-button"
      >
        Generate AI Summary
        <span>→</span>
      </Link>

    </section>

  );

}


/* =====================================================
   LOADING MESSAGE
===================================================== */

function LoadingMessage() {

  return (

    <section className="dashboard-section">

      <p>
        Loading patient data...
      </p>

    </section>

  );

}


/* =====================================================
   ERROR MESSAGE
===================================================== */

function ErrorMessage({
  message,
}) {

  return (

    <section className="dashboard-section">

      <p>
        Failed to load patient data.
      </p>

      <p>
        {message}
      </p>

    </section>

  );

}


/* =====================================================
   PATIENT NAME
===================================================== */

function getPatientName(
  patient
) {

  if (!patient) {
    return "Patient";
  }


  const name =
    patient.name?.[0];


  if (!name) {
    return "Patient";
  }


  const prefix =
    name.prefix?.join(" ") || "";


  const given =
    name.given?.join(" ") || "";


  const family =
    name.family || "";


  return [
    prefix,
    given,
    family,
  ]
    .filter(Boolean)
    .join(" ");

}


/* =====================================================
   INITIALS
===================================================== */

function getInitials(
  name
) {

  const parts =
    name
      .replace("Mr. ", "")
      .trim()
      .split(/\s+/);


  if (parts.length === 1) {
    return parts[0]
      .substring(0, 2)
      .toUpperCase();
  }


  return (
    parts[0][0] +
    parts[parts.length - 1][0]
  ).toUpperCase();

}


/* =====================================================
   DATE FORMATTER
===================================================== */

function formatDate(
  value
) {

  if (!value) {
    return "Not available";
  }


  const parsed =
    new Date(value);


  if (Number.isNaN(
    parsed.getTime()
  )) {

    return value;

  }


  return parsed.toLocaleDateString(
    "en-GB",
    {
      day: "2-digit",
      month: "short",
      year: "numeric",
    }
  );

}


/* =====================================================
   OBSERVATION VALUE FORMATTER
===================================================== */

function formatObservationValue(
  observation
) {

  // Normal observation

  if (
    observation.value !== null &&
    observation.value !== undefined
  ) {

    return `${observation.value}${
      observation.unit
        ? ` ${observation.unit}`
        : ""
    }`;

  }


  // Blood pressure or other component-based
  // observation

  if (
    observation.components &&
    observation.components.length > 0
  ) {

    return observation.components
      .map(
        (component) =>
          `${component.name}: ${
            component.value
          }${
            component.unit
              ? ` ${component.unit}`
              : ""
          }`
      )
      .join(" / ");

  }


  return "Not available";

}


export default PatientDashboard;