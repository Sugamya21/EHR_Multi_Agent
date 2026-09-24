import api from "./patientApi";

export const getPendingRequests = async () => {
  const response = await api.get("/relationships/doctor/pending");
  return response.data;
};

export const getActivePatients = async () => {
  const response = await api.get("/relationships/doctor/active");
  return response.data;
};

export const acceptPatientRequest = async (patientId) => {
  const response = await api.put(
    `/relationships/accept/${patientId}`
  );
  return response.data;
};

export const getDoctors = async () => {
  const response = await api.get("/relationships/doctors");
  return response.data;
};

export const requestDoctorConnection = async (doctorId) => {
  const response = await api.post("/relationships/request", {
    doctorId,
  });
  return response.data;
};