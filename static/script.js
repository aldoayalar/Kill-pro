function validarFormulario() {
  // Obtener los valores de los campos del formulario
  var rut = document.getElementById('txtrut').value;
  var nombre = document.getElementById('txtnombre').value;
  var correo = document.getElementById('txtcorreo').value;
  var apellidopa = document.getElementById('txtpaterno').value;
  var apellidoma = document.getElementById('txtmaterno').value;
  var genero = document.getElementById('txtgenero').value;
  var password = document.getElementById('txtpassword').value;
  

  // Obtener referencia al elemento del mensaje de aviso
  var mensajeAviso = document.getElementById('mensaje-aviso');

  // Validar campos del formulario
  if (rut === '' || nombre === '' || correo === '' || apellidopa === '' || apellidoma === '' || genero === '' || password === '') {
    mensajeAviso.textContent = 'Por favor, complete todos los campos.';

    // Agregar clase CSS adicional a los campos vacíos
    if (rut === '') {
        document.getElementById('txtrut').classList.add('campo-vacio');
      }
      if (nombre === '') {
        document.getElementById('txtnombre').classList.add('campo-vacio');
      }
      if (correo === '') {
        document.getElementById('txtcorreo').classList.add('campo-vacio');
      }
      
    return false; // Detener el envío del formulario
  }
  
  // Si todos los campos están completos, se puede enviar el formulario
  return true;
}


function validarFormularioMed() {
  // Obtener los valores de los campos del formulario
  var nombre = document.getElementById('txtnombre').value;
  var descripcion = document.getElementById('txtdescripcion').value;

  // Obtener referencia al elemento del mensaje de aviso
  var mensajeAviso = document.getElementById('mensaje-aviso');

  // Validar campos del formulario
  if (nombre === '' || descripcion === '') {
    mensajeAviso.textContent = 'Por favor, complete todos los campos.';

    // Agregar clase CSS adicional a los campos vacíos
    if (nombre === '') {
      document.getElementById('txtnombre').classList.add('campo-vacio');
    }
    if (descripcion === '') {
      document.getElementById('txtdescripcion').classList.add('campo-vacio');
    }

    return false; // Detener el envío del formulario
  }

  // Si todos los campos están completos, se puede enviar el formulario
  return true;
}
