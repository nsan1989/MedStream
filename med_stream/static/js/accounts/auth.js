document.addEventListener("DOMContentLoaded", function() {

    const leftContent = document.getElementById("left-content");
    const rightContent = document.getElementById("right-content");

    const titleContent = document.querySelector(".title-content");
    const logoContent = document.querySelector(".logo-content");
    const titleInfo = document.querySelector(".title-info");
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
        registerInfo.classList.add("hidden");;

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


document.addEventListener("DOMContentLoaded", function () {

            const adminBtn = document.getElementById(
                "showAdminRegister"
            );

            const staffBtn = document.getElementById(
                "showStaffRegister"
            );

            const adminForm = document.getElementById(
                "adminRegisterForm"
            );

            const staffForm = document.getElementById(
                "staffRegisterForm"
            );

            adminBtn.addEventListener("click", function (e) {
                e.preventDefault();

                adminForm.style.display = "block";
                staffForm.style.display = "none";
            });

            staffBtn.addEventListener("click", function (e) {
                e.preventDefault();

                adminForm.style.display = "none";
                staffForm.style.display = "block";
            });

        });

document.addEventListener(
    "DOMContentLoaded",
    function () {

    // ====================
    // ADMIN OTP
    // ====================

    const sendAdminOTP =
        document.getElementById(
            "sendAdminOTP"
        );

    const adminOtpSection =
        document.getElementById(
            "adminOtpSection"
        );

    const verifyAdminOTP =
        document.getElementById(
            "verifyAdminOTP"
        );

    const adminRegisterBtn =
        document.getElementById(
            "adminRegisterBtn"
        );

    sendAdminOTP?.addEventListener(
        "click",
        async function () {

        const phone =
            document.getElementById(
                "register_phone_number"
            ).value;

        if (!phone) {
            alert(
                "Enter phone number"
            );
            return;
        }

        const response =
            await fetch(
            "/accounts/send-otp/",
            {
                method: "POST",
                headers: {
                    "Content-Type":
                    "application/json",
                    "X-CSRFToken":
                    getCSRFToken(),
                },
                body: JSON.stringify({
                    phone_number:
                    phone
                }),
            });

        const data =
            await response.json();

        if (data.success) {

            adminOtpSection
                .style.display =
                "block";

            alert(
                "OTP sent successfully"
            );
        }
    });

    verifyAdminOTP
        ?.addEventListener(
        "click",
        async function () {

        const otp =
            document.getElementById(
                "admin_otp"
            ).value;

        const phone =
            document.getElementById(
                "register_phone_number"
            ).value;

        const response =
            await fetch(
            "/accounts/verify-otp/",
            {
                method: "POST",
                headers: {
                    "Content-Type":
                    "application/json",
                    "X-CSRFToken":
                    getCSRFToken(),
                },
                body: JSON.stringify({
                    phone_number:
                    phone,
                    otp: otp,
                }),
            });

        const data =
            await response.json();

        if (data.success) {

            document
                .getElementById(
                "adminOtpVerified"
            ).value = "true";

            adminRegisterBtn
                .disabled = false;

            alert(
                "Phone verified"
            );
        }
    });

});

function getCSRFToken() {
    return document
        .querySelector(
            "[name=csrfmiddlewaretoken]"
        )
        .value;
}