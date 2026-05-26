const { deviceId, deviceType, deviceOrientation } = document.currentScript.dataset;

let lastCommandId = null;
let playlistTimer = null;

const statusNode = document.getElementById("player-status");
const stageNode = document.getElementById("player-stage");
const headerDeviceInfo = document.getElementById("player-device-info");
const headerMarquee = document.getElementById("player-marquee");
const headerMarqueeText = document.getElementById("player-marquee-text");

const deviceTypeClass = `device-${deviceType.toLowerCase().replace(/_/g, "-")}`;
document.body.classList.add(deviceTypeClass);
document.body.classList.add(deviceOrientation.toLowerCase());

function setStatus(text, isError = false) {
    if (!statusNode) {
        return;
    }
    statusNode.textContent = text;
    statusNode.style.color = isError ? "#ff9999" : "#9ad39a";
}

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

function absoluteUrl(rawUrl) {
    if (!rawUrl) return "";
    try {
        return new URL(rawUrl, window.location.origin).toString();
    } catch (e) {
        return rawUrl;
    }
}

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
    clearStage();

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

async function renderSchedule(commandId, payload) {
    clearStage();

    const isDoctor = payload.source_type === "DOCTOR_SCHEDULE" || payload.source_type === "SCHEDULE";
    
    if (isDoctor && payload.all_doctor_schedules && Array.isArray(payload.all_doctor_schedules)) {
        const schedules = payload.all_doctor_schedules;
        
        if (schedules.length) {
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
        payload.source_type ===
            "OPD_SCHEDULE" &&
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

    // SINGLE RECORD FALLBACK
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

async function pollCommand() {
    try {
        const response = await fetch(`/device/player/${deviceId}/next-command/`);
        const data = await response.json();

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
            stageNode.innerHTML = '<div class="placeholder">Playback stopped.</div>';
            setStatus("Playback stopped");
            await sendAck(data.command_id, "STOPPED", "Playback stopped");
            return;
        }

        if (payload.command !== "PLAY") {
            return;
        }

        const loop = Boolean(payload.loop);

        if (payload.source_type === "MEDIA_ASSET") {
            renderMedia(payload.media_type, payload.file_url, loop);
            setStatus(
                `Playing media: ${payload.title || "Untitled"}` +
                (loop ? " (looping)" : "")
            );
            await sendAck(data.command_id, "PLAYING", "Media playback started");
            return;
        }

        if (payload.source_type === "PLAYLIST") {
            renderPlaylist(payload.items || [], loop);
            setStatus(
                `Playing playlist: ${payload.playlist_name || "Untitled"}` +
                (loop ? " (looping)" : "")
            );
            await sendAck(data.command_id, "PLAYING", "Playlist playback started");
            return;
        }

        if (
            payload.source_type === "DOCTOR_SCHEDULE" ||
            payload.source_type === "OPD_SCHEDULE" ||
            payload.source_type === "SCHEDULE"
        ) {
            await renderSchedule(data.command_id, payload);
            return;
        }

        setStatus("Unknown source type", true);
    } catch (error) {
        console.error(error);
        setStatus("Polling error", true);
    }
}

pollCommand();
setInterval(pollCommand, 5000);
