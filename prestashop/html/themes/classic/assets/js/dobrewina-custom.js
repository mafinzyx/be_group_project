document.addEventListener('DOMContentLoaded', function() {
  const ageModal = document.getElementById('age-verification-modal');
  const ageYesBtn = document.getElementById('age-yes');
  const ageNoBtn = document.getElementById('age-no');

  if (!ageModal) return;

  const ageVerified = localStorage.getItem('ageVerified');

  if (!ageVerified) {
    ageModal.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
  } else {
    ageModal.classList.add('hidden');
  }

  if (ageYesBtn) {
    ageYesBtn.addEventListener('click', function() {
      localStorage.setItem('ageVerified', 'true');
      ageModal.classList.add('hidden');
      document.body.style.overflow = '';
    });
  }

  if (ageNoBtn) {
    ageNoBtn.addEventListener('click', function() {
      window.location.href = 'https://www.google.com';
    });
  }
});

