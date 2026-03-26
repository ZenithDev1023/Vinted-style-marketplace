function validatePostcode() {
    const input = document.getElementById('id_postcode').value.trim().toUpperCase();

    const postcodePattern = /^[A-Z]{1,2}[0-9]{1,2}[A-Z]?\s?[0-9][A-Z]{2}$/;

    if (input === "") {
        return true;
    }

    if (!postcodePattern.test(input)) {
        document.getElementById('postcodeError').innerText = 'Invalid postcode format.';
        return false;
    }

    document.getElementById('postcodeError').innerText = '';
    return true;
};