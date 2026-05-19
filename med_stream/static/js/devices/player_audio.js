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
