function imprSelec(nombre, titulo) {
  var ficha = document.getElementById(nombre);
  var ventimp = window.open('', 'popimpr');
  
  ventimp.document.write('<html><head><title>' + titulo + '</title>');
  
  // Agregar referencias a los estilos
  var stylesheets = document.styleSheets;
  for (var i = 0; i < stylesheets.length; i++) {
      var styleSheet = stylesheets[i];
      if (styleSheet.href) {
          ventimp.document.write('<link rel="stylesheet" href="' + styleSheet.href + '">');
      }
  }

  ventimp.document.write('</head><body>');
  
  // Agregar el contenido a imprimir
  ventimp.document.write('<div>' + ficha.innerHTML + '</div>');
  
  ventimp.document.write('</body></html>');
  ventimp.document.close();
  
  ventimp.onload = function () {
      ventimp.print();
      ventimp.close();
  };
}


function evitarCaracter(event, caracterProhibido) {
  var key = String.fromCharCode(event.keyCode);
  if (key === caracterProhibido) {
      event.preventDefault();
      return false;
  }
  return true;
}



//
function set_message_count(n) {
    const count = document.getElementById('message_count');
    count.innerText = n;
    count.style.visibility = n ? 'visible' : 'hidden';
}

// funcion para mostrar los mensajes en pantalla
function update_badge() {
    fetch('/mensajes/sin-leer-count')
        .then(response => response.json())
        .then(data => set_message_count(data.count));
}
update_badge(); // llamada inmediata al cargar
setInterval(update_badge, 30000); // cada 30 segundos



// window.addEventListener('load', () => {
//   // Elemento HTML donde se muestra el QR
//   const contenedorQR = document.getElementById('contenedorQR');

//   // Obtiene el valor del div contenedorQR
//   const valorParaQR = contenedorQR.textContent;

//   // Opciones para el tamaño del QR
//   const opcionesQR = {
//     text: valorParaQR,
//     width: 175, // Ancho en píxeles
//     height: 175 // Alto en píxeles
//   };

//   // Crea una instancia de QRCode con el valor obtenido y las opciones
//   const QR = new QRCode(contenedorQR, opcionesQR);
// });