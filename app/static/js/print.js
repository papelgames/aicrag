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