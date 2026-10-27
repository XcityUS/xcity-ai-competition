/* GitHub Pages is static: registration is sent by the visitor's email client. */
(function () {
  var form = document.getElementById('interestForm');
  if (!form) return;
  var email = form.querySelector('input[type="email"]');
  var message = document.getElementById('interestMessage');
  function english() { return document.documentElement.getAttribute('data-lang') === 'en'; }
  function registrationText() {
    return 'XCITY — Register interest\nCall: ' + form.getAttribute('data-call') + '\nEmail: ' + email.value.trim() + '\nPlease notify me about call updates.';
  }
  form.addEventListener('submit', function (event) {
    event.preventDefault();
    if (!form.reportValidity()) return;
    message.textContent = english()
      ? 'Send the email in your mail app to complete registration. If it does not open, copy the details and email competition@xcity.ai.'
      : '请在邮件客户端中发送邮件，发送后才完成登记。若未打开，请复制信息并发送至 competition@xcity.ai。';
    window.location.href = 'mailto:competition@xcity.ai?subject=' + encodeURIComponent('XCITY — Register interest — ' + form.getAttribute('data-call')) + '&body=' + encodeURIComponent(registrationText());
  });
  form.querySelector('[data-interest-copy]').addEventListener('click', async function () {
    if (!form.reportValidity()) return;
    var text = registrationText();
    try {
      await navigator.clipboard.writeText(text);
      message.textContent = english() ? 'Details copied. Send them to competition@xcity.ai to complete registration.' : '已复制登记信息，请发送至 competition@xcity.ai 完成登记。';
    } catch (error) {
      message.textContent = (english() ? 'Copy these details and email competition@xcity.ai:\n' : '请复制以下信息并发送至 competition@xcity.ai：\n') + text;
    }
  });
})();
