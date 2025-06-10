import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  scenarios: {
    carga_maxima: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '30s', target: 50 },   // Subida rápida a 50 VUs
        { duration: '30s', target: 100 },  // Sube a 100 VUs
        { duration: '30s', target: 200 },  // Sube a 200 VUs
        { duration: '1m', target: 400 },   // Sube a 400 VUs (carga máxima)
        { duration: '30s', target: 0 },    // Bajada
      ],
      gracefulRampDown: '10s',
    },
    resiliencia: {
      executor: 'per-vu-iterations',
      vus: 20,
      iterations: 10,
      startTime: '3m', // Empieza después de la carga máxima
    },
    endurance: {
      executor: 'constant-vus',
      vus: 50,
      duration: '5m', // 5 minutos de carga constante
      startTime: '5m',
    },
  },
  thresholds: {
    http_req_duration: ['p(95)<1500'], // 95% de las requests < 1.5s
    http_req_failed: ['rate<0.05'],    // menos del 5% de fallos
    checks: ['rate>0.95'],            // al menos 95% de checks deben pasar
  },
};

export default function () {
  let res = http.get('https://emilianomtz.github.io/ICS2do/');
  check(res, {
    'status is 200': (r) => r.status === 200,
    'body contiene ICS2do': (r) => r.body && r.body.includes('ICS2do'),
  });
  sleep(1);
}
