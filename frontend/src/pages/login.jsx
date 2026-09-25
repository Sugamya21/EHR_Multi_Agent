import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "../App.css";
import { loginUser, signupUser } from "../api/authApi";

function Login() {
  const [role, setRole] = useState("patient");
  const [showPassword, setShowPassword] = useState(false);
  const [isSignup, setIsSignup] = useState(false);

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const [name, setName] = useState("");
  const [gender, setGender] = useState("");
  const [birthDate, setBirthDate] = useState("");
  const [specialization, setSpecialization] = useState("");

  const navigate = useNavigate();

  const handleLogin = async (e) => {
  e.preventDefault();

  setError("");
  setSuccess("");

  try {
    const data = await loginUser(email, password);

    const actualRole = data.user.role.toLowerCase();
    const selectedRole = role.toLowerCase();

    if (actualRole !== selectedRole) {
      setError(
        `This account is registered as ${actualRole === "patient" ? "Patient" : "Doctor"}. Please select the correct role.`
      );
      return;
    }

    localStorage.setItem("access_token", data.access_token);
    localStorage.setItem("user", JSON.stringify(data.user));

    if (actualRole === "patient") {
      navigate("/patient");
    } else if (actualRole === "doctor") {
      navigate("/doctor");
    } else {
      setError("Unknown user role.");
    }
  } catch (error) {
    console.error("Login error:", error);

    if (error.response?.data?.detail) {
      setError(error.response.data.detail);
    } else {
      setError("Unable to login. Please try again.");
    }
  }
};

  const handleSignup = async (e) => {
    e.preventDefault();

    setError("");
    setSuccess("");

    try {
      const signupData = {
        email,
        password,
        role: role.toUpperCase(),
        name,
      };

      if (role === "patient") {
        signupData.gender = gender;
        signupData.birthDate = birthDate;
      }

      if (role === "doctor") {
        signupData.specialization = specialization;
      }

      await signupUser(signupData);

      setSuccess("Account created successfully. Please sign in.");

      setIsSignup(false);
      setPassword("");
      setName("");
      setGender("");
      setBirthDate("");
      setSpecialization("");
    } catch (error) {
      console.error("Signup error:", error);

      if (error.response?.data?.detail) {
        setError(error.response.data.detail);
      } else {
        setError("Unable to create account. Please try again.");
      }
    }
  };

  const switchMode = () => {
    setIsSignup(!isSignup);
    setError("");
    setSuccess("");
  };

  return (
    <div className="app-shell">

      <div className="background-glow glow-one"></div>
      <div className="background-glow glow-two"></div>

      <header className="topbar">

        <div className="brand">
          <div className="brand-icon">
            <span>+</span>
          </div>

          <div className="brand-text">
            <span className="brand-name">
              EHR<span>AI</span>
            </span>

            <span className="brand-tagline">
              Intelligent Health Records
            </span>
          </div>
        </div>

        <div className="security-badge">
          <span className="security-dot"></span>
          Secure & Private
        </div>

      </header>

      <main className="main-container">

        <section className="hero-section">

          <div className="eyebrow">
            <span className="sparkle">✦</span>
            AI-POWERED HEALTHCARE
          </div>

          <h1>
            Your health data,
            <br />
            <span>intelligently connected.</span>
          </h1>

          <p className="hero-description">
            A smarter way to organize, understand and manage your
            complete medical history with AI-powered EHR analysis.
          </p>

          <div className="feature-list">

            <div className="feature-item">
              <div className="feature-icon">
                <svg viewBox="0 0 24 24">
                  <path d="M12 3L4 7v5c0 5 3.4 8.9 8 10 4.6-1.1 8-5 8-10V7l-8-4z" />
                  <path d="M9 12l2 2 4-4" />
                </svg>
              </div>

              <div>
                <strong>Authenticated access</strong>
                <span>Access medical records through secure login and authorization.</span>
              </div>
            </div>

            <div className="feature-item">
              <div className="feature-icon">
                <svg viewBox="0 0 24 24">
                  <path d="M12 3v18" />
                  <path d="M5 8l7-5 7 5" />
                  <path d="M5 16l7 5 7-5" />
                </svg>
              </div>

              <div>
                <strong>Unified health history</strong>
                <span>Keep your medical records in one place.</span>
              </div>
            </div>

            <div className="feature-item">
              <div className="feature-icon">
                <svg viewBox="0 0 24 24">
                  <circle cx="12" cy="12" r="8" />
                  <path d="M12 8v4l3 2" />
                </svg>
              </div>

              <div>
                <strong>AI-powered analysis</strong>
                <span>Turn complex medical data into clear summaries.</span>
              </div>
            </div>

          </div>

          <div className="ai-mini-card">

            <div className="ai-orb">
              <span>✦</span>
            </div>

            <div className="ai-mini-content">
              <div className="ai-mini-title">
                Intelligent EHR processing
               
              </div>

              <p>
                Medical documents are analyzed and structured automatically.
              </p>
            </div>


          </div>

        </section>

        <section className="login-section">

          <div className="login-card">

            <div className="login-header">

              <div className="welcome-icon">
                <span>✦</span>
              </div>

              <div>
                <p className="login-label">
                  {isSignup ? "GET STARTED" : "WELCOME BACK"}
                </p>

                <h2>
                  {isSignup
                    ? "Create your workspace"
                    : "Sign in to your workspace"}
                </h2>
              </div>

            </div>

            <p className="login-description">
              {isSignup
                ? "Create your account to access your personalized healthcare workspace."
                : "Access your personalized electronic health record."}
            </p>

            <form onSubmit={isSignup ? handleSignup : handleLogin}>

              {isSignup && (
                <div className="input-group">

                  <label htmlFor="name">
                    Full name
                  </label>

                  <div className="input-wrapper">

                    <svg viewBox="0 0 24 24" className="input-icon">
                      <circle cx="12" cy="8" r="3" />
                      <path d="M5 21c.7-4 2.9-6 7-6s6.3 2 7 6" />
                    </svg>

                    <input
                      id="name"
                      type="text"
                      placeholder="Enter your full name"
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      required
                    />

                  </div>

                </div>
              )}

              <div className="input-group">

                <label htmlFor="email">
                  Email address
                </label>

                <div className="input-wrapper">

                  <svg viewBox="0 0 24 24" className="input-icon">
                    <rect x="3" y="5" width="18" height="14" rx="2" />
                    <path d="M3 7l9 6 9-6" />
                  </svg>

                  <input
                    id="email"
                    type="email"
                    placeholder="you@example.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                  />

                </div>

              </div>

              <div className="input-group">

                <div className="label-row">

                  <label htmlFor="password">
                    Password
                  </label>

                  {!isSignup && (
                    <button
                      type="button"
                      className="forgot-link"
                      onClick={() =>
                        alert("Password recovery will be connected later.")
                      }
                    >
                      Forgot password?
                    </button>
                  )}

                </div>

                <div className="input-wrapper">

                  <svg viewBox="0 0 24 24" className="input-icon">
                    <rect x="4" y="10" width="16" height="11" rx="2" />
                    <path d="M8 10V7a4 4 0 018 0v3" />
                  </svg>

                  <input
                    id="password"
                    type={showPassword ? "text" : "password"}
                    placeholder={
                      isSignup
                        ? "Create your password"
                        : "Enter your password"
                    }
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                  />

                  <button
                    type="button"
                    className="password-toggle"
                    onClick={() => setShowPassword(!showPassword)}
                    aria-label="Toggle password visibility"
                  >
                    {showPassword ? "Hide" : "Show"}
                  </button>

                </div>

              </div>

              <div className="role-section">

                <label>
                  {isSignup ? "Create account as" : "Continue as"}
                </label>

                <div className="role-selector">

                  <button
                    type="button"
                    className={`role-option ${
                      role === "patient" ? "selected" : ""
                    }`}
                    onClick={() => setRole("patient")}
                  >

                    <div className="role-icon patient-icon">
                      <svg viewBox="0 0 24 24">
                        <circle cx="12" cy="8" r="3" />
                        <path d="M5 21c.7-4 2.9-6 7-6s6.3 2 7 6" />
                      </svg>
                    </div>

                    <div className="role-text">
                      <strong>Patient</strong>
                      <span>My health records</span>
                    </div>

                    <div className="check-circle">
                      {role === "patient" && "✓"}
                    </div>

                  </button>

                  <button
                    type="button"
                    className={`role-option ${
                      role === "doctor" ? "selected" : ""
                    }`}
                    onClick={() => setRole("doctor")}
                  >

                    <div className="role-icon doctor-icon">
                      <svg viewBox="0 0 24 24">
                        <path d="M8 3v4" />
                        <path d="M16 3v4" />
                        <path d="M5 7h14" />
                        <path d="M7 7v7a5 5 0 0010 0V7" />
                        <path d="M12 12v4" />
                        <path d="M10 14h4" />
                      </svg>
                    </div>

                    <div className="role-text">
                      <strong>Doctor</strong>
                      <span>Patient workspace</span>
                    </div>

                    <div className="check-circle">
                      {role === "doctor" && "✓"}
                    </div>

                  </button>

                </div>

              </div>

              {isSignup && role === "patient" && (
                <>
                  <div className="input-group">

                    <label htmlFor="gender">
                      Gender
                    </label>

                    <div className="input-wrapper">

                      <select
                        id="gender"
                        value={gender}
                        className="signup-gender-select"
                        onChange={(e) => setGender(e.target.value)}
                        required
                      >
                        <option value="">Select gender</option>
                        <option value="male">Male</option>
                        <option value="female">Female</option>
                        <option value="other">Other</option>
                      </select>

                    </div>

                  </div>

                  <div className="input-group">

                    <label htmlFor="birthDate">
                      Date of birth
                    </label>

                    <div className="input-wrapper">

                      <input
                        id="birthDate"
                        type="date"
                        value={birthDate}
                        onChange={(e) => setBirthDate(e.target.value)}
                        required
                      />

                    </div>

                  </div>
                </>
              )}

              {isSignup && role === "doctor" && (
                <div className="input-group">

                  <label htmlFor="specialization">
                    Specialization
                  </label>

                  <div className="input-wrapper">

                    <input
                      id="specialization"
                      type="text"
                      placeholder="e.g. Cardiology"
                      value={specialization}
                      onChange={(e) =>
                        setSpecialization(e.target.value)
                      }
                      required
                    />

                  </div>

                </div>
              )}

              {error && (
                <div className="login-error">
                  {error}
                </div>
              )}

              {success && (
                <div className="login-success">
                  {success}
                </div>
              )}

              <button type="submit" className="login-button">

                <span>
                  {isSignup
                    ? "Create Account"
                    : `Continue as ${
                        role === "patient" ? "Patient" : "Doctor"
                      }`}
                </span>

                <span className="button-arrow">
                  →
                </span>

              </button>

            </form>

            <div className="login-footer">

              <div className="footer-security">

                <svg viewBox="0 0 24 24">
                  <path d="M12 3L5 6v5c0 4.5 3 8 7 10 4-2 7-5.5 7-10V6l-7-3z" />
                </svg>

                <span>
                  Protected healthcare workspace
                </span>

              </div>

              <span className="version">
                v1.0
              </span>

            </div>

            <div className="auth-switch">
              {isSignup ? (
                <>
                  Already have an account?{" "}
                  <button
                    type="button"
                    className="sign-in-button"
                    onClick={switchMode}
                  >
                    Sign in
                  </button>
                </>
              ) : (
                <>
                  Don't have an account?{" "}
                  <button
                      type="button"
                      className="create-account-button"
                      onClick={() => setIsSignup(true)}
                    >
                      Create account
                    </button>
                </>
              )}
            </div>

          </div>

        </section>

      </main>

      <footer className="app-footer">

        <span>
          © 2026 EHR AI
        </span>

        <div className="footer-links">
          <span>Privacy</span>
          <span>Security</span>
          <span>Help</span>
        </div>

      </footer>

    </div>
  );
}

export default Login;