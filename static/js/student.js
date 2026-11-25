
function getCookie(name) {
    const cookies = document.cookie ? document.cookie.split(";") : [];

    for (const cookie of cookies) {
        const item = cookie.trim();

        if (item.startsWith(name + "=")) {
            return decodeURIComponent(item.substring(name.length + 1));
        }
    }

    return null;
}

async function refreshSession() {
    try {
        const response = await fetch("/api/accounts/refresh/", {
            method: "POST",
            credentials: "same-origin",
            headers: {
                "X-CSRFToken": getCookie("csrftoken")
            }
        });

        return response.ok;
    } catch (error) {
        console.error("Token yangilash xatosi:", error);
        return false;
    }
}

// API so'rovlarida 401 javobi olinsa, tokenni yangilab qayta urinadi.
async function apiRequest(url, options = {}) {
    let response = await fetch(url, {
        ...options,
        credentials: "same-origin"
    });

    if (response.status === 401) {
        const refreshed = await refreshSession();

        if (refreshed) {
            response = await fetch(url, {
                ...options,
                credentials: "same-origin"
            });
        }
    }

    return response;
}

// Tizimdan chiqish
async function logout() {
    const button = document.getElementById("logoutButton");

    if (button) {
        button.disabled = true;
        button.textContent = "Chiqilmoqda...";
    }

    try {
        const response = await fetch("/api/accounts/logout/", {
            method: "POST",
            credentials: "same-origin",
            headers: {
                "X-CSRFToken": getCookie("csrftoken")
            }
        });

        if (response.ok) {
            window.location.href = "/";
        } else {
            alert("Tizimdan chiqishda xatolik yuz berdi.");
            if (button) {
                button.disabled = false;
                button.textContent = "Chiqish";
            }
        }
    } catch (error) {
        console.error(error);
        alert("Server bilan bog'lanib bo'lmadi.");

        if (button) {
            button.disabled = false;
            button.textContent = "Chiqish";
        }
    }
}

document.addEventListener("DOMContentLoaded", () => {
    const logoutButton = document.getElementById("logoutButton");

    if (logoutButton) {
        logoutButton.addEventListener("click", logout);
    }

    document.querySelectorAll('a[href="#"]').forEach(link => {
        link.addEventListener("click", event => {
            event.preventDefault();
        });
    });
});
