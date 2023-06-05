function imprSelec(nombre, titulo) {
    var ficha = document.getElementById(nombre);
    var ventimp = window.open('', 'popimpr');
    ventimp.document.write('<html><head><title>'+titulo+'</title>');
    ventimp.document.write(
      '<link rel="stylesheet" href="/static/css/bootstrap/bootstrap.min.css">'
    );
    ventimp.document.write(
      '<link rel="stylesheet" href="/static/css/style.css">'
    );
    ventimp.document.write('</head><body>');
    ventimp.document.write(ficha.innerHTML);
    ventimp.document.write('</body></html>');
    ventimp.document.close();
    
    ventimp.print();
    ventimp.close();
    
  }

