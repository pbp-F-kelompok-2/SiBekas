const ProductPage = {
    selectedBoxes(){
        return document.querySelectorAll('input[name="ids"]:checked');
    },
    updateBulkButton() {
        const button = document.querySelector("#bulk button");
        if (!button) return;
        const count = this.selectedBoxes().length;
        button.textContent = `Hapus yang dipilih (${count})`;
        button.disabled = count === 0;
    },
    toggleAll(checked) {
        document.querySelectorAll('input[name="ids"]').forEach((box) => {
            box.checked = checked;
        });
        this.updateBulkButton();
    },
    init() {
        document.addEventListener("change", (event) => {
            if (event.target.id === "select-all")
                this.toggleAll(event.target.checked);
            if (event.target.name === "ids")
                this.updateBulkButton()
        });
        htmx.onLoad(() => this.updateBulkButton());
    },
};

ProductPage.init();