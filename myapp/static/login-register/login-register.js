function validateRegisterForm() {
    const username = document.getElementById('id_username').value.trim().toLowerCase();
    const postcodeInput = document.getElementById('id_postcode').value.trim().toUpperCase();
    const password = document.getElementById('id_password1').value;
    const confirmPassword = document.getElementById('id_password2').value;
    const postcodePattern = /^[A-Z]{1,2}[0-9]{1,2}[A-Z]?\s?[0-9][A-Z]{2}$/;

        if (password.length < 8) {
        document.getElementById('passwordError').innerText = 'Password must be at least 8 characters long.';
        return false;
    }

    if (!/\d/.test(password)) {
        document.getElementById('passwordError').innerText = 'Password must include at least 1 number.';
        return false;
    }

    if (username && (password.toLowerCase().includes(username) || username.includes(password.toLowerCase()))) {
        document.getElementById('passwordError').innerText = 'Password cannot be similar to your username.';
        return false;
    }

    if (password !== confirmPassword) {
        document.getElementById('passwordError').innerText = 'Passwords do not match.';
        return false;
    }

    document.getElementById('passwordError').innerText = '';

    if (postcodeInput === "") {
        return true;
    }

    if (!postcodePattern.test(postcodeInput)) {
        document.getElementById('postcodeError').innerText = 'Invalid postcode format.';
        return false;
    }

    document.getElementById('postcodeError').innerText = '';
    return true;
};