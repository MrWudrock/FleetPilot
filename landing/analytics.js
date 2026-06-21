/**
 * FleetPilot — analytics (Yandex Metrika + GA4)
 */
(function () {
  var cfg = window.FLEETPILOT_CONFIG || {};

  function initYandexMetrika(id) {
    (function (m, e, t, r, i, k, a) {
      m[i] = m[i] || function () { (m[i].a = m[i].a || []).push(arguments); };
      m[i].l = 1 * new Date();
      for (var j = 0; j < document.scripts.length; j++) {
        if (document.scripts[j].src === r) return;
      }
      k = e.createElement(t); a = e.getElementsByTagName(t)[0];
      k.async = 1; k.src = r; a.parentNode.insertBefore(k, a);
    })(window, document, 'script', 'https://mc.yandex.ru/metrika/tag.js', 'ym');
    window.ym(id, 'init', { clickmap: true, trackLinks: true, accurateTrackBounce: true, webvisor: true });
  }

  function initGA4(id) {
    var s = document.createElement('script');
    s.async = true; s.src = 'https://www.googletagmanager.com/gtag/js?id=' + id;
    document.head.appendChild(s);
    window.dataLayer = window.dataLayer || [];
    function gtag() { window.dataLayer.push(arguments); }
    window.gtag = gtag; gtag('js', new Date()); gtag('config', id);
  }

  if (cfg.yandexMetrikaId) initYandexMetrika(cfg.yandexMetrikaId);
  if (cfg.ga4MeasurementId) initGA4(cfg.ga4MeasurementId);

  window.FleetPilotAnalytics = {
    track: function (eventName, params) {
      params = params || {};
      if (cfg.yandexMetrikaId && window.ym) window.ym(cfg.yandexMetrikaId, 'reachGoal', eventName, params);
      if (cfg.ga4MeasurementId && window.gtag) window.gtag('event', eventName, params);
    }
  };

  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('[data-analytics]').forEach(function (el) {
      el.addEventListener('click', function () {
        window.FleetPilotAnalytics.track(el.getAttribute('data-analytics'), {
          label: (el.textContent || '').trim().slice(0, 80)
        });
      });
    });
  });
})();
