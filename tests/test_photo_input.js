const test = require("node:test");
const assert = require("node:assert/strict");
const {
  MAX_PHOTO_BYTES,
  validatePhotoFile,
  attachPhotoInput,
} = require("../web/photo-input.js");

function makeElement() {
  const listeners = {};
  return {
    listeners,
    addEventListener(name, callback) {
      listeners[name] = callback;
    },
    trigger(name) {
      assert.equal(typeof listeners[name], "function", `Missing listener: ${name}`);
      listeners[name]();
    },
  };
}

function makeHarness() {
  const input = makeElement();
  input.files = [];
  input.value = "";

  const preview = {
    src: "",
    onerror: null,
    removeAttribute(name) {
      if (name === "src") this.src = "";
    },
  };
  const previewWrap = { hidden: true };
  const analyzeButton = { disabled: true };
  const clearButton = makeElement();
  const statusText = { textContent: "" };
  const resultTitle = { textContent: "" };
  const resultText = { textContent: "" };
  let nextUrl = 0;
  const created = [];
  const revoked = [];
  const urlApi = {
    createObjectURL(file) {
      const url = `blob:photo-${++nextUrl}`;
      created.push({ url, file });
      return url;
    },
    revokeObjectURL(url) {
      revoked.push(url);
    },
  };

  const elements = {
    input,
    preview,
    previewWrap,
    analyzeButton,
    clearButton,
    statusText,
    resultTitle,
    resultText,
  };
  attachPhotoInput(elements, urlApi);
  return { elements, urlApi, created, revoked };
}

test("accepts non-empty image files up to 25 MB", () => {
  assert.equal(validatePhotoFile({ type: "image/jpeg", size: 1024 }).ok, true);
  assert.equal(validatePhotoFile({ type: "image/png", size: MAX_PHOTO_BYTES }).ok, true);
});

test("rejects non-images, empty files and files over 25 MB", () => {
  assert.match(validatePhotoFile({ type: "text/plain", size: 100 }).message, /Bilddatei/);
  assert.match(validatePhotoFile({ type: "image/jpeg", size: 0 }).message, /leer/);
  assert.match(
    validatePhotoFile({ type: "image/jpeg", size: MAX_PHOTO_BYTES + 1 }).message,
    /25 MB/,
  );
});

test("keeps a valid photo local and never enables unavailable inference", () => {
  const { elements, created } = makeHarness();
  elements.input.files = [{ type: "image/jpeg", size: 2048, name: "strasse.jpg" }];
  elements.input.trigger("change");

  assert.equal(created.length, 1);
  assert.equal(elements.preview.src, created[0].url);
  assert.equal(elements.previewWrap.hidden, false);
  assert.equal(elements.analyzeButton.disabled, true);
  assert.match(elements.statusText.textContent, /lokal geladen/);
  assert.match(elements.resultText.textContent, /kein Verkehrszeichen erkannt/);
});

test("invalid replacement clears and revokes the previous local preview", () => {
  const { elements, revoked } = makeHarness();
  elements.input.files = [{ type: "image/jpeg", size: 2048, name: "strasse.jpg" }];
  elements.input.trigger("change");
  const previousUrl = elements.preview.src;

  elements.input.files = [{ type: "text/plain", size: 100, name: "not-image.txt" }];
  elements.input.trigger("change");

  assert.deepEqual(revoked, [previousUrl]);
  assert.equal(elements.preview.src, "");
  assert.equal(elements.previewWrap.hidden, true);
  assert.equal(elements.analyzeButton.disabled, true);
  assert.equal(elements.input.value, "");
  assert.match(elements.statusText.textContent, /Bilddatei/);
});

test("clear button revokes the preview and resets the input", () => {
  const { elements, revoked } = makeHarness();
  elements.input.files = [{ type: "image/webp", size: 4096, name: "schild.webp" }];
  elements.input.trigger("change");
  const previousUrl = elements.preview.src;

  elements.clearButton.trigger("click");

  assert.deepEqual(revoked, [previousUrl]);
  assert.equal(elements.preview.src, "");
  assert.equal(elements.previewWrap.hidden, true);
  assert.equal(elements.analyzeButton.disabled, true);
  assert.equal(elements.input.value, "");
  assert.match(elements.statusText.textContent, /Foto entfernt/);
});

test("an unsupported browser image format clears only the current preview", () => {
  const { elements, revoked } = makeHarness();
  elements.input.files = [{ type: "image/heic", size: 4096, name: "schild.heic" }];
  elements.input.trigger("change");
  const currentUrl = elements.preview.src;

  elements.preview.onerror();

  assert.deepEqual(revoked, [currentUrl]);
  assert.equal(elements.preview.src, "");
  assert.equal(elements.previewWrap.hidden, true);
  assert.match(elements.statusText.textContent, /JPG, PNG oder WEBP/);
});
