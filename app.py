from flask import Flask
from flask import render_template, request, redirect, Response, url_for, session
from flask_mysqldb import MySQL,MySQLdb # pip install Flask-MySQLdb
from functools import wraps

app = Flask(__name__, template_folder='template')

app.config['MYSQL_HOST'] = 'killcoronabd.mysql.database.azure.com'  # Por ejemplo, 'localhost' o la dirección IP del servidor
app.config['MYSQL_USER'] = 'killcorona'  # El nombre de usuario para acceder a la base de datos
app.config['MYSQL_PASSWORD'] = 'Corona1313'  # La contraseña correspondiente al nombre de usuario
app.config['MYSQL_DB'] = 'bdkill'  # El nombre de la base de datos que deseas utilizar
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

@app.route('/')
def index():
    return render_template('index.html')


##Funcion de login
@app.route('/acceso-login', methods=["GET", "POST"])
def login():
    if request.method == 'POST' and 'txtcorreo' in request.form and 'txtpassword' in request.form:
        _correo = request.form['txtcorreo']
        _password = request.form['txtpassword']
        
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM tbl_usuario WHERE s_email = %s and s_contrasena = %s', (_correo, _password,))
        account = cur.fetchone()
        
        if account:
            session['logeado'] = True
            session['id_usuario'] = account['id_usuario']
            session['fk_id_perfil'] = account['fk_id_perfil']
            session['s_nombreUsuario'] = account['s_nombreUsuario']

            
            if session['fk_id_perfil'] == 1:
                return render_template("admin/admin.html")
            elif session['fk_id_perfil'] == 2:
                return render_template("medico/medico.html")
        
        # Agregar el return para devolver una respuesta en caso de error
        return render_template('index.html', mensaje="Usuario o contraseña incorrecto")
    
    # Agregar el return para devolver una respuesta en caso de error
    return render_template('index.html', mensaje="Error en el formulario de login")


# Decorador para verificar si el usuario es administrador y está logueado
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logeado') or session.get('fk_id_perfil') != 1:
            mensaje = "No tienes permiso para acceder a esta página."
            session['mensaje'] = mensaje
            return redirect(url_for('medico'))
        return f(*args, **kwargs)
    return decorated_function

# Decorador para verificar si el usuario es administrador y está logueado
def medic_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logeado') or session.get('fk_id_perfil') != 2:
            mensaje = "No tienes permiso para acceder a esta página."
            session['mensaje'] = mensaje
            return redirect(url_for('admin'))
        return f(*args, **kwargs)
    return decorated_function

# Decorador para verificar si el usuario está logueado
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logeado'):
            return redirect(url_for('index'))  # Redirigir a la página de inicio de sesión o a donde desees
        return f(*args, **kwargs)
    return decorated_function


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    return redirect(url_for('index'))

      
      
      
      
      
########################################
## Rutas para el perfil ADMINISTRADOR

@app.route('/admin')
@login_required
@admin_required
def admin():
    return render_template('admin/admin.html', session=session)


###########################
## DOCTORES ##

## Listar todos los docs
@app.route('/admin/medicos/alldocs')
@login_required
@admin_required
def allDoc():
    # Realizar consulta SQL para obtener los registros con fk_id_perfil = 2
    sql = "SELECT * FROM tbl_usuario WHERE fk_id_perfil = 2"
    cursor = mysql.connection.cursor()
    cursor.execute(sql)
    usuarios = cursor.fetchall()

    # Cerrar el cursor
    cursor.close()

    mensaje = request.args.get('mensaje')  # Obtener el mensaje de la URL si existe

    # Renderizar la plantilla alldocs.html y pasar la lista de usuarios y el mensaje
    return render_template('admin/medicos/alldocs.html', usuarios=usuarios, mensaje=mensaje)



## Ver información del doctor
@app.route('/admin/medicos/<int:id>')
@login_required
@admin_required
def showMedico(id):
    # Realizar consulta SQL para obtener la información del médico en función de su ID
    sql = "SELECT * FROM tbl_usuario WHERE id_usuario = %s"
    cursor = mysql.connection.cursor()
    cursor.execute(sql, (id,))
    medico = cursor.fetchone()

    # Cerrar el cursor
    cursor.close()

    return render_template('admin/medicos/show.html', medico=medico)



## Eliminar doc
@app.route('/admin/medicos/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def deleteDoctor(id):
    # Verificar si el doctor existe en la base de datos
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM tbl_usuario WHERE id_usuario = %s', (id,))
    doctor = cursor.fetchone()
    if doctor:
        # Actualizar el estado del campo b_activo a 0 (inactivo)
        cursor.execute('UPDATE tbl_usuario SET b_activo = 0 WHERE id_usuario = %s', (id,))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('allDoc', mensaje='Usuario eliminado exitosamente'))
    else:
        cursor.close()
        return redirect(url_for('allDoc', mensaje='No se encontró el usuario a eliminar'))




## Editar Usuario
@app.route('/admin/medicos/edit/<int:id>')
@login_required
@admin_required
def edit(id):
    
    sql = "SELECT * FROM tbl_usuario WHERE id_usuario = %s"
    cursor = mysql.connection.cursor()
    cursor.execute(sql, (id,))
    medico = cursor.fetchone()

    # Cerrar el cursor
    cursor.close()
    
    success = request.args.get('success', False)  # Obtener el valor del parámetro 'success' de la URL
    
    return render_template('admin/medicos/edit.html', medico=medico, success=success)


## Up date
@app.route('/update', methods=['POST'])
@login_required
@admin_required
def update():
    
    if request.method == 'POST':
    
        _rut=request.form['txtrut']
        _nombre=request.form['txtnombre']
        _correo=request.form['txtcorreo']
        _apellidopa=request.form['txtpaterno']
        _apellidoma=request.form['txtmaterno']
        _password=request.form['txtpassword']
        _especialidad=request.form['txtespecialidad']
        _especialidaddos=request.form['txtespecialidaddos']
        _especialidadtres=request.form['txtespecialidadtres']    
        _idempleado=request.form['txtid']    
        _activo = int(request.form.get('active'))

        
        sql = "UPDATE `tbl_usuario` SET `s_rut` = %s, `s_nombreUsuario` = %s, `s_email` = %s, `s_apellidoPaterno` = %s, `s_apellidoMaterno` = %s, `s_espe1` = %s, `s_espe2` = %s, `s_espe3` = %s, `s_contrasena` = %s, `b_activo` = %s WHERE `id_usuario` = %s"

        datos = (_rut, _nombre, _correo, _apellidopa, _apellidoma, _especialidad, _especialidaddos, _especialidadtres, _password, _activo, _idempleado)

        
        # Ejecutar la sentencia SQL
        cursor = mysql.connection.cursor()
        cursor.execute(sql, datos)

        # Confirmar los cambios en la base de datos
        mysql.connection.commit()

        # Cerrar el cursor
        cursor.close()
         
        return redirect(url_for('edit', id=_idempleado, success=True)) 


    else:
        # Obtener el ID del médico a partir de los parámetros de la URL
        medico_id = request.args.get('medico_id')

        # Obtener el médico de la base de datos utilizando el ID y mostrar el formulario edit.html
        return render_template('edit.html', medico_id=medico_id, success=False)


## Crear un doctor
@app.route('/admin/medicos/create')
@login_required
@admin_required
def createDoc():
    return render_template('admin/medicos/create.html')

@app.route('/store', methods=['POST'])
@login_required
@admin_required
def storage():
    _rut=request.form['txtrut']
    _nombre=request.form['txtnombre']
    _correo=request.form['txtcorreo']
    _apellidopa=request.form['txtpaterno']
    _apellidoma=request.form['txtmaterno']
    _genero=request.form['txtgenero']
    _password=request.form['txtpassword']
    _especialidad=request.form['txtespecialidad']
    _especialidaddos=request.form['txtespecialidaddos']
    _especialidadtres=request.form['txtespecialidadtres']
    _useractive=request.form['active']
    
    
    sql ="INSERT INTO `tbl_usuario` (`s_rut`,`s_nombreUsuario`, `s_email`, `s_apellidoPaterno`, `s_apellidoMaterno`,`fk_id_perfil`,`s_espe1`,`s_espe2`,`s_espe3`,`fk_id_genero`,`b_activo`,`s_contrasena`) VALUES (%s, %s, %s, %s, %s,2,%s,%s,%s,%s,%s,%s);"
    
     
    datos=(_rut,_nombre, _correo,_apellidopa,_apellidoma,_especialidad,_especialidaddos,_especialidadtres,_genero,_useractive,_password )
    
    # Ejecutar la sentencia SQL
    cursor = mysql.connection.cursor()
    cursor.execute(sql, datos)

    # Confirmar los cambios en la base de datos
    mysql.connection.commit()

    # Cerrar el cursor
    cursor.close()


    # Redirigir o mostrar un mensaje de éxito
    return render_template('admin/medicos/create.html', mensaje="Usuario creado exitosamente")


@app.route('/admin/medicos/archivados')
@login_required
@admin_required
def archivedDoctors():
    # Realizar consulta SQL para obtener los registros con fk_id_perfil = 2
    sql = "SELECT * FROM tbl_usuario WHERE fk_id_perfil = 2"
    cursor = mysql.connection.cursor()
    cursor.execute(sql)
    usuarios = cursor.fetchall()

    # Cerrar el cursor
    cursor.close()

    mensaje = request.args.get('mensaje')  # Obtener el mensaje de la URL si existe

    # Renderizar la plantilla alldocs.html y pasar la lista de usuarios y el mensaje
    return render_template('admin/medicos/archived.html', usuarios=usuarios, mensaje=mensaje)







#######################################
## MEDICAMENTOS ##

## Listar todos los Medicamentos
@app.route('/admin/medicamentos/allmedicamentos')
@login_required
@admin_required
def allmedicamentos():
    # Realizar consulta SQL para obtener los registros
    sql = "SELECT * FROM tbl_medicamento"
    cursor = mysql.connection.cursor()
    cursor.execute(sql)
    medicamentos = cursor.fetchall()

    # Cerrar el cursor
    cursor.close()

    mensaje = request.args.get('mensaje')  # Obtener el mensaje de la URL si existe

    # Renderizar la plantilla y pasar la lista de usuarios y el mensaje
    return render_template('admin/medicamentos/allmedicamentos.html', medicamentos=medicamentos, mensaje=mensaje)


## Crear un Medicamento
@app.route('/admin/medicamentos/create')
@login_required
@admin_required
def createMedicamentos():
    return render_template('admin/medicamentos/create.html')

@app.route('/mediStr', methods=['POST'])
@login_required
@admin_required
def storagemed():
    _nombre=request.form['txtnombre']
    _descripcion=request.form['txtdescripcion']
    _active=request.form['active']
    
    
    sql ="INSERT INTO `tbl_medicamento` (`s_nombreMedicamento`, `s_descripcion`,`b_activo`) VALUES (%s, %s, %s);"
    
     
    datos=(_nombre, _descripcion,_active )
    
    # Ejecutar la sentencia SQL
    cursor = mysql.connection.cursor()
    cursor.execute(sql, datos)

    # Confirmar los cambios en la base de datos
    mysql.connection.commit()

    # Cerrar el cursor
    cursor.close()


    # Redirigir o mostrar un mensaje de éxito
    return render_template('admin/medicamentos/create.html', mensaje="Medicamento creado exitosamente")


## Editar Medicamento
@app.route('/admin/medicamentos/edit/<int:id>')
@login_required
@admin_required
def editMed(id):
    
    sql = "SELECT * FROM tbl_medicamento WHERE id_medicamento = %s"
    cursor = mysql.connection.cursor()
    cursor.execute(sql, (id,))
    medicamentos = cursor.fetchone()

    # Cerrar el cursor
    cursor.close()
    
    success = request.args.get('success', False)  # Obtener el valor del parámetro 'success' de la URL
    
    return render_template('admin/medicamentos/edit.html', medicamentos=medicamentos, success=success)



## Up date
@app.route('/mediUpdate', methods=['POST'])
@login_required
@admin_required
def mediUpdate():
    
    if request.method == 'POST':
        _nombre=request.form['txtnombre']
        _descripcion=request.form['txtdescripcion']
        _idmedicamento=request.form['txtid']
        _active = int(request.form.get('active'))

        sql = "UPDATE `tbl_medicamento` SET `s_nombreMedicamento` = %s, `s_descripcion` = %s, `b_activo` = %s  WHERE `id_medicamento` = %s"

        datos = (_nombre, _descripcion, _active, _idmedicamento)

       # Ejecutar la sentencia SQL
        cursor = mysql.connection.cursor()
        cursor.execute(sql, datos)

        # Confirmar los cambios en la base de datos
        mysql.connection.commit()

        # Cerrar el cursor
        cursor.close()
         
        return redirect(url_for('editMed', id=_idmedicamento, success=True))



    else:
        # Obtener el ID del médico a partir de los parámetros de la URL
        medicamento_id = request.args.get('medicamento_id')

        # Obtener el médico de la base de datos utilizando el ID y mostrar el formulario edit.html
        return render_template('edit.html', medicamento_id=medicamento_id, success=False)



## Eliminar Medicamento
@app.route('/admin/medicamentos/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def deleteMedicamento(id):
    # Verificar si el medicamento existe en la base de datos
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM tbl_medicamento WHERE id_medicamento = %s', (id,))
    medicamento = cursor.fetchone()
    if medicamento:
        # Actualizar el estado del campo b_activo a 0 (inactivo)
        cursor.execute('UPDATE tbl_medicamento SET b_activo = 0 WHERE id_medicamento = %s', (id,))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('allmedicamentos', mensaje='Medicamento eliminado exitosamente'))
    else:
        cursor.close()
        return redirect(url_for('allmedicamentos', mensaje='No se encontró el medicamento a eliminar'))
    
    
@app.route('/admin/medicamentos/archivados')
@login_required
@admin_required
def archivedMedicamentos():
    # Realizar consulta SQL para obtener los registros
    sql = "SELECT * FROM tbl_medicamento "
    cursor = mysql.connection.cursor()
    cursor.execute(sql)
    medicamentos = cursor.fetchall()

    # Cerrar el cursor
    cursor.close()

    mensaje = request.args.get('mensaje')  # Obtener el mensaje de la URL si existe

    # Renderizar la plantilla alldocs.html y pasar la lista de usuarios y el mensaje
    return render_template('admin/medicamentos/archived.html', medicamentos=medicamentos, mensaje=mensaje)
 













#######################################
## EXAMENES ##

## Listar todos los Exámenes
@app.route('/admin/examenes/allexamenes')
@login_required
@admin_required
def allexamenes():
    # Realizar consulta SQL para obtener los registros
    sql = "SELECT * FROM tbl_examen"
    cursor = mysql.connection.cursor()
    cursor.execute(sql)
    examenes = cursor.fetchall()

    # Cerrar el cursor
    cursor.close()

    mensaje = request.args.get('mensaje')  # Obtener el mensaje de la URL si existe

    # Renderizar la plantilla y pasar la lista de usuarios y el mensaje
    return render_template('admin/examenes/allexamenes.html', examenes=examenes, mensaje=mensaje)


## Crear un Exámen
@app.route('/admin/examenes/create')
@login_required
@admin_required
def createexamenes():
    return render_template('admin/examenes/create.html')

@app.route('/exaStr', methods=['POST'])
@login_required
@admin_required
def storageexa():
    _nombre=request.form['txtnombre']
    _descripcion=request.form['txtdescripcion']
    _active=request.form['active']
    
    
    sql ="INSERT INTO `tbl_examen` (`s_nombreExamen`, `s_descripcion`,`b_activo`) VALUES (%s, %s, %s);"
    
     
    datos=(_nombre, _descripcion,_active )
    
    # Ejecutar la sentencia SQL
    cursor = mysql.connection.cursor()
    cursor.execute(sql, datos)

    # Confirmar los cambios en la base de datos
    mysql.connection.commit()

    # Cerrar el cursor
    cursor.close()


    # Redirigir o mostrar un mensaje de éxito
    return render_template('admin/examenes/create.html', mensaje="Exámen creado exitosamente")



## Editar Medicamento
@app.route('/admin/examenes/edit/<int:id>')
@login_required
@admin_required
def editExa(id):
    
    sql = "SELECT * FROM tbl_examen WHERE id_examen = %s"
    cursor = mysql.connection.cursor()
    cursor.execute(sql, (id,))
    examenes = cursor.fetchone()

    # Cerrar el cursor
    cursor.close()
    
    success = request.args.get('success', False)  # Obtener el valor del parámetro 'success' de la URL
    
    return render_template('admin/examenes/edit.html', examenes=examenes, success=success)



## Up date
@app.route('/exaUpdate', methods=['POST'])
@login_required
@admin_required
def exaUpdate():
    
    if request.method == 'POST':
        _nombre=request.form['txtnombre']
        _descripcion=request.form['txtdescripcion']
        _idexamen=request.form['txtid']
        _active = int(request.form.get('active'))

        sql = "UPDATE `tbl_examen` SET `s_nombreExamen` = %s, `s_descripcion` = %s, `b_activo` = %s  WHERE `id_examen` = %s"

        datos = (_nombre, _descripcion, _active, _idexamen)

       # Ejecutar la sentencia SQL
        cursor = mysql.connection.cursor()
        cursor.execute(sql, datos)

        # Confirmar los cambios en la base de datos
        mysql.connection.commit()

        # Cerrar el cursor
        cursor.close()
         
        return redirect(url_for('editExa', id=_idexamen, success=True))



    else:
        # Obtener el ID del médico a partir de los parámetros de la URL
        examen_id = request.args.get('examen_id')

        # Obtener el médico de la base de datos utilizando el ID y mostrar el formulario edit.html
        return render_template('edit.html', examen_id=examen_id, success=False)


    
@app.route('/medico/examenes/delete/<int:id>', methods=['POST'])
@login_required
@medic_required
def deleteExamen(id):
    # Verificar si el examen existe en la base de datos
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM tbl_examen WHERE id_examen = %s', (id,))
    examenes = cursor.fetchone()
    if examenes:
        # Actualizar el estado del campo b_activo a 0 (inactivo)
        cursor.execute('UPDATE tbl_examen SET b_activo = 0 WHERE id_examen = %s', (id,))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('allexamenes', mensaje='Examen eliminado exitosamente'))
    else:
        cursor.close()
        return redirect(url_for('allexamenes', mensaje='No se encontró el examen a eliminar'))
    
    
    
    
@app.route('/admin/examenes/archivados')
@login_required
@admin_required
def archivedExamen():
    # Realizar consulta SQL para obtener los registros
    sql = "SELECT * FROM tbl_examen"
    cursor = mysql.connection.cursor()
    cursor.execute(sql)
    examenes = cursor.fetchall()

    # Cerrar el cursor
    cursor.close()

    mensaje = request.args.get('mensaje')  # Obtener el mensaje de la URL si existe

    # Renderizar la plantilla alldocs.html y pasar la lista de usuarios y el mensaje
    return render_template('admin/examenes/archived.html', examenes=examenes, mensaje=mensaje)
 












## Rutas para el perfil MEDICO
@app.route('/medico')
def medico():
    mensaje = session.pop('mensaje', None)
    return render_template('medico/medico.html', mensaje=mensaje)


## Crear un Paciente
@app.route('/medico/paciente/create')
@login_required
@medic_required
def createPac():
    return render_template('/medico/paciente/create.html')

@app.route('/pacienteStr', methods=['POST'])
@login_required
@medic_required
def storagePac():
    _rut=request.form['txtrut']
    _datenacimiento=request.form['txtdate']
    _nombre=request.form['txtnombre']
    _apellidopa=request.form['txtpaterno']
    _apellidoma=request.form['txtmaterno']
    _genero=request.form['txtgenero']
    _pacactive=request.form['active']
    
    
    sql ="INSERT INTO `tbl_paciente` (`d_fechaNacimiento`,`s_rutPaciente`,`s_nombrePaciente`, `s_apellidoPaterno`,`s_apellidoMaterno`, `fk_id_genero`,`b_activo`) VALUES (%s, %s, %s, %s, %s, %s, %s);"
    
     
    datos=(_datenacimiento, _rut, _nombre, _apellidopa,_apellidoma,_genero,_pacactive)
    
    # Ejecutar la sentencia SQL
    cursor = mysql.connection.cursor()
    cursor.execute(sql, datos)

    # Confirmar los cambios en la base de datos
    mysql.connection.commit()

    # Cerrar el cursor
    cursor.close()


    # Redirigir o mostrar un mensaje de éxito
    return render_template('/medico/paciente/create.html', mensaje="Paciente creado exitosamente")



## Listar todos los Pacientes
@app.route('/medico/paciente/allpac')
@login_required
@medic_required
def allPac():
    # Realizar consulta SQL para obtener los registros con b_activo = 1
    sql = "SELECT * FROM tbl_paciente"
    cursor = mysql.connection.cursor()
    cursor.execute(sql)
    pacientes = cursor.fetchall()

    # Cerrar el cursor
    cursor.close()

    mensaje = request.args.get('mensaje')  # Obtener el mensaje de la URL si existe

    return render_template('/medico/paciente/allpac.html', pacientes=pacientes, mensaje=mensaje)

## Ver información del doctor
@app.route('/medico/paciente/<int:id>')
@login_required
@medic_required
def showPac(id):
    # Realizar consulta SQL para obtener la información del paciente en función de su ID
    sql = "SELECT * FROM tbl_paciente WHERE id_paciente = %s"
    cursor = mysql.connection.cursor()
    cursor.execute(sql, (id,))
    paciente = cursor.fetchone()

    # Cerrar el cursor 
    cursor.close()

    return render_template('medico/paciente/show.html', paciente=paciente, paciente_id=id)










## Editar Paciente
@app.route('/medico/paciente/edit/<int:id>')
@login_required
@medic_required
def editPac(id):
    
    sql = "SELECT * FROM tbl_paciente WHERE id_paciente = %s"
    cursor = mysql.connection.cursor()
    cursor.execute(sql, (id,))
    pacientes = cursor.fetchone()

    # Cerrar el cursor
    cursor.close()
    
    success = request.args.get('success', False)  # Obtener el valor del parámetro 'success' de la URL
    
    return render_template('/medico/paciente/edit.html', pacientes=pacientes, success=success)



## Up date
@app.route('/pacUpdate', methods=['POST'])
@login_required
@medic_required
def pacUpdate():
    
    if request.method == 'POST':
        _rut=request.form['txtrut']
        _datenacimiento=request.form['txtdate']
        _nombre=request.form['txtnombre']
        _apellidopa=request.form['txtpaterno']
        _apellidoma=request.form['txtmaterno']
        _idpaciente = request.form.get('txtid')
        _genero  = int(request.form.get('txtgenero'))
        _pacactive  = int(request.form.get('txtactive'))



        sql = "UPDATE `tbl_paciente` SET `d_fechaNacimiento` = %s, `s_rutPaciente` = %s, `s_nombrePaciente` = %s, `s_apellidoPaterno` = %s, `s_apellidoMaterno` = %s, `fk_id_genero` = %s, `b_activo` = %s  WHERE `id_paciente` = %s"

        datos = (_datenacimiento, _rut, _nombre, _apellidopa, _apellidoma, _genero, _pacactive, _idpaciente)


       # Ejecutar la sentencia SQL
        cursor = mysql.connection.cursor()
        cursor.execute(sql, datos)

        # Confirmar los cambios en la base de datos
        mysql.connection.commit()

        # Cerrar el cursor
        cursor.close()
         
        return redirect(url_for('editPac', id=_idpaciente, success=True))



    else:
        # Obtener el ID del paciente a partir de los parámetros de la URL
        paciente_id = request.args.get('paciente_id')

        # Obtener el paciente de la base de datos utilizando el ID y mostrar el formulario edit.html
        return render_template('edit.html', paciente_id=paciente_id, success=False)



## Eliminar paciente
@app.route('/medico/paciente/delete/<int:id>', methods=['POST'])
@login_required
@medic_required
def deletePaciente(id):
    # Verificar si el paciente existe en la base de datos
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM tbl_paciente WHERE id_paciente = %s', (id,))
    paciente = cursor.fetchone()
    if paciente:
        # Actualizar el estado del campo b_activo a 0 (inactivo)
        cursor.execute('UPDATE tbl_paciente SET b_activo = 0 WHERE id_paciente = %s', (id,))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('allPac', mensaje='Paciente eliminado exitosamente'))
    else:
        cursor.close()
        return redirect(url_for('allPac', mensaje='No se encontró el paciente a eliminar'))
    
    
    
@app.route('/medico/paciente/archivados')
@login_required
@medic_required
def archivedPaciente():
    # Realizar consulta SQL para obtener los registros
    sql = "SELECT * FROM tbl_paciente WHERE b_activo = 0"
    cursor = mysql.connection.cursor()
    cursor.execute(sql)
    pacientes = cursor.fetchall()

    # Cerrar el cursor
    cursor.close()

    mensaje = request.args.get('mensaje')  # Obtener el mensaje de la URL si existe

    if not pacientes:  # Verificar si la lista de pacientes está vacía
        pacientes = []  # Establecer una lista vacía en lugar de registros vacíos

    # Renderizar la plantilla allpac.html y pasar la lista de pacientes y el mensaje
    return render_template('medico/paciente/archived.html', pacientes=pacientes, mensaje=mensaje)




@app.route('/medico/paciente/<int:paciente_id>/ficha_medica/create', methods=['GET', 'POST'])
@login_required
@medic_required
def createFichaMedica(paciente_id):
    if request.method == 'POST':
        _descripcion = request.form['txtdescripcion']
        
        # Verificar si el paciente ya tiene una ficha médica
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM tbl_fichamedica WHERE fk_id_paciente = %s", (paciente_id,))
        ficha_medica = cursor.fetchone()
        if ficha_medica:
            # Si el paciente ya tiene una ficha médica, redirigir o mostrar un mensaje de error
            return render_template('/medico/paciente/create_ficha_medica.html', mensaje="El paciente ya tiene una ficha médica", paciente_id=paciente_id)
        
        # Insertar la nueva ficha médica en la base de datos
        sql = "INSERT INTO tbl_fichamedica (s_descripcion, fk_id_paciente) VALUES (%s, %s);"
        datos = (_descripcion, paciente_id)
        cursor.execute(sql, datos)
        mysql.connection.commit()
        
        # Obtener el ID de la ficha médica recién creada
        ficha_medica_id = cursor.lastrowid
        
        # Actualizar el campo fk_id_fichaMedica en la tabla tbl_paciente
        sql_update = "UPDATE tbl_paciente SET fk_id_fichaMedica = %s WHERE id_paciente = %s"
        cursor.execute(sql_update, (ficha_medica_id, paciente_id))
        mysql.connection.commit()
        
        cursor.close()
        
        # Redirigir o mostrar un mensaje de éxito
        return render_template('/medico/paciente/create_ficha_medica.html', mensaje="Ficha médica creada exitosamente", paciente_id=paciente_id)
    
    return render_template('/medico/paciente/create_ficha_medica.html', paciente_id=paciente_id)




@app.route('/medico/paciente/<int:paciente_id>/ficha_medica/<int:ficha_medica_id>')
@login_required
@medic_required
def showFichaMedica(paciente_id, ficha_medica_id):
    # Realizar consulta SQL para obtener los detalles de la ficha médica
    sql_ficha = "SELECT * FROM tbl_fichamedica WHERE id_fichaMedica = %s AND fk_id_paciente = %s"
    cursor = mysql.connection.cursor()
    cursor.execute(sql_ficha, (ficha_medica_id, paciente_id))
    ficha_medica = cursor.fetchone()

    # Realizar consulta SQL para obtener los datos del paciente
    sql_paciente = "SELECT * FROM tbl_paciente WHERE id_paciente = %s"
    cursor.execute(sql_paciente, (paciente_id,))
    paciente = cursor.fetchone()

    # Cerrar el cursor
    cursor.close()

    return render_template('medico/ficha_medica/show.html', ficha_medica=ficha_medica, paciente=paciente)


def tieneFichaMedica(paciente_id):
    # Realizar consulta SQL para verificar si el paciente tiene una ficha médica
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM tbl_fichamedica WHERE fk_id_paciente = %s", (paciente_id,))
    ficha_medica = cursor.fetchone()
    cursor.close()
    
    # Verificar si se encontró una ficha médica para el paciente
    if ficha_medica:
        return True
    else:
        return False
    


if __name__ == '__main__':
    app.secret_key="marioh"
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True) 