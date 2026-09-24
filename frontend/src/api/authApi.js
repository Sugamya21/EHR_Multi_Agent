import api from "./patientApi";

export const loginUser = async (email, password) => {
  const response = await api.post("/auth/login", {
    email,
    password,
  });

  return response.data;
};

export const signupUser = async (signupData) => {
  const response = await api.post("/auth/signup", signupData);

  return response.data;
};  