
        const deviceId = "{{ device.id }}";
        const deviceType = "{{ device.device_type|default:'TV'|escapejs }}";
        const deviceOrientation = "{{ device.orientation|default:'LANDSCAPE'|escapejs }}";
        let lastCommandId = null;
        let playlistTimer = null;

        const statusNode = document.getElementById("player-status");
        const stageNode = document.getElementById("player-stage");

        const deviceTypeClass = `device-${deviceType.toLowerCase().replace(/_/g, "-")}`;
        document.body.classList.add(deviceTypeClass);
        document.body.classList.add(deviceOrientation.toLowerCase());

        function setStatus(text, isError = false) {
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

function renderImage(fileUrl, isLedWall) {
    const img = document.createElement("img");
    img.src = fileUrl;
    img.alt = "Media Asset";
    img.style.objectFit = isLedWall ? "cover" : "contain";
    img.style.maxWidth = "100%";
    img.style.maxHeight = "100%";
    stageNode.appendChild(img);
}

function renderVideo(fileUrl, isKiosk, loop) {
    const video = document.createElement("video");
    video.src = fileUrl;
    video.autoplay = true;
    video.muted = !isKiosk;
    video.loop = Boolean(loop);
    video.controls = isKiosk;
    video.style.maxWidth = "100%";
    video.style.maxHeight = "100%";
    if (deviceType === "LED_WALL") {
        video.playsInline = true;
        video.style.objectFit = "cover";
    }
    stageNode.appendChild(video);
}

function renderAudio(fileUrl, isKiosk, loop) {
    const audio = document.createElement("audio");
    audio.src = fileUrl;
    audio.autoplay = true;
    audio.muted = !isKiosk;
    audio.loop = Boolean(loop);
    audio.controls = true;
    audio.style.maxWidth = "100%";
    audio.style.maxHeight = "100%";
    stageNode.appendChild(audio);
}

function renderPdf(fileUrl) {
    const iframe = document.createElement("iframe");
    iframe.src = fileUrl;
    iframe.width = "100%";
    iframe.height = "100%";
    iframe.style.border = "none";
    stageNode.appendChild(iframe);
}

function renderHtml(fileUrl) {
    const iframe = document.createElement("iframe");
    iframe.src = fileUrl;
    iframe.width = "100%";
    iframe.height = "100%";
    iframe.style.border = "none";
    stageNode.appendChild(iframe);
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

                if (payload.source_type === "SCHEDULE") {
                    clearStage();
                    const doctorName = payload.doctor_name || "Unknown doctor";
                    const doctorDay = payload.doctor_schedule_day || "Unknown day";
                    const doctorStart = payload.doctor_schedule_start || "--:--";
                    const doctorEnd = payload.doctor_schedule_end || "--:--";
                    const opdRoomName = payload.opd_room_name || "Unknown OPD room";
                    const opdDay = payload.opd_schedule_day || "Unknown day";
                    const opdStart = payload.opd_schedule_start || "--:--";
                    const opdEnd = payload.opd_schedule_end || "--:--";

                    const details = document.createElement("div");
                    details.className = "placeholder";
                    details.innerHTML = `
                        <strong>Doctor Schedule</strong><br>
                        ${doctorName}<br>
                        ${doctorDay} ${doctorStart} - ${doctorEnd}<br><br>
                        <strong>OPD Schedule</strong><br>
                        ${opdRoomName}<br>
                        ${opdDay} ${opdStart} - ${opdEnd}
                    `;
                    stageNode.appendChild(details);
                    setStatus(`Displaying schedule for ${doctorName} in ${opdRoomName}`);
                    await sendAck(data.command_id, "PLAYING", "Schedule display started");
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
    