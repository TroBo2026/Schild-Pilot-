const signs = [
  { id:"205", name:"Vorfahrt gewähren", meaning:"Du musst dem Verkehr auf der bevorrechtigten Straße Vorfahrt gewähren. Das Schild steht normalerweise vor einer Kreuzung oder Einmündung.", options:["Vorfahrt gewähren","Halt. Vorfahrt gewähren","Vorfahrtstraße","Vorrang vor dem Gegenverkehr"], shape:"yield" },
  { id:"206", name:"Halt. Vorfahrt gewähren", meaning:"Du musst anhalten und Vorfahrt gewähren. Ohne Haltlinie hältst du dort, wo du die andere Straße gut überblicken kannst.", options:["Vorfahrt gewähren","Halt. Vorfahrt gewähren","Verbot der Einfahrt","Vorrang vor dem Gegenverkehr"], shape:"stop" },
  { id:"267", name:"Verbot der Einfahrt", meaning:"Du darfst mit einem Fahrzeug nicht in die Fahrbahn einfahren, für die das Schild angeordnet ist.", options:["Verbot für Fahrzeuge aller Art","Verbot der Einfahrt","Absolutes Haltverbot","Vorgeschriebene Fahrtrichtung"], shape:"noentry" },
  { id:"274", name:"Zulässige Höchstgeschwindigkeit", meaning:"Du darfst nicht schneller als die angegebene Höchstgeschwindigkeit fahren. In diesem Beispiel beträgt sie 50 km/h.", options:["Vorgeschriebene Mindestgeschwindigkeit","Zulässige Höchstgeschwindigkeit","Ende sämtlicher Streckenverbote","Beginn einer Tempo-30-Zone"], shape:"speed" },
  { id:"301", name:"Vorfahrt", meaning:"Das Zeichen zeigt an, dass du an der nächsten Kreuzung oder Einmündung Vorfahrt hast.", options:["Vorfahrtstraße","Vorfahrt","Ende der Vorfahrtstraße","Vorrang vor dem Gegenverkehr"], shape:"priority" },
  { id:"306", name:"Vorfahrtstraße", meaning:"Du befindest dich auf einer Vorfahrtstraße. Sie gilt bis zu einem Ende-Schild oder bis zu einem entsprechenden Warte- oder Haltgebot.", options:["Vorfahrt","Vorfahrtstraße","Vorfahrt gewähren","Einbahnstraße"], shape:"priority-road" },
  { id:"250", name:"Verbot für Fahrzeuge aller Art", meaning:"Die Straße darf grundsätzlich nicht mit Fahrzeugen befahren werden. Maßgeblich sind die StVO-Regelung und mögliche Zusatzzeichen.", options:["Verbot der Einfahrt","Verbot für Fahrzeuge aller Art","Verbot des Wendens","Eingeschränktes Haltverbot"], shape:"all-vehicles" },
  { id:"350", name:"Fußgängerüberweg", meaning:"Das Schild kennzeichnet einen Fußgängerüberweg. Fahrzeugführende müssen sich vorsichtig nähern und zu Fuß Gehenden das Überqueren ermöglichen.", options:["Gehweg","Fußgängerzone","Fußgängerüberweg","Gemeinsamer Geh- und Radweg"], shape:"crossing" }
];

const svg = (body, label) => `<svg viewBox="0 0 200 200" role="img" aria-label="${label}" xmlns="http://www.w3.org/2000/svg">${body}</svg>`;
function signSvg(sign) {
  const shapes = {
    yield: svg('<path d="M34 45 L166 45 L100 166 Z" fill="#fff" stroke="#d6292f" stroke-width="13" stroke-linejoin="round"/>', sign.name),
    stop: svg('<polygon points="67,20 133,20 180,67 180,133 133,180 67,180 20,133 20,67" fill="#d8202f" stroke="#fff" stroke-width="8"/><text x="100" y="111" text-anchor="middle" font-size="43" font-weight="800" fill="#fff">STOP</text>', sign.name),
    noentry: svg('<circle cx="100" cy="100" r="76" fill="#d8202f"/><rect x="35" y="82" width="130" height="36" rx="4" fill="#fff"/>', sign.name),
    speed: svg('<circle cx="100" cy="100" r="76" fill="#fff" stroke="#d8202f" stroke-width="13"/><text x="100" y="116" text-anchor="middle" font-size="58" font-weight="700" fill="#161616">50</text>', sign.name),
    priority: svg('<path d="M100 14 L186 100 L100 186 L14 100 Z" fill="#f4cf35" stroke="#fff" stroke-width="11"/><path d="M100 30 L170 100 L100 170 L30 100 Z" fill="#f4cf35" stroke="#1c1c1c" stroke-width="4"/>', sign.name),
    "priority-road": svg('<path d="M100 14 L186 100 L100 186 L14 100 Z" fill="#f4cf35" stroke="#fff" stroke-width="12"/><path d="M100 31 L169 100 L100 169 L31 100 Z" fill="#f4cf35" stroke="#1c1c1c" stroke-width="3"/>', sign.name),
    "all-vehicles": svg('<circle cx="100" cy="100" r="76" fill="#fff" stroke="#d8202f" stroke-width="13"/>', sign.name),
    crossing: svg('<rect x="14" y="14" width="172" height="172" rx="7" fill="#0875b9" stroke="#fff" stroke-width="5"/><path d="M100 35 L165 158 L35 158 Z" fill="#fff"/><circle cx="100" cy="75" r="9" fill="#111"/><path d="M98 85 L89 112 L105 122 M92 99 L76 112 M92 110 L82 137 M102 119 L119 139" stroke="#111" stroke-width="7" fill="none" stroke-linecap="round"/><path d="M42 147 H158 M49 137 H151" stroke="#111" stroke-width="5"/>', sign.name)
  };
  return shapes[sign.shape] || "";
}

const lessonArtwork = document.querySelector("#lessonArtwork");
const lessonTitle = document.querySelector("#lessonTitle");
const lessonName = document.querySelector("#lessonName");
const lessonMeaning = document.querySelector("#lessonMeaning");
const lessonCount = document.querySelector("#lessonCount");
const quizStart = document.querySelector("#quizStartButton");
const quizPanel = document.querySelector("#quizPanel");
const quizArtwork = document.querySelector("#quizArtwork");
const answerOptions = document.querySelector("#answerOptions");
const quizFeedback = document.querySelector("#quizFeedback");
const nextSign = document.querySelector("#nextSignButton");
let lessonIndex = 0;
let answered = false;

function renderLesson() {
  const sign = signs[lessonIndex];
  lessonTitle.textContent = `Verkehrszeichen ${sign.id}`;
  lessonName.textContent = sign.name;
  lessonMeaning.textContent = sign.meaning;
  lessonArtwork.innerHTML = signSvg(sign);
  lessonCount.textContent = `${String(lessonIndex + 1).padStart(2,"0")} / ${String(signs.length).padStart(2,"0")}`;
  quizPanel.hidden = true;
  quizStart.hidden = false;
  quizStart.textContent = "Verstanden – jetzt abfragen";
  nextSign.hidden = true;
  answered = false;
}

function shuffled(items) {
  const copy = [...items];
  for (let i = copy.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [copy[i], copy[j]] = [copy[j], copy[i]];
  }
  return copy;
}

function startQuiz() {
  const sign = signs[lessonIndex];
  quizPanel.hidden = false;
  quizArtwork.innerHTML = signSvg(sign);
  quizFeedback.textContent = "";
  answerOptions.innerHTML = "";
  answered = false;
  const options = shuffled(sign.options);
  for (const option of options) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "answer-option";
    button.textContent = option;
    button.addEventListener("click", () => chooseAnswer(option, button));
    answerOptions.append(button);
  }
  quizStart.hidden = true;
}

function chooseAnswer(option, selectedButton) {
  if (answered) return;
  answered = true;
  const sign = signs[lessonIndex];
  const correct = option === sign.name;
  for (const button of answerOptions.querySelectorAll("button")) {
    button.disabled = true;
    if (button.textContent === sign.name) button.classList.add("correct");
  }
  if (correct) {
    selectedButton.classList.add("correct");
    quizFeedback.textContent = `Richtig. ${sign.name}: ${sign.meaning}`;
    quizFeedback.className = "quiz-feedback success";
  } else {
    selectedButton.classList.add("incorrect");
    quizFeedback.textContent = `Noch nicht ganz. Richtig ist „${sign.name}“. ${sign.meaning}`;
    quizFeedback.className = "quiz-feedback";
  }
  nextSign.hidden = false;
}

quizStart.addEventListener("click", startQuiz);
nextSign.addEventListener("click", () => {
  lessonIndex = (lessonIndex + 1) % signs.length;
  renderLesson();
});
renderLesson();

// Fotoeingabe bleibt eine Vorschau. Ohne eingebundenes Modell wird kein Erkennungsergebnis erfunden.
const input = document.querySelector("#imageInput");
const wrap = document.querySelector("#previewWrap");
const preview = document.querySelector("#preview");
const analyze = document.querySelector("#analyzeButton");
const clear = document.querySelector("#clearButton");
const status = document.querySelector("#statusText");
let objectUrl = null;
input.addEventListener("change", () => {
  const file = input.files?.[0];
  if (!file) return;
  if (!file.type.startsWith("image/")) {
    status.textContent = "Bitte wähle eine Bilddatei aus.";
    input.value = "";
    return;
  }
  if (objectUrl) URL.revokeObjectURL(objectUrl);
  objectUrl = URL.createObjectURL(file);
  preview.src = objectUrl;
  wrap.hidden = false;
  analyze.disabled = false;
  status.textContent = `Bild geladen: ${file.name} · ${Math.round(file.size / 1024)} KB`;
  document.querySelector("#resultTitle").textContent = "Foto bereit – KI noch nicht verbunden";
  document.querySelector("#resultText").textContent = "Die Fotoeingabe funktioniert. Die KI-Fotoerkennung wird erst nach Modellintegration und Tests aktiviert. Es wird kein Ergebnis geraten.";
});
clear.addEventListener("click", () => {
  input.value = "";
  preview.removeAttribute("src");
  wrap.hidden = true;
  analyze.disabled = true;
  status.textContent = "Noch kein Bild ausgewählt. Die KI-Fotoerkennung ist noch nicht verbunden.";
  if (objectUrl) URL.revokeObjectURL(objectUrl);
  objectUrl = null;
});
analyze.addEventListener("click", () => {
  document.querySelector("#resultTitle").textContent = "KI-Fotoerkennung noch nicht verbunden";
  document.querySelector("#resultText").textContent = "Das Bild ist bereit. Der Lernmodus funktioniert bereits, die eigentliche Erkennung eigener Fotos folgt nach dem Training und der Integration des Modells.";
  status.textContent = "Fotoeingabe bereit · Modellintegration folgt.";
});
