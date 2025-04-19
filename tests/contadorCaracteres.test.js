/**
 * @jest-environment jsdom
 */
import { contadorCaracteres } from '../assets/js/index.js';

describe('contadorCaracteres', () => {
    test('Debe actualizar correctamente el contenedor con la cantidad de caracteres', () => {
        document.body.innerHTML = `
            <input id="inputTest" value="JavaScript" />
            <div id="contenedorTest"></div>
        `;

        let inputTest = document.getElementById('inputTest');
        let contenedorTest = document.getElementById('contenedorTest');

        contadorCaracteres(inputTest, 'contenedorTest');

        expect(contenedorTest.innerHTML).toBe('<span>10 Caracteres </span>');
    });
});
