function renderHtml(fileUrl) {
    // Apply background image
    stageNode.style.backgroundImage = "url('/static/images/html-bg.jpg')";
    stageNode.style.backgroundSize = "cover";
    stageNode.style.backgroundPosition = "center";
    stageNode.style.backgroundRepeat = "no-repeat";

    const wrapper = document.createElement("div");
    wrapper.style.width = "100%";
    wrapper.style.height = "100%";
    wrapper.style.background = "rgba(0,0,0,0.20)";

    const iframe = document.createElement("iframe");
    iframe.src = fileUrl;
    iframe.width = "100%";
    iframe.height = "100%";
    iframe.style.border = "none";
    iframe.style.background = "transparent";

    wrapper.appendChild(iframe);
    stageNode.appendChild(wrapper);
}
