import API from "./api";

export const setUserConsent = async (data) => {
  const response = await API.post("/users/consent/", data);
  return response.data;
};