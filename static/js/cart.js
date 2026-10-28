(function () {

    const statusBox =
        document.getElementById(
            "cart-ajax-status"
        );


    function showStatus(
        message,
        isError = false
    ) {

        if (!statusBox) {
            return;
        }


        statusBox.textContent =
            message || "";


        statusBox.classList.toggle(
            "is-error",
            isError
        );

    }


    function updateCartBadge(
        count
    ) {

        const cartButtons =
            document.querySelectorAll(
                ".sb-cart-button"
            );


        cartButtons.forEach(
            function (button) {

                let badge =
                    button.querySelector(
                        ".sb-cart-badge"
                    );


                if (count > 0) {

                    if (!badge) {

                        badge =
                            document.createElement(
                                "span"
                            );

                        badge.className =
                            "sb-cart-badge";

                        button.appendChild(
                            badge
                        );

                    }


                    badge.textContent =
                        String(count);

                } else if (badge) {

                    badge.remove();

                }


                button.setAttribute(
                    "aria-label",
                    "Keranjang, "
                    + count
                    + " barang"
                );

            }
        );

    }


    function updateSummary(
        data
    ) {

        const subtotal =
            document.getElementById(
                "cart-summary-subtotal"
            );

        const total =
            document.getElementById(
                "cart-summary-total"
            );

        const count =
            document.getElementById(
                "cart-summary-count"
            );


        if (subtotal) {
            subtotal.textContent =
                data.subtotal_display;
        }


        if (total) {
            total.textContent =
                data.subtotal_display;
        }


        if (count) {
            count.textContent =
                String(
                    data.available_count
                );
        }


        updateCartBadge(
            Number(
                data.cart_count || 0
            )
        );

    }


    function updateCheckout(
        data
    ) {

        const area =
            document.getElementById(
                "cart-checkout-area"
            );


        if (!area) {
            return;
        }


        area.innerHTML = "";


        if (
            data.checkout_allowed
        ) {

            const link =
                document.createElement(
                    "a"
                );


            link.href =
                data.checkout_url;


            link.className =
                "cart-checkout-button";


            link.textContent =
                "Lanjut ke checkout";


            area.appendChild(
                link
            );

        } else {

            const paragraph =
                document.createElement(
                    "p"
                );


            paragraph.textContent =
                "Hapus barang yang tidak "
                + "tersedia atau sesuaikan "
                + "jumlahnya sebelum checkout.";


            area.appendChild(
                paragraph
            );

        }

    }


    async function sendAjax(
        form,
        submitter
    ) {

        const formData =
            new FormData(
                form
            );


        if (
            submitter
            && submitter.name
        ) {

            formData.append(
                submitter.name,
                submitter.value
            );

        }


        const url =
            form.getAttribute(
                "action"
            );


        const response =
            await fetch(
                url,
                {
                    method: "POST",

                    body:
                        formData,

                    credentials:
                        "same-origin",

                    headers: {
                        "X-Requested-With":
                            "XMLHttpRequest",
                    },
                }
            );


        let data;


        const contentType =
            response.headers.get(
                "content-type"
            ) || "";


        if (
            !contentType.includes(
                "application/json"
            )
        ) {

            const responseText =
                await response.text();


            console.error(
                "Cart AJAX non-JSON response:",
                response.status,
                responseText
            );


            throw new Error(
                "Gagal memperbarui keranjang "
                + "(HTTP "
                + response.status
                + ")."
            );

        }


        data =
            await response.json();


        if (
            !response.ok
            || !data.success
        ) {

            throw new Error(
                data.message
                || "Permintaan gagal."
            );

        }


        return data;

    }


    function updateQuantityCard(
        form,
        data
    ) {

        const card =
            form.closest(
                ".cart-card"
            );


        if (!card) {
            return;
        }


        const value =
            card.querySelector(
                ".cart-quantity-value"
            );


        const decrease =
            card.querySelector(
                'button[value="decrease"]'
            );


        const increase =
            card.querySelector(
                'button[value="increase"]'
            );


        if (value) {

            value.textContent =
                String(
                    data.quantity
                );

        }


        if (decrease) {

            decrease.disabled =
                data.quantity <= 1;

        }


        if (increase) {

            increase.disabled =
                Boolean(
                    data.max_reached
                );

        }


        let warning =
            card.querySelector(
                ".cart-stock-warning"
            );


        if (
            data.max_reached
        ) {

            if (!warning) {

                warning =
                    document.createElement(
                        "p"
                    );


                warning.className =
                    "cart-stock-warning";


                card
                    .querySelector(
                        ".cart-product-content"
                    )
                    .appendChild(
                        warning
                    );

            }


            warning.textContent =
                "Stok maksimal tercapai "
                + "("
                + data.stock
                + " unit).";

        } else if (warning) {

            warning.remove();

        }

    }


    function removeCartItem(
        data
    ) {

        const selector =
            '[data-cart-item-id="'
            + data.removed_id
            + '"]';


        const item =
            document.querySelector(
                selector
            );


        if (item) {

            const alert =
                item.closest(
                    ".cart-alert"
                );


            item.remove();


            if (
                alert
                && data.unavailable_count === 0
            ) {

                alert.remove();

            }

        }

    }


    document.addEventListener(
        "submit",
        async function (event) {

            const form =
                event.target.closest(
                    "form[data-cart-ajax]"
                );


            if (!form) {
                return;
            }


            event.preventDefault();


            const submitter =
                event.submitter;


            const buttons =
                Array.from(
                    form.querySelectorAll(
                        "button"
                    )
                );


            const originalStates =
                buttons.map(
                    function (button) {
                        return button.disabled;
                    }
                );


            buttons.forEach(
                function (button) {
                    button.disabled = true;
                }
            );


            showStatus("");


            try {

                const data =
                    await sendAjax(
                        form,
                        submitter
                    );


                const action =
                    form.dataset
                        .cartAction;


                if (
                    action === "update"
                ) {

                    updateQuantityCard(
                        form,
                        data
                    );

                }


                if (
                    action === "remove"
                ) {

                    removeCartItem(
                        data
                    );

                }


                updateSummary(
                    data
                );


                updateCheckout(
                    data
                );


                showStatus(
                    data.message
                );


                if (
                    data.cart_empty
                ) {

                    window.location.reload();
                    return;

                }


                if (
                    typeof lucide
                    !== "undefined"
                ) {

                    lucide.createIcons();

                }

            } catch (error) {

                buttons.forEach(
                    function (
                        button,
                        index
                    ) {

                        button.disabled =
                            originalStates[
                            index
                            ];

                    }
                );


                showStatus(
                    error.message,
                    true
                );

            }

        }
    );

})();