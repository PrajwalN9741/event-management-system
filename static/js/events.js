/* ── Dynamic Flower Rows ───────────────────────────────────────────────────── */
const flowerTemplate = `
<div class="flower-row row g-2 mb-2 align-items-center">
  <div class="col-md-4">
    <input type="text" name="flower_type[]" class="form-control" placeholder="Flower type (e.g. Rose)"/>
  </div>
  <div class="col-md-3">
    <div class="input-group">
      <input type="number" name="flower_qty[]" class="form-control" placeholder="Qty" min="0" value="0"/>
      <span class="input-group-text">pcs</span>
    </div>
  </div>
  <div class="col-md-3">
    <div class="input-group">
      <span class="input-group-text">₹</span>
      <input type="number" name="flower_price[]" class="form-control" placeholder="Unit price" min="0" step="0.01" value="0"/>
    </div>
  </div>
  <div class="col-md-2">
    <button type="button" class="btn btn-outline-danger btn-sm remove-flower"><i class="bi bi-trash"></i></button>
  </div>
</div>`;

document.getElementById('addFlowerRow')?.addEventListener('click', () => {
    document.getElementById('flowerContainer').insertAdjacentHTML('beforeend', flowerTemplate);
});

document.getElementById('flowerContainer')?.addEventListener('click', e => {
    if (e.target.closest('.remove-flower')) {
        const rows = document.querySelectorAll('.flower-row');
        if (rows.length > 1) e.target.closest('.flower-row').remove();
        else { /* keep at least one row */ }
    }
});

/* ── Dynamic Inventory Rows ────────────────────────────────────────────────── */
function buildInvTemplate() {
    const select = document.querySelector('.inv-item-select');
    let options = '<option value="">Select inventory item…</option>';
    if (select) {
        select.querySelectorAll('option').forEach(opt => {
            options += `<option value="${opt.value}" data-price="${opt.dataset.price || 0}" data-unit="${opt.dataset.unit || 'pcs'}">${opt.textContent}</option>`;
        });
    }
    return `
<div class="inv-row row g-2 mb-2 align-items-center">
  <div class="col-md-7">
    <select name="inv_item_id[]" class="form-select inv-item-select">${options}</select>
  </div>
  <div class="col-md-3">
    <div class="input-group">
      <input type="number" name="inv_quantity[]" class="form-control inv-qty" placeholder="Qty" min="0" step="0.01" value="0"/>
      <span class="input-group-text inv-unit">pcs</span>
    </div>
  </div>
  <div class="col-md-2">
    <button type="button" class="btn btn-outline-danger btn-sm remove-inv"><i class="bi bi-trash"></i></button>
  </div>
</div>`;
}

document.getElementById('addInvRow')?.addEventListener('click', () => {
    document.getElementById('invContainer').insertAdjacentHTML('beforeend', buildInvTemplate());
    attachInvListeners();
});

document.getElementById('invContainer')?.addEventListener('click', e => {
    if (e.target.closest('.remove-inv')) {
        const rows = document.querySelectorAll('.inv-row');
        if (rows.length > 1) e.target.closest('.inv-row').remove();
    }
});

function attachInvListeners() {
    document.querySelectorAll('.inv-item-select').forEach(sel => {
        sel.onchange = function () {
            const opt = this.selectedOptions[0];
            const row = this.closest('.inv-row');
            if (row && opt) {
                const unitSpan = row.querySelector('.inv-unit');
                if (unitSpan) unitSpan.textContent = opt.dataset.unit || 'pcs';
            }
        };
    });
}

attachInvListeners();

/* ── Event Form Validation ─────────────────────────────────────────────────── */
const eventForm = document.getElementById('eventForm');
if (eventForm) {
    eventForm.addEventListener('submit', function (e) {
        const name = this.querySelector('[name="name"]')?.value.trim();
        const type = this.querySelector('[name="event_type"]')?.value;
        const date = this.querySelector('[name="event_date"]')?.value;
        const venue = this.querySelector('[name="venue"]')?.value.trim();
        const client = this.querySelector('[name="client_name"]')?.value.trim();

        if (!name || !type || !date || !venue || !client) {
            e.preventDefault();
            alert('Please fill in all required fields (marked with *).');
            return false;
        }

        // Date must not be in the past (warn only)
        const selectedDate = new Date(date);
        const today = new Date(); today.setHours(0, 0, 0, 0);
        if (selectedDate < today) {
            if (!confirm('The selected date is in the past. Are you sure?')) {
                e.preventDefault();
            }
        }
    });
}
