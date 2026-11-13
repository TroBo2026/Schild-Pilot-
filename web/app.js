const input=document.querySelector("#imageInput");
const wrap=document.querySelector("#previewWrap");
const preview=document.querySelector("#preview");
const analyze=document.querySelector("#analyzeButton");
const clear=document.querySelector("#clearButton");
const status=document.querySelector("#statusText");
let objectUrl=null;
input.addEventListener("change",()=>{
 const file=input.files?.[0];if(!file)return;
 if(!file.type.startsWith("image/")){status.textContent="Bitte wähle eine Bilddatei aus.";input.value="";return;}
 if(objectUrl)URL.revokeObjectURL(objectUrl);
 objectUrl=URL.createObjectURL(file);preview.src=objectUrl;wrap.hidden=false;analyze.disabled=false;
 status.textContent=`Bild geladen: ${file.name} · ${Math.round(file.size/1024)} KB`;
 document.querySelector("#resultTitle").textContent="Bild erfolgreich geladen";
 document.querySelector("#resultText").textContent="Die Fotoeingabe funktioniert. Als Nächstes verbinden wir Detektor und Klassifikationsmodell. Bis dahin wird bewusst keine Erkennung simuliert.";
});
clear.addEventListener("click",()=>{
 input.value="";preview.removeAttribute("src");wrap.hidden=true;analyze.disabled=true;status.textContent="Noch kein Bild ausgewählt.";
 if(objectUrl)URL.revokeObjectURL(objectUrl);objectUrl=null;
});
analyze.addEventListener("click",()=>{
 document.querySelector("#resultTitle").textContent="KI-Modell noch nicht verbunden";
 document.querySelector("#resultText").textContent="Das Bild ist bereit. Die eigentliche Verkehrszeichenerkennung wird nach Training, Einbindung und Tests aktiviert. Es wird kein Ergebnis erfunden.";
 status.textContent="Fotoeingabe bereit · Modell folgt in der nächsten Entwicklungsphase.";
});