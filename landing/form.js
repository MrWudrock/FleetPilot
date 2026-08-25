(function () {
  var cfg = window.FLEETPILOT_CONFIG || {};
  var SUPPORT_EMAIL = cfg.supportEmail || 'hello@fleetpilot.ru';

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

  function formatPhone(value) {
    var digits = value.replace(/\D/g, '');
    if (digits.length === 0) return '';
    if (digits[0] === '7' || digits[0] === '8') {
      var formatted = '+7';
      if (digits.length > 1) formatted += ' (' + digits.slice(1, 4);
      if (digits.length > 4) formatted += ') ' + digits.slice(4, 7);
      if (digits.length > 7) formatted += '-' + digits.slice(7, 9);
      if (digits.length > 9) formatted += '-' + digits.slice(9, 11);
      return formatted;
    }
    return '+' + digits;
  }

  function validateEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  }

  document.addEventListener('DOMContentLoaded', function () {
    var form = document.getElementById('lead-form');
    var messageEl = document.getElementById('form-message');
    if (!form || !messageEl) return;

    var phoneInput = form.querySelector('input[name="phone"]');
    if (phoneInput) {
      phoneInput.addEventListener('input', function () {
        var cursorPos = this.selectionStart;
        var oldLen = this.value.length;
        this.value = formatPhone(this.value);
        var newLen = this.value.length;
        this.setSelectionRange(cursorPos + (newLen - oldLen), cursorPos + (newLen - oldLen));
      });
    }

    form.addEventListener('submit', async function (e) {
      e.preventDefault();
      messageEl.classList.add('hidden');

      var email = form.querySelector('input[name="email"]');
      if (email && !validateEmail(email.value)) {
        showMessage(messageEl, 'error', 'Введите корректный email');
        return;
      }

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
      formData.append('submitted_at', new Date().toISOString());
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
