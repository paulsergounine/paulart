// subtle parallax on painting images
(function () {
  var plates = document.querySelectorAll('.work__plate');
  if (!plates.length) return;

  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var wideEnough = window.matchMedia('(min-width: 768px)').matches;
  if (reduceMotion || !wideEnough || !('IntersectionObserver' in window)) return;

  var metrics = new WeakMap(); // plate -> { top, height, img }
  var active = new Set();
  var scrollY = window.scrollY;
  var ticking = false;

  function measure(plate) {
    var rect = plate.getBoundingClientRect();
    metrics.set(plate, {
      top: rect.top + window.scrollY,
      height: rect.height,
      img: plate.querySelector('img')
    });
  }

  function applyParallax(plate) {
    var m = metrics.get(plate);
    if (!m || !m.img) return;
    var viewportTop = m.top - scrollY;
    var vh = window.innerHeight;
    var progress = (vh - viewportTop) / (vh + m.height);
    progress = Math.min(1, Math.max(0, progress));
    var maxDrift = m.height * 0.1;
    var offset = (progress - 0.5) * maxDrift;
    m.img.style.transform = 'translateY(' + offset.toFixed(1) + 'px)';
  }

  function update() {
    active.forEach(applyParallax);
    ticking = false;
  }

  function onScroll() {
    scrollY = window.scrollY;
    if (!ticking) {
      ticking = true;
      requestAnimationFrame(update);
    }
  }

  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        measure(entry.target);
        active.add(entry.target);
        applyParallax(entry.target);
      } else {
        active.delete(entry.target);
      }
    });
  }, { rootMargin: '200px 0px 200px 0px' });

  plates.forEach(function (p) { io.observe(p); });

  window.addEventListener('scroll', onScroll, { passive: true });
  window.addEventListener('resize', function () {
    active.forEach(measure);
    scrollY = window.scrollY;
    update();
  });
})();
