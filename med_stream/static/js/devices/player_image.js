function renderImage(fileUrl, isLedWall) {
    const img = document.createElement("img");
    img.src = fileUrl;
    img.alt = "Media Asset";
    img.style.objectFit = isLedWall ? "cover" : "contain";
    img.style.maxWidth = "100%";
    img.style.maxHeight = "100%";
    stageNode.appendChild(img);
}
