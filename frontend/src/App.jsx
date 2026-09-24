import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import Login from "./pages/login";
import PatientDashboard from "./pages/PatientDashboard";
import DoctorDashboard from "./pages/DoctorDashboard";


function ProtectedRoute({ children, allowedRole }) {
  const token = localStorage.getItem("access_token");
  const storedUser = localStorage.getItem("user");

  // No login session
  if (!token || !storedUser) {
    return <Navigate to="/" replace />;
  }

  let user;

  try {
    user = JSON.parse(storedUser);
  } catch {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user");
    return <Navigate to="/" replace />;
  }

  // User is logged in, but does not have permission
  if (allowedRole && user.role?.toLowerCase() !== allowedRole.toLowerCase()) {
    if (user.role?.toLowerCase() === "patient") {
      return <Navigate to="/patient" replace />;
    }

    if (user.role?.toLowerCase() === "doctor") {
      return <Navigate to="/doctor" replace />;
    }

    return <Navigate to="/" replace />;
  }

  return children;
}


function App() {
  return (
    <BrowserRouter>
      <Routes>

        {/* Login */}
        <Route path="/" element={<Login />} />

        {/* Patient Dashboard */}
        <Route
          path="/patient/*"
          element={
            <ProtectedRoute allowedRole="PATIENT">
              <PatientDashboard />
            </ProtectedRoute>
          }
        />

        {/* Doctor Dashboard */}
        <Route
          path="/doctor/*"
          element={
            <ProtectedRoute allowedRole="DOCTOR">
              <DoctorDashboard />
            </ProtectedRoute>
          }
        />

        {/* Unknown route */}
        <Route path="*" element={<Navigate to="/" replace />} />

      </Routes>
    </BrowserRouter>
  );
}

export default App;