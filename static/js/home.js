/* =====================================================================
   Cards are now rendered server-side (Jinja, in home.html) using real
   data from marketplace_service.py - static models + approved creator
   models combined. This file ONLY handles the client-side search filter
   on top of those already-rendered cards.
   ===================================================================== */
document.addEventListener('DOMContentLoaded', () => {
  const searchInput = document.getElementById('searchInput');
  if (!searchInput) return;

  searchInput.addEventListener('input', (e) => {
    const q = e.target.value.toLowerCase().trim();
    document.querySelectorAll('.card').forEach(c => {
      c.style.display = c.dataset.name.includes(q) ? '' : 'none';
    });
  });
});
