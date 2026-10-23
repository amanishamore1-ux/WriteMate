'use strict';

/*-----------------------------------*\
  #script.js — Anisha More Developer World
  Vanilla JS: theme switcher, sidebar toggle, start screen
  loader, project filters, contact form, avatar lightbox,
  and the card-3d mouse-parallax tilt effect.
\*-----------------------------------*/

(function () {

  var prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var THEME_KEY = 'am-portfolio-theme';
  var VALID_THEMES = ['dark', 'light', 'arcade-dark', 'arcade-light'];


  /*-----------------------------------*\
    #THEME SWITCHER
  \*-----------------------------------*/

  function initThemeSwitcher() {
    var root = document.querySelector('[data-theme-switcher]');
    if (!root) return;

    var toggleBtn = root.querySelector('[data-theme-toggle]');
    var menu = root.querySelector('[data-theme-menu]');
    var options = Array.prototype.slice.call(root.querySelectorAll('[data-theme-value]'));

    function applyTheme(theme, opts) {
      opts = opts || {};
      if (VALID_THEMES.indexOf(theme) === -1) theme = 'dark';

      document.body.setAttribute('data-theme', theme);

      // Keep the coding animation visually matched to the selected site theme.
      var developerLottie = document.querySelector('[data-developer-lottie]');
      if (developerLottie) {
        var animationSources = {
          'dark': './assets/animations/developer-dark.lottie',
          'light': './assets/animations/developer-light.lottie',
          'arcade-dark': './assets/animations/developer-arcade-dark.lottie',
          'arcade-light': './assets/animations/developer-arcade-light.lottie'
        };
        var nextSource = animationSources[theme] || animationSources.dark;
        if (developerLottie.getAttribute('src') !== nextSource) developerLottie.setAttribute('src', nextSource);
      }

      try { window.localStorage.setItem(THEME_KEY, theme); } catch (e) { /* storage unavailable */ }

      options.forEach(function (btn) {
        var li = btn.closest('[data-theme-option]');
        var isMatch = btn.getAttribute('data-theme-value') === theme;
        if (li) li.setAttribute('aria-selected', isMatch ? 'true' : 'false');
      });

      if (opts.pulse && !prefersReducedMotion) {
        root.classList.remove('is-pulsing');
        // force reflow so the animation can re-trigger
        void root.offsetWidth;
        root.classList.add('is-pulsing');
      }
    }

    function openMenu() {
      root.classList.add('is-open');
      toggleBtn.setAttribute('aria-expanded', 'true');
      var selected = root.querySelector('[aria-selected="true"] button');
      if (selected) selected.focus({ preventScroll: true });
    }

    function closeMenu(returnFocus) {
      root.classList.remove('is-open');
      toggleBtn.setAttribute('aria-expanded', 'false');
      if (returnFocus) toggleBtn.focus();
    }

    toggleBtn.addEventListener('click', function () {
      if (root.classList.contains('is-open')) {
        closeMenu(false);
      } else {
        openMenu();
      }
    });

    options.forEach(function (btn) {
      btn.addEventListener('click', function () {
        applyTheme(btn.getAttribute('data-theme-value'), { pulse: true });
        closeMenu(true);
      });
    });

    document.addEventListener('click', function (event) {
      if (!root.contains(event.target)) closeMenu(false);
    });

    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape' && root.classList.contains('is-open')) {
        closeMenu(true);
      }
    });

    menu.addEventListener('keydown', function (event) {
      if (event.key !== 'ArrowDown' && event.key !== 'ArrowUp' && event.key !== 'Home' && event.key !== 'End') return;
      event.preventDefault();
      var index = options.indexOf(document.activeElement);
      if (event.key === 'Home') index = 0;
      else if (event.key === 'End') index = options.length - 1;
      else index = (index + (event.key === 'ArrowDown' ? 1 : -1) + options.length) % options.length;
      options[index].focus();
    });

    root.addEventListener('focusout', function (event) {
      if (!root.contains(event.relatedTarget)) closeMenu(false);
    });

    // restore saved theme (falls back to whatever the page shipped with)
    var saved = null;
    try { saved = window.localStorage.getItem(THEME_KEY); } catch (e) { /* storage unavailable */ }
    if (saved && VALID_THEMES.indexOf(saved) !== -1) {
      applyTheme(saved, { pulse: false });
    } else {
      applyTheme(document.body.getAttribute('data-theme') || 'dark', { pulse: false });
    }
  }


  /*-----------------------------------*\
    #SIDEBAR (player card) TOGGLE
  \*-----------------------------------*/

  function initSidebar() {
    var sidebar = document.querySelector('[data-sidebar]');
    var btn = document.querySelector('[data-sidebar-btn]');
    if (!sidebar || !btn) return;

    btn.addEventListener('click', function () {
      var isActive = sidebar.classList.toggle('active');
      btn.setAttribute('aria-expanded', isActive ? 'true' : 'false');
    });
  }


  /*-----------------------------------*\
    #START SCREEN LOADER
  \*-----------------------------------*/

  function initStartScreen() {
    var screen = document.querySelector('[data-start-screen]');
    if (!screen) return;

    var statusEl = screen.querySelector('[data-start-status]');
    var barFill = screen.querySelector('[data-start-bar]');
    var percentEl = screen.querySelector('[data-start-percent]');
    var detectedEl = screen.querySelector('[data-start-detected]');
    var nameEl = screen.querySelector('[data-start-name]');
    var actionsEl = screen.querySelector('[data-start-actions]');
    var enterBtn = screen.querySelector('[data-enter-world]');
    var skipBtn = screen.querySelector('[data-skip-intro]');

    function hideScreen() {
      screen.classList.add('is-hidden');
      try { window.sessionStorage.setItem('am-portfolio-intro-seen', 'true'); } catch (e) { /* storage unavailable */ }
      window.setTimeout(function () {
        screen.setAttribute('aria-hidden', 'true');
      }, 320);
    }

    try {
      if (window.sessionStorage.getItem('am-portfolio-intro-seen') === 'true') {
        hideScreen();
        return;
      }
    } catch (e) { /* storage unavailable */ }

    if (enterBtn) enterBtn.addEventListener('click', hideScreen);
    if (skipBtn) skipBtn.addEventListener('click', hideScreen);

    if (prefersReducedMotion) {
      if (percentEl) percentEl.textContent = '100%';
      if (barFill) barFill.style.width = '100%';
      if (statusEl) statusEl.textContent = 'WORLD READY';
      if (detectedEl) detectedEl.classList.add('is-visible');
      if (nameEl) nameEl.classList.add('is-visible');
      if (actionsEl) actionsEl.classList.add('is-visible');
      return;
    }

    var progress = 0;
    var messages = [
      [0, 'INITIALIZING WORLD...'],
      [30, 'LOADING TERRAIN...'],
      [55, 'SPAWNING ASSETS...'],
      [80, 'SCANNING PLAYER DATA...'],
      [100, 'WORLD READY']
    ];

    var timer = window.setInterval(function () {
      progress = Math.min(100, progress + Math.round(4 + Math.random() * 10));

      if (barFill) barFill.style.width = progress + '%';
      if (percentEl) percentEl.textContent = progress + '%';
      var progressBar = screen.querySelector('[role="progressbar"]');
      if (progressBar) progressBar.setAttribute('aria-valuenow', String(progress));

      if (statusEl) {
        for (var i = messages.length - 1; i >= 0; i--) {
          if (progress >= messages[i][0]) {
            statusEl.textContent = messages[i][1];
            break;
          }
        }
      }

      if (progress >= 100) {
        window.clearInterval(timer);
        if (detectedEl) detectedEl.classList.add('is-visible');
        window.setTimeout(function () {
          if (nameEl) nameEl.classList.add('is-visible');
        }, 250);
        window.setTimeout(function () {
          if (actionsEl) actionsEl.classList.add('is-visible');
        }, 550);
      }
    }, 140);
  }


  /*-----------------------------------*\
    #PROJECT FILTERS (Project Worlds page)
  \*-----------------------------------*/

  function initProjectFilters() {
    var items = Array.prototype.slice.call(document.querySelectorAll('[data-filter-item]'));
    if (!items.length) return;

    var listButtons = Array.prototype.slice.call(document.querySelectorAll('[data-filter-btn]'));
    var selectBtn = document.querySelector('[data-select]');
    var selectValue = document.querySelector('[data-select-value]');
    var selectItems = Array.prototype.slice.call(document.querySelectorAll('[data-select-item]'));

    function applyFilter(filter, label) {
      items.forEach(function (item) {
        var match = filter === 'all' || item.getAttribute('data-category') === filter;
        item.classList.toggle('active', match);
      });

      listButtons.forEach(function (btn) {
        var isActive = btn.getAttribute('data-filter') === filter;
        btn.classList.toggle('active', isActive);
        btn.setAttribute('aria-pressed', isActive ? 'true' : 'false');
      });

      if (selectValue && label) selectValue.textContent = label;
      selectItems.forEach(function (button) { button.parentElement.setAttribute('aria-selected', button.getAttribute('data-filter') === filter ? 'true' : 'false'); });
    }

    listButtons.forEach(function (btn) {
      btn.addEventListener('click', function () {
        applyFilter(btn.getAttribute('data-filter'), btn.textContent.trim());
      });
    });

    selectItems.forEach(function (btn) {
      btn.addEventListener('click', function () {
        applyFilter(btn.getAttribute('data-filter'), btn.textContent.trim());
        if (selectBtn) { selectBtn.classList.remove('active'); selectBtn.setAttribute('aria-expanded', 'false'); }
      });
    });

    if (selectBtn) {
      selectBtn.addEventListener('click', function () {
        var open = selectBtn.classList.toggle('active');
        selectBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
      });

      document.addEventListener('keydown', function (event) {
        if (event.key === 'Escape' && selectBtn.classList.contains('active')) { selectBtn.classList.remove('active'); selectBtn.setAttribute('aria-expanded', 'false'); selectBtn.focus(); }
      });

      document.addEventListener('click', function (event) {
        if (!selectBtn.contains(event.target) && !selectBtn.nextElementSibling.contains(event.target)) {
          selectBtn.classList.remove('active');
          selectBtn.setAttribute('aria-expanded', 'false');
        }
      });
    }
  }


  /*-----------------------------------*\
    #CONTACT FORM
  \*-----------------------------------*/

  function initContactForm() {
    var form = document.querySelector('[data-form]');
    if (!form) return;

    var inputs = Array.prototype.slice.call(form.querySelectorAll('[data-form-input]'));
    var submitBtn = form.querySelector('[data-form-btn]');
    var statusEl = form.querySelector('[data-form-status]');

    function checkValidity() {
      var isValid = inputs.every(function (input) { return input.value.trim() !== '' && input.checkValidity(); });
      if (submitBtn) submitBtn.disabled = !isValid;
      return isValid;
    }

    inputs.forEach(function (input) {
      input.addEventListener('input', checkValidity);
    });

    checkValidity();

    form.addEventListener('submit', function (event) {
      event.preventDefault();
      if (!checkValidity()) return;

      var data = {};
      inputs.forEach(function (input) { data[input.name] = input.value.trim(); });

      var subject = 'Portfolio message from ' + data.fullname;
      var body = data.message + '\n\n— ' + data.fullname + ' (' + data.email + ')';
      var mailto = 'mailto:' + form.getAttribute('data-recipient')
        + '?subject=' + encodeURIComponent(subject)
        + '&body=' + encodeURIComponent(body);

      window.location.href = mailto;

      if (statusEl) statusEl.textContent = 'Opening your email app...';
    });
  }


  /*-----------------------------------*\
    #AVATAR LIGHTBOX (click-to-zoom preview)
    Opens a fullscreen glass-framed preview of the avatar.
    Handles: open/close, backdrop click, ESC, focus
    management, and body-scroll locking.
  \*-----------------------------------*/

  function initAvatarLightbox() {
    var trigger = document.querySelector('[data-avatar-trigger]');
    var lightbox = document.querySelector('[data-avatar-lightbox]');
    if (!trigger || !lightbox) return;

    var backdrop = lightbox.querySelector('[data-avatar-backdrop]');
    var dialog = lightbox.querySelector('[data-avatar-dialog]');
    var closeBtn = lightbox.querySelector('[data-avatar-close]');

    var isOpen = false;
    var lastFocusedEl = null;

    function getFocusableEls() {
      return Array.prototype.slice.call(
        dialog.querySelectorAll('button, [href], [tabindex]:not([tabindex="-1"])')
      ).filter(function (el) { return !el.hasAttribute('disabled'); });
    }

    function trapFocus(event) {
      if (event.key !== 'Tab') return;

      var focusable = getFocusableEls();
      if (!focusable.length) return;

      var first = focusable[0];
      var last = focusable[focusable.length - 1];

      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    }

    function onKeydown(event) {
      if (event.key === 'Escape') {
        closeLightbox();
        return;
      }
      trapFocus(event);
    }

    function openLightbox() {
      if (isOpen) return;
      isOpen = true;

      lastFocusedEl = document.activeElement;

      lightbox.classList.add('is-open');
      lightbox.setAttribute('aria-hidden', 'false');
      document.body.classList.add('has-lightbox-open');

      document.addEventListener('keydown', onKeydown);

      // move focus into the dialog once the open transition starts
      window.requestAnimationFrame(function () {
        if (closeBtn) closeBtn.focus();
      });
    }

    function closeLightbox() {
      if (!isOpen) return;
      isOpen = false;

      lightbox.classList.remove('is-open');
      lightbox.setAttribute('aria-hidden', 'true');
      document.body.classList.remove('has-lightbox-open');

      document.removeEventListener('keydown', onKeydown);

      if (lastFocusedEl && typeof lastFocusedEl.focus === 'function') {
        lastFocusedEl.focus();
      } else {
        trigger.focus();
      }
    }

    trigger.addEventListener('click', openLightbox);

    if (closeBtn) closeBtn.addEventListener('click', closeLightbox);
    if (backdrop) backdrop.addEventListener('click', closeLightbox);
  }


  /*-----------------------------------*\
    #CARD-3D MOUSE PARALLAX TILT
  \*-----------------------------------*/



  /*-----------------------------------*\\
    #PROFILE TYPING ANIMATIONS
  \\*-----------------------------------*/
  function initProfileTyping() {
    var nameEl = document.querySelector('[data-name-typing]');
    var roleEl = document.querySelector('[data-role-typing]');
    if (!nameEl || !roleEl) return;

    nameEl.textContent = nameEl.getAttribute('aria-label') || 'Anisha More';
    var roles = ['AI & Data Science Student', 'Python • Django REST • SQL', 'AI/ML • Ollama • MQTT', 'PLC & HMI Automation'];
    if (prefersReducedMotion) { roleEl.textContent = roles[0]; return; }

    function typer(el, words, typeSpeed, hold, eraseSpeed) {
      var wi=0, ci=0, deleting=false;
      function tick(){
        var word=words[wi];
        if(!deleting){ ci++; el.textContent=word.slice(0,ci); if(ci>=word.length){ deleting=true; return setTimeout(tick,hold); } setTimeout(tick,typeSpeed); }
        else { ci--; el.textContent=word.slice(0,Math.max(0,ci)); if(ci<=0){ deleting=false; wi=(wi+1)%words.length; return setTimeout(tick,350); } setTimeout(tick,eraseSpeed); }
      }
      tick();
    }
    window.setTimeout(function(){ typer(roleEl,roles,55,1150,28); },450);
  }
  function initCardTilt() {
    if (prefersReducedMotion) return;

    var supportsFinePointer = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
    if (!supportsFinePointer) return;

    var cards = Array.prototype.slice.call(document.querySelectorAll('.card-3d:not(.profile-hud)'));
    if (!cards.length) return;

    cards.forEach(function (card) {
      var inner = card.querySelector('.card-3d__inner');
      if (!inner) return;

      var maxTilt = parseFloat(getComputedStyle(card).getPropertyValue('--tilt-max')) || 8;
      var rafId = null;
      var pendingEvent = null;

      function update() {
        rafId = null;
        if (!pendingEvent) return;

        var rect = card.getBoundingClientRect();
        var relX = (pendingEvent.clientX - rect.left) / rect.width;
        var relY = (pendingEvent.clientY - rect.top) / rect.height;

        var tiltY = (relX - 0.5) * (maxTilt * 2);
        var tiltX = (0.5 - relY) * (maxTilt * 2);

        card.style.setProperty('--tilt-x', tiltX.toFixed(2) + 'deg');
        card.style.setProperty('--tilt-y', tiltY.toFixed(2) + 'deg');
      }

      card.addEventListener('mousemove', function (event) {
        pendingEvent = event;
        if (rafId === null) rafId = window.requestAnimationFrame(update);
      });

      card.addEventListener('mouseleave', function () {
        pendingEvent = null;
        if (rafId !== null) {
          window.cancelAnimationFrame(rafId);
          rafId = null;
        }
        card.style.setProperty('--tilt-x', '0deg');
        card.style.setProperty('--tilt-y', '0deg');
      });
    });
  }




  /*-----------------------------------*\
    #IN-PAGE RESUME VIEWER
  \*-----------------------------------*/
  function initResumeViewer() {
    var viewer = document.querySelector('[data-resume-viewer]');
    var triggers = document.querySelectorAll('[data-resume-open]');
    if (!viewer || !triggers.length) return;

    var closeBtn = viewer.querySelector('[data-resume-close]');
    var backdrop = viewer.querySelector('[data-resume-backdrop]');
    var lastFocused = null;

    function openResume() {
      lastFocused = document.activeElement;
      var frame = viewer.querySelector('[data-resume-frame]');
      if (frame && !frame.getAttribute('src')) frame.setAttribute('src', frame.getAttribute('data-src'));
      viewer.classList.add('is-open');
      viewer.setAttribute('aria-hidden', 'false');
      document.body.classList.add('has-resume-open');
      if (closeBtn) closeBtn.focus();
    }

    function closeResume() {
      viewer.classList.remove('is-open');
      viewer.setAttribute('aria-hidden', 'true');
      document.body.classList.remove('has-resume-open');
      if (lastFocused && typeof lastFocused.focus === 'function') lastFocused.focus();
    }

    triggers.forEach(function (trigger) { trigger.addEventListener('click', openResume); });
    if (closeBtn) closeBtn.addEventListener('click', closeResume);
    if (backdrop) backdrop.addEventListener('click', closeResume);
    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape' && viewer.classList.contains('is-open')) closeResume();
      if (event.key === 'Tab' && viewer.classList.contains('is-open')) {
        var focusable = Array.prototype.slice.call(viewer.querySelectorAll('a[href], button, iframe'));
        var first = focusable[0];
        var last = focusable[focusable.length - 1];
        if (event.shiftKey && document.activeElement === first) {
          event.preventDefault();
          last.focus();
        } else if (!event.shiftKey && document.activeElement === last) {
          event.preventDefault();
          first.focus();
        }
      }
    });
  }


  /* Project details stay local when no public project URL was supplied. */
  function initProjectViewer() {
    var dialog = document.querySelector('[data-project-dialog]');
    if (!dialog) return;
    var title = dialog.querySelector('[data-project-title]');
    var content = dialog.querySelector('[data-project-content]');
    var closeBtn = dialog.querySelector('[data-project-close]');
    var lastFocused = null;
    function closeProject() { dialog.close(); }
    document.querySelectorAll('[data-project-open]').forEach(function (trigger) {
      trigger.addEventListener('click', function () {
        var template = document.getElementById('details-' + trigger.getAttribute('data-project-open'));
        if (!template) return;
        lastFocused = trigger;
        title.textContent = template.getAttribute('data-title');
        content.replaceChildren(template.content.cloneNode(true));
        dialog.showModal();
        document.body.classList.add('has-project-open');
        closeBtn.focus();
      });
    });
    closeBtn.addEventListener('click', closeProject);
    dialog.addEventListener('click', function (event) {
      var rect = dialog.getBoundingClientRect();
      if (event.target === dialog && (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom)) closeProject();
    });
    dialog.addEventListener('close', function () {
      document.body.classList.remove('has-project-open');
      if (lastFocused) lastFocused.focus();
    });
  }

  /*-----------------------------------*\
    #INIT
  \*-----------------------------------*/

  document.addEventListener('DOMContentLoaded', function () {
    initThemeSwitcher();
    initSidebar();
    initStartScreen();
    initProjectFilters();
    initContactForm();
    initAvatarLightbox();
    initResumeViewer();
    initProfileTyping();
    initCardTilt();
    initProjectViewer();
  });

})();
