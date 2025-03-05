// src/api/FlowchartApi.ts
import axios from "axios";

const API_URL = "http://localhost:8001";

export const saveFlowchart = async (id: string, data: any) => {
  console.log("Request body for saveFlowchart:", data);
  return axios.post(`${API_URL}/flowchart/${id}`, data);
};

export const runFlowchart = async (id: string, data: any) => {
  console.log("Request body for runFlowchart:", data);
  const response = await axios.post(`${API_URL}/flowchart/${id}/run`, data);
  return response.data;
};

export const getFlowchart = async (id: string) => {
  console.log("Fetching flowchart for id:", id);
  const response = await axios.get(`${API_URL}/flowchart/${id}`);
  return response.data;
};
