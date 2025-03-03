import axios from "axios";

const API_URL = "http://localhost:8000"; // Adjust the URL based on your backend

export const saveFlowchart = async (name: string, data: any) => {
  return axios.post(`${API_URL}/flowchart/${id}`, data);
};

export const runFlowchart = async (name: string) => {
  const response = await axios.post(`${API_URL}/flowchart/${id}/run`);
  return response.data;
};

export const getFlowchart = async (name: string) => {
  const response = await axios.get(`${API_URL}/flowchart/${id}`);
  return response.data;
};
