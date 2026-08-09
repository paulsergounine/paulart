// reveal works on scroll
(function () {
  var works = document.querySelectorAll('.work');
  if (!works.length) return;

  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (reduceMotion || !('IntersectionObserver' in window)) return;

  // hidden state is applied here, not in the CSS, so works stay visible if JS fails to run
  works.forEach(function (w) { w.classList.add('reveal'); });

  var io = new IntersectionObserver(function (entries) {
    entries
      .filter(function (e) { return e.isIntersecting; })
      .forEach(function (entry, i) {
        entry.target.style.transitionDelay = (i * 80) + 'ms';
        entry.target.classList.add('is-in');
        io.unobserve(entry.target);
      });
  }, { threshold: 0.15, rootMargin: '0px 0px -10% 0px' });

  works.forEach(function (w) { io.observe(w); });
})();
