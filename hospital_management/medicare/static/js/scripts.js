
document.addEventListener("DOMContentLoaded", function () {

    // Automatically close mobile navbar after clicking a link
    const navLinks = document.querySelectorAll(
        ".navbar-nav .nav-link"
    );

    const navbarMenu = document.getElementById("mainNavbar");

    navLinks.forEach(function (link) {
        link.addEventListener("click", function () {

            if (
                window.innerWidth < 992 &&
                navbarMenu &&
                navbarMenu.classList.contains("show")
            ) {
                const collapse = bootstrap.Collapse.getOrCreateInstance(
                    navbarMenu
                );

                collapse.hide();
            }

        });
    });

    // Automatically hide Bootstrap alerts after 4 seconds
    const alerts = document.querySelectorAll(".alert");

    alerts.forEach(function (alertElement) {
        setTimeout(function () {

            const alert = bootstrap.Alert.getOrCreateInstance(
                alertElement
            );

            alert.close();

        }, 4000);
    });

});
