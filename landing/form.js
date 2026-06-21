(function () {
  var cfg = window.FLEETPILOT_CONFIG || {};
  var SUPPORT_EMAIL = 'hello@fleetpilot.ru';

  function hasFormSubmitEmail() {
    return cfg.formSubmitEmail && String(cfg.formSubmitEmail).indexOf('@') > 0;
  }
  function hasFormspreeId() {
    return cfg.formspreeId && cfg.formspreeId !== 'YOUR_FORMSPREE_ID';
  }

  function getFormEndpoint(intent) {
    if (intent === 'founding' && hasFormspreeId()) {
      return { url: 'https://formspree.io/f/' + cfg.formspreeId, provider: 'formspree' };
    }
    if (hasFormSubmitEmail()) {
      return { url: 'https://formsubmit.co/ajax/' + encodeURIComponent(cfg.formSubmitEmail), provider: 'formsubmit' };
    }
    if (hasFormspreeId()) {
      return { url: 'https://formspree.io/f/' + cfg.formspreeId, provider: 'formspree' };
    }
    return null;
  }

  function showMessage(el, type, text) {
    el.className = 'rounded-xl p-4 text-sm ' + (type === 'success' ? 'bg-green-50 text-green-800 border border-green-200' : type === 'error' ? 'bg-red-50 text-red-800 border border-red-200' : 'bg-blue-50 text-blue-800 border border-blue-200');
    el.textContent = text;
    el.classList.remove('hidden');
  }

  document.addEventListener('DOMContentLoaded', function () {
    var form = document.getElementById('lead-form');
    var messageEl = document.getElementById('form-message');
    if (!form || !messageEl) return;

    form.addEventListener('submit', async function (e) {
      e.preventDefault();
      var intent = form.dataset.intent || 'pilot';
      var endpoint = getFormEndpoint(intent);
      if (!endpoint) {
        showMessage(messageEl, 'error', 'Форма не настроена. Напишите на ' + SUPPORT_EMAIL);
        return;
      }

      var submitBtn = form.querySelector('button[type="submit"]');
      var originalText = submitBtn.textContent;
      submitBtn.disabled = true;
      submitBtn.textContent = 'Отправка…';

      var formData = new FormData(form);
      formData.append('_subject', '[FleetPilot] ' + (intent === 'founding' ? 'Founding slot' : 'Pilot request'));
      formData.append('intent', intent);
      formData.append('page_url', window.location.href);
      if (endpoint.provider === 'formsubmit') {
        formData.append('_captcha', 'false');
        formData.append('_template', 'table');
      }

      try {
        var res = await fetch(endpoint.url, { method: 'POST', body: formData, headers: { Accept: 'application/json' } });
        if (!res.ok) throw new Error('HTTP ' + res.status);
        if (window.FleetPilotAnalytics) window.FleetPilotAnalytics.track('form_submit', { intent: intent });
        form.reset();
        showMessage(messageEl, 'success', intent === 'founding' ? 'Заявка принята! Свяжемся в течение 24 часов.' : 'Спасибо! Отправим расчёт ROI для вашего автопарка в течение 24 часов.');
      } catch (err) {
        showMessage(messageEl, 'error', 'Ошибка отправки. Напишите на ' + SUPPORT_EMAIL);
      } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = originalText;
      }
    });
  });
})();
