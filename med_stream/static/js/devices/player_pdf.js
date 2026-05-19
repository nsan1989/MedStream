function renderPdf(fileUrl) {
    const iframe = document.createElement("iframe");
    iframe.src = fileUrl;
    iframe.width = "100%";
    iframe.height = "100%";
    iframe.style.border = "none";
    stageNode.appendChild(iframe);
}
