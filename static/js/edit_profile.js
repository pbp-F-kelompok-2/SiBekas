document.addEventListener("DOMContentLoaded", function () {
    function openModal() {
        const modal = document.getElementById("editProfileModal");

        if (!modal) return;

        modal.classList.add("is-open");
        document.body.style.overflow = "hidden";
    }

    function closeModal() {
        const modal = document.getElementById("editProfileModal");

        if (!modal) return;

        modal.classList.remove("is-open");
        document.body.style.overflow = "";
    }

    // Membuka modal
    document.addEventListener("click", function (event) {
        if (event.target.closest("#openEditProfile")) {
            openModal();
        }
    });

    // Menutup modal melalui tombol close
    document.addEventListener("click", function (event) {
        if (event.target.closest("#closeEditProfile")) {
            closeModal();
        }
    });

    // Menutup modal jika user klik area overlay
    document.addEventListener("click", function (event) {
        const modal = document.getElementById("editProfileModal");

        if (modal && event.target === modal) {
            closeModal();
        }
    });

    // Menutup modal dengan tombol Escape
    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape") {
            closeModal();
        }
    });

    // Menyesuaikan scroll setelah respons HTMX diterima
    document.body.addEventListener("htmx:afterSwap", function (event) {
        if (event.detail.target.id !== "editProfileModal") return;

        const modal = document.getElementById("editProfileModal");

        if (modal && modal.classList.contains("is-open")) {
            document.body.style.overflow = "hidden";
        } else {
            document.body.style.overflow = "";
        }
    });

    // Jika halaman dibuka kembali dengan form yang memiliki error
    const modal = document.getElementById("editProfileModal");

    if (modal && modal.classList.contains("is-open")) {
        document.body.style.overflow = "hidden";
    }
});