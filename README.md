# Gestión de Catequesis Parroquial

Este proyecto es una aplicación web desarrollada en Django que facilita la gestión de las catequesis en una organización parroquial. La aplicación permite gestionar inscripciones, usuarios, materiales y comunicaciones, mejorando la eficiencia y organización de las actividades catequéticas.

## Resumen de la Aplicación

Alguna de las funcionalidades que incluye la aplicación son:

- Gestión de inscripciones y datos de catequistas y catecúmenos.
- Administración de sesiones y los materiales necesarios.
- Envío de comunicaciones y notificaciones.
- Control de asistencia a las sesiones de catequesis.
- Gestión de salas y eventos.

## Manual de Instalación

### Prerrequisitos

Asegúrate de tener instalado lo siguiente:

- Python 3.8 o superior
- PostgreSQL

### Instalación en Local

1. **Clona el repositorio:**

    ```bash
    git clone https://github.com/antoniopelaezmoreno/proyecto_parroquia.git
    ```

2. **Crea y activa un entorno virtual:**

    ```bash
    python -m venv venv
    source venv/bin/activate  # En Windows usa `venv\Scripts\activate`
    ```

3. **Instala las dependencias:**

    ```bash
    cd 'ruta_al_proyecto'
    pip install -r requirements.txt
    ```

4. **Configura las variables de entorno en el archivo `.env`:**

    Crea un archivo `.env` en el directorio raíz del proyecto y añade las siguientes variables:

    ```plaintext
    ALLOWED_HOSTS="localhost 127.0.0.1"
    DEBUG=True
    SECRET_KEY=tu_clave_secreta_django
    GOOGLE_SECRET_KEY=clave_de_encriptación_fernet
    OAUTHLIB_INSECURE_TRANSPORT = 1
    ```

    Si no tienes clave de encriptación, puedes generar una aquí: https://8gwifi.org/fernet.jsp
    
    Si no tienes clave secreta de django, puedes generar una aquí: https://djecrety.ir/
### Configuración del Proyecto de Google Cloud

1. **Crea un nuevo proyecto en Google Cloud.**

2. **Habilita las APIs de Gmail y Google Calendar:**

    - Con el proyecto seleccionado, en la consola de Google CLoud, abre el menú lateral, entra en la sección "APIs y servicios" > "Biblioteca".
    - Busca y habilita las APIs de Gmail y Google Calendar.

3. **Crea una página de consentimiento:**

    - En el menú lateral, entra en la sección "APIs y servicios" > "Pantalla de consentimiento de OAuth", selecciona el tipo de usuario 'Externo' y pulsa en crear.
    - Rellena el formulario completando los campos.
    - En el apartado de 'Permisos' o 'Scopes' en ingles, debes añadir los correspondientes a leer y redactar emails y a los eventos de calendario, es decir:
        + "/auth/gmail.readonly"
        + "/auth/gmail.send"
        + "/auth/gmail.modify"
        + "/auth/calendar"
    - Es importante que en el apartado 'Usuarios de prueba' añadas los correos que vas a usar para utilizar la aplicación mientras se encuentre en estado de testeo.

4. **Crea credenciales de acceso:**

    - En el menú lateral, entra en la sección "APIs y servicios" > "Credenciales" y pulsa en 'Crear Credenciales'
    - Debes seleccionar el tipo de credencial 'ID de clientes OAuth'
    - Rellena los campos del formulario.
    - En el apartado 'URI de redireccionamiento autorizados' incluye:
        + "http://localhost:8000/auth/google/callback"
        + "http://127.0.0.1:8000/auth/google/callback"

    Ten en cuenta que el puerto 8000 debe cambiarse en caso de que ejecutes el proyecto en otro puerto.

    Si quieres desplegar el proyecto en la nube, debes añadir una nueva URI con la siguiente estructura: "https://[tu_dominio]/auth/google/callback"

5. **Descarga el archivo de credenciales JSON y añadelo a la carpeta raíz del código del proyecto con el nombre "credentials.json".

### Configuración de la Base de Datos PostgreSQL

1. **Crea una base de datos PostgreSQL:**

    ```sql
    CREATE DATABASE parroquiaDB;
    CREATE USER parroquiaUser WITH PASSWORD 'password';
    ALTER ROLE parroquiaUser SET client_encoding TO 'utf8';
    ALTER ROLE parroquiaUser SET default_transaction_isolation TO 'read committed';
    ALTER ROLE parroquiaUser SET timezone TO 'UTC';
    GRANT ALL PRIVILEGES ON DATABASE parroquiaDB TO parroquiaUser;
    ```
    Este paso puede ser más sencillo en una herramienta como pgAdmin o dbeaver.

2. **Aplica las migraciones de la base de datos:**

    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

### Ejecución de la Aplicación

1. **Crea un superusuario para acceder al panel de administración:**

    ```bash
    python manage.py createsuperuser
    ```
    - Introduce email y contraseña. Ten en cuenta que para usar las funcionalidades de correo y calendario, el email introducido debe estar en la lista de 'Usuarios de prueba' de tu proyecto de Google Cloud
2. **Inicia el servidor de desarrollo:**

    ```bash
    python manage.py runserver
    ```

    Accede a la aplicación en `http://localhost:8000`. #El número 8000 debes cambiarlo por el puerto en el que hayas ejecutado la aplicación

¡Y eso es todo! Ahora deberías tener la aplicación de gestión de catequesis en funcionamiento en tu entorno local.
