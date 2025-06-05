/**
 * @jest-environment jsdom
 */
import { contadorCaracteres } from '../assets/js/index.js';

describe('contadorCaracteres', () => {
    let input, contenedor;

    beforeEach(() => {
        document.body.innerHTML = `
            <input id="inputTest" value="Hola" />
            <div id="contenedorTest"></div>
        `;
        input = document.getElementById('inputTest');
        contenedor = document.getElementById('contenedorTest');
    });

    test('actualiza el contenedor con la cantidad de caracteres', () => {
        contadorCaracteres(input, 'contenedorTest');
        expect(contenedor.innerHTML).toBe('<span>4 Caracteres </span>');
    });

    test('muestra advertencia si el contenedor no existe', () => {
        const warnSpy = jest.spyOn(console, 'warn').mockImplementation(() => {});
        contadorCaracteres(input, 'noExiste');
        expect(warnSpy).toHaveBeenCalledWith('No se encontró un elemento con el ID: noExiste');
        warnSpy.mockRestore();
    });

    test('muestra 0 caracteres si el input está vacío', () => {
        input.value = '';
        contadorCaracteres(input, 'contenedorTest');
        expect(contenedor.innerHTML).toBe('<span>0 Caracteres </span>');
    });
});
