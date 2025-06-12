export const contadorCaracteres = (elemento, idContenedor) => {
   let contenedorElement = document.getElementById(idContenedor);
   if (!contenedorElement) {
       console.warn(`No se encontró un elemento con el ID: ${idContenedor}`);
       return;
   }
   let tamanioTexto = elemento.value.length+1;
   console.log('tamanioTexto :>>', tamanioTexto);
   contenedorElement.innerHTML = `<span>${tamanioTexto} Caracteres </span>`;
};

// Hacer que la función sea accesible globalmente
window.contadorCaracteres = contadorCaracteres;
