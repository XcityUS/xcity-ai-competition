/* GitHub Pages is static: registration is sent by the visitor's email client. */
(function () {
  var form = document.getElementById('interestForm');
  if (!form) return;
  var email = form.querySelector('input[type="email"]');
  var message = document.getElementById('interestMessage');
  function english() { return document.documentElement.getAttribute('data-lang') === 'en'; }
  function selectedCalls() { return Array.from(form.querySelectorAll('input[name=tracks]:checked')).map(function(input){ return input.value; }); }
  function valid() {
    if (!form.reportValidity()) return false;
    if (!selectedCalls().length) { message.textContent = english() ? 'Choose at least one call.' : '请至少选择一项征集。'; return false; }
    return true;
  }
  function registrationText() {
    return 'XCITY — Receive competition updates\nCall: ' + selectedCalls().join(' + ') + '\nEmail: ' + email.value.trim() + '\nPlease notify me about call updates.';
  }
  form.addEventListener('submit', function (event) {
    event.preventDefault();
    if (!valid()) return;
    message.textContent = english()
      ? 'Send the email in your mail app to subscribe for updates. If it does not open, copy the details and email competition@xcity.ai.'
      : '请在邮件客户端中发送邮件，发送后才完成更新订阅。若未打开，请复制信息并发送至 competition@xcity.ai。';
    window.location.href = 'mailto:competition@xcity.ai?subject=' + encodeURIComponent('XCITY — Receive competition updates — ' + selectedCalls().join(' + ')) + '&body=' + encodeURIComponent(registrationText());
  });
  form.querySelector('[data-interest-copy]').addEventListener('click', async function () {
    if (!valid()) return;
    var text = registrationText();
    try {
      await navigator.clipboard.writeText(text);
      message.textContent = english() ? 'Details copied. Send them to competition@xcity.ai to subscribe for updates.' : '已复制更新订阅信息，请发送至 competition@xcity.ai。';
    } catch (error) {
      message.textContent = (english() ? 'Copy these details and email competition@xcity.ai:\n' : '请复制以下信息并发送至 competition@xcity.ai：\n') + text;
    }
  });
})();
