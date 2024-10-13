document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('login-form');

    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault(); // Evita el envío normal del formulario

            // Obtener los valores de los campos de entrada
            const username = document.getElementById('username').value.trim();
            const password = document.getElementById('password').value.trim();
            const errorMessage = document.getElementById('error-message');
            const successMessage = document.getElementById('success-message');
            
            // Resetear los mensajes de error y éxito
            errorMessage.style.display = 'none';
            errorMessage.textContent = '';
            successMessage.style.display = 'none';

            // Validación en el frontend para asegurarse de que los campos no estén vacíos
            if (!username || !password) {
                errorMessage.textContent = 'Por favor, completa todos los campos.';
                errorMessage.style.display = 'block';
                return; // Evita continuar si los campos están vacíos
            }

            console.log("Username:", username);
            console.log("Password:", password);

            // Enviar los datos al servidor usando fetch
            fetch('/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username: username, password: password })
            })
            .then(response => {
                if (!response.ok) {
                    // Si el servidor devuelve un error, lanzar una excepción
                    return response.json().then(errData => {
                        throw new Error(errData.message || 'Error en la respuesta del servidor');
                    });
                }
                return response.json(); // Convierte la respuesta a JSON
            })
            .then(data => {
                if (data.success) {
                    // Mostrar mensaje de éxito y redirigir a la página principal
                    successMessage.style.display = 'block';
                    successMessage.textContent = 'Inicio de sesión exitoso. Redirigiendo...';
                    setTimeout(() => {
                        window.location.href = data.redirect; // Redirigir a la página principal
                    }, 1500); // Redirigir después de 1.5 segundos
                } else {
                    // Mostrar mensaje de error proporcionado por el backend
                    errorMessage.textContent = data.message || 'Usuario o contraseña incorrectos. Por favor, inténtalo de nuevo.';
                    errorMessage.style.display = 'block';
                }
            })
            .catch(error => {
                console.error('Error:', error); // Loguear el error en la consola
                errorMessage.textContent = 'Ocurrió un error. Por favor, inténtalo de nuevo más tarde.';
                errorMessage.style.display = 'block'; // Mostrar mensaje de error
            });
        });
    }
});
