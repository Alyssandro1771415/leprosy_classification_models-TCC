import API from "./api";

export const savePrediction = async (data) => {
  const response = await API.post("/predictions/save/", data);
  return response.data;
};

export const getUserHistory = async (userId) => {
  const response = await API.get(`/predictions/history/${userId}`);
  return response.data;
};