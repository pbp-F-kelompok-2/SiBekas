(() => {
    const form = document.getElementById("checkout-form");
    if (!form) return;
    const method = document.getElementById("id_delivery_method");
    const quoteInput = document.getElementById("id_shipping_quote");
    const courierFields = document.getElementById("courier-fields");
    const pickupHint = document.getElementById("pickup-hint");
    const costLabel = document.getElementById("shipping-cost");
    const totalLabel = document.getElementById("checkout-total");
    const note = document.getElementById("quote-note");
    const destination = document.getElementById("destination-select");
    const options = document.getElementById("shipping-options");
    const feedback = document.getElementById("shipping-feedback");
    const searchButton = document.getElementById("find-destination");
    const search = document.getElementById("destination-search");
    const csrf = form.querySelector("[name=csrfmiddlewaretoken]").value;
    const subtotal = Number(form.dataset.subtotal);
    const rupiah = value => `Rp ${new Intl.NumberFormat("id-ID").format(value)}`;
    const payment = document.getElementById("id_payment_method");
    const codOption = payment.querySelector('[value="cod"]');
    const courierOption = method.querySelector('[value="courier"]');
    if (form.dataset.shippingAvailable !== "true" && courierOption && method.value !== "courier") courierOption.disabled = true;
    let selectedCost = form.dataset.selectedCost === "" ? null : Number(form.dataset.selectedCost);
    let searchVersion = 0;
    let quoteVersion = 0;

    function clearQuote() {
        quoteInput.value = "";
        selectedCost = null;
        if (options) options.replaceChildren(Object.assign(document.createElement("legend"), {textContent: "Pilihan kurir"}));
        costLabel.textContent = method.value === "pickup" ? "Gratis" : "Pilih kurir";
        totalLabel.textContent = rupiah(subtotal);
        note.textContent = "Ongkir kurir ditampilkan setelah memilih tujuan dan layanan.";
    }
    function deliveryChanged() {
        courierFields.hidden = method.value !== "courier";
        pickupHint.hidden = method.value !== "pickup";
        if (codOption) codOption.disabled = method.value === "courier";
        if (method.value === "courier" && payment.value === "cod" && payment.querySelector('[value="demo"]')) payment.value = "demo";
        if (method.value === "pickup") {
            costLabel.textContent = "Gratis";
            totalLabel.textContent = rupiah(subtotal);
        } else if (selectedCost !== null) {
            costLabel.textContent = rupiah(selectedCost);
            totalLabel.textContent = rupiah(subtotal + selectedCost);
        } else if (!quoteInput.value) {
            costLabel.textContent = "Pilih kurir";
        }
    }
    method.addEventListener("change", deliveryChanged);
    deliveryChanged();

    async function readResponse(response) {
        if (response.redirected || !response.headers.get("content-type")?.includes("application/json")) {
            throw new Error("Sesi berakhir. Muat ulang halaman lalu masuk kembali.");
        }
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || "Ongkir belum dapat dimuat. Coba lagi.");
        return data;
    }
    if (searchButton) {
        search.addEventListener("input", () => {
            searchVersion++;
            quoteVersion++;
            destination.disabled = true;
            destination.replaceChildren(new Option("Cari dan pilih tujuan", ""));
            clearQuote();
        });
        search.addEventListener("keydown", event => {
            if (event.key === "Enter") { event.preventDefault(); searchButton.click(); }
        });
        searchButton.addEventListener("click", async () => {
            const query = search.value.trim();
            if (query.length < 3) { feedback.textContent = "Masukkan minimal 3 karakter nama lokasi atau kode pos."; search.focus(); return; }
            const version = ++searchVersion;
            ++quoteVersion;
            clearQuote();
            destination.disabled = true;
            searchButton.disabled = true;
            feedback.textContent = "Mencari tujuan…";
            try {
                const url = new URL(form.dataset.destinationsUrl, window.location.origin);
                url.searchParams.set("q", query);
                const data = await readResponse(await fetch(url, {headers: {Accept: "application/json"}}));
                if (version !== searchVersion) return;
                destination.replaceChildren(new Option("Pilih tujuan pengiriman", ""));
                data.destinations.forEach(item => destination.add(new Option(item.label, item.token)));
                destination.disabled = !data.destinations.length;
                feedback.textContent = data.destinations.length ? "Pilih tujuan untuk menghitung ongkir." : "Tujuan tidak ditemukan. Coba kecamatan atau kode pos lainnya.";
            } catch (error) { if (version === searchVersion) feedback.textContent = error.message; }
            finally { searchButton.disabled = false; }
        });
        destination.addEventListener("change", async () => {
            const version = ++quoteVersion;
            clearQuote();
            if (!destination.value) return;
            feedback.textContent = "Menghitung ongkir…";
            try {
                const body = new URLSearchParams({destination_token: destination.value});
                const data = await readResponse(await fetch(form.dataset.quotesUrl, {
                    method: "POST", headers: {"X-CSRFToken": csrf, Accept: "application/json"}, body,
                }));
                if (version !== quoteVersion) return;
                data.quotes.forEach((quote, index) => {
                    const label = document.createElement("label");
                    label.className = "order-shipping-choice";
                    const radio = document.createElement("input");
                    radio.type = "radio";
                    radio.name = "shipping_choice";
                    radio.value = String(index);
                    const text = document.createElement("span");
                    text.textContent = `${quote.service} · ${rupiah(quote.cost)}${quote.etd ? ` · ${quote.etd}` : ""}`;
                    radio.addEventListener("change", () => {
                        quoteInput.value = quote.token;
                        selectedCost = quote.cost;
                        deliveryChanged();
                        note.textContent = `${quote.service} · ${quote.destination}`;
                    });
                    label.append(radio, text);
                    options.append(label);
                });
                feedback.textContent = "Pilih satu layanan. Ongkir berlaku 15 menit.";
            } catch (error) { if (version === quoteVersion) feedback.textContent = error.message; }
        });
    }
    form.addEventListener("submit", event => {
        if (method.value === "courier" && !quoteInput.value) {
            event.preventDefault();
            if (feedback) feedback.textContent = "Pilih tujuan dan layanan kurir terlebih dahulu.";
            courierFields.scrollIntoView({behavior: "smooth", block: "center"});
            return;
        }
        const button = document.getElementById("place-order");
        button.disabled = true;
        button.textContent = "Membuat pesanan…";
    });
    window.addEventListener("pageshow", event => {
        if (event.persisted) window.location.reload();
    });
})();
