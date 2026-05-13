document.addEventListener("DOMContentLoaded", function() {
    const sidebar = document.getElementById("sidebar");
    const collapseBtn = document.getElementById("collapseSidebar");
    const expandBtn = document.getElementById("expandSidebar");

    // Collapse sidebar.
    collapseBtn.addEventListener("click", function () {
        sidebar.classList.add("collapsed");

        collapseBtn.classList.add("hidden");
        expandBtn.classList.remove("hidden");

        localStorage.setItem("sidebarState", "collapsed");
    });

    // Expand sidebar.
    expandBtn.addEventListener("click", function () {
        sidebar.classList.remove("collapsed");

        expandBtn.classList.add("hidden");
        collapseBtn.classList.remove("hidden");

        localStorage.setItem("sidebarState", "expanded");
    });

    // Restore sidebar state on page reload
    const savedState = localStorage.getItem("sidebarState");

    if (savedState === "collapsed") {
        sidebar.classList.add("collapsed");
        collapseBtn.classList.add("hidden");
        expandBtn.classList.remove("hidden");
    }
});
