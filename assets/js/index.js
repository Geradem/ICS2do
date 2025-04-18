const contadorCaracteres = (elemento, idContenedor)=>{
   let contenedorElement = document.getElementById(idContenedor);
   let tamanioTexto = elemento.value.length;
   console.log('tamanioTexto :>>', tamanioTexto);
   let html = `<span>${tamanioTexto} Caracteres </span>`;
   contenedorElement.innerHTML = html;
}
