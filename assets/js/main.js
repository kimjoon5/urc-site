/* URC — interactions
   nav (hide on scroll / mobile menu), full-screen section scrolling, section dots,
   scroll reveal, members generation switcher, hash deep links */
(function () {
  "use strict";
  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const coarse = window.matchMedia("(pointer: coarse)").matches;
  const body = document.body;

  /* ── nav ─────────────────────────────────────────────────── */
  (function nav() {
    let last = window.scrollY, ticking = false;
    const update = () => {
      const y = window.scrollY;
      body.classList.toggle("is-scrolled", y > window.innerHeight - 120);
      if (Math.abs(y - last) > 6) {
        body.classList.toggle("nav-hidden", y > 120 && y > last && !body.classList.contains("menu-open"));
        last = y;
      }
      ticking = false;
    };
    window.addEventListener("scroll", () => { if (!ticking) { ticking = true; requestAnimationFrame(update); } }, { passive: true });
    update();
    const burger = document.querySelector(".burger");
    const menu = document.querySelector(".menu");
    if (!burger || !menu) return;
    const setOpen = (open) => {
      body.classList.toggle("menu-open", open);
      burger.setAttribute("aria-expanded", String(open));
      menu.setAttribute("aria-hidden", String(!open));
      body.style.overflow = open ? "hidden" : "";
    };
    burger.addEventListener("click", () => setOpen(!body.classList.contains("menu-open")));
    window.addEventListener("keydown", (e) => { if (e.key === "Escape") setOpen(false); });
    window.matchMedia("(min-width: 768px)").addEventListener("change", (e) => { if (e.matches) setOpen(false); });
  })();

  /* ── reveal on scroll ────────────────────────────────────── */
  const io = ("IntersectionObserver" in window && !reduced)
    ? new IntersectionObserver((entries) => {
        entries.forEach((en) => { if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); } });
      }, { threshold: 0.12, rootMargin: "0px 0px -6% 0px" })
    : null;
  const observe = (root) => root.querySelectorAll("[data-reveal], .gens").forEach((el) => { if (io) io.observe(el); else el.classList.add("in"); });
  const rearm = (root) => {
    root.querySelectorAll("[data-reveal], .gens").forEach((el) => { el.classList.remove("in"); if (io) io.unobserve(el); });
    requestAnimationFrame(() => requestAnimationFrame(() => observe(root)));
  };
  observe(document);

  /* ── full-screen sections ────────────────────────────────── */
  const secs = Array.from(document.querySelectorAll(".sec"));
  const dots = document.querySelector(".dots");
  let current = 0, lock = false, tween = 0, acc = 0, accTimer = 0, lastJump = 0;

  const topOf = (i) => Math.round(secs[i].getBoundingClientRect().top + window.scrollY);
  const indexAt = () => {
    const y = window.scrollY + 2;
    let best = 0;
    secs.forEach((s, i) => { if (topOf(i) <= y) best = i; });
    return best;
  };
  const setActive = (i) => {
    current = i;
    secs.forEach((s, k) => s.classList.toggle("is-active", k === i));
    if (dots) dots.querySelectorAll("button").forEach((b, k) => b.setAttribute("aria-current", String(k === i)));
  };
  const scrollTo = (y, dur = 900) => {
    cancelAnimationFrame(tween);
    const from = window.scrollY, dist = y - from, t0 = performance.now();
    if (reduced || Math.abs(dist) < 2) { window.scrollTo(0, y); return; }
    const ease = (t) => 1 - Math.pow(1 - t, 4);
    const step = (now) => {
      const p = Math.min((now - t0) / dur, 1);
      window.scrollTo(0, from + dist * ease(p));
      if (p < 1) tween = requestAnimationFrame(step);
    };
    tween = requestAnimationFrame(step);
  };
  const go = (i, dur = 900) => {
    if (!secs.length) return;
    i = Math.max(0, Math.min(secs.length - 1, i));
    lock = true; lastJump = performance.now();
    setActive(i);
    scrollTo(topOf(i), dur);
    setTimeout(() => { lock = false; acc = 0; }, dur + 150);
  };

  // wheel: one gesture = one section (mouse / trackpad)
  if (secs.length > 1 && !coarse && !body.classList.contains("scroll-natural")) {
    window.addEventListener("wheel", (e) => {
      if (body.classList.contains("menu-open")) return;
      if (lock) { e.preventDefault(); return; }
      const i = indexAt();
      const s = secs[i];
      const top = topOf(i), bottom = top + s.offsetHeight, vh = window.innerHeight, y = window.scrollY;
      const tall = s.offsetHeight > vh + 4;
      if (e.deltaY > 0) {
        if (tall && y + vh < bottom - 4) return;               // native scroll inside a tall section
        if (i >= secs.length - 1) return;
      } else {
        if (tall && y > top + 4) return;
        if (i <= 0) return;
      }
      e.preventDefault();
      if (performance.now() - lastJump < 1400 && Math.abs(e.deltaY) < 40) return;   // trackpad inertia
      acc += e.deltaY;
      clearTimeout(accTimer); accTimer = setTimeout(() => { acc = 0; }, 220);
      if (Math.abs(acc) >= 40) { acc = 0; go(i + (e.deltaY > 0 ? 1 : -1)); }
    }, { passive: false });

    window.addEventListener("keydown", (e) => {
      if (body.classList.contains("menu-open") || e.metaKey || e.ctrlKey || e.altKey) return;
      if (/INPUT|TEXTAREA|SELECT/.test((e.target && e.target.tagName) || "")) return;
      const i = indexAt();
      const s = secs[i], top = topOf(i), bottom = top + s.offsetHeight, vh = window.innerHeight, y = window.scrollY;
      const tall = s.offsetHeight > vh + 4;
      if (e.key === "ArrowDown" || e.key === "PageDown" || (e.key === " " && !e.shiftKey)) {
        if (tall && y + vh < bottom - 4) return;
        e.preventDefault(); go(i + 1);
      } else if (e.key === "ArrowUp" || e.key === "PageUp" || (e.key === " " && e.shiftKey)) {
        if (tall && y > top + 4) return;
        e.preventDefault(); go(i - 1);
      } else if (e.key === "Home") { e.preventDefault(); go(0); }
      else if (e.key === "End") { e.preventDefault(); go(secs.length - 1); }
    });
  }

  // keep dots / active section in sync with native or touch scrolling
  let syncTick = false;
  window.addEventListener("scroll", () => {
    if (lock || syncTick) return;
    syncTick = true;
    requestAnimationFrame(() => { syncTick = false; const i = indexAt(); if (i !== current) setActive(i); });
  }, { passive: true });

  if (dots) dots.querySelectorAll("button").forEach((b, k) => b.addEventListener("click", () => go(k)));

  const jumpTo = (id, push = true) => {
    const el = id && document.getElementById(id);
    if (!el) return false;
    const i = secs.indexOf(el.closest(".sec"));
    if (i < 0) return false;
    go(i);
    if (push) history.replaceState(null, "", "#" + id);
    return true;
  };
  document.querySelectorAll('a[href^="#"]').forEach((a) => {
    a.addEventListener("click", (e) => { if (jumpTo(a.getAttribute("href").slice(1))) e.preventDefault(); });
  });

  /* ── home hero photo parallax ────────────────────────────── */
  (function parallax() {
    const img = document.querySelector(".hero-photo img");
    if (img && !body.classList.contains("scroll-natural")) return;
    if (!img || reduced) return;
    let t = false;
    const upd = () => { const y = Math.min(window.scrollY, window.innerHeight); img.style.transform = `translateY(${y * 0.18}px) scale(1.06)`; t = false; };
    window.addEventListener("scroll", () => { if (!t) { t = true; requestAnimationFrame(upd); } }, { passive: true });
  })();

  /* ── members: generation strip ───────────────────────────── */
  const gens = Array.from(document.querySelectorAll(".gen[data-gen]"));
  const genPanels = Array.from(document.querySelectorAll(".gen-panel"));
  let currentGen = null;
  const showGen = (slug, { push = true } = {}) => {
    const btn = gens.find((g) => g.dataset.gen === slug) || gens[0];
    if (!btn) return;
    currentGen = btn.dataset.gen;
    gens.forEach((g) => { const on = g === btn; g.setAttribute("aria-selected", String(on)); g.tabIndex = on ? 0 : -1; });
    genPanels.forEach((p) => {
      const on = p.dataset.gen === currentGen;
      if (on && p.hidden) {
        p.hidden = false; p.classList.remove("enter"); void p.offsetWidth; p.classList.add("enter");
        p.querySelectorAll(".mcard[data-reveal]").forEach((c, i) => c.style.setProperty("--d", Math.min(i, 11) * 55 + "ms"));
        rearm(p);
      } else if (!on) { p.hidden = true; p.classList.remove("enter"); }
    });
    if (push) history.replaceState(null, "", "#members-" + currentGen);
  };
  gens.forEach((g) => {
    g.addEventListener("click", () => showGen(g.dataset.gen));
    g.addEventListener("keydown", (e) => {
      const i = gens.indexOf(g);
      if (e.key === "ArrowRight" || e.key === "ArrowLeft") {
        e.preventDefault();
        const n = gens[(i + (e.key === "ArrowRight" ? 1 : -1) + gens.length) % gens.length];
        n.focus(); showGen(n.dataset.gen);
      }
    });
  });
  if (gens.length) showGen(gens[0].dataset.gen, { push: false });

  /* ── project: Issue Report semester selector ─────────────── */
  document.querySelectorAll("[data-semester-select]").forEach((select) => {
    const report = select.closest(".issue-report");
    const panels = Array.from(report.querySelectorAll(".semester-panel"));
    const showSemester = (id) => panels.forEach((panel) => { panel.hidden = panel.dataset.semester !== id; });
    showSemester(select.value);
    select.addEventListener("change", () => showSemester(select.value));
  });

  /* ── initial state from hash ─────────────────────────────── */
  const applyHash = () => {
    const h = (location.hash || "").replace(/^#/, "");
    if (!h) { setActive(indexAt()); return; }
    const m = h.match(/^members(?:-([a-z0-9]+))?$/i);
    if (m && gens.length) { showGen(m[1] || gens[0].dataset.gen, { push: false }); jumpTo("members", false); return; }
    if (!jumpTo(h, false)) setActive(indexAt());
  };
  if ("scrollRestoration" in history) history.scrollRestoration = "manual";
  window.addEventListener("load", applyHash);
  window.addEventListener("hashchange", applyHash);
  setActive(indexAt());
})();
