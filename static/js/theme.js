(function () {
    const root = document.documentElement;
    const toggle = document.getElementById("theme-toggle");

    if (!toggle) return;

    const savedTheme = localStorage.getItem("sibekas-theme");
    const prefersDark = window.matchMedia(
        "(prefers-color-scheme: dark)"
    ).matches;

    function applyTheme(theme) {
        const isDark = theme === "dark";

        root.setAttribute("data-theme", isDark ? "dark" : "light");
        toggle.setAttribute("aria-pressed", String(isDark));
        toggle.setAttribute(
            "aria-label",
            isDark ? "Aktifkan light mode" : "Aktifkan dark mode"
        );

        const icon = toggle.querySelector("i, svg");
        if (icon) {
            icon.setAttribute("data-lucide", isDark ? "sun" : "moon");
            icon.setAttribute("aria-hidden", "true");
        }

        const label = toggle.querySelector(".sb-theme-label");
        if (label) {
            label.textContent = isDark ? "Tema terang" : "Tema gelap";
        }

        if (window.lucide) {
            window.lucide.createIcons();
        }
    }

    applyTheme(savedTheme || (prefersDark ? "dark" : "light"));

    toggle.addEventListener("click", function () {
        const currentTheme = root.getAttribute("data-theme");
        const nextTheme = currentTheme === "dark" ? "light" : "dark";

        localStorage.setItem("sibekas-theme", nextTheme);
        applyTheme(nextTheme);
    });
})();