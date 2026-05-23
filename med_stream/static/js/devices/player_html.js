function renderTable(data, title = "") {
    stageNode.innerHTML = "";

    stageNode.style.display = "block";
    stageNode.style.overflow = "auto";

    // Background
    stageNode.style.backgroundImage = "url('/static/images/html-bg.jpg')";
    stageNode.style.backgroundSize = "cover";
    stageNode.style.backgroundPosition = "center";
    stageNode.style.backgroundRepeat = "no-repeat";

    // Wrapper
    const wrapper = document.createElement("div");
    wrapper.style.width = "100%";
    wrapper.style.height = "100%";
    wrapper.style.padding = "20px";
    wrapper.style.boxSizing = "border-box";
    wrapper.style.overflow = "auto";
    wrapper.style.background = "rgba(0,0,0,0.2)";

    if (title) {
        const titleEl = document.createElement("h2");
        titleEl.innerText = title;
        titleEl.style.color = "#fff";
        titleEl.style.marginBottom = "16px";
        titleEl.style.fontSize = "2rem";
        titleEl.style.letterSpacing = "1px";
        titleEl.style.textTransform = "uppercase";
        wrapper.appendChild(titleEl);
    }

    // Table
    const table = document.createElement("table");
    table.style.width = "100%";
    table.style.borderCollapse = "collapse";
    table.style.background = "#fff";
    table.style.color = "#000";
    table.style.fontSize = "18px";

    // Header
    const thead = document.createElement("thead");
    const headerRow = document.createElement("tr");

    Object.keys(data[0]).forEach(key => {
        const th = document.createElement("th");
        th.innerText = key.replace(/_/g, " ").toUpperCase();
        th.style.border = "1px solid #000";
        th.style.color = "#fff";
        th.style.padding = "14px";
        th.style.background = "#4e0606";
        th.style.position = "sticky";
        th.style.top = "0";
        headerRow.appendChild(th);
    });

    thead.appendChild(headerRow);
    table.appendChild(thead);

    // Body
    const tbody = document.createElement("tbody");

    data.forEach(row => {
        const tr = document.createElement("tr");

        Object.entries(row).forEach(([key, value]) => {
            const td = document.createElement("td");
            td.textContent = value ?? (
                key === "opd_room"
                ? "Unknown OPD room"
                : key === 
                "day"
                ? "Unknown day"
                : "--:--"
            );
            td.style.padding = "10px";
            td.style.border = "1px solid #ddd";
            td.style.textAlign = "center";
            tr.appendChild(td);
        });

        tbody.appendChild(tr);
    });

    table.appendChild(tbody);
    wrapper.appendChild(table);
    stageNode.appendChild(wrapper);
}

async function renderHtml(fileUrl) {
    try {
        // Fetch data from URL
        const response = await fetch(fileUrl);
        const data = await response.json();

        let renderData = data;

        // Fix OPD payload
        if (
            data &&
            data.source_type ===
                "OPD_SCHEDULE"
        ) {
            renderData =
                data.opd_schedules || [];
        }

        // No data
        if (
            !Array.isArray(
                renderData
            ) ||
            !renderData.length
        ) {
            stageNode.innerHTML =
                "<h2>No data available</h2>";
            return;
        }

        renderTable(
            renderData,
            data.source_type ===
                "OPD_SCHEDULE"
                ? "Today's OPD Schedule"
                : ""
        );
    } catch (error) {
        console.error(
            "Error loading table:",
            error
        );

        stageNode.innerHTML =
            `<div style="color:red;">${error.message}</div>`;
    }
}