import http from "k6/http";
import { check } from "k6";

// Find breaking point: no think-time, ramp VUs until latency/errors spike.
// Stop interpreting "max" as unlimited — max = highest load that still meets SLO.
export const options = {
  stages: [
    { duration: "15s", target: 50 },
    { duration: "15s", target: 100 },
    { duration: "15s", target: 200 },
    { duration: "15s", target: 300 },
    { duration: "15s", target: 0 },
  ],
  thresholds: {
    http_req_failed: ["rate<0.05"],
    http_req_duration: ["p(95)<3000"],
  },
};

const BASE_URL = __ENV.BASE_URL || "http://localhost:8000";

export default function () {
  const payload = JSON.stringify({
    question: "How many confirmed sale orders are there?",
  });
  const res = http.post(`${BASE_URL}/chat`, payload, {
    headers: { "Content-Type": "application/json" },
    timeout: "60s",
  });
  check(res, {
    "status 200": (r) => r.status === 200,
    "route data": (r) => r.json("route") === "data",
  });
}
