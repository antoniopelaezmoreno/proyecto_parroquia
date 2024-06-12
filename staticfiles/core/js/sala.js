document.addEventListener("DOMContentLoaded", function () {
    const openModalBtns = document.querySelectorAll(".openModalBtn");
    const modal = document.getElementById("myModal");
    const closeModal = document.querySelector(".close");
    const avisoAprobacion = document.getElementById("avisoAprobacion");
    const mensajeConfirmacionElement = document.getElementById(
        "mensajeConfirmacion"
    );
    const reservarBtn = document.getElementById("reservarBtn");
    const fechaInput = document.getElementById("fecha");
    const horaInicioSelect = document.getElementById("hora_inicio");
    const horaFinSelect = document.getElementById("hora_fin");
    const guardarBtn = document.getElementById("guardarBtn");

    // Rellenar los selectores de hora
    for (let hora = 8; hora < 24; hora++) {
        for (let minuto = 0; minuto < 60; minuto += 30) {
            let hora_str = (hora < 10 ? "0" : "") + hora;
            let minuto_str = minuto === 0 ? "00" : minuto;
            let opcion = document.createElement("option");
            opcion.text = hora_str + ":" + minuto_str;
            opcion.value = hora_str + ":" + minuto_str;
            horaInicioSelect.add(opcion);
            horaFinSelect.add(opcion.cloneNode(true)); // Clonamos la opción para el selector de fin
        }
    }

    const fechaActual = new Date().toISOString().split("T")[0];
    fechaInput.min = fechaActual;

    openModalBtns.forEach(function (btn) {
        btn.addEventListener("click", function () {
            const sala = btn.getAttribute("data-sala-nombre");
            const salaId = btn.getAttribute("data-sala-id");
            const requiereAprobacion = btn.getAttribute("data-sala-aprobacion");
            let fecha = sessionStorage.getItem("fechaSeleccionada");
            let inicio = sessionStorage.getItem("horaInicioSeleccionada");
            let fin = sessionStorage.getItem("horaFinSeleccionada");
            mensajeConfirmacionElement.textContent =
                "Va a reservar la sala " +
                sala +
                " para el día " +
                fecha +
                " desde las " +
                inicio +
                " hasta las " +
                fin;
            modal.style.display = "block";

            if (requiereAprobacion == "True") {
                avisoAprobacion.textContent = "Esta sala requiere aprobación";
                document.getElementById("motivoLabel").style.display = "block";
                document.getElementById("motivo").style.display = "block";
                document.getElementById("motivoError").style.display = "block";
            } else {
                avisoAprobacion.textContent = "";
                document.getElementById("motivoLabel").style.display = "none";
                document.getElementById("motivo").style.display = "none";
                document.getElementById("motivoError").style.display = "none";
            }

            reservarBtn.addEventListener("click", function () {
                console.log("voy a reservar");
                const motivo = document.getElementById("motivo").value;
                const liberar_sala = document.getElementById("liberar_sala").checked;
                reservarSala(salaId, fecha, inicio, fin, motivo, liberar_sala);
            });
        });
    });

    closeModal.addEventListener("click", function () {
        modal.style.display = "none";
    });

    window.addEventListener("click", function (event) {
        if (event.target === modal) {
            modal.style.display = "none";
        }
    });

    // Al cargar la página, establecer los valores seleccionados en los selectores de hora y fecha
    fechaInput.value = sessionStorage.getItem("fechaSeleccionada") || "";
    horaInicioSelect.value =
        sessionStorage.getItem("horaInicioSeleccionada") || "";
    horaFinSelect.value = sessionStorage.getItem("horaFinSeleccionada") || "";

    // Guardar los valores seleccionados en sessionStorage cuando se cambian
    fechaInput.addEventListener("change", function () {
        const fechaSeleccionada = this.value;
        if (fechaSeleccionada < fechaActual) {
            alert("No se puede seleccionar una fecha anterior a la actual");
            guardarBtn.disabled = true;
            this.value = fechaActual;
        } else {
            sessionStorage.setItem("fechaSeleccionada", fechaSeleccionada);
            guardarBtn.disabled = false;
        }
    });

    horaInicioSelect.addEventListener("change", function () {
        horaFin = horaFinSelect.value;
        horaInicio = this.value;
        if (horaFin && horaInicio) {
            if (horaInicio >= horaFin) {
                alert("La hora de inicio debe ser anterior a la hora de fin");
                guardarBtn.disabled = true;
            } else {
                sessionStorage.setItem("horaInicioSeleccionada", this.value);
                guardarBtn.disabled = false;
            }
        } else if (horaInicio) {
            sessionStorage.setItem("horaInicioSeleccionada", this.value);
        }
    });

    horaFinSelect.addEventListener("change", function () {
        horaFin = this.value;
        horaInicio = horaInicioSelect.value;
        if (horaFin && horaInicio) {
            if (horaInicio >= horaFin) {
                alert("La hora de inicio debe ser anterior a la hora de fin");
                guardarBtn.disabled = true;
            } else {
                sessionStorage.setItem("horaFinSeleccionada", this.value);
                guardarBtn.disabled = false;
            }
        } else if (horaFin) {
            sessionStorage.setItem("horaFinSeleccionada", this.value);
        }
    });
});

function reservarSala(salaId, fecha, horaInicio, horaFin, motivo, liberar_sala) {
    let formData = new FormData();
    formData.append("sala_id", salaId);
    formData.append("fecha", fecha);
    formData.append("hora_inicio", horaInicio);
    formData.append("hora_fin", horaFin);
    formData.append("motivo", motivo);
    formData.append("liberar_sala", liberar_sala);

    const motivoError = document.getElementById("motivoError");
    const motivoInput = document.getElementById("motivo");

    if (motivo.length === 0 && motivoInput.style.display !== "none") {
        motivoError.textContent = "Debe ingresar un motivo para la reserva";
        motivoError.style.display = "block";
        motivoInput.style.borderColor = "red";
        return;
    } else if (motivo.length > 250 && motivoInput.style.display !== "none") {
        motivoError.textContent = "El motivo no puede tener más de 250 caracteres";
        motivoError.style.display = "block";
        motivoInput.style.borderColor = "red";
        return;
    } else {
        motivoError.textContent = ""; // Limpiar el mensaje de error si no hay problemas
        motivoError.style.display = "none";
        motivoInput.style.borderColor = ""; // Restaurar el color del borde
    }

    // Enviar la solicitud POST utilizando fetch
    fetch("/sala/reservar/", {
        method: "POST",
        body: formData,
        headers: {
            "X-CSRFToken": getCookie("csrftoken"), // Obtener el token CSRF de las cookies
        },
    })
        .then((response) => {
            if (response.ok) {
                console.log("Reserva creada correctamente");
                window.location.href = "/sala/mis_reservas/";
            } else {
                console.error("Error al crear la reserva");
            }
        })
        .catch((error) => {
            console.error("Error al crear la reserva:", error);
        });
    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(";").shift();
    }
}
