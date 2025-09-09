import axios from "axios";

// const API_BASE = "http://127.0.0.1:8000"; // replace with your backend URL
// Correct for browser calls
const API_BASE = "http://localhost:8080";

const client = axios.create({
  baseURL: API_BASE,
  headers: {
    "Content-Type": "application/json",
  },
});

export default client;
