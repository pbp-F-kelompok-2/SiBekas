
document.addEventListener("DOMContentLoaded", function () {
    const openButton = document.getElementById("openEditProfile");
    const modal = document.getElementById("editProfileModal");
    const closeButton = document.getElementById("closeEditProfile");

    if (!openButton || !modal || !closeButton) {
        console.error("Tombol atau modal edit profil tidak ditemukan.");
        return;
    }

    openButton.addEventListener("click", function () {
        modal.style.display = "flex";
        document.body.style.overflow = "hidden";
    });

    function closeModal() {
        modal.style.display = "none";
        document.body.style.overflow = "";
    }

    closeButton.addEventListener("click", closeModal);

    modal.addEventListener("click", function (event) {
        if (event.target === modal) {
            closeModal();
        }
    });

    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape") {
            closeModal();
        }
    });
});
