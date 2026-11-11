/* Builds every chart and table on the page from window.EVIDENCE (assets/data.js) and window.FILES (assets/files.js). */
(function () {
  "use strict";
  var E = window.EVIDENCE, V = window.Viz, fmt = V.fmt;
  var $ = function (id) { return document.getElementById(id); };
  var pm = "±", minus = "−";
  function safe(name, fn) { try { fn(); } catch (err) { if (window.console) console.error("section failed: " + name, err); } }

  /* ---------- theme toggle and permalinks */
  safe("chrome", function () {
    $("theme-toggle").addEventListener("click", function () {
      var root = document.documentElement, cur = root.getAttribute("data-theme");
      if (!cur) cur = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
      var next = cur === "dark" ? "light" : "dark";
      root.setAttribute("data-theme", next);
      try { localStorage.setItem("theme", next); } catch (e) {}
    });
    var toast = $("toast"), timer;
    Array.prototype.forEach.call(document.querySelectorAll(".permalink"), function (a) {
      a.addEventListener("click", function () {
        var url = location.href.split("#")[0] + a.getAttribute("href");
        if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(url).then(function () {
          toast.textContent = "Link copied"; toast.classList.add("on"); clearTimeout(timer); timer = setTimeout(function () { toast.classList.remove("on"); }, 1600);
        }, function () {});
      });
    });
  });
  if (!E) return;

  /* ---------- E1 folded transit */
  safe("transit", function () {
    V.xy($("chart-transit"), {
      label: "Folded transit light curve: a 0.97 percent dip lasting about two hours", height: 380,
      x: { min: -5, max: 5, label: "Hours from mid-transit", name: "From mid-transit", fmt: function (v) { return fmt(v, 2) + " h"; } },
      y: { min: -1.9, max: 0.9, label: "Change in brightness (%)", name: "Brightness", fmt: function (v) { return fmt(v, 3) + "%"; } },
      series: [
        { kind: "cloud", color: "--muted", data: E.folded.cloud, opacity: 0.3 },
        { kind: "line", name: "Transit model", color: "--s2", data: E.folded.model },
        { kind: "points", name: "10-minute averages", color: "--s1", data: E.folded.bins, r: 4 }
      ]
    });
  });

  /* ---------- E2 sectors */
  safe("sectors", function () {
    var host = $("chart-sectors"), months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    var when = function (btjd) { var d = new Date((btjd + 2457000 - 2440587.5) * 86400000); return months[d.getUTCMonth()] + " " + d.getUTCFullYear(); };
    E.lightcurves.forEach(function (lc) {
      var box = V.html("div", null, host), title = V.html("p", "sm-title", box, "Sector " + lc.sector + " ");
      V.html("span", null, title, "· " + when(lc.t0) + (when(lc.t0) !== when(lc.t1) ? " – " + when(lc.t1) : "") + " · " + lc.transits.length + " transits");
      var div = V.html("div", null, box);
      V.xy(div, {
        label: "Sector " + lc.sector + " light curve", height: 170, marginLeft: 40,
        x: { min: lc.t0 - 0.4, max: lc.t1 + 0.4, name: "Day (BTJD)", fmt: function (v) { return fmt(v, 2); }, digits: 0 },
        y: { min: -1.5, max: 0.6, name: "Brightness", ticks: [-1, -0.5, 0, 0.5], digits: 1, fmt: function (v) { return fmt(v, 2) + "%"; } },
        marks: lc.transits.map(function (t) { return { kind: "vline", x: t, faint: true }; }),
        series: [{ kind: "points", color: "--s1", data: lc.points, r: 1.7, ring: false }]
      });
    });
  });

  /* ---------- E3 period search */
  safe("bls", function () {
    var pk = E.bls.peak_period, top = Math.ceil(E.bls.peak_snr / 10) * 10 + 10;
    V.xy($("chart-bls"), {
      label: "Period search: one peak at 3.48 days", height: 300,
      x: { min: 0.5, max: 30, log: true, label: "Trial period (days, logarithmic)", name: "Period", fmt: function (v) { return fmt(v, 3) + " d"; } },
      y: { min: 0, max: top, label: "Signal-to-noise of the best box-shaped dip", name: "Signal-to-noise", fmt: function (v) { return fmt(v, 1); } },
      marks: [{ kind: "text", x: pk * 1.07, y: E.bls.peak_snr - 1, text: fmt(pk, 4) + " d" }].concat([[2, "2× period"], [0.5, "½×"], [3, "3×"], [4, "4×"]].map(function (h) {
        var p0 = pk * h[0], best = 0; E.bls.points.forEach(function (q) { if (Math.abs(q[0] / p0 - 1) < 0.03 && q[1] > best) best = q[1]; });
        return { kind: "text", x: p0, y: best + 2.5, text: h[1], anchor: "middle" };
      })),
      series: [{ kind: "line", color: "--s1", data: E.bls.points, width: 1.5, hover: true }]
    });
  });

  /* ---------- E4 difference images */
  safe("centroid", function () {
    var host = $("chart-cutouts");
    E.centroid.forEach(function (c) {
      var box = V.html("div", null, host), pair = V.html("div", "cutout-pair", box);
      var tx = Math.round(c.target[0]), ty = Math.round(c.target[1]), peak = 0, dpeak = 0;
      for (var y = ty - 2; y <= ty + 2; y++) for (var x = tx - 2; x <= tx + 2; x++) { peak = Math.max(peak, c.oot[y][x]); dpeak = Math.max(dpeak, Math.abs(c.diff[y][x])); }
      V.pixels(pair, c.oot, { label: "Sector " + c.sector + " out-of-transit image", scale: peak, markers: [{ kind: "cross", x: c.target[0], y: c.target[1] }] });
      V.pixels(pair, c.diff, { label: "Sector " + c.sector + " difference image", diverging: true, scale: dpeak, markers: [{ kind: "ring", x: c.diffc[0], y: c.diffc[1] }, { kind: "cross", x: c.target[0], y: c.target[1] }] });
      var cap = V.html("div", "cutout-cap", box); V.html("b", null, cap, "Sector " + c.sector);
      cap.appendChild(document.createTextNode(" · offset " + fmt(c.off, 1) + " " + pm + " " + fmt(c.err, 1) + "″ · " + c.n + " transits"));
    });
    V.table($("table-centroid"), [
      { label: "Sector" }, { label: "Transits", num: true }, { label: "Offset (arcsec)", num: true }, { label: "Uncertainty (arcsec)", num: true }, { label: "Offset / uncertainty", num: true }
    ], E.centroid.map(function (c) { return ["Sector " + c.sector, c.n, fmt(c.off, 1), fmt(c.err, 1), fmt(c.off / c.err, 1)]; }));
  });

  /* ---------- E5 neighbours */
  safe("neighbours", function () {
    var nb = E.neighbours.filter(function (n) { return n.sep > 0.5; }), target = E.neighbours[0];
    var tip = function (p) { var n = p[3]; return [["Separation", fmt(n.sep, 1) + "″"], ["Gaia G magnitude", fmt(n.G, 2)], ["Light relative to target", fmt(n.fr * 100, 3) + "%"]]; };
    V.xy($("chart-neighbours"), {
      label: "Map of Gaia sources within 150 arcseconds of the target", square: true, marginLeft: 46,
      x: { min: 155, max: -155, label: "Offset east (arcsec)", ticks: [{ v: 100, label: "100" }, { v: 0, label: "0" }, { v: -100, label: minus + "100" }] },
      y: { min: -155, max: 155, label: "Offset north (arcsec)", ticks: [-100, 0, 100], digits: 0 },
      marks: [{ kind: "circle", x: 0, y: 0, r: 21, label: "21″" }, { kind: "circle", x: 0, y: 0, r: 63, label: "63″" }],
      series: [
        { kind: "points", name: "Gaia neighbours", color: "--ink-2", ring: false, err: false, data: nb.map(function (n) { return [n.dx, n.dy, null, n]; }), r: function (p) { return Math.max(1.6, Math.min(8, 1.6 + (21 - p[3].T) * 1.0)); }, tip: tip },
        { kind: "points", name: "Target", color: "--s1", err: false, data: [[0, 0, null, target]], r: 7, tip: function () { return [["TIC 219329329", "G = " + fmt(target.G, 2)]]; } }
      ]
    });
    V.table($("table-neighbours"), [
      { label: "Gaia DR3 source" }, { label: "Separation (arcsec)", num: true }, { label: "G mag", num: true }, { label: "Light vs target", num: true }
    ], nb.map(function (n) { return [n.id, fmt(n.sep, 1), fmt(n.G, 2), fmt(n.fr * 100, 3) + "%"]; }), { limit: 12 });
  });

  /* ---------- E6 aperture */
  safe("aperture", function () {
    var sectors = []; E.apertures.forEach(function (a) { if (sectors.indexOf(a.sector) < 0) sectors.push(a.sector); });
    var defs = [["2x2", "2×2 pixels", "--s1", -0.2], ["3x3", "3×3 pixels", "--s2", 0], ["5x5", "5×5 pixels", "--s3", 0.2]];
    V.xy($("chart-aperture"), {
      label: "Transit depth per sector for three aperture sizes", height: 320, marginLeft: 58,
      x: { min: 0.5, max: sectors.length + 0.5, label: "TESS sector", ticks: sectors.map(function (s, i) { return { v: i + 1, label: String(s) }; }) },
      y: { min: 8400, max: 11200, label: "Transit depth (parts per million)", digits: 0 },
      series: defs.map(function (d) {
        return { kind: "points", name: d[1], color: d[2], dx: d[3], r: 4.5,
          data: E.apertures.filter(function (a) { return a.aperture === d[0]; }).map(function (a) { return [sectors.indexOf(a.sector) + 1, a.depth, a.err, a]; }),
          tip: function (p) { return [["Sector", String(p[3].sector)], ["Depth", fmt(p[1], 0) + " " + pm + " " + fmt(p[2], 0) + " ppm"]]; } };
      })
    });
    V.table($("table-aperture"), [{ label: "Sector" }, { label: "Aperture" }, { label: "Depth (ppm)", num: true }, { label: "Uncertainty (ppm)", num: true }, { label: "Star flux in aperture (e⁻/s)", num: true }],
      E.apertures.map(function (a) { return ["Sector " + a.sector, a.aperture.replace("x", "×") + " pixels", fmt(a.depth, 0), fmt(a.err, 0), fmt(a.net, 0)]; }));
  });

  /* ---------- E7 reduction */
  safe("reduction", function () {
    V.table($("table-reduction"), [{ label: "Light curve and detrending" }, { label: "Depth (ppm)", num: true }, { label: "Uncertainty", num: true }, { label: "Per sector (ppm)" }],
      E.detrending.map(function (d) { return [d.label.replace("biweight", "window").replace("SPOC S68", "SPOC sector 68"), fmt(d.depth, 0), pm + " " + fmt(d.err, 0), d.per_sector.map(function (v) { return fmt(v, 0); }).join(" · ")]; }));
  });

  /* ---------- E9 odd / even */
  safe("oddeven", function () {
    V.xy($("chart-oddeven"), {
      label: "Odd and even transits overlaid", height: 320,
      x: { min: -4, max: 4, label: "Hours from mid-transit", name: "From mid-transit", fmt: function (v) { return fmt(v, 2) + " h"; } },
      y: { min: -1.25, max: 0.35, label: "Change in brightness (%)", name: "Brightness", fmt: function (v) { return fmt(v, 3) + "%"; } },
      series: [
        { kind: "points", name: "Odd transits", color: "--s1", data: E.oddeven.odd, dx: -0.03 },
        { kind: "points", name: "Even transits", color: "--s2", data: E.oddeven.even, dx: 0.03 }
      ]
    });
    var rows = E.oddeven.odd.map(function (p) { return ["Odd", fmt(p[0], 2), fmt(p[1], 3), fmt(p[2], 3)]; }).concat(E.oddeven.even.map(function (p) { return ["Even", fmt(p[0], 2), fmt(p[1], 3), fmt(p[2], 3)]; }));
    V.table($("table-oddeven"), [{ label: "Transits" }, { label: "Hours from mid-transit", num: true }, { label: "Brightness change (%)", num: true }, { label: "Uncertainty (%)", num: true }], rows, { limit: 32 });
  });

  /* ---------- E10 full orbit */
  safe("phase", function () {
    V.xy($("chart-phase"), {
      label: "Brightness around the whole orbit with the transit removed: flat", height: 300, marginLeft: 54,
      x: { min: 0, max: 1, label: "Orbital phase (transit at 0)", name: "Phase", fmt: function (v) { return fmt(v, 3); } },
      y: { min: -900, max: 900, label: "Change in brightness (parts per million)", name: "Brightness", digits: 0, fmt: function (v) { return fmt(v, 0) + " ppm"; } },
      marks: [{ kind: "vline", x: 0.5, label: "A secondary eclipse would be here" }],
      series: [{ kind: "points", color: "--s1", data: E.phase, r: 3.5 }]
    });
    V.table($("table-phase"), [{ label: "Orbital phase", num: true }, { label: "Brightness change (ppm)", num: true }, { label: "Uncertainty (ppm)", num: true }],
      E.phase.map(function (p) { return [fmt(p[0], 3), fmt(p[1], 0), fmt(p[2], 0)]; }), { limit: 40 });
  });

  /* ---------- E12 timing */
  safe("timing", function () {
    var rows = E.timing.rows, marks = [{ kind: "hline", y: 0 }], secs = [];
    rows.forEach(function (r) { var s = secs.length && secs[secs.length - 1].sector === r[1] ? secs[secs.length - 1] : null; if (!s) { s = { sector: r[1], a: r[0], b: r[0] }; secs.push(s); } s.b = r[0]; });
    secs.forEach(function (s, i) {
      if (i % 2 === 0) marks.push({ kind: "band", x0: s.a - 0.5, x1: s.b + 0.5 });
      marks.push({ kind: "text", x: (s.a + s.b) / 2, y: 10.4, text: String(s.sector), anchor: "middle" });
    });
    var tip = function (p) { var r = p[3]; return [["Sector", String(r[1])], ["Mid-transit (BTJD)", fmt(r[2], 4).replace(/,/g, "")], ["Observed " + minus + " predicted", fmt(r[3], 1) + " " + pm + " " + fmt(r[4], 1) + " min"]]; };
    var pts = function (keep) { return rows.filter(keep).map(function (r) { return [r[0], r[3], r[4], r]; }); };
    V.xy($("chart-timing"), {
      label: "Transit timing residuals for 34 transits", height: 320,
      x: { min: 0, max: rows.length + 1, label: "Individual transits in time order, grouped by TESS sector (numbers at top)", ticks: [] },
      y: { min: -12, max: 12, label: "Observed minus predicted mid-transit time (minutes); 0 = on time", digits: 0 },
      marks: marks,
      series: [
        { kind: "points", name: "Sectors 68–104 (used to fit the period)", color: "--s1", data: pts(function (r) { return r[1] !== 105; }), tip: tip },
        { kind: "points", name: "Sector 105 (held out)", color: "--s2", data: pts(function (r) { return r[1] === 105; }), tip: tip }
      ]
    });
    V.table($("table-timing"), [{ label: "#", num: true }, { label: "Sector", num: true }, { label: "Mid-transit (BTJD)", num: true }, { label: "Observed " + minus + " predicted (min)", num: true }, { label: "Uncertainty (min)", num: true }, { label: "Depth (ppm)", num: true }],
      rows.map(function (r) { return [r[0], r[1], fmt(r[2], 5).replace(/,/g, ""), fmt(r[3], 1), fmt(r[4], 1), fmt(r[5], 0)]; }));
  });

  /* ---------- E15 TRICERATOPS */
  safe("fpp", function () {
    var names = {
      TP: ["Planet on the target star", "Planet"], PTP: ["Planet on the target, plus an unseen bound companion", "Planet"], DTP: ["Planet on the target, plus an unseen background star", "Planet"],
      PEB: ["Eclipsing binary on the target, plus an unseen bound companion", "False positive"], STP: ["Planet on an unseen bound companion", "False positive"], SEB: ["Eclipsing binary on an unseen bound companion", "False positive"],
      EB: ["Eclipsing binary on the target", "False positive"], BTP: ["Planet on an unseen background star", "False positive"], BEB: ["Eclipsing binary on an unseen background star", "False positive"]
    };
    var sc = E.triceratops.own1e7.scenarios, rows = [];
    Object.keys(sc).forEach(function (k) { if (names[k] && sc[k] >= 0.0005) rows.push({ label: names[k][0], group: names[k][1], value: sc[k] }); });
    rows.sort(function (a, b) { return b.value - a.value; });
    V.bars($("chart-scenarios"), { rows: rows, max: 0.8, colors: { "Planet": "--s1", "False positive": "--s2" }, fmt: function (v) { return fmt(v * 100, v < 0.01 ? 2 : 1) + "%"; } });

    var groups = [["mission1e7", "Pipeline light curve", "--s1", 1], ["own1e7", "Own photometry", "--s2", 2]];
    V.xy($("chart-fpp"), {
      label: "False-positive probability of each run", height: 280, marginLeft: 54,
      x: { min: 0.4, max: 2.6, ticks: groups.map(function (g) { return { v: g[3], label: g[1] }; }) },
      y: { min: 0, max: 0.22, label: "False-positive probability", digits: 2 },
      marks: [{ kind: "hline", y: 0.015, label: "Validation threshold 0.015" }],
      series: groups.map(function (g) {
        var f = E.triceratops[g[0]].fpp;
        return { kind: "points", name: g[1], color: g[2], err: false, data: f.map(function (v, i) { return [g[3] + (i - (f.length - 1) / 2) * 0.1, v, null, i + 1]; }),
          tip: function (p) { return [["Run", String(p[3])], ["False-positive probability", fmt(p[1], 3)]]; } };
      })
    });
    var trows = [];
    Object.keys(E.triceratops).forEach(function (k) { var t = E.triceratops[k]; t.fpp.forEach(function (v, i) { trows.push([t.label.replace("10^7", "10⁷").replace("10^6", "10⁶"), i + 1, fmt(v, 4), fmt(t.nfpp[i], 4)]); }); });
    V.table($("table-fpp"), [{ label: "Light curve and sample count" }, { label: "Run", num: true }, { label: "False-positive probability", num: true }, { label: "Nearby-star probability", num: true }], trows);
  });

  /* ---------- E16 ASAS-SN */
  safe("asassn", function () {
    var A = E.asassn; if (!A) return;
    var hfmt = function (v) { return fmt(v, 2) + " h"; }, pfmt = function (v) { return fmt(v, 2) + "%"; };
    V.xy($("chart-asassn"), {
      label: "ASAS-SN photometry folded on the TESS period: a dip at the predicted time", height: 340,
      x: { min: -8, max: 8, label: "Hours from predicted mid-transit", name: "From predicted mid-transit", fmt: hfmt },
      y: { min: -1.9, max: 1.3, label: "Change in brightness (%)", name: "Brightness", fmt: pfmt },
      series: [
        { kind: "line", name: "Transit model (g band)", color: "--s2", data: A.bands.g.model },
        { kind: "points", name: "g band, half-hour averages", color: "--s1", data: A.bands.g.bins, dx: -0.06 },
        { kind: "points", name: "V band, half-hour averages", color: "--s3", data: A.bands.V.bins, dx: 0.06 }
      ]
    });
    V.xy($("chart-asassn-scan"), {
      label: "Significance of a transit-shaped dip at every orbital phase in ASAS-SN data", height: 280,
      x: { min: -0.5, max: 0.5, label: "Offset from the predicted transit time (fraction of an orbit)", name: "Phase offset", fmt: function (v) { return fmt(v, 3); }, digits: 1 },
      y: { min: -3.5, max: 6, label: "Depth divided by its uncertainty", name: "Significance", fmt: function (v) { return fmt(v, 1) + "σ"; }, digits: 0 },
      marks: [{ kind: "vline", x: 0, label: "Predicted transit" }],
      series: [{ kind: "line", color: "--s1", data: A.scan, width: 1.75, hover: true }]
    });
    var rows = [];
    ["g", "V"].forEach(function (b) { A.bands[b].bins.forEach(function (p) { rows.push([b, fmt(p[0], 2), fmt(p[1], 3), fmt(p[2], 3), p[3]]); }); });
    V.table($("table-asassn"), [{ label: "Band" }, { label: "Hours from predicted mid-transit", num: true }, { label: "Brightness change (%)", num: true }, { label: "Uncertainty (%)", num: true }, { label: "Measurements", num: true }], rows, { limit: 40 });
  });

  /* ---------- E17 TRICERATOPS with whole-orbit limits */
  safe("fpp-phase", function () {
    var T = E.triceratops; if (!T.own1e7_phase) return;
    var defs = [["mission1e7", "--s1", 1, 0], ["own1e7", "--s2", 1, 1], ["mission1e7_phase", "--s1", 2, 0], ["own1e7_phase", "--s2", 2, 1]];
    var series = [["Pipeline light curve", "--s1", 0], ["Own photometry", "--s2", 1]].map(function (g) {
      var data = [];
      defs.forEach(function (d) {
        if (d[3] !== g[2]) return;
        var f = T[d[0]].fpp; f.forEach(function (v, i) { data.push([d[2] + (g[2] ? 0.07 : -0.37) + i * 0.06, v, null, [d[2] === 1 ? "Transit only" : "With whole-orbit limits", i + 1]]); });
      });
      return { kind: "points", name: g[0], color: g[1], err: false, data: data, tip: function (p) { return [[p[3][0], "run " + p[3][1]], ["False-positive probability", fmt(p[1], 3)]]; } };
    });
    V.xy($("chart-fpp-phase"), {
      label: "False-positive probability of each run, before and after adding whole-orbit limits", height: 300, marginLeft: 54,
      x: { min: 0.4, max: 2.6, ticks: [{ v: 1, label: "Transit only (E15)" }, { v: 2, label: "With whole-orbit limits" }] },
      y: { min: 0, max: 0.22, label: "False-positive probability", digits: 2 },
      marks: [{ kind: "hline", y: 0.015, label: "Validation threshold 0.015" }],
      series: series
    });
  });

  /* ---------- parameters */
  safe("params", function () {
    var P = E.params, spec = [
      ["period_d", "Period (days)", 6], ["T0_btjd", "Mid-transit time (BTJD)", 5], ["rp_over_rs", "Radius ratio, candidate / star", 4], ["impact_parameter", "Impact parameter", 3],
      ["a_over_rs", "Orbital distance / stellar radius", 2], ["inclination_deg", "Inclination (degrees)", 1], ["t14_hours", "Transit duration (hours)", 2], ["stellar_density_solar", "Stellar density from transit (Sun = 1)", 2], ["radius_rjup", "Radius (Jupiter radii)", 2]
    ];
    var show = function (o, d) { var a = fmt(o.plus, d), b = fmt(o.minus, d); return fmt(o.median, d).replace(/,/g, "") + (a === b ? " " + pm + " " + a : " (+" + a + " / " + minus + b + ")"); };
    var rows = spec.map(function (s) { return [s[1], show(P.own[s[0]], s[2]), show(P.pipeline[s[0]], s[2])]; });
    rows.push(["Mid-transit depth (ppm)", "≈ 9,700", "≈ 8,700"]);
    V.table($("table-params"), [{ label: "Parameter" }, { label: "Own photometry, 6 sectors", num: true }, { label: "Pipeline light curves, 5 sectors", num: true }], rows);
  });

  /* ---------- next transits */
  safe("next", function () {
    var ep = E.ephemeris, tdb = 69.184 / 86400, nowBjd = Date.now() / 86400000 + 2440587.5 + tdb, n0 = Math.ceil((nowBjd - ep.T0_bjd) / ep.P), rows = [];
    for (var i = 0; i < 6; i++) {
      var n = n0 + i, bjd = ep.T0_bjd + n * ep.P, d = new Date((bjd - tdb - 2440587.5) * 86400000);
      var unc = Math.sqrt(ep.T0_err * ep.T0_err + n * n * ep.P_err * ep.P_err) * 1440;
      rows.push([String(n), fmt(bjd, 4).replace(/,/g, ""), d.toISOString().slice(0, 16).replace("T", " "), pm + " " + fmt(unc, 1)]);
    }
    V.table($("table-next"), [{ label: "Orbit number", num: true }, { label: "Mid-transit (BJD TDB)", num: true }, { label: "Approximate UTC", num: true }, { label: "Uncertainty (min)", num: true }], rows);
  });

  /* ---------- files and sources */
  safe("files", function () {
    var F = window.FILES || [], host = $("table-files"), groups = [];
    F.forEach(function (f) { if (groups.indexOf(f.group) < 0) groups.push(f.group); });
    groups.forEach(function (g) {
      V.html("h4", null, host, g);
      V.table(host, [{ label: "File", get: function (f) { return { href: f.path, text: f.path }; } }, { label: "What it is", get: function (f) { return f.desc; } }, { label: "Size", num: true, get: function (f) { return f.size; } }],
        F.filter(function (f) { return f.group === g; })).classList.add("files-table");
    });
    var mast = "https://mast.stsci.edu/api/v0.1/Download/file?uri=", cut = "https://mast.stsci.edu/tesscut/api/v0.1/astrocut?ra=335.349583800419&dec=-55.8374378147405&y=15&x=15&units=px&sector=";
    var rows = E.mast.map(function (m) { return [{ href: mast + m.uri, text: m.product }, m.author + " " + (m.product.indexOf("_tp") > 0 ? "target pixel file" : "light curve") + ", " + m.mission.replace("TESS ", "").toLowerCase()]; });
    [68, 95, 102, 103, 104, 105].forEach(function (s) { rows.push([{ href: cut + s, text: "TESScut 15×15 pixel cutout, sector " + s }, "Full-frame image cutout used for own photometry and difference images (zip, about 50 MB)"]); });
    rows.push([{ href: "https://exofop.ipac.caltech.edu/tess/target.php?id=219329329", text: "ExoFOP-TESS: TIC 219329329" }, "Catalogue parameters and community follow-up status"]);
    rows.push([{ href: "https://gea.esac.esa.int/archive/", text: "Gaia archive" }, "Source 6507925182103208960 and its neighbours (query in scripts/05_gaia.py)"]);
    V.table($("table-sources"), [{ label: "Link" }, { label: "What it is" }], rows);
  });
})();
