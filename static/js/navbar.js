const navToggle =
    document.getElementById(
        "nav-toggle"
    );

const navMenu =
    document.getElementById(
        "nav-menu"
    );


if (navToggle && navMenu) {

    navToggle.addEventListener(
        "click",
        function () {

            const isOpen =
                navMenu.classList.toggle(
                    "nav-menu-open"
                );


            navToggle.setAttribute(
                "aria-expanded",
                String(isOpen)
            );


            navToggle.innerHTML =
                isOpen
                    ? '<i data-lucide="x"></i>'
                    : '<i data-lucide="menu"></i>';


            if (
                typeof lucide !==
                "undefined"
            ) {
                lucide.createIcons();
            }

        }
    );


    navMenu
        .querySelectorAll("a")
        .forEach(function (link) {

            link.addEventListener(
                "click",
                function () {

                    navMenu
                        .classList
                        .remove(
                            "nav-menu-open"
                        );


                    navToggle
                        .setAttribute(
                            "aria-expanded",
                            "false"
                        );

                }
            );

        });

}