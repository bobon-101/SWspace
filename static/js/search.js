// Live client-side search: filters cards whose [data-search-text] contains the
// typed query, and toggles a "no results" element when nothing matches.
document.addEventListener('input', function (e) {
  if (!e.target.matches('.sw-search-input')) return;

  var input = e.target;
  var container = document.getElementById(input.dataset.searchTarget);
  var emptyEl = input.dataset.searchEmpty ? document.getElementById(input.dataset.searchEmpty) : null;
  if (!container) return;

  var query = input.value.trim().toLowerCase();
  var visibleCount = 0;

  container.querySelectorAll('[data-search-text]').forEach(function (card) {
    var match = card.dataset.searchText.toLowerCase().indexOf(query) !== -1;
    card.style.display = match ? '' : 'none';
    if (match) visibleCount++;
  });

  if (emptyEl) {
    emptyEl.classList.toggle('d-none', visibleCount !== 0);
  }
});
