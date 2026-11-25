
document.addEventListener("DOMContentLoaded", () => {

    // ======================================
    // CSRF TOKEN
    // ======================================

    function getCookie(name) {
        const cookies = document.cookie.split(";");

        for (const cookie of cookies) {
            const item = cookie.trim();

            if (item.startsWith(name + "=")) {
                return decodeURIComponent(
                    item.substring(name.length + 1)
                );
            }
        }

        return null;
    }


    // ======================================
    // MESSAGE
    // ======================================

    function showMessage(element, text, type = "error") {
        if (!element) return;

        element.textContent = text;
        element.className = `auth-message show ${type}`;
    }


    function getErrorText(data) {
        if (data.message) return data.message;

        if (typeof data === "string") return data;

        return Object.entries(data)
            .map(([field, errors]) => {
                const messages = Array.isArray(errors)
                    ? errors.join(", ")
                    : String(errors);

                return `${field}: ${messages}`;
            })
            .join("\n");
    }


    // ======================================
    // PASSWORD VISIBILITY
    // ======================================

    document.querySelectorAll(".password-toggle").forEach((button) => {
        button.addEventListener("click", () => {
            const targetId = button.dataset.target;
            const input = document.getElementById(targetId);

            if (!input) return;

            const visible = input.type === "text";

            input.type = visible ? "password" : "text";
            button.textContent = visible ? "Ko‘rsatish" : "Yashirish";
        });
    });


    // ======================================
    // REGISTER
    // ======================================

    const registerForm = document.getElementById("registerForm");

    if (registerForm) {
        registerForm.addEventListener("submit", async (event) => {
            event.preventDefault();

            const message = document.getElementById("message");
            const submitButton = document.getElementById("submitButton");

            const firstName = document.getElementById("first_name").value.trim();
            const lastName = document.getElementById("last_name").value.trim();
            const username = document.getElementById("username").value.trim();
            const email = document.getElementById("email").value.trim();
            const grade = document.getElementById("grade").value;
            const password = document.getElementById("password").value;
            const confirmPassword =
                document.getElementById("confirm_password").value;

            if (password.length < 8) {
                showMessage(message, "Parol kamida 8 ta belgidan iborat bo‘lishi kerak.");
                return;
            }

            if (password !== confirmPassword) {
                showMessage(message, "Parollar bir xil emas.");
                return;
            }

            if (!grade) {
                showMessage(message, "Sinfingizni tanlang.");
                return;
            }

            const csrfToken = getCookie("csrftoken");

            if (!csrfToken) {
                showMessage(
                    message,
                    "CSRF token topilmadi. Sahifani qayta yuklang."
                );
                return;
            }

            submitButton.disabled = true;
            submitButton.textContent = "Hisob yaratilmoqda...";

            try {
                const response = await fetch("/api/accounts/register/", {
                    method: "POST",
                    credentials: "same-origin",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": csrfToken
                    },
                    body: JSON.stringify({
                        first_name: firstName,
                        last_name: lastName,
                        username: username,
                        email: email,
                        grade: grade,
                        password: password
                    })
                });

                const data = await response.json();

                if (response.ok) {
                    showMessage(
                        message,
                        data.message || "Hisob yaratildi. Yo‘naltirilmoqda...",
                        "success"
                    );

                    if (data.redirect_url) {
                        window.location.replace(data.redirect_url);
                    } else {
                        window.location.replace("/");
                    }

                    return;
                }

                showMessage(message, getErrorText(data));

            } catch (error) {
                showMessage(
                    message,
                    "Server bilan bog‘lanib bo‘lmadi. Internet yoki serverni tekshiring."
                );

                console.error(error);

            } finally {
                submitButton.disabled = false;
                submitButton.textContent = "Hisob yaratish";
            }
        });
    }


    // ======================================
    // LOGIN
    // ======================================

    const loginForm = document.getElementById("loginForm");

    if (loginForm) {
        loginForm.addEventListener("submit", async (event) => {
            event.preventDefault();

            const message = document.getElementById("message");
            const submitButton = document.getElementById("submitButton");

            const username = document.getElementById("username").value.trim();
            const password = document.getElementById("password").value;

            if (!username || !password) {
                showMessage(message, "Login va parolni kiriting.");
                return;
            }

            const csrfToken = getCookie("csrftoken");

            if (!csrfToken) {
                showMessage(
                    message,
                    "CSRF token topilmadi. Sahifani qayta yuklang."
                );
                return;
            }

            submitButton.disabled = true;
            submitButton.textContent = "Kirilmoqda...";

            try {
                const response = await fetch("/api/accounts/login/", {
                    method: "POST",
                    credentials: "same-origin",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": csrfToken
                    },
                    body: JSON.stringify({
                        username: username,
                        password: password
                    })
                });

                const data = await response.json();

                if (response.ok) {
                    showMessage(
                        message,
                        data.message || "Muvaffaqiyatli kirildi.",
                        "success"
                    );

                    if (data.redirect_url) {
                        window.location.replace(data.redirect_url);
                    } else {
                        window.location.replace("/");
                    }

                    return;
                }

                showMessage(message, getErrorText(data));

            } catch (error) {
                showMessage(
                    message,
                    "Server bilan bog‘lanib bo‘lmadi."
                );

                console.error(error);

            } finally {
                submitButton.disabled = false;
                submitButton.textContent = "Kirish";
            }
        });
    }

});
