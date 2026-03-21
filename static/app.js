document.addEventListener("DOMContentLoaded", () => {
  const $ = id => document.getElementById(id);
  const icons = {
    spinner: "icon-spinner",
    upload: "icon-upload",
    safe: "icon-safe",
    warning: "icon-warning",
    danger: "icon-danger",
    ela: "icon-ela"
  };

  const [
    upState, grid, resetBtn, dropZone, fileIn,
    img, overlay, runBtn, btnOrig, btnEla,
    qSlider, qVal, aSlider, aVal, results
  ] = [
    "uploadState","analysisState","resetBtn","dropZone","fileIn",
    "img","overlay","runBtn","btnOrig","btnEla",
    "qSlider","qVal","aSlider","aVal","results"
  ].map($);

  let file, origUrl, elaUrl, view = "original";

  qSlider.oninput = () => qVal.textContent = `${qSlider.value}%`;
  aSlider.oninput = () => aVal.textContent = `${aSlider.value}x`;

  dropZone.onclick = () => fileIn.click();
  fileIn.onchange = ({ target: { files } }) => files[0] && load(files[0]);

  dropZone.ondragover = e => (e.preventDefault(), dropZone.classList.add("dragging"));
  dropZone.ondragleave = () => dropZone.classList.remove("dragging");

  dropZone.ondrop = e => {
    e.preventDefault();
    dropZone.classList.remove("dragging");
    const f = e.dataTransfer.files[0];
    f && load(f);
  };

  const load = f => {
    if (!f.type.startsWith("image/")) return;

    file = f;

    const reader = new FileReader();
    reader.onload = ({ target: { result } }) => {
      origUrl = result;
      elaUrl = null;

      upState.style.display = "none";
      grid.style.display = "";
      resetBtn.style.display = "";

      img.src = origUrl;

      setView("original");
      btnEla.disabled = true;
      results.style.display = "none";
    };

    reader.readAsDataURL(f);
  };

  const setView = mode => {
    view = mode;
    img.src = mode === "ela" ? elaUrl : origUrl;

    btnOrig.className = `btn ${mode === "original" ? "btn-pri" : "btn-ghost"} btn-sm`;
    btnEla.className = `btn ${mode === "ela" ? "btn-ok" : "btn-ghost"} btn-sm`;
  };

  btnOrig.onclick = () => setView("original");
  btnEla.onclick = () => elaUrl && setView("ela");

  runBtn.onclick = async () => {
    if (!file) return;

    runBtn.disabled = true;
    overlay.style.display = "";
    runBtn.innerHTML = `
      <span class="flex w-full items-center justify-center gap-2">
        <span class="icon btn-ico-lg spinner btn-spinner ${icons.spinner}" aria-hidden="true"></span>
        <span>Analyzing...</span>
      </span>
    `;

    await new Promise(r => setTimeout(r, 300));

    const fd = new FormData();
    fd.append("image", file);
    fd.append("quality", qSlider.value);
    fd.append("amplification", aSlider.value);

    try {
      const res = await fetch("/analyze", { method: "POST", body: fd });
      const data = await res.json();

      elaUrl = data.elaDataUrl;
      btnEla.disabled = false;
      setView("ela");

      showResults(data);
    } catch (e) {
      console.error(e);
    } finally {
      overlay.style.display = "none";
      runBtn.disabled = false;
      runBtn.innerHTML = `
        <span class="flex w-full items-center justify-center gap-2">
          <span class="icon btn-ico-lg ${icons.upload}" aria-hidden="true"></span>
          <span>Run ELA Analysis</span>
        </span>
      `;
    }
  };

  const showResults = ({
    verdict, confidenceScore, maxDifference, avgDifference, suspiciousRegions
  }) => {
    results.style.display = "";

    const map = {
      likely_authentic: {
        label: "Likely Authentic",
        text: "t-safe",
        card: "v-safe",
        bar: "bg-safe",
        icon: icons.safe
      },
      possibly_tampered: {
        label: "Possibly Tampered",
        text: "t-warn",
        card: "v-warn",
        bar: "bg-warn",
        icon: icons.warning
      },
      likely_tampered: {
        label: "Likely Tampered",
        text: "t-danger",
        card: "v-danger",
        bar: "bg-danger",
        icon: icons.danger
      }
    };

    const s = map[verdict];

    $("vCard").className = `verdict ${s.card}`;
    $("vLabel").textContent = s.label;
    $("vLabel").className = `v-label ${s.text}`;
    $("vIcon").className = `v-icon icon ${s.text} ${s.icon}`;

    $("confVal").textContent = `${confidenceScore}%`;
    $("confBar").className = `conf-fill ${s.bar}`;
    $("confBar").style.width = `${confidenceScore}%`;

    $("sMax").textContent = maxDifference;
    $("sAvg").textContent = avgDifference;
    $("sSusp").textContent = `${suspiciousRegions}%`;
  };

  resetBtn.onclick = () => {
    file = origUrl = elaUrl = null;

    upState.style.display = "";
    grid.style.display = "none";
    resetBtn.style.display = "none";
    results.style.display = "none";
    fileIn.value = "";
  };
});