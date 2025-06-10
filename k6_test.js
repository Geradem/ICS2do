import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  vus: 10, // usuarios virtuales concurrentes
  duration: '30s', // duración de la prueba
  thresholds: {
    http_req_duration: ['p(95)<800'], // 95% de las requests deben ser < 800ms
    http_req_failed: ['rate<0.01'],   // menos del 1% de requests fallidas
  },
};

export default function () {
  let res = http.get('hhttps://geradem.github.io/ICS2do/'); // URL real del sitio desplegado
  check(res, {
    'status is 200': (r) => r.status === 200,
  });
  sleep(1);
}
