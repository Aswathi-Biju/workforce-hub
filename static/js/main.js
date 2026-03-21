/**
 * main.js — WorkForce Hub frontend utilities
 */

document.addEventListener('DOMContentLoaded', function () {

    // ── Auto-dismiss flash alerts after 4 seconds ──
    const alerts = document.querySelectorAll('.alert.alert-dismissible');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) bsAlert.close();
        }, 4000);
    });

    // ── Add loading state to all submit buttons ──
    document.querySelectorAll('form').forEach(function (form) {
        form.addEventListener('submit', function () {
            const btn = form.querySelector('button[type="submit"]');
            if (btn && !btn.disabled) {
                btn.classList.add('btn-loading');
                btn.disabled = true;
                // Re-enable after 5s as fallback
                setTimeout(function () {
                    btn.classList.remove('btn-loading');
                    btn.disabled = false;
                }, 5000);
            }
        });
    });

    // ── Highlight active sidebar link ──
    const currentPath = window.location.pathname;
    document.querySelectorAll('.sidebar .nav-link').forEach(function (link) {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });

    // ── Salary formatter: add comma separators as user types ──
    const salaryInput = document.querySelector('input[name="salary"]');
    if (salaryInput) {
        salaryInput.addEventListener('blur', function () {
            const val = parseFloat(this.value);
            if (!isNaN(val)) {
                // Just validate it's positive
                if (val < 0) this.value = 0;
            }
        });
    }

    // ── Password strength indicator ──
    const passwordInput = document.querySelector('input[name="password"]');
    if (passwordInput) {
        const strengthBar = document.createElement('div');
        strengthBar.className = 'progress mt-1';
        strengthBar.style.height = '4px';
        strengthBar.innerHTML = '<div class="progress-bar" id="strengthBar" style="width:0%;transition:width .3s,background .3s;border-radius:4px;"></div>';
        passwordInput.parentNode.insertAdjacentElement('afterend', strengthBar);

        passwordInput.addEventListener('input', function () {
            const bar = document.getElementById('strengthBar');
            const len = this.value.length;
            const hasUpper = /[A-Z]/.test(this.value);
            const hasNum   = /[0-9]/.test(this.value);
            const hasSpec  = /[^A-Za-z0-9]/.test(this.value);
            let score = 0;
            if (len >= 6)  score++;
            if (len >= 10) score++;
            if (hasUpper)  score++;
            if (hasNum)    score++;
            if (hasSpec)   score++;

            const colors = ['#ef4444','#f97316','#eab308','#22c55e','#16a34a'];
            const widths = ['20%','40%','60%','80%','100%'];
            bar.style.width   = len === 0 ? '0%' : widths[Math.min(score - 1, 4)];
            bar.style.background = len === 0 ? '' : colors[Math.min(score - 1, 4)];
        });
    }

    // ── Confirm delete with keyboard shortcut ──
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') {
            // Close any open modals
            document.querySelectorAll('.modal.show').forEach(function (modal) {
                bootstrap.Modal.getInstance(modal)?.hide();
            });
        }
    });

    // ── Tooltip initialization ──
    const tooltipTriggers = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltipTriggers.forEach(function (el) {
        new bootstrap.Tooltip(el);
    });
});
