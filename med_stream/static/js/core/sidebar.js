document.addEventListener("DOMContentLoaded", function() {
    const layoutWrapper = document.querySelector(".layout-wrapper");
    const expandBtn = document.querySelector(".sidebar-toggle-expand");
    const collapseBtn = document.querySelector(".sidebar-toggle-collapse");

    if (!layoutWrapper) {
        return;
    }

    function expandSidebar() {
        layoutWrapper.classList.add("sidebar-expanded");
    }

    function collapseSidebar() {
        layoutWrapper.classList.remove("sidebar-expanded");
    }

    expandBtn?.addEventListener("click", expandSidebar);
    collapseBtn?.addEventListener("click", collapseSidebar);
});
