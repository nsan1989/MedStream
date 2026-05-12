document.addEventListener("DOMContentLoaded", function() {

    const leftContent = document.getElementById("left-content");
    const rightContent = document.getElementById("right-content");

    const loginContent = document.querySelector(".login-content");
    const loginInfo = document.querySelector(".login-info");
    const registerContent = document.querySelector(".register-content");
    const registerInfo = document.querySelector(".register-info");

    const showLoginLeftBtn = document.getElementById("showLoginLeft");
    const showRegisterRightBtn = document.getElementById("showRegisterRight");
    const loginPath = "/accounts/login/";
    const registerPath = "/accounts/register/";

    function showLoginState(updateUrl = true) {
        leftContent.style.backgroundColor = "#FFFFFF";
        rightContent.style.backgroundColor = "#6B1D20";

        loginContent.classList.remove("hidden");
        loginInfo.classList.add("hidden");

        registerContent.classList.add("hidden");
        registerInfo.classList.remove("hidden");

        if (updateUrl && window.location.pathname !== loginPath) {
            window.history.pushState({ authView: "login" }, "", loginPath);
        }
    }

    function showRegisterState(updateUrl = true) {
        leftContent.style.backgroundColor = "#6B1D20";
        rightContent.style.backgroundColor = "#FFFFFF";

        loginContent.classList.add("hidden");
        loginInfo.classList.remove("hidden");

        registerContent.classList.remove("hidden");
        registerInfo.classList.add("hidden");

        if (updateUrl && window.location.pathname !== registerPath) {
            window.history.pushState({ authView: "register" }, "", registerPath);
        }
    }

    if (window.location.pathname === registerPath) {
        showRegisterState(false);
    } else {
        showLoginState(false);
    }

    showLoginLeftBtn?.addEventListener("click", showLoginState);
    showRegisterRightBtn?.addEventListener("click", showRegisterState);

    window.addEventListener("popstate", function() {
        if (window.location.pathname === registerPath) {
            showRegisterState(false);
        } else {
            showLoginState(false);
        }
    });

});
