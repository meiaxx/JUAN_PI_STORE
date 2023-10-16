/*

Sanitization of form fields:

field requirements:
1) for the name that only allows characters with a maximum of 10
2) for the same surname
3) for the phone (which will be the user) a maximum and minimum of 11
4) mail regex
5) Maximum password of 12 and minimum of 8, the password must contain characters, numbers and symbols

*/ 

document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('registro-form');

    // Add an 'input' event to all input fields
    const camposDeEntrada = form.querySelectorAll('input[type="text"], input[type="email"], input[type="tel"], input[type="password"]');
    camposDeEntrada.forEach(function (campo) {
        campo.addEventListener('input', function () {
            validarCampo(this);
        });
    });

    // Function to validate an individual field
    function validarCampo(campo) {
        const valor = campo.value.trim();
        const id = campo.id;
        const mensajeError = document.getElementById(id + '-error');

        // Delete any existing error messages
        mensajeError.innerHTML = '';

        // Perform specific validations based on the field
        switch (id) {
            case 'nombre':
                // Validate name (maximum 10 characters)
                if (valor.length > 10) {
                    mensajeError.innerHTML = 'El nombre debe tener un máximo de 10 caracteres.';
                }
                break;
            case 'apellido':
                // Validate surname (maximum 10 caracteres)
                if (valor.length > 10) {
                    mensajeError.innerHTML = 'El apellido debe tener un máximo de 10 caracteres.';
                }
                break;
            case 'telefono':
                // Validate phone (minimum and maximum of 11 characters, numbers only)
                if (valor.length !== 11 || isNaN(valor)) {
                    mensajeError.innerHTML = 'El teléfono debe tener 11 dígitos y contener solo números.';
                }
                break;
            case 'correo':
                // Validate mail (uses HTML5 validation)
                if (!campo.checkValidity()) {
                    mensajeError.innerHTML = 'Ingrese una dirección de correo válida.';
                }
                break;
            case 'contrasena':
                // Validate password (minimum 8 characters, maximum 12, letters, numbers and symbols)
                if (!/^(?=.*[a-zA-Z])(?=.*\d)(?=.*[\W_]).{8,12}$/.test(valor)) {
                    mensajeError.innerHTML = 'La contraseña debe tener entre 8 y 12 caracteres y contener al menos una letra, un número y un símbolo.';
                }
                break;
        }
    }
});

/* Hide And Show Password */
const ShowPassword = document.querySelector("#show-password");
const passwordField = document.querySelector("#contrasena");

ShowPassword.addEventListener("click",function(){
    if(passwordField.type === "password"){
        passwordField.type = "text";
        ShowPassword.classList.remove('fa-eye');
        ShowPassword.classList.add('fa-eye-slash')
    }
    else{
        passwordField.type = "password";
        ShowPassword.classList.remove('fa-eye-slash');
        ShowPassword.classList.add('fa-eye');
    }

})


/* Confirm Password */
const confirmPassword = document.querySelector("#confirmar-contrasena");
const ShowPassword2 = document.querySelector("#show-password2");


ShowPassword2.addEventListener("click",function(){
    if(confirmPassword.type === "password"){
        confirmPassword.type = "text";
        ShowPassword2.classList.remove('fa-eye');
        ShowPassword2.classList.add('fa-eye-slash')
    }
    else{
        confirmPassword.type = "password";
        ShowPassword2.classList.remove('fa-eye-slash');
        ShowPassword2.classList.add('fa-eye');
    }
})

