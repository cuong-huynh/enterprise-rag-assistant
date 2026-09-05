import http from "k6/http";
import { check, sleep } from "k6";

export const options = {
  stages: [
    { duration: "30s", target: 5 },
    { duration: "30s", target: 10 },
    { duration: "30s", target: 0 },
  ],
  thresholds: {
    http_req_failed: ["rate<0.05"],
    http_req_duration: ["p(95)<5000"],
  },
};

const BASE_URL = __ENV.BASE_URL || "http://localhost:8000";

export default function () {
  const payload = JSON.stringify({
    question: "How many confirmed sale orders are there?",
  });
  const res = http.post(`${BASE_URL}/chat`, payload, {
    headers: { "Content-Type": "application/json" },
  });
  check(res, {
    "status 200": (r) => r.status === 200,
    "has answer": (r) => r.json("answer") !== undefined,
  });
  sleep(1);
}
