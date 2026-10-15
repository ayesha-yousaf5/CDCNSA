// Exports the app's Disease Library (app.js -> diseaseKnowledge, only the classes each model detects)
// to chatbot/app_disease_library.json so the chatbot answers from the SAME verified text.
// Run after editing the library:   node tools/export_library_for_chatbot.js
const fs = require('fs'), path = require('path'), vm = require('vm');
const root = path.resolve(__dirname, '..');
const src = fs.readFileSync(path.join(root, 'app.js'), 'utf8');
const ctx = { console: { warn() {}, log() {} }, state: { lang: 'en' } }; vm.createContext(ctx);
vm.runInContext(src.slice(0, src.indexOf('const i18n')) + '\n;this.__dk=diseaseKnowledge;this.__deep=diseaseDeepDetail;this.__chem=chemicalGuidance;', ctx);
const out = {};
for (const [crop, entries] of Object.entries(ctx.__dk)) {
  out[crop] = entries.map(e => { const d = ctx.__deep(crop, e); return {
    name: e.en, name_ur: e.ur, aliases: e.aliases || [], type: d.kind, cause: d.agent, risk: d.risk,
    symptoms: e.symptoms, symptoms_ur: e.urduSymptoms, management: e.management, prevention: e.prevention,
    chemical: ctx.__chem(e), note: e.classNote || '' }; });
}
fs.writeFileSync(path.join(root, 'chatbot', 'app_disease_library.json'), JSON.stringify(out, null, 1));
console.log('wrote chatbot/app_disease_library.json:', Object.entries(out).map(([c, a]) => c + ' ' + a.length).join(', '));
