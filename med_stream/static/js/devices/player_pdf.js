function renderPdf(fileUrl) {
    // Apply background image
    stageNode.style.backgroundImage = "url('/static/images/pdf-bg.jpg')";
    stageNode.style.backgroundSize = "cover";
    stageNode.style.backgroundPosition = "center";
    stageNode.style.backgroundRepeat = "no-repeat";

    // Create wrapper for overlay effect
    const wrapper = document.createElement("div");
    wrapper.style.width = "100%";
    wrapper.style.height = "100%";
    wrapper.style.display = "flex";
    wrapper.style.justifyContent = "center";
    wrapper.style.alignItems = "center";
    wrapper.style.background = "rgba(0,0,0,0.25)";
    wrapper.style.backdropFilter = "blur(2px)";

    // PDF iframe
    const iframe = document.createElement("iframe");
    iframe.src = fileUrl;
    iframe.style.width = "95%";
    iframe.style.height = "95%";
    iframe.style.border = "none";
    iframe.style.borderRadius = "16px";
    iframe.style.background = "#fff";
    iframe.style.boxShadow = "0 8px 30px rgba(0,0,0,0.35)";

    wrapper.appendChild(iframe);
    stageNode.appendChild(wrapper);
}
