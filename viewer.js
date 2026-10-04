/* Full-screen image viewer for the Work page. Own code, no libraries, no tracking.
   Without JavaScript the work images stay plain links to the 1600 px file. */
(function () {
  'use strict';
  var links = Array.prototype.slice.call(document.querySelectorAll('a.work__open'));
  if (!links.length || !window.PointerEvent) return;
  document.documentElement.classList.add('viewer-ready');

  var MAX = 5, DOUBLE = 2.5, TAP_MOVE = 6, SWIPE = 50;
  var root, stage, img, cap, btnClose, btnPrev, btnNext;
  var index = -1, opener = null, prevOverflow = '';
  var s = 1, tx = 0, ty = 0;
  var pointers = {}, gesture = null, lastTap = 0;

  function el(tag, cls, parent) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (parent) parent.appendChild(e);
    return e;
  }

  function button(cls, label, text, parent) {
    var b = el('button', 'viewer__btn ' + cls, parent);
    b.type = 'button';
    b.setAttribute('aria-label', label);
    b.textContent = text;
    return b;
  }

  function build() {
    root = el('div', 'viewer', document.body);
    root.hidden = true;
    root.setAttribute('role', 'dialog');
    root.setAttribute('aria-modal', 'true');
    root.setAttribute('aria-label', 'Image viewer');
    stage = el('div', 'viewer__stage', root);
    img = el('img', 'viewer__img', stage);
    img.draggable = false;
    var bar = el('div', 'viewer__bar', root);
    btnPrev = button('viewer__prev', 'Previous work', '←', bar);
    cap = el('div', 'viewer__cap', bar);
    btnNext = button('viewer__next', 'Next work', '→', bar);
    btnClose = button('viewer__close', 'Close', '×', root);

    btnClose.addEventListener('click', close);
    btnPrev.addEventListener('click', function () { go(-1); });
    btnNext.addEventListener('click', function () { go(1); });
    root.addEventListener('click', function (e) { if (e.target === root) close(); });
    stage.addEventListener('wheel', onWheel, { passive: false });
    stage.addEventListener('pointerdown', onDown);
    stage.addEventListener('pointermove', onMove);
    stage.addEventListener('pointerup', onUp);
    stage.addEventListener('pointercancel', onUp);
    window.addEventListener('resize', function () { if (!root.hidden) { clamp(); apply(); } });
  }

  function apply() {
    img.style.transform = 'translate(' + tx + 'px,' + ty + 'px) scale(' + s + ')';
    root.classList.toggle('is-zoomed', s > 1);
  }

  function clamp() {
    var r = stage.getBoundingClientRect();
    var mx = Math.max(0, (img.offsetWidth * s - r.width) / 2);
    var my = Math.max(0, (img.offsetHeight * s - r.height) / 2);
    tx = Math.min(mx, Math.max(-mx, tx));
    ty = Math.min(my, Math.max(-my, ty));
  }

  /* zoom to scale ns, keeping the image point under (px, py) fixed */
  function zoomAt(ns, px, py) {
    ns = Math.min(MAX, Math.max(1, ns));
    var r = stage.getBoundingClientRect();
    var dx = px - (r.left + r.width / 2), dy = py - (r.top + r.height / 2);
    tx = dx - (dx - tx) * ns / s;
    ty = dy - (dy - ty) * ns / s;
    s = ns;
    clamp();
    apply();
  }

  function toggleZoom(px, py) { zoomAt(s > 1 ? 1 : DOUBLE, px, py); }

  function onWheel(e) {
    e.preventDefault();
    var d = e.deltaMode === 1 ? e.deltaY * 33 : e.deltaY;
    zoomAt(s * Math.exp(-d * (e.ctrlKey ? 0.01 : 0.0015)), e.clientX, e.clientY);
  }

  function pts() { return Object.keys(pointers).map(function (k) { return pointers[k]; }); }

  function pinchState() {
    var p = pts();
    return {
      d: Math.hypot(p[0].x - p[1].x, p[0].y - p[1].y) || 1,
      x: (p[0].x + p[1].x) / 2,
      y: (p[0].y + p[1].y) / 2
    };
  }

  function startOne(e) {
    gesture = { type: 'one', x0: e.clientX, y0: e.clientY, tx0: tx, ty0: ty,
                moved: false, onImg: e.target === img };
  }

  function onDown(e) {
    if (e.pointerType === 'mouse' && e.button !== 0) return;
    stage.setPointerCapture(e.pointerId);
    pointers[e.pointerId] = { x: e.clientX, y: e.clientY };
    if (pts().length === 1) {
      startOne(e);
    } else if (pts().length === 2) {
      gesture = { type: 'pinch', last: pinchState() };
    }
  }

  function onMove(e) {
    if (!pointers[e.pointerId] || !gesture) return;
    pointers[e.pointerId] = { x: e.clientX, y: e.clientY };
    if (gesture.type === 'pinch' && pts().length === 2) {
      var now = pinchState(), last = gesture.last;
      tx += now.x - last.x;
      ty += now.y - last.y;
      zoomAt(s * now.d / last.d, now.x, now.y);
      gesture.last = now;
    } else if (gesture.type === 'one') {
      var dx = e.clientX - gesture.x0, dy = e.clientY - gesture.y0;
      if (Math.abs(dx) > TAP_MOVE || Math.abs(dy) > TAP_MOVE) gesture.moved = true;
      if (s > 1 && gesture.moved) {
        tx = gesture.tx0 + dx;
        ty = gesture.ty0 + dy;
        clamp();
        apply();
      }
    }
  }

  function onUp(e) {
    if (!pointers[e.pointerId]) return;
    var g = gesture;
    delete pointers[e.pointerId];
    if (!g) return;
    if (g.type === 'pinch') {
      var rest = pts();
      if (rest.length === 1) {
        startOne({ clientX: rest[0].x, clientY: rest[0].y, target: img });
        gesture.moved = true;
      } else {
        gesture = null;
      }
      return;
    }
    gesture = null;
    if (e.type === 'pointercancel') return;
    var dx = e.clientX - g.x0, dy = e.clientY - g.y0;
    if (g.moved) {
      if (s === 1 && Math.abs(dx) > SWIPE && Math.abs(dx) > 1.5 * Math.abs(dy)) go(dx < 0 ? 1 : -1);
    } else if (!g.onImg) {
      close();
    } else if (e.pointerType === 'mouse') {
      toggleZoom(e.clientX, e.clientY);
    } else {
      var t = Date.now();
      if (t - lastTap < 300) { toggleZoom(e.clientX, e.clientY); lastTap = 0; } else { lastTap = t; }
    }
  }

  function show(i) {
    index = i;
    s = 1; tx = 0; ty = 0;
    apply();
    var link = links[i];
    img.alt = link.getAttribute('data-caption') || '';
    img.src = link.href;
    cap.textContent = img.alt;
    btnPrev.disabled = i === 0;
    btnNext.disabled = i === links.length - 1;
  }

  function go(dir) {
    var i = index + dir;
    if (i >= 0 && i < links.length) show(i);
  }

  function setInert(on) {
    Array.prototype.forEach.call(document.body.children, function (c) {
      if (c !== root) c.inert = on;
    });
  }

  function onKey(e) {
    if (e.key === 'Escape') { close(); }
    else if (e.key === 'ArrowLeft') { go(-1); }
    else if (e.key === 'ArrowRight') { go(1); }
    else if (e.key === 'Tab') {
      var f = [btnPrev, btnNext, btnClose].filter(function (b) { return !b.disabled; });
      var i = f.indexOf(document.activeElement);
      e.preventDefault();
      f[(i + (e.shiftKey ? f.length - 1 : 1)) % f.length].focus();
    }
  }

  function open(i, from) {
    if (!root) build();
    opener = from;
    prevOverflow = document.documentElement.style.overflow;
    document.documentElement.style.overflow = 'hidden';
    root.hidden = false;
    setInert(true);
    show(i);
    btnClose.focus();
    document.addEventListener('keydown', onKey);
  }

  function close() {
    root.hidden = true;
    pointers = {}; gesture = null;
    setInert(false);
    document.documentElement.style.overflow = prevOverflow;
    document.removeEventListener('keydown', onKey);
    if (opener) opener.focus({ preventScroll: true });
  }

  links.forEach(function (link, i) {
    link.addEventListener('click', function (e) {
      if (e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
      e.preventDefault();
      open(i, link);
    });
  });
})();
