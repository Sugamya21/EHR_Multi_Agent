import api from "./patientApi";

export const generatePatientSummary = async (patientId) => {
  const response = await api.post(`/patients/${patientId}/summary`);
  return response.data;
};