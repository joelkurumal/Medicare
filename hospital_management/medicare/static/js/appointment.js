
document.addEventListener("DOMContentLoaded", function () {

    const departmentSelect = document.getElementById("id_department");
    const doctorSelect = document.getElementById("id_doctor");

    if (!departmentSelect || !doctorSelect) {
        return;
    }

    departmentSelect.addEventListener("change", function () {

        const departmentId = this.value;

        doctorSelect.innerHTML =
            '<option value="">Loading doctors...</option>';

        if (!departmentId) {
            doctorSelect.innerHTML =
                '<option value="">Select Department First</option>';
            return;
        }

        fetch(`/get-doctors/?department_id=${encodeURIComponent(departmentId)}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error("Unable to load doctors");
                }
                return response.json();
            })
            .then(data => {

                doctorSelect.innerHTML =
                    '<option value="">Select Doctor</option>';

                if (data.doctors.length === 0) {
                    doctorSelect.innerHTML =
                        '<option value="">No doctors available</option>';
                    return;
                }

                data.doctors.forEach(doctor => {

                    const option = document.createElement("option");

                    option.value = doctor.id;
                    option.textContent =
                        `${doctor.name} - ${doctor.specialization}`;

                    doctorSelect.appendChild(option);
                });

            })
            .catch(error => {
                console.error(error);

                doctorSelect.innerHTML =
                    '<option value="">Could not load doctors</option>';
            });

    });

});
