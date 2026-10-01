const navToggle =
    document.getElementById("nav-toggle");

const navMenu =
    document.getElementById("nav-menu");

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

            navToggle.innerHTML = isOpen
                ? '<i data-lucide="x"></i>'
                : '<i data-lucide="menu"></i>';

            lucide.createIcons();
        }
    );
}