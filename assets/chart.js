/* Small dependency-free chart helpers. Colours come from CSS custom properties, so light and dark follow the page. */
(function () {
  "use strict";
  var NS = "http://www.w3.org/2000/svg";

  function svg(tag, attrs, parent) {
    var e = document.createElementNS(NS, tag);
    for (var k in attrs) if (attrs[k] !== undefined && attrs[k] !== null) e.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(e);
    return e;
  }
  function html(tag, cls, parent, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text !== undefined) e.textContent = text;
    if (parent) parent.appendChild(e);
    return e;
  }
  function niceTicks(lo, hi, n) {
    var span = hi - lo, raw = span / Math.max(1, n), p = Math.pow(10, Math.floor(Math.log10(raw))), f = raw / p;
    var step = p * (f >= 7.5 ? 10 : f >= 3.5 ? 5 : f >= 1.5 ? 2 : 1), out = [];
    for (var v = Math.ceil(lo / step - 1e-9) * step; v <= hi + step * 1e-9; v += step) out.push(+v.toFixed(10));
    return { values: out, step: step };
  }
  function decimals(step) { return Math.max(0, Math.min(6, -Math.floor(Math.log10(step) + 1e-9))); }
  function fmt(v, d) { if (Math.abs(v) < 0.5 * Math.pow(10, -d)) v = 0; return v.toLocaleString("en-US", { minimumFractionDigits: d, maximumFractionDigits: d }).replace("-", "−"); }

  /* ------------------------------------------------------------------ x/y chart */
  function xy(root, cfg) {
    root.classList.add("viz");
    root.innerHTML = "";
    var named = cfg.series.filter(function (s) { return s.name; });
    if (named.length >= 2) {
      var legend = html("div", "viz-legend", root);
      named.forEach(function (s) {
        var item = html("span", "viz-legend-item", legend);
        var sw = html("span", "viz-swatch viz-swatch-" + (s.kind === "line" ? "line" : "dot"), item);
        sw.style.setProperty("--c", "var(" + s.color + ")");
        html("span", null, item, s.name);
      });
    }
    if (cfg.y.label) html("div", "viz-ylabel", root, cfg.y.label);
    var frame = html("div", "viz-frame", root);
    var tip = html("div", "viz-tip", frame); tip.hidden = true;
    var el = svg("svg", { role: "img", "aria-label": cfg.label || "" }, frame);
    var uid = "c" + Math.random().toString(36).slice(2, 8);

    function draw() {
      var W = Math.max(260, Math.floor(frame.clientWidth));
      var m = { l: cfg.marginLeft || 50, r: 14, t: 10, b: cfg.x.label ? 42 : 24 };
      var H = cfg.square ? (W - m.l - m.r) + m.t + m.b : (cfg.height || 300);
      while (el.firstChild) el.removeChild(el.firstChild);
      el.setAttribute("viewBox", "0 0 " + W + " " + H); el.setAttribute("width", W); el.setAttribute("height", H);
      var pw = W - m.l - m.r, ph = H - m.t - m.b;
      var lx = cfg.x.log ? Math.log10 : function (v) { return v; };
      var x0 = lx(cfg.x.min), x1 = lx(cfg.x.max);
      var X = function (v) { return m.l + (lx(v) - x0) / (x1 - x0) * pw; };
      var Y = function (v) { return m.t + (1 - (v - cfg.y.min) / (cfg.y.max - cfg.y.min)) * ph; };
      svg("clipPath", { id: uid }, el).appendChild(svg("rect", { x: m.l, y: m.t - 4, width: pw, height: ph + 8 }));
      var back = svg("g", {}, el), plot = svg("g", { "clip-path": "url(#" + uid + ")" }, el), front = svg("g", {}, el);

      // bands (behind everything)
      (cfg.marks || []).forEach(function (k) {
        if (k.kind !== "band") return;
        svg("rect", { x: X(k.x0), y: m.t, width: Math.max(0, X(k.x1) - X(k.x0)), height: ph, class: "viz-band" }, back);
        if (k.label) svg("text", { x: (X(k.x0) + X(k.x1)) / 2, y: m.t + 12, class: "viz-mark-label", "text-anchor": "middle" }, front).textContent = k.label;
      });
      // y grid + ticks
      var yt = cfg.y.ticks ? { values: cfg.y.ticks, step: cfg.y.step || 1 } : niceTicks(cfg.y.min, cfg.y.max, Math.max(3, Math.round(ph / 55)));
      var yd = cfg.y.digits !== undefined ? cfg.y.digits : decimals(yt.step);
      yt.values.forEach(function (v) {
        svg("line", { x1: m.l, x2: m.l + pw, y1: Y(v), y2: Y(v), class: v === 0 && cfg.y.zeroLine ? "viz-axis" : "viz-grid" }, back);
        svg("text", { x: m.l - 8, y: Y(v) + 4, class: "viz-tick", "text-anchor": "end" }, back).textContent = fmt(v, yd);
      });
      // x axis + ticks
      svg("line", { x1: m.l, x2: m.l + pw, y1: m.t + ph, y2: m.t + ph, class: "viz-axis" }, back);
      var xt;
      if (cfg.x.ticks) xt = cfg.x.ticks;
      else if (cfg.x.log) xt = [0.5, 1, 2, 5, 10, 20, 50].filter(function (v) { return v >= cfg.x.min && v <= cfg.x.max; }).map(function (v) { return { v: v, label: String(v) }; });
      else { var t = niceTicks(cfg.x.min, cfg.x.max, Math.max(3, Math.round(pw / 90))), xd = cfg.x.digits !== undefined ? cfg.x.digits : decimals(t.step); xt = t.values.map(function (v) { return { v: v, label: fmt(v, xd) }; }); }
      xt.forEach(function (k) {
        svg("line", { x1: X(k.v), x2: X(k.v), y1: m.t + ph, y2: m.t + ph + 4, class: "viz-axis" }, back);
        svg("text", { x: X(k.v), y: m.t + ph + 17, class: "viz-tick", "text-anchor": "middle" }, back).textContent = k.label;
      });
      if (cfg.x.label) svg("text", { x: m.l + pw / 2, y: H - 6, class: "viz-axis-title", "text-anchor": "middle" }, back).textContent = cfg.x.label;

      // reference marks
      (cfg.marks || []).forEach(function (k) {
        if (k.kind === "vline") {
          svg("line", { x1: X(k.x), x2: X(k.x), y1: m.t, y2: m.t + ph, class: "viz-ref" + (k.faint ? " viz-ref-faint" : "") }, plot);
          if (k.label) {
            var right = X(k.x) > m.l + pw * 0.6;
            svg("text", { x: X(k.x) + (right ? -6 : 6), y: m.t + (k.dy || 12), class: "viz-mark-label", "text-anchor": right ? "end" : "start" }, front).textContent = k.label;
          }
        } else if (k.kind === "hline") {
          svg("line", { x1: m.l, x2: m.l + pw, y1: Y(k.y), y2: Y(k.y), class: "viz-ref" }, plot);
          if (k.label) svg("text", { x: m.l + pw - 4, y: Y(k.y) - 5, class: "viz-mark-label", "text-anchor": "end" }, front).textContent = k.label;
        } else if (k.kind === "circle") {
          svg("circle", { cx: X(k.x), cy: Y(k.y), r: Math.abs(X(k.r) - X(0)), class: "viz-ref-circle" }, plot);
          if (k.label) svg("text", { x: X(k.x), y: Y(k.y + k.r) - 4, class: "viz-mark-label", "text-anchor": "middle" }, front).textContent = k.label;
        } else if (k.kind === "text") {
          svg("text", { x: X(k.x), y: Y(k.y), class: "viz-mark-label", "text-anchor": k.anchor || "start" }, front).textContent = k.text;
        }
      });

      // series
      var hover = [];
      cfg.series.forEach(function (s) {
        var col = "var(" + s.color + ")", dx = s.dx || 0;
        if (s.kind === "line") {
          var d = "";
          s.data.forEach(function (p, i) { d += (i ? "L" : "M") + X(p[0]).toFixed(1) + " " + Y(p[1]).toFixed(1); });
          svg("path", { d: d, fill: "none", stroke: col, "stroke-width": s.width || 2, "stroke-linejoin": "round", "stroke-linecap": "round" }, plot);
          if (s.hover) s.data.forEach(function (p) { hover.push({ px: X(p[0]), py: Y(p[1]), s: s, p: p }); });
        } else if (s.kind === "cloud") {
          var g = svg("g", { fill: col, opacity: s.opacity || 0.28 }, plot);
          s.data.forEach(function (p) { svg("circle", { cx: X(p[0]).toFixed(1), cy: Y(p[1]).toFixed(1), r: s.r || 1.1 }, g); });
        } else {
          var ge = svg("g", { stroke: col, "stroke-width": 1.25, opacity: 0.55 }, plot), gp = svg("g", { fill: col }, plot);
          s.data.forEach(function (p) {
            var px = X(p[0] + dx), py = Y(p[1]);
            if (p[2] !== null && p[2] !== undefined && s.err !== false) svg("line", { x1: px, x2: px, y1: Y(p[1] - p[2]), y2: Y(p[1] + p[2]) }, ge);
            var r = typeof s.r === "function" ? s.r(p) : (s.r || 4);
            svg("circle", { cx: px.toFixed(1), cy: py.toFixed(1), r: r, class: s.ring === false ? "" : "viz-ring" }, gp);
            if (s.hover !== false) hover.push({ px: px, py: py, s: s, p: p, r: r });
          });
        }
      });
      var ring = svg("circle", { r: 7, class: "viz-hover-ring", visibility: "hidden" }, front);

      function show(ev) {
        var box = el.getBoundingClientRect(), mx = ev.clientX - box.left, my = ev.clientY - box.top, best = null, bd = 1e9;
        for (var i = 0; i < hover.length; i++) { var h = hover[i], dd = (h.px - mx) * (h.px - mx) + (h.py - my) * (h.py - my); if (dd < bd) { bd = dd; best = h; } }
        if (!best || bd > 60 * 60) { hide(); return; }
        ring.setAttribute("cx", best.px); ring.setAttribute("cy", best.py); ring.setAttribute("r", (best.r || 3) + 4); ring.setAttribute("visibility", "visible");
        tip.innerHTML = "";
        if (named.length >= 2 && best.s.name) html("div", "viz-tip-title", tip, best.s.name);
        var lines = best.s.tip ? best.s.tip(best.p) : [
          [cfg.x.name || cfg.x.label, cfg.x.fmt ? cfg.x.fmt(best.p[0]) : String(best.p[0])],
          [cfg.y.name || cfg.y.label, (cfg.y.fmt ? cfg.y.fmt(best.p[1]) : String(best.p[1])) + (best.p[2] !== null && best.p[2] !== undefined && best.s.err !== false ? " ± " + (cfg.y.fmt ? cfg.y.fmt(best.p[2]) : best.p[2]) : "")]
        ];
        lines.forEach(function (l) { var row = html("div", "viz-tip-row", tip); html("span", "viz-tip-key", row, l[0]); html("span", "viz-tip-val", row, l[1]); });
        tip.hidden = false;
        var tw = tip.offsetWidth, left = best.px + 14; if (left + tw > W - 4) left = best.px - tw - 14;
        tip.style.left = Math.max(4, left) + "px"; tip.style.top = Math.max(4, best.py - tip.offsetHeight - 10) + "px";
      }
      function hide() { tip.hidden = true; ring.setAttribute("visibility", "hidden"); }
      el.onpointermove = show; el.onpointerdown = show; el.onpointerleave = hide;
    }
    draw();
    if (window.ResizeObserver) { var last = 0; new ResizeObserver(function () { var w = Math.floor(frame.clientWidth); if (w !== last) { last = w; draw(); } }).observe(frame); }
  }

  /* ------------------------------------------------------------------ horizontal bars */
  function bars(root, cfg) {
    root.classList.add("viz"); root.innerHTML = "";
    var groups = []; cfg.rows.forEach(function (r) { if (groups.indexOf(r.group) < 0) groups.push(r.group); });
    var legend = html("div", "viz-legend", root);
    groups.forEach(function (g) {
      var item = html("span", "viz-legend-item", legend), sw = html("span", "viz-swatch viz-swatch-bar", item);
      sw.style.setProperty("--c", "var(" + cfg.colors[g] + ")"); html("span", null, item, g);
    });
    var list = html("div", "viz-bars", root);
    cfg.rows.forEach(function (r) {
      var row = html("div", "viz-bar-row", list);
      html("div", "viz-bar-label", row, r.label);
      var track = html("div", "viz-bar-track", row), bar = html("div", "viz-bar", track);
      bar.style.width = Math.max(0.4, r.value / cfg.max * 100) + "%"; bar.style.background = "var(" + cfg.colors[r.group] + ")";
      html("div", "viz-bar-value", row, cfg.fmt(r.value));
      row.title = r.label + ": " + cfg.fmt(r.value) + (r.note ? " — " + r.note : "");
    });
  }

  /* ------------------------------------------------------------------ pixel images */
  function pixels(root, img, opt) {
    var n = img.length, cell = 10, s = svg("svg", { viewBox: "0 0 " + n * cell + " " + n * cell, class: "viz-pixels", role: "img", "aria-label": opt.label }, root);
    svg("rect", { x: 0, y: 0, width: n * cell, height: n * cell, class: "viz-pixels-bg" }, s);
    for (var y = 0; y < n; y++) for (var x = 0; x < n; x++) {
      var v = img[y][x], a, col;
      if (opt.diverging) { a = Math.min(1, Math.abs(v) / opt.scale); col = v >= 0 ? "var(--s1)" : "var(--div-neg)"; }
      else { a = Math.sqrt(Math.max(0, Math.min(1, v / opt.scale))); col = "var(--s1)"; }
      if (a < 0.02) continue;
      var r = svg("rect", { x: x * cell, y: (n - 1 - y) * cell, width: cell, height: cell, fill: col, "fill-opacity": a.toFixed(3) }, s);
      svg("title", {}, r).textContent = "pixel (" + x + ", " + y + "): " + v + " e⁻/s";
    }
    (opt.markers || []).forEach(function (k) {
      var cx = (k.x + 0.5) * cell, cy = (n - 1 - k.y + 0.5) * cell;
      if (k.kind === "cross") {
        svg("line", { x1: cx - 6, x2: cx + 6, y1: cy, y2: cy, class: "viz-marker-cross" }, s);
        svg("line", { x1: cx, x2: cx, y1: cy - 6, y2: cy + 6, class: "viz-marker-cross" }, s);
      } else svg("circle", { cx: cx, cy: cy, r: 5, class: "viz-marker-ring" }, s);
    });
    return s;
  }

  /* ------------------------------------------------------------------ table view */
  function table(root, cols, rows, opt) {
    opt = opt || {};
    var wrap = html("div", "table-wrap", root), t = html("table", "data-table", wrap), tr = html("tr", null, html("thead", null, t));
    cols.forEach(function (c) { var th = html("th", c.num ? "num" : null, tr, c.label); th.scope = "col"; });
    var tb = html("tbody", null, t);
    rows.slice(0, opt.limit || rows.length).forEach(function (r) {
      var row = html("tr", null, tb);
      cols.forEach(function (c, i) {
        var v = c.get ? c.get(r) : r[i], td = html("td", c.num ? "num" : null, row);
        if (v && v.href) { var a = html("a", null, td, v.text); a.href = v.href; } else td.textContent = v === null || v === undefined ? "—" : v;
      });
    });
    if (opt.limit && rows.length > opt.limit) html("p", "table-note", root, "Showing " + opt.limit + " of " + rows.length + " rows. The linked file has all of them.");
    return t;
  }

  window.Viz = { xy: xy, bars: bars, pixels: pixels, table: table, fmt: fmt, html: html };
})();
