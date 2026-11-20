
document.addEventListener("DOMContentLoaded", function () {

    const modal = document.getElementById("doctorAppointmentModal");

    if (!modal) {
        return;
    }

    const doctorIdInput = document.getElementById("modalDoctorId");
    const doctorName = document.getElementById("appointmentDoctorName");

    const dateInput = document.getElementById("modalAppointmentDate");
    const timeInput = document.getElementById("modalAppointmentTime");
    const reasonInput = document.getElementById("modalAppointmentReason");

    const appointmentForm = document.getElementById("doctorAppointmentForm");


    // Get today's date in local YYYY-MM-DD format
    function getLocalDate() {

        const today = new Date();

        const year = today.getFullYear();
        const month = String(today.getMonth() + 1).padStart(2, "0");
        const day = String(today.getDate()).padStart(2, "0");

        return `${year}-${month}-${day}`;
    }


    // Get current local time in HH:MM format
    function getLocalTime() {

        const now = new Date();

        const hours = String(now.getHours()).padStart(2, "0");
        const minutes = String(now.getMinutes()).padStart(2, "0");

        return `${hours}:${minutes}`;
    }


    // Update minimum selectable date and time
    function updateDateAndTimeLimits() {

        const today = getLocalDate();

        dateInput.min = today;

        if (dateInput.value === today) {
            timeInput.min = getLocalTime();
        } else {
            timeInput.removeAttribute("min");
        }
    }


    // Set initial date restrictions
    updateDateAndTimeLimits();


    // Open appointment modal
    modal.addEventListener("show.bs.modal", function (event) {

        const trigger = event.relatedTarget;

        if (!trigger) {
            return;
        }

        const selectedDoctorId = trigger.dataset.doctorId || "";
        const selectedDoctorName = trigger.dataset.doctorName || "Selected Doctor";


        // Reset old form values
        appointmentForm.reset();


        // Set selected doctor AFTER resetting the form
        doctorIdInput.value = selectedDoctorId;

        doctorName.textContent = selectedDoctorName;


        // Reset date and time limits
        updateDateAndTimeLimits();

    });


    // When the appointment date changes
    dateInput.addEventListener("change", function () {

        const today = getLocalDate();

        if (dateInput.value < today) {

            alert("Please select today or a future date.");

            dateInput.value = "";

            timeInput.value = "";

            updateDateAndTimeLimits();

            return;
        }

        // Clear time if it is earlier than the current time
        if (
            dateInput.value === today &&
            timeInput.value &&
            timeInput.value <= getLocalTime()
        ) {
            timeInput.value = "";
        }

        updateDateAndTimeLimits();

    });


    // Validate selected time
    timeInput.addEventListener("change", function () {

        const today = getLocalDate();

        if (
            dateInput.value === today &&
            timeInput.value &&
            timeInput.value <= getLocalTime()
        ) {

            alert("Please select a future appointment time.");

            timeInput.value = "";

        }

    });


    // Validate form before submitting
    appointmentForm.addEventListener("submit", function (event) {

        if (!doctorIdInput.value) {

            event.preventDefault();

            alert("Please select a doctor.");

            return;
        }


        if (!dateInput.value) {

            event.preventDefault();

            alert("Please select an appointment date.");

            dateInput.focus();

            return;
        }


        if (!timeInput.value) {

            event.preventDefault();

            alert("Please select an appointment time.");

            timeInput.focus();

            return;
        }


        if (dateInput.value < getLocalDate()) {

            event.preventDefault();

            alert("You cannot book an appointment for a past date.");

            return;
        }


        if (
            dateInput.value === getLocalDate() &&
            timeInput.value <= getLocalTime()
        ) {

            event.preventDefault();

            alert("Please select a future appointment time.");

            return;
        }

    });


    // Clear values when modal closes
    modal.addEventListener("hidden.bs.modal", function () {

        appointmentForm.reset();

        doctorIdInput.value = "";

        doctorName.textContent = "Selected Doctor";

        updateDateAndTimeLimits();

    });

});
