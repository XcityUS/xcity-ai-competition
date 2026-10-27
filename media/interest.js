/* Homepage subscriptions are saved by the private intake API, not a mail client. */
(function () {
  var form = document.getElementById('interestForm');
  if (!form) return;
  var email = form.querySelector('input[type="email"]');
  var message = document.getElementById('interestMessage');
  var button = form.querySelector('button[type="submit"]');
  var api = /^(localhost|127\.0\.0\.1)$/.test(location.hostname)
    ? 'http://127.0.0.1:8787' : 'https://xcity-practice-applications.jingyuan-huang.chatgpt.site';
  var busy = false;
  function english() { return document.documentElement.getAttribute('data-lang') === 'en'; }
  function say(en, zh) { message.textContent = english() ? en : zh; }
  function calls() { return Array.from(form.querySelectorAll('input[name=tracks]:checked')).map(function (input) { return input.value === 'Open Agent Call' ? 'agent' : 'practice'; }); }
  form.addEventListener('submit', async function (event) {
    event.preventDefault();
    if (busy || !form.reportValidity()) return;
    var tracks = calls();
    if (!tracks.length) { say('Choose at least one call.', '请至少选择一项征集。'); return; }
    busy = true; button.disabled = true; form.setAttribute('aria-busy', 'true');
    say('Subscribing…', '正在订阅…');
    try {
      var session = await fetch(api + '/api/session', {method: 'POST', credentials: 'omit'});
      if (!session.ok) throw new Error(session.status === 429 ? 'rate' : 'session');
      var nonce = await session.json();
      var response = await fetch(api + '/api/subscribe', {method: 'POST', credentials: 'omit', headers: {'Content-Type': 'application/json', 'x-form-token': nonce.token}, body: JSON.stringify({email: email.value.trim(), tracks: tracks, language: english() ? 'en' : 'zh', consent: true})});
      var result = await response.json();
      if (!response.ok || result.subscribed !== true) throw new Error(response.status === 429 ? 'rate' : 'save');
      say('Subscribed. We will email updates for your selected calls.', '订阅成功。我们会将所选征集的更新发送至你的邮箱。');
    } catch (error) {
      if (error.message === 'rate') say('Too many attempts. Please try again later.', '操作较频繁，请稍后重试。');
      else say('Subscription was not saved. Please try again.', '订阅未成功保存，请重试。');
    } finally { busy = false; button.disabled = false; form.removeAttribute('aria-busy'); }
  });
})();
