import http from 'k6/http';
import { check, sleep } from 'k6';

const SITES = [
  'https://geradem.github.io/ICS2do/',
  'https://geradem.wuaze.com/'
];

export let options = {
  scenarios: {
    carga_maxima: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '30s', target: 500 },   // Sube a 500 VUs
        { duration: '30s', target: 2000 },  // Sube a 2000 VUs
        { duration: '30s', target: 4000 },  // Sube a 4000 VUs
        { duration: '1m', target: 8000 },   // Sube a 8000 VUs (carga máxima)
        { duration: '1m', target: 0 },      // Bajada
      ],
      gracefulRampDown: '20s',
    },
    resiliencia: {
      executor: 'per-vu-iterations',
      vus: 200,
      iterations: 50,
      startTime: '4m', // Empieza después de la carga máxima
    },
  },
  thresholds: {
    http_req_duration: ['p(95)<10000', 'avg<5000'], // 95% de las requests < 10s, promedio < 5s
    http_req_failed: ['rate<0.50'],    // hasta 50% de fallos tolerados
    checks: ['rate>0.50'],            // al menos 50% de checks deben pasar
  },
};

export default function () {
  for (const url of SITES) {
    let res = http.get(url);
    check(res, {
      'status is 200': (r) => r.status === 200,
      'body contiene ICS2do': (r) => r.body && r.body.includes('ICS2do'),
      'latencia < 10s': (r) => r.timings.duration < 10000,
    });
    sleep(1);
  }
}
