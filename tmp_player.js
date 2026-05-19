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

        {% include "device/player_image.html" %}
        {% include "device/player_video.html" %}
        {% include "device/player_audio.html" %}
        {% include "device/player_pdf.html" %}
        {% include "device/player_html.html" %}

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