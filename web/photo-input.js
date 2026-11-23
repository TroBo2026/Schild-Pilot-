const MAX_PHOTO_BYTES = 25 * 1024 * 1024;

function validatePhotoFile(file) {
  if (!file || typeof file.type !== "string" || !file.type.startsWith("image/")) {
    return { ok: false, message: "Bitte wähle eine Bilddatei aus." };
  }
  if (typeof file.size !== "number" || !Number.isFinite(file.size) || file.size <= 0) {
    return { ok: false, message: "Die Bilddatei ist leer oder hat eine ungültige Größe." };
  }
  if (file.size > MAX_PHOTO_BYTES) {
    return { ok: false, message: "Das Foto ist größer als 25 MB. Bitte wähle eine kleinere Aufnahme." };
  }
  return { ok: true, message: "" };
}

function attachPhotoInput(elements, urlApi = URL) {
  let objectUrl = null;

  function releasePreview() {
    if (objectUrl) {
      urlApi.revokeObjectURL(objectUrl);
      objectUrl = null;
    }
    elements.preview.onerror = null;
    elements.preview.removeAttribute("src");
    elements.previewWrap.hidden = true;
    elements.analyzeButton.disabled = true;
  }

  function resetPhoto(message) {
    releasePreview();
    elements.input.value = "";
    elements.statusText.textContent = message;
    elements.resultTitle.textContent = "Kein verwendbares Foto geladen";
    elements.resultText.textContent =
      "Wähle ein unterstütztes Bild aus. Die eigentliche Verkehrszeichenerkennung ist noch nicht verbunden.";
  }

  elements.input.addEventListener("change", () => {
    const file = elements.input.files?.[0];
    if (!file) return;

    const validation = validatePhotoFile(file);
    if (!validation.ok) {
      resetPhoto(validation.message);
      return;
    }

    if (objectUrl) {
      urlApi.revokeObjectURL(objectUrl);
      objectUrl = null;
    }

    let nextUrl;
    try {
      nextUrl = urlApi.createObjectURL(file);
    } catch {
      resetPhoto("Das Foto konnte im Browser nicht geöffnet werden.");
      return;
    }

    objectUrl = nextUrl;
    elements.preview.onerror = () => {
      if (objectUrl === nextUrl) {
        resetPhoto("Dieses Bildformat kann der Browser nicht anzeigen. Bitte nutze JPG, PNG oder WEBP.");
      }
    };
    elements.preview.src = nextUrl;
    elements.previewWrap.hidden = false;
    elements.analyzeButton.disabled = true;
    elements.statusText.textContent =
      `Foto lokal geladen: ${file.name || "ohne Dateinamen"} · ${Math.round(file.size / 1024)} KB. Noch keine KI-Analyse.`;
    elements.resultTitle.textContent = "Foto bereit – KI noch nicht verbunden";
    elements.resultText.textContent =
      "Das Foto wird nur in dieser Browseransicht angezeigt. Es wird noch kein Verkehrszeichen erkannt und kein Ergebnis geraten.";
  });

  elements.clearButton.addEventListener("click", () => {
    resetPhoto("Foto entfernt. Du kannst ein neues Bild aufnehmen oder auswählen.");
  });

  return { releasePreview };
}

const photoInputApi = { MAX_PHOTO_BYTES, validatePhotoFile, attachPhotoInput };

if (typeof module !== "undefined" && module.exports) {
  module.exports = photoInputApi;
}
if (typeof globalThis !== "undefined") {
  globalThis.SchildPilotPhotoInput = photoInputApi;
}
