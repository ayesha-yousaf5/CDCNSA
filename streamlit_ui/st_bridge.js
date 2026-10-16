/* CDCNSA - Streamlit bridge.
 * The original website (index.html + app.js + styles.css, unchanged) runs inside a Streamlit
 * component. app.js calls fetch('/api/...') exactly as on the FastAPI server; this script catches
 * those calls and sends them to streamlit_app.py through the Streamlit component messages, then
 * hands the Python answer back to app.js as a normal fetch Response. Other URLs use the real fetch.
 */
(function () {
  const pending = new Map();   // id -> {req, resolve, reject}
  let seq = 0;

  function post(type, extra) {
    window.parent.postMessage(Object.assign({ isStreamlitMessage: true, type: type }, extra || {}), '*');
  }
  function flush() {
    const requests = [...pending.entries()].map(([id, p]) => Object.assign({ id: id }, p.req));
    post('streamlit:setComponentValue', { value: { requests: requests, sent: Date.now() }, dataType: 'json' });
  }
  function toResponse(r) {
    const type = r.content_type || 'application/json';
    let body;
    if (r.b64 != null) {
      const bin = atob(r.b64);
      const bytes = new Uint8Array(bin.length);
      for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
      body = new Blob([bytes], { type: type });
    } else {
      body = r.text || '';
    }
    return new Response(body, { status: r.status || 200, headers: { 'Content-Type': type } });
  }
  async function blobToB64(blob) {
    const bytes = new Uint8Array(await blob.arrayBuffer());
    let s = '';
    for (let i = 0; i < bytes.length; i += 0x8000) s += String.fromCharCode.apply(null, bytes.subarray(i, i + 0x8000));
    return btoa(s);
  }

  window.addEventListener('message', function (ev) {
    const d = ev.data;
    if (!d || d.type !== 'streamlit:render') return;
    const responses = (d.args && d.args.responses) || {};
    Object.keys(responses).forEach(function (id) {
      const p = pending.get(id);
      if (!p) return;
      pending.delete(id);
      p.resolve(toResponse(responses[id]));
    });
  });

  const realFetch = window.fetch.bind(window);
  window.fetch = async function (input, init) {
    const url = typeof input === 'string' ? input : (input && input.url) || '';
    if (!url.startsWith('/api/')) return realFetch(input, init);
    init = init || {};
    const req = { path: url.split('?')[0], method: (init.method || 'GET').toUpperCase() };
    if (init.body instanceof FormData) {
      const form = {};
      for (const [k, v] of init.body.entries()) {
        form[k] = (v instanceof Blob) ? { b64: await blobToB64(v), name: v.name || 'upload', type: v.type || '' } : String(v);
      }
      req.form = form;
    } else if (typeof init.body === 'string') {
      req.json = init.body;
    }
    const id = 'r' + (++seq) + '_' + Date.now();
    return new Promise(function (resolve, reject) {
      pending.set(id, { req: req, resolve: resolve, reject: reject });
      flush();
      setTimeout(function () {
        if (pending.has(id)) { pending.delete(id); reject(new Error('The server took too long. Please try again.')); }
      }, 240000);
    });
  };

  post('streamlit:componentReady', { apiVersion: 1 });
})();
