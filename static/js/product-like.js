document.addEventListener("submit", function (event) {
    var form = event.target.closest(".product-like-form");
    if (!form) {
        return;
    }
    event.preventDefault();
    if (form.dataset.busy === "true") {
        return;
    }
    form.dataset.busy = "true";

    fetch(form.action, {
        method: "POST",
        body: new FormData(form),
        headers: { "X-Requested-With": "XMLHttpRequest" },
        credentials: "same-origin",
    })
        .then(function (response) {
            if (response.status === 401) {
                form.submit();
                return null;
            }
            if (!response.ok) {
                throw new Error("Gagal menyimpan like");
            }
            return response.json();
        })
        .then(function (data) {
            if (!data) {
                return;
            }
            document.querySelectorAll('.product-like-form[action="' + form.getAttribute("action") + '"]').forEach(function (other) {
                var otherButton = other.querySelector("button");
                otherButton.classList.toggle("is-liked", data.liked);
                otherButton.setAttribute("aria-pressed", data.liked ? "true" : "false");
                otherButton.querySelector(".like-count").textContent = data.like_count;
            });
        })
        .catch(function () {
            form.submit();
        })
        .finally(function () {
            form.dataset.busy = "false";
        });
});