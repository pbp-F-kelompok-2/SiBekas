(function () {

    const statusBox =
        document.getElementById(
            "cart-ajax-status"
        );

    const bulkForm =
        document.querySelector(
            "[data-cart-bulk-form]"
        );


    const selectAll =
        document.querySelector(
            "[data-cart-select-all]"
        );


    const selectAllLabel =
        document.querySelector(
            "[data-cart-select-all-label]"
        );


    const selectedCount =
        document.querySelector(
            "[data-cart-selected-count]"
        );


    const deleteSelected =
        document.getElementById(
            "cart-delete-selected"
        );


    const checkoutSelected =
        document.getElementById(
            "cart-checkout-selected"
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
        const checkbox =
            card.querySelector(
                "[data-cart-select-item]"
            );


        if (checkbox) {

            checkbox.dataset
                .cartQuantity =
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

    function getItemCheckboxes() {

        return Array.from(
            document.querySelectorAll(
                "[data-cart-select-item]"
            )
        );

    }


    function getCheckedItems() {

        return getItemCheckboxes()
            .filter(
                function (checkbox) {
                    return checkbox.checked;
                }
            );

    }

    function updateBulkState() {

        const checkboxes =
            getItemCheckboxes();


        const checked =
            getCheckedItems();


        const availableChecked =
            checked.filter(
                function (checkbox) {

                    return (
                        checkbox.dataset
                            .cartAvailable
                        === "true"
                    );

                }
            );


        const hasUnavailable =
            checked.some(
                function (checkbox) {

                    return (
                        checkbox.dataset
                            .cartAvailable
                        !== "true"
                    );

                }
            );


        let selectedSubtotal = 0;


        availableChecked.forEach(
            function (checkbox) {

                const price =
                    Number(
                        checkbox.dataset
                            .cartPrice || 0
                    );


                const quantity =
                    Number(
                        checkbox.dataset
                            .cartQuantity || 0
                    );


                selectedSubtotal +=
                    price * quantity;

            }
        );


        if (selectedCount) {

            selectedCount.textContent =
                checked.length
                + " dipilih";

        }


        if (deleteSelected) {

            deleteSelected.disabled =
                checked.length === 0;

        }


        if (checkoutSelected) {

            checkoutSelected.disabled =
                availableChecked.length === 0
                || hasUnavailable;

        }


        if (selectAll) {

            selectAll.checked =
                checkboxes.length > 0
                && checked.length
                === checkboxes.length;


            selectAll.indeterminate =
                checked.length > 0
                && checked.length
                < checkboxes.length;

        }


        if (selectAllLabel) {

            selectAllLabel.textContent =
                (
                    selectAll
                    && selectAll.checked
                )
                    ? "Batalkan semua"
                    : "Pilih semua";

        }


        const summaryCount =
            document.getElementById(
                "cart-summary-count"
            );


        const summarySubtotal =
            document.getElementById(
                "cart-summary-subtotal"
            );


        const summaryTotal =
            document.getElementById(
                "cart-summary-total"
            );


        const rupiah =
            new Intl.NumberFormat(
                "id-ID"
            ).format(
                selectedSubtotal
            );


        if (summaryCount) {

            summaryCount.textContent =
                String(
                    availableChecked.length
                );

        }


        if (summarySubtotal) {

            summarySubtotal.textContent =
                "Rp " + rupiah;

        }


        if (summaryTotal) {

            summaryTotal.textContent =
                "Rp " + rupiah;

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

                    updateBulkState();

                }


                updateSummary(
                    data
                );


                updateCheckout(
                    data
                );

                updateBulkState();


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

    if (selectAll) {

        selectAll.addEventListener(
            "change",
            function () {

                getItemCheckboxes()
                    .forEach(
                        function (
                            checkbox
                        ) {

                            checkbox.checked =
                                selectAll.checked;

                        }
                    );


                updateBulkState();

            }
        );

    }


    document.addEventListener(
        "change",
        function (event) {

            if (
                event.target.matches(
                    "[data-cart-select-item]"
                )
            ) {

                updateBulkState();

            }

        }
    );


    if (checkoutSelected) {

        checkoutSelected
            .addEventListener(
                "click",
                function () {

                    const checked =
                        getCheckedItems();


                    if (
                        checked.length === 0
                    ) {

                        showStatus(
                            "Pilih minimal satu "
                            + "barang untuk checkout.",
                            true
                        );

                        return;

                    }


                    const unavailable =
                        checked.filter(
                            function (
                                checkbox
                            ) {

                                return (
                                    checkbox
                                        .dataset
                                        .cartAvailable
                                    !== "true"
                                );

                            }
                        );


                    if (
                        unavailable.length > 0
                    ) {

                        showStatus(
                            "Barang yang tidak "
                            + "tersedia tidak dapat "
                            + "di-checkout.",
                            true
                        );

                        return;

                    }


                    const url =
                        new URL(
                            checkoutSelected
                                .dataset
                                .checkoutUrl,

                            window.location.origin
                        );


                    checked.forEach(
                        function (
                            checkbox
                        ) {

                            url.searchParams
                                .append(
                                    "item",
                                    checkbox.value
                                );

                        }
                    );


                    window.location.href =
                        url.toString();

                }
            );

    }


    if (bulkForm) {

        bulkForm.addEventListener(
            "submit",
            async function (event) {

                event.preventDefault();


                const submitter =
                    event.submitter;


                if (!submitter) {
                    return;
                }


                const action =
                    submitter.value;


                const checked =
                    getCheckedItems();


                if (
                    action === "selected"
                    && checked.length === 0
                ) {

                    showStatus(
                        "Pilih minimal satu barang.",
                        true
                    );

                    return;

                }


                let confirmed;


                if (
                    action === "all"
                ) {

                    confirmed =
                        window.confirm(
                            "Hapus semua barang "
                            + "dari keranjang?"
                        );

                } else {

                    confirmed =
                        window.confirm(
                            "Hapus "
                            + checked.length
                            + " barang yang dipilih?"
                        );

                }


                if (!confirmed) {
                    return;
                }


                showStatus("");


                try {

                    const data =
                        await sendAjax(
                            bulkForm,
                            submitter
                        );


                    data.removed_ids
                        .forEach(
                            function (
                                itemId
                            ) {

                                const item =
                                    document
                                        .querySelector(
                                            '[data-cart-item-id="'
                                            + itemId
                                            + '"]'
                                        );


                                if (item) {
                                    item.remove();
                                }

                            }
                        );


                    const alert =
                        document.querySelector(
                            ".cart-alert"
                        );


                    if (
                        alert
                        && !document
                            .querySelector(
                                ".cart-unavailable-row"
                            )
                    ) {

                        alert.remove();

                    }


                    updateSummary(
                        data
                    );


                    updateCheckout(
                        data
                    );


                    updateBulkState();


                    showStatus(
                        data.message
                    );


                    if (
                        data.cart_empty
                        || getItemCheckboxes()
                            .length === 0
                    ) {

                        window.location.reload();

                    }

                } catch (error) {

                    showStatus(
                        error.message,
                        true
                    );

                }

            }
        );

    }


    updateBulkState();

})();