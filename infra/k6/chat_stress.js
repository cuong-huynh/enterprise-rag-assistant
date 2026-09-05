import http from "k6/http";
import { check, sleep } from "k6";

// Aggressive ramp to probe upper bound on this machine (data-route question).
export const options = {
  stages: [
    { duration: "20s", target: 20 },
    { duration: "20s", target: 50 },
    { duration: "20s", target: 100 },
    { duration: "20s", target: 150 },
    { duration: "20s", target: 0 },
  ],
  thresholds: {
    http_req_failed: ["rate<0.20"],
  },
};

const BASE_URL = __ENV.BASE_URL || "http://localhost:8000";

export default function () {
  const payload = JSON.stringify({
    question: "How many confirmed sale orders are there?",
  });
  const res = http.post(`${BASE_URL}/chat`, payload, {
    headers: { "Content-Type": "application/json" },
    timeout: "30s",
  });
  check(res, {
    "status 200": (r) => r.status === 200,
    "route data": (r) => r.json("route") === "data",
  });
  sleep(0.1);
}
