// Object destructuring.
const {
    deviceId,
    deviceType,
    deviceOrientation,
    offDutyText = ""
} = document.currentScript.dataset;

// Variable declaration.
let lastCommandId = null;
let playlistTimer = null;
let contentSlideTimer = null;
let contentSlides = [];
let contentSlideIndex = 0;

// Get the element with the specified ID.
const statusNode = document.getElementById("player-status");
const layoutNode = document.getElementById("player-layout");
const stageNode = document.getElementById("media-pane");
const contentPane = document.getElementById("content-pane");

// add css classes
const deviceTypeClass = `device-${deviceType.toLowerCase().replace(/_/g, "-")}`;
document.body.classList.add(deviceTypeClass);
document.body.classList.add(deviceOrientation.toLowerCase());

// Function to set layout
function setLayout(mode) {

    if (mode === "fullscreen") {
        layoutNode.classList.remove("split");
        layoutNode.classList.add("fullscreen");
    } else {
        layoutNode.classList.remove("fullscreen");
        layoutNode.classList.add("split");
    }

}

// Function to update status message
function setStatus(text, isError = false) {
    if (!statusNode) {
        return;
    }
    statusNode.textContent = text;
    statusNode.style.color = isError ? "#ff9999" : "#9ad39a";
}

// Device settings
function applyDeviceSettings() {
    if (deviceType === "LED_WALL") {
        stageNode.style.background = "#000";
    } else if (deviceType === "KIOSK") {
        stageNode.style.background = "#12151c";
    }
    if (deviceOrientation === "PORTRAIT") {
        stageNode.style.justifyContent = "center";
    }
}

applyDeviceSettings();

// Function to clear the content of the pane
function clearContentPane() {
    if (contentSlideTimer) {
        clearInterval(contentSlideTimer);
        contentSlideTimer = null;
    }
    contentPane.innerHTML = "";
}

// Security utility to prevent HTML injection and Cross-Site Scripting (XSS)
function escapeHtml(value) {
    return String(value ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/\"/g, "&quot;")
        .replace(/'/g, "&#39;");
}

// Function to split long text into smaller.
function splitTextIntoSlides(text, maxChars = 220) {
    const cleaned = String(text || "").replace(/\r/g, "").trim();
    if (!cleaned) {
        return ["No content available."];
    }

    const paragraphs = cleaned
        .split(/\n+/)
        .map((part) => part.trim())
        .filter(Boolean);

    if (paragraphs.length > 1) {
        return paragraphs;
    }

    if (cleaned.length <= maxChars) {
        return [cleaned];
    }

    const chunks = [];
    for (let index = 0; index < cleaned.length; index += maxChars) {
        chunks.push(cleaned.slice(index, index + maxChars));
    }
    return chunks;
}

// Function to display text content as a slideshow
function renderContentSlides(slides, title = "Content", subtitle = "") {
    clearContentPane();

    const normalizedSlides = (slides || [])
        .map((slide) => String(slide ?? "").trim())
        .filter(Boolean);

    if (!normalizedSlides.length) {
        const placeholder = document.createElement("div");
        placeholder.className = "content-slide";
        const titleEl = document.createElement("div");
        titleEl.className = "content-title";
        titleEl.textContent = title;
        const bodyEl = document.createElement("div");
        bodyEl.className = "content-body";
        bodyEl.textContent = "No content available.";
        placeholder.appendChild(titleEl);
        placeholder.appendChild(bodyEl);
        contentPane.appendChild(placeholder);
        return;
    }

    contentSlides = normalizedSlides;
    contentSlideIndex = 0;

    function renderCurrentSlide() {
        const slide = document.createElement("div");
        slide.className = "content-slide";

        const titleEl = document.createElement("div");
        titleEl.className = "content-title";
        titleEl.textContent = title;

        const bodyEl = document.createElement("div");
        bodyEl.className = "content-body";
        bodyEl.textContent = contentSlides[contentSlideIndex] || "";

        slide.appendChild(titleEl);
        slide.appendChild(bodyEl);

        if (subtitle) {
            const metaEl = document.createElement("div");
            metaEl.className = "content-meta";
            metaEl.textContent = subtitle;
            slide.appendChild(metaEl);
        }

        contentPane.innerHTML = "";
        contentPane.appendChild(slide);
    }

    renderCurrentSlide();

    if (contentSlides.length > 1) {
        contentSlideTimer = setInterval(() => {
            contentSlideIndex = (contentSlideIndex + 1) % contentSlides.length;
            renderCurrentSlide();
        }, 7000);
    }
}

// Default content
function renderDefaultContent() {
    const slides = splitTextIntoSlides(offDutyText);
    renderContentSlides(slides, "Content not available", "Live update");
}

// Function to convert payloads into standard array
function buildContentSlidesFromPayload(payload) {
    if (!payload) {
        return splitTextIntoSlides(offDutyText || "No content available.");
    }

    if (payload.source_type === "MEDIA_ASSET") {
        const slides = [];
        if (payload.title) {
            slides.push(`Now playing: ${payload.title}`);
        }
        if (payload.media_type) {
            slides.push(`Type: ${payload.media_type}`);
        }
        if (payload.file_url) {
            slides.push(`Source: ${payload.file_url}`);
        }
        return slides.length ? slides : splitTextIntoSlides(offDutyText || "No media available.");
    }

    if (payload.source_type === "PLAYLIST") {
        return [
            `Playlist: ${payload.playlist_name || "Untitled"}`,
            `Items: ${payload.items?.length || 0}`
        ];
    }

    if (
        payload.source_type === "DOCTOR_SCHEDULE" ||
        payload.source_type === "OPD_SCHEDULE" ||
        payload.source_type === "SCHEDULE"
    ) {
        const slides = [];

        if (payload.all_doctor_schedules && Array.isArray(payload.all_doctor_schedules)) {
            payload.all_doctor_schedules.forEach((record) => {
                slides.push(`Doctor: ${record.Doctor || "Unknown"}\nStatus: ${record.Status || "-"}`);
            });
        } else if (payload.opd_schedules && Array.isArray(payload.opd_schedules)) {
            payload.opd_schedules.forEach((record) => {
                slides.push(`Doctor: ${record.doctor || "Unknown"}\nRoom: ${record.opd_room || "-"}\nTime: ${record.start_time || "--"} - ${record.end_time || "--"}`);
            });
        } else {
            slides.push(`Schedule source: ${payload.source_type || "Unknown"}`);
        }

        return slides.length ? slides : splitTextIntoSlides(offDutyText || "No schedule data available.");
    }

    return splitTextIntoSlides(offDutyText || "No content available.");
}

// Function to convert URL to Absolute/Complete URL
function absoluteUrl(rawUrl) {
    if (!rawUrl) return "";
    try {
        return new URL(rawUrl, window.location.origin).toString();
    } catch (e) {
        return rawUrl;
    }
}

// To stop any active playlist timer and remove everything currently displayed in the media area
function clearStage() {
    if (playlistTimer) {
        clearInterval(playlistTimer);
        playlistTimer = null;
    }
    stageNode.innerHTML = "";
}

function renderFallbackTable(rows, title) {
    clearStage();
    const wrapper = document.createElement("div");
    wrapper.style.padding = "16px";
    wrapper.style.boxSizing = "border-box";
    wrapper.style.width = "100%";
    wrapper.style.height = "100%";
    wrapper.style.overflow = "auto";
    wrapper.style.background = "#0b0f14";
    wrapper.style.color = "#fff";

    if (title) {
        const heading = document.createElement("h2");
        heading.textContent = title;
        heading.style.margin = "0 0 12px 0";
        heading.style.fontSize = "28px";
        wrapper.appendChild(heading);
    }

    const table = document.createElement("table");
    table.style.width = "100%";
    table.style.borderCollapse = "collapse";
    table.style.background = "#fff";
    table.style.color = "#000";

    const headers = Object.keys(rows[0] || {});
    const thead = document.createElement("thead");
    const headRow = document.createElement("tr");
    headers.forEach((key) => {
        const th = document.createElement("th");
        th.textContent = key;
        th.style.border = "1px solid #ddd";
        th.style.padding = "10px";
        th.style.background = "#e9eef5";
        headRow.appendChild(th);
    });
    thead.appendChild(headRow);
    table.appendChild(thead);

    const tbody = document.createElement("tbody");
    rows.forEach((row) => {
        const tr = document.createElement("tr");
        headers.forEach((key) => {
            const td = document.createElement("td");
            td.textContent = row[key] ?? "-";
            td.style.border = "1px solid #ddd";
            td.style.padding = "10px";
            tr.appendChild(td);
        });
        tbody.appendChild(tr);
    });
    table.appendChild(tbody);
    wrapper.appendChild(table);
    stageNode.appendChild(wrapper);
}

async function sendAck(commandId, status, message) {
    try {
        await fetch(`/device/player/${deviceId}/ack/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                command_id: commandId,
                status: status,
                message: message
            })
        });
    } catch (error) {
        console.error("Ack failed:", error);
    }
}

function renderMedia(mediaType, fileUrl, loop = false) {

    setLayout("fullscreen");

    clearContentPane();

    const absUrl = absoluteUrl(fileUrl);
    if (!absUrl) {
        stageNode.innerHTML = '<div class="placeholder">Missing media URL.</div>';
        return;
    }

    const type = (mediaType || "").toUpperCase();
    const isKiosk = deviceType === "KIOSK";
    const isLedWall = deviceType === "LED_WALL";

    if (type === "IMAGE") {
        renderImage(absUrl, isLedWall);
        return;
    }

    if (type === "VIDEO") {
        renderVideo(absUrl, isKiosk, loop);
        return;
    }

    if (type === "AUDIO") {
        renderAudio(absUrl, isKiosk, loop);
        return;
    }

    if (type === "PDF") {
        renderPdf(absUrl);
        return;
    }

    if (type === "HTML") {
        renderHtml(absUrl);
        return;
    }

    stageNode.innerHTML = '<div class="placeholder">Unsupported media type.</div>';
}

function renderPlaylist(items, loop = false) {
    clearStage();

    if (!items || !items.length) {
        stageNode.innerHTML = '<div class="placeholder">Playlist has no items.</div>';
        return;
    }

    let index = 0;
    let playlistLoop = Boolean(loop);

    function showCurrentItem() {
        const item = items[index];
        renderMedia(item.media_type, item.file_url, playlistLoop);
        setStatus(`Playing playlist item ${index + 1} of ${items.length}`);
        const durationSeconds = Number(item.duration || 10);
        const waitMs = Math.max(1, durationSeconds) * 1000;

        if (playlistTimer) {
            clearTimeout(playlistTimer);
        }
        if (playlistLoop || index < items.length - 1) {
            playlistTimer = setTimeout(() => {
                index = (index + 1) % items.length;
                showCurrentItem();
            }, waitMs);
        }
    }

    showCurrentItem();
}

/*
async function renderSchedule(commandId, payload) {
    clearStage();

    // Prioritize doctor schedules over OPD schedules
    if (payload.all_doctor_schedules && Array.isArray(payload.all_doctor_schedules)) {
        const schedules = payload.all_doctor_schedules;
        
        if (schedules.length) {
            renderContentSlides(
                schedules.map((schedule) => `Doctor: ${schedule.Doctor || "Unknown"}\nStatus: ${schedule.Status || "-"}`),
                "Doctor schedule",
                "Live update"
            );
            const outOfStationCount = schedules.filter(s => s.Status === "Out of Station").length;
            const unavailableCount = schedules.filter(s => s.Status === "Unavailable").length;
            
            let marqueeText = "Doctor schedules";
            if (outOfStationCount > 0) {
                marqueeText = `${outOfStationCount} doctor(s) out of station`;
            } else if (unavailableCount > 0) {
                marqueeText = `${unavailableCount} doctor(s) unavailable`;
            }
            
            renderTable(schedules, "All Doctors Schedules");
            setStatus(`Displaying all doctor schedules`);
            await sendAck(commandId, "PLAYING", "All doctor schedules displayed");
            return;
        }
    }

    if (
        payload.opd_schedules &&
        Array.isArray(
            payload.opd_schedules
        )
    ) {
        const schedules =
            payload.opd_schedules;

        if (schedules.length) {

            const tableData =
                schedules.map(item => ({
                    Schedule:
                        "OPD Schedule",
                    Date:
                        item.opd_date ||
                        "Recurring",
                    Doctor:
                        item.doctor ||
                        "Unknown doctor",
                    "OPD Room":
                        item.opd_room ||
                        "Unknown OPD room",
                    Department:
                        item.department ||
                        "-",
                    Day:
                        item.day ||
                        "Unknown day",
                    Start:
                        item.start_time ||
                        "--:--",
                    End:
                        item.end_time ||
                        "--:--",
                }));

            renderContentSlides(
                tableData.map((item) => `${item.Doctor}\nRoom: ${item["OPD Room"]}\nTime: ${item.Start} - ${item.End}`),
                "OPD schedule",
                "Live update"
            );

            if (typeof renderTable === "function") {
                renderTable(
                    tableData,
                    "Today's OPD Schedule"
                );
            } else {
                renderFallbackTable(
                    tableData,
                    "Today's OPD Schedule"
                );
            }

            setStatus(
                "Displaying OPD schedule"
            );

            await sendAck(
                commandId,
                "PLAYING",
                "OPD schedule displayed"
            );

            return;
        }
    }

    // SINGLE RECORD FALLBACK - Default to doctor schedule
    const isDoctor = true;
    
    const title = isDoctor
        ? "Doctor Schedule"
        : "OPD Schedule";

    const name = isDoctor
        ? payload.doctor_name ||
          "Unknown doctor"
        : payload.opd_room_name ||
          "Unknown OPD room";

    const detail = (
        isDoctor
            ? payload.specialization
            : payload.department_name
    ) || "-";

    const day = (
        isDoctor
            ? payload.doctor_schedule_day
            : payload.opd_schedule_day
    ) || "Unknown day";

    const start = (
        isDoctor
            ? payload.doctor_schedule_start
            : payload.opd_schedule_start
    ) || "--:--";

    const end = (
        isDoctor
            ? payload.doctor_schedule_end
            : payload.opd_schedule_end
    ) || "--:--";

    const isAvailable =
        payload.doctor_schedule_is_available !== false;

    const record = {
        Schedule: title,
        [isDoctor
            ? "Doctor"
            : "OPD Room"]: name,
        [isDoctor
            ? "Specialization"
            : "Department"]:
            detail,
        Day: day,
        Start: start,
        End: end,
    };

    renderContentSlides(
        [
            `${title}\n${name}\n${detail}\nDay: ${day}\nTime: ${start} - ${end}`
        ],
        title,
        "Live update"
    );

    renderTable(
        [record],
        title
    );

    setStatus(
        `Displaying ${
            isDoctor
                ? "doctor"
                : "OPD"
        } schedule: ${name}`
    );

    await sendAck(
        commandId,
        "PLAYING",
        `${
            isDoctor
                ? "Doctor"
                : "OPD"
        } schedule displayed`
    );
}
*/

async function renderDoctorSchedule(commandId, payload) {

    clearContentPane();

    const schedules = payload.all_doctor_schedules || [];

    if (!schedules.length) {
        renderContentSlides(
            ["No doctor schedules available."],
            "Doctor Off Schedule",
            "Live update"
        );

        setStatus("No doctor schedules available.");
        
        await sendAck(
            commandId,
            "PLAYING",
            "No doctor schedules available."
        );

        return;
    }

    const slides = schedules.map(item => 
        `Doctor : ${item.Doctor}
        Status : ${item.Status}
        Date : ${item.From} - ${item.To}`
    );

    renderContentSlides(
        slides,
        "Doctor Off Schedule",
        "Live update"
    );

    setStatus("Displaying doctor schedules");

    await sendAck(
        commandId,
        "PLAYING",
        "Doctor schedules displayed"
    );
}

async function renderOpdSchedule(commandId, payload) {

    setLayout("split");

    clearStage();

    const schedules = payload.opd_schedules || [];

    if (!schedules.length) {

        stageNode.innerHTML = '<div class="placeholder">No OPD schedules available.</div>';

        setStatus("No OPD schedules available.");

        await sendAck(
            commandId,
            "PLAYING",
            "No OPD schedules available."
        );

        return;
    }

    /* table data */

    const grouped = {};

    schedules.forEach(item => {
        const key = [
            item.doctor,
            item.opd_room,
            item.department,
            item.opd_date || "Recurring",
            item.start_time,
            item.end_time
        ].join("|");

        if (!grouped[key]) {
            grouped[key] = {
                Doctor: item.doctor,
                Department: item.department,
                Days: [],
                Timing: `${item.start_time} - ${item.end_time}`,
            };
        }

        grouped[key].Days.push(item.day);
    });

    const tableData = Object.values(grouped).map(item => ({
        ...item,
        Days: item.Days.join(", "),
    }));

    /* end */

    if (typeof renderTable === "function") {
        renderTable(
            tableData,
            "OPD Schedule"
        );
    } else {
        renderFallbackTable(
            tableData,
            "OPD Schedule"
        );
    }

    setStatus(
        "Displaying OPD schedule"
    );

    await sendAck(
        commandId,
        "PLAYING",
        "OPD schedule displayed"
    );

}

async function pollCommand() {
    try {
        const response = await fetch(`/device/player/${deviceId}/next-command/`);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || `Polling failed with status ${response.status}`);
        }

        if (!data.command_id || !data.payload || !data.payload.command) {
            return;
        }

        if (data.command_id === lastCommandId) {
            return;
        }

        lastCommandId = data.command_id;
        const payload = data.payload;

        if (payload.command === "STOP") {
            clearStage();
            clearContentPane();
            stageNode.innerHTML = '<div class="placeholder">Playback stopped.</div>';
            renderDefaultContent();
            setStatus("Playback stopped");
            await sendAck(data.command_id, "STOPPED", "Playback stopped");
            return;
        }

        if (payload.command !== "PLAY") {
            return;
        }

        const loop = Boolean(payload.loop);

        if (payload.media) {

            switch (payload.media.media_type) {

                case "IMAGE":
                case "VIDEO":
                case "AUDIO":
                case "HTML":

                    setLayout("fullscreen");

                    clearContentPane();

                    renderMedia(
                        payload.media.media_type,
                        payload.media.file_url,
                        loop
                    );

                    break;

                case "PDF":

                    setLayout("split");

                    renderPdf(
                        payload.media.file_url,
                        loop
                    );

                    break;
            }
        }

        if (payload.playlist) {

            setLayout("fullscreen");

            clearContentPane();

            renderPlaylist(
                payload.playlist.items || [],
                loop
            );

            await sendAck(
                data.command_id,
                "PLAYING",
                "Playlist playback started"
            );
        }

        /*
        if (
            payload.source_type === "DOCTOR_SCHEDULE" ||
            payload.source_type === "OPD_SCHEDULE"
        ) {
            await renderSchedule(data.command_id, payload);
            return;
        }
        */
        
        if (payload.doctor_schedule) {

            setLayout("split");

            await renderDoctorSchedule(
                data.command_id,
                payload.doctor_schedule
            );
        }

        if (payload.opd_schedule) {

            setLayout("split");

            await renderOpdSchedule(
                data.command_id,
                payload.opd_schedule
            );
        }

        await sendAck(
            data.command_id,
            "PLAYING",
            "Playback started"
        );

    } catch (error) {
        console.error(error);
        setStatus("Polling error", true);
    }
}

renderDefaultContent();
pollCommand();
setInterval(pollCommand, 5000);
