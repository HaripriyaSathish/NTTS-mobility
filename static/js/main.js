document.addEventListener("DOMContentLoaded", () => {
  /* ---------------- Mobile nav ---------------- */
  const toggle = document.getElementById("navToggle");
  const menu = document.getElementById("navMenu");
  const closeMenu = () => {
    menu?.classList.remove("is-open");
    toggle?.setAttribute("aria-expanded", "false");
  };
  toggle?.addEventListener("click", () => {
    const open = menu.classList.toggle("is-open");
    toggle.setAttribute("aria-expanded", String(open));
  });
  menu?.querySelectorAll("a").forEach((a) => a.addEventListener("click", closeMenu));

  /* ---------------- Active link on scroll ---------------- */
  const links = [...document.querySelectorAll(".navbar__link[href^='#']")];
  const sections = links.map((l) => document.querySelector(l.getAttribute("href"))).filter(Boolean);
  if (sections.length) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        links.forEach((l) => l.classList.toggle("is-active", l.getAttribute("href") === `#${entry.target.id}`));
      });
    }, { rootMargin: "-45% 0px -50% 0px" });
    sections.forEach((s) => observer.observe(s));
  }

  /* ---------------- Fleet slider (auto-plays; timing set in admin) ---------------- */
  document.querySelectorAll("[data-slider]").forEach((deck) => {
    const slides = [...deck.querySelectorAll(".fleet__slide")];
    const tabs = [...deck.querySelectorAll(".fleet__tab")];
    const dots = [...deck.querySelectorAll(".fleet__dot")];
    if (slides.length < 2) return;

    const seconds = parseFloat(deck.dataset.autoplay) || 0;
    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    let current = 0;
    let timer = null;
    let paused = false;
    let inView = false;

    const show = (index) => {
      const next = (index + slides.length) % slides.length;
      if (next === current) return;
      const prev = slides[current];
      prev.classList.remove("is-active");
      prev.classList.add("is-leaving");
      prev.setAttribute("aria-hidden", "true");
      setTimeout(() => prev.classList.remove("is-leaving"), 600);

      slides[next].classList.add("is-active");
      slides[next].removeAttribute("aria-hidden");
      tabs.forEach((t, i) => {
        t.classList.toggle("is-active", i === next);
        t.setAttribute("aria-selected", String(i === next));
      });
      dots.forEach((d, i) => d.classList.toggle("is-active", i === next));
      current = next;
    };

    const stop = () => { clearInterval(timer); timer = null; };
    const start = () => {
      stop();
      if (seconds > 0 && inView && !paused && !reduceMotion && !document.hidden) {
        timer = setInterval(() => show(current + 1), seconds * 1000);
      }
    };
    // Any manual choice restarts the countdown so the slide doesn't jump right away
    const go = (index) => { show(index); start(); };

    deck.querySelectorAll("[data-go]").forEach((btn) => btn.addEventListener("click", () => go(+btn.dataset.go)));
    deck.querySelector("[data-prev]")?.addEventListener("click", () => go(current - 1));
    deck.querySelector("[data-next]")?.addEventListener("click", () => go(current + 1));

    // Arrow keys when the slider has focus
    deck.addEventListener("keydown", (e) => {
      if (e.key === "ArrowRight") go(current + 1);
      if (e.key === "ArrowLeft") go(current - 1);
    });

    // Pause while the visitor is reading / interacting
    const pause = () => { paused = true; stop(); };
    const resume = () => { paused = false; start(); };
    deck.addEventListener("mouseenter", pause);
    deck.addEventListener("mouseleave", resume);
    deck.addEventListener("focusin", pause);
    deck.addEventListener("focusout", (e) => { if (!deck.contains(e.relatedTarget)) resume(); });
    document.addEventListener("visibilitychange", start);

    // Swipe on touch screens
    let startX = null;
    deck.addEventListener("touchstart", (e) => { startX = e.touches[0].clientX; }, { passive: true });
    deck.addEventListener("touchend", (e) => {
      if (startX === null) return;
      const dx = e.changedTouches[0].clientX - startX;
      if (Math.abs(dx) > 50) go(current + (dx < 0 ? 1 : -1));
      startX = null;
    });

    // Only run while the slider is on screen
    new IntersectionObserver(([entry]) => { inView = entry.isIntersecting; start(); }, { threshold: 0.3 }).observe(deck);
  });

  /* ---------------- Stats: count up when scrolled into view ---------------- */
  // Works with any format typed in admin: "10M+" → 0…10 + "M+", "4.9" → 0.0…4.9, "1,420" keeps commas, "24/7" → 0…24 + "/7".
  const counters = [...document.querySelectorAll("[data-count]")];
  const reduceMotionStats = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (counters.length && "IntersectionObserver" in window && !reduceMotionStats) {
    const parse = (text) => {
      const m = text.match(/^(\D*?)(\d[\d,]*(?:\.\d+)?)(.*)$/);
      if (!m) return null;
      const [, prefix, num, suffix] = m;
      return {
        prefix, suffix,
        target: parseFloat(num.replace(/,/g, "")),
        decimals: (num.split(".")[1] || "").length,
        commas: num.includes(","),
      };
    };
    const format = (value, p) => {
      const fixed = value.toFixed(p.decimals);
      const shown = p.commas ? Number(fixed).toLocaleString("en-IN", { minimumFractionDigits: p.decimals }) : fixed;
      return p.prefix + shown + p.suffix;
    };
    const run = (el) => {
      const p = el._count;
      const duration = 1800;
      const t0 = performance.now();
      const tick = (now) => {
        const t = Math.min((now - t0) / duration, 1);
        const eased = 1 - Math.pow(1 - t, 3); // ease-out
        el.textContent = format(p.target * eased, p);
        if (t < 1) requestAnimationFrame(tick);
        else el.textContent = el.dataset.count; // end exactly on the admin text
      };
      requestAnimationFrame(tick);
    };
    const statsObserver = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        statsObserver.unobserve(entry.target);
        run(entry.target);
      });
    }, { threshold: 0.6 });
    counters.forEach((el) => {
      const p = parse(el.dataset.count);
      if (!p) return;
      el._count = p;
      el.textContent = format(0, p);
      statsObserver.observe(el);
    });
  }

  /* ---------------- Floating contact buttons: hide when the footer is on screen ---------------- */
  const fab = document.getElementById("floatingContact");
  const siteFooter = document.querySelector(".site-footer");
  if (fab && siteFooter && "IntersectionObserver" in window) {
    new IntersectionObserver(([entry]) => fab.classList.toggle("is-hidden", entry.isIntersecting))
      .observe(siteFooter);
  }

  /* ---------------- Hero card: Date (calendar) + Ride window (time slots) ---------------- */
  const quick = document.getElementById("quickBook");
  const heroDate = quick?.querySelector('[name="hero_date"]');
  const heroSlot = quick?.querySelector('[name="ride_slot"]');
  const heroDateText = quick?.querySelector("[data-date-display]");
  const pad = (n) => String(n).padStart(2, "0");
  const isoDate = (d) => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
  const todayISO = () => isoDate(new Date());
  const tomorrowISO = () => { const d = new Date(); d.setDate(d.getDate() + 1); return isoDate(d); };

  const dateLabel = (value) => {
    if (value === todayISO()) return heroDate.dataset.todayLabel;
    if (value === tomorrowISO()) return "Tomorrow";
    const [y, m, d] = value.split("-").map(Number);
    return new Date(y, m - 1, d).toLocaleDateString("en-IN", { weekday: "short", day: "numeric", month: "short" });
  };
  const slotLabel = (h, m) =>
    new Date(2000, 0, 1, h, m).toLocaleTimeString("en-IN", { hour: "numeric", minute: "2-digit", hour12: true }).toUpperCase();

  const buildSlots = () => {
    const previous = heroSlot.value;
    const isToday = heroDate.value === todayISO();
    heroSlot.innerHTML = "";
    if (isToday) heroSlot.add(new Option(heroSlot.dataset.nowLabel, "now"));
    // Half-hour slots; for today start at least 30 minutes from now
    const now = new Date();
    let startMinutes = 0;
    if (isToday) startMinutes = Math.ceil((now.getHours() * 60 + now.getMinutes() + 30) / 30) * 30;
    for (let t = startMinutes; t < 24 * 60; t += 30) {
      const h = Math.floor(t / 60), m = t % 60;
      heroSlot.add(new Option(slotLabel(h, m), `${pad(h)}:${pad(m)}`));
    }
    if ([...heroSlot.options].some((o) => o.value === previous)) heroSlot.value = previous;
  };

  if (heroDate && heroSlot) {
    heroDate.min = todayISO();
    if (!heroDate.value || heroDate.value < heroDate.min) heroDate.value = todayISO();
    const refreshDate = () => {
      if (!heroDate.value || heroDate.value < todayISO()) heroDate.value = todayISO();
      heroDateText.textContent = dateLabel(heroDate.value);
      buildSlots();
    };
    heroDate.addEventListener("change", refreshDate);
    heroDate.addEventListener("click", () => { try { heroDate.showPicker(); } catch (_) { /* older browsers */ } });
    refreshDate();
  }

  /* ---------------- Scroll animations: sections & cards fade/slide in ---------------- */
  // Added by JS only, so without JavaScript everything is simply visible.
  if ("IntersectionObserver" in window && !window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    const groups = [
      // [selector, animation style]
      [".fleet__deck", "up"],
      [".stat", "up"],
      [".rides__head, .how__head, .pricing__head, .reviews__head", "up"],
      [".safety__intro", "left"],
      [".ride, .step, .sfeature, .plan, .review", "up"],
      [".how__banner, .app-cta__card", "zoom"],
      [".site-footer__grid > *", "up"],
    ];
    const revealObserver = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        // Show when it scrolls into view, or straight away if the visitor already jumped past it
        // (e.g. clicked "Pricing" in the menu) so nothing above stays hidden.
        const passed = entry.boundingClientRect.bottom < 0;
        if (!entry.isIntersecting && !passed) return;
        entry.target.classList.add("is-visible");
        revealObserver.unobserve(entry.target);
      });
    }, { threshold: 0.15, rootMargin: "0px 0px -40px 0px" });

    groups.forEach(([selector, style]) => {
      document.querySelectorAll(selector).forEach((el) => {
        // cards in the same row come in one after another
        const index = [...el.parentElement.children].indexOf(el);
        el.classList.add("reveal", `reveal--${style}`);
        el.style.setProperty("--reveal-delay", `${Math.min(index, 5) * 110}ms`);
        revealObserver.observe(el);
      });
    });

    // Safety net: anything already scrolled past (page reloaded mid-way, or a menu link jumped
    // over it) is shown straight away so it never stays hidden.
    const showPassed = () => {
      document.querySelectorAll(".reveal:not(.is-visible)").forEach((el) => {
        if (el.getBoundingClientRect().bottom < 0) el.classList.add("is-visible");
      });
    };
    let passedTicking = false;
    window.addEventListener("scroll", () => {
      if (passedTicking) return;
      passedTicking = true;
      setTimeout(() => { showPassed(); passedTicking = false; }, 150);
    }, { passive: true });
    window.addEventListener("load", showPassed);
    showPassed();
  }

  /* ---------------- Modals ---------------- */
  const bookingModal = document.getElementById("bookingModal");
  const successModal = document.getElementById("successModal");
  let lastFocus = null;

  const openModal = (modal) => {
    if (!modal) return;
    lastFocus = document.activeElement;
    modal.hidden = false;
    document.body.classList.add("no-scroll");
    (modal.querySelector("input:not([type=hidden]):not(.hp)") || modal.querySelector("button"))?.focus();
  };
  const closeModal = (modal) => {
    if (!modal || modal.hidden) return;
    modal.hidden = true;
    if (!document.querySelector(".modal:not([hidden])")) document.body.classList.remove("no-scroll");
    lastFocus?.focus?.();
  };
  document.querySelectorAll(".modal").forEach((modal) => {
    modal.querySelectorAll("[data-close-modal]").forEach((el) => el.addEventListener("click", () => closeModal(modal)));
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") document.querySelectorAll(".modal:not([hidden])").forEach(closeModal);
  });

  if (!bookingModal) return;
  const form = document.getElementById("bookingForm");
  const submitBtn = document.getElementById("bookingSubmit");
  const vehicleName = document.getElementById("bookingVehicleName");
  const formError = document.getElementById("bookingError");

  document.querySelectorAll("[data-open-booking]").forEach((btn) =>
    btn.addEventListener("click", (e) => {
      e.preventDefault();
      closeMenu();
      // Buttons on car cards open the popup with that car already picked
      const radio = btn.dataset.vehicle && form.querySelector(`[name="vehicle"][value="${btn.dataset.vehicle}"]`);
      if (radio) {
        radio.checked = true;
        vehicleName.textContent = radio.dataset.buttonName;
      }
      openModal(bookingModal);
    })
  );

  /* ---------------- Errors ---------------- */
  const clearErrors = (scope) => {
    scope.querySelectorAll("[data-error-for]").forEach((el) => (el.textContent = ""));
    scope.querySelectorAll(".has-error").forEach((el) => el.classList.remove("has-error"));
    if (scope === form) formError.hidden = true;
  };
  const showError = (scope, name, message) => {
    const slot = scope.querySelector(`[data-error-for="${name}"]`);
    if (!slot) return false;
    slot.textContent = message;
    slot.closest("label")?.classList.add("has-error");
    return true;
  };
  const focusFirstError = (scope) => scope.querySelector(".has-error input")?.focus();

  // Pickup & destination: any characters allowed (addresses, landmarks, numbers…) – only required.
  const checkRoute = (scope) => {
    let ok = true;
    ["pickup", "destination"].forEach((name) => {
      const input = scope.querySelector(`[name="${name}"]`);
      input.value = input.value.replace(/\s+/g, " ").trim();
      if (!input.value) {
        showError(scope, name, name === "pickup" ? "Please enter your pickup point." : "Please enter your destination.");
        ok = false;
      }
    });
    return ok;
  };

  /* ---------------- Strict checks: name, mobile, email (same rules as the server) ---------------- */
  const rules = {
    name(value) {
      const v = value.replace(/\s+/g, " ").trim();
      if (!v) return "Please enter your name.";
      if (!/^\p{L}[\p{L}\p{M} .'-]*$/u.test(v)) return "Name can only contain letters and spaces.";
      if ((v.match(/\p{L}/gu) || []).length < 2) return "Please enter your full name.";
      if (v.length > 50) return "Name is too long (max 50 characters).";
      return "";
    },
    phone(value) {
      const v = value.trim();
      if (!v) return "Please enter your mobile number.";
      if (!/^\d{10}$/.test(v)) return "Mobile number must be 10 digits.";
      if (!/^[6-9]/.test(v)) return "Enter a valid Indian mobile number (starts with 6, 7, 8 or 9).";
      if (/^(\d)\1{9}$/.test(v)) return "Please enter a real mobile number.";
      return "";
    },
    email(value) {
      const v = value.trim().toLowerCase();
      if (!v) return "Please enter your email address.";
      const valid = /^[a-z0-9!#$%&'*+/=?^_`{|}~-]+(\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?!-)[a-z0-9-]+(\.[a-z0-9-]+)*\.[a-z]{2,}$/.test(v);
      return valid ? "" : "Please enter a valid email address, e.g. name@gmail.com.";
    },
  };

  const checkField = (input) => {
    const message = rules[input.dataset.validate](input.value);
    const label = input.closest("label");
    const slot = form.querySelector(`[data-error-for="${input.name}"]`);
    if (slot) slot.textContent = message;
    label?.classList.toggle("has-error", !!message);
    label?.classList.toggle("is-valid", !message);
    return !message;
  };

  form.querySelectorAll("[data-validate]").forEach((input) => {
    // Block wrong characters while typing
    input.addEventListener("input", () => {
      if (input.dataset.validate === "name") {
        const cleaned = input.value.replace(/[^\p{L}\p{M} .'-]/gu, "").replace(/\s{2,}/g, " ");
        if (cleaned !== input.value) input.value = cleaned;
      } else if (input.dataset.validate === "phone") {
        let digits = input.value.replace(/\D/g, "");
        if (digits.length > 10 && digits.startsWith("91")) digits = digits.slice(2); // pasted +91…
        if (digits.length > 10 && digits.startsWith("0")) digits = digits.slice(1);
        input.value = digits.slice(0, 10);
      } else if (input.dataset.validate === "email") {
        input.value = input.value.replace(/\s/g, "");
      }
      // Re-check live once the field has been touched
      if (input.dataset.touched) checkField(input);
    });
    input.addEventListener("blur", () => {
      if (input.dataset.validate === "name") input.value = input.value.replace(/\s+/g, " ").trim();
      if (input.dataset.validate === "email") input.value = input.value.trim().toLowerCase();
      if (input.value) {
        input.dataset.touched = "1";
        checkField(input);
      }
    });
  });

  /* ---------------- Hero card → popup ---------------- */
  quick?.addEventListener("submit", (e) => {
    e.preventDefault();
    clearErrors(quick);
    if (!checkRoute(quick)) return focusFirstError(quick);
    ["pickup", "destination"].forEach((name) => {
      form.elements[name].value = quick.elements[name].value;
    });
    // Carry the chosen date / time into the popup:
    // today + "Depart Now" → Ride Now, anything else → Schedule with date & time filled in
    const rideNow = heroDate.value === todayISO() && heroSlot.value === "now";
    form.elements.date_option.value = heroDateText.textContent;
    form.elements.ride_window.value = heroSlot.options[heroSlot.selectedIndex]?.text || "";
    form.querySelector(`[name="ride_type"][value="${rideNow ? "now" : "schedule"}"]`).checked = true;
    form.elements.scheduled_date.value = rideNow ? "" : heroDate.value;
    form.elements.scheduled_time.value = rideNow || heroSlot.value === "now" ? "" : heroSlot.value;
    setWhen();
    openModal(bookingModal);
    form.elements.name.focus();
  });
  quick?.addEventListener("input", (e) => {
    e.target.closest("label")?.classList.remove("has-error");
    const slot = quick.querySelector(`[data-error-for="${e.target.name}"]`);
    if (slot) slot.textContent = "";
  });

  /* ---------------- Ride now / schedule ---------------- */
  const setWhen = () => {
    const mode = form.elements.ride_type.value;
    form.querySelectorAll("[data-when]").forEach((el) => (el.hidden = el.dataset.when !== mode));
  };
  form.querySelectorAll('[name="ride_type"]').forEach((r) => r.addEventListener("change", setWhen));

  /* ---------------- Vehicle → button label ---------------- */
  form.querySelectorAll('[name="vehicle"]').forEach((r) =>
    r.addEventListener("change", () => (vehicleName.textContent = r.dataset.buttonName))
  );

  form.addEventListener("input", (e) => {
    if (e.target.dataset.validate) return; // name / mobile / email handle their own messages
    e.target.closest("label")?.classList.remove("has-error");
    const slot = form.querySelector(`[data-error-for="${e.target.name}"]`);
    if (slot) slot.textContent = "";
  });

  /* ---------------- Submit ---------------- */
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    clearErrors(form);

    let ok = checkRoute(form);
    form.querySelectorAll("[data-validate]").forEach((input) => {
      input.dataset.touched = "1";
      if (!checkField(input)) ok = false;
    });
    if (form.elements.ride_type.value === "schedule") {
      if (!form.elements.scheduled_date.value) ok = showError(form, "scheduled_date", "Please choose a pickup date.") && false;
      if (!form.elements.scheduled_time.value) ok = showError(form, "scheduled_time", "Please choose a pickup time.") && false;
    }
    if (!ok) return focusFirstError(form);

    submitBtn.disabled = true;
    try {
      const res = await fetch(form.action, {
        method: "POST",
        body: new FormData(form),
        headers: { "X-Requested-With": "XMLHttpRequest" },
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok || !data.ok) {
        const errors = data.errors || {};
        let shown = false;
        Object.entries(errors).forEach(([name, msg]) => (shown = showError(form, name, msg) || shown));
        const general = errors.__all__ || (!shown && "Something went wrong. Please try again.");
        if (general) {
          formError.textContent = general;
          formError.hidden = false;
        }
        focusFirstError(form);
        return;
      }
      form.reset();
      quick?.reset();
      heroDate?.dispatchEvent(new Event("change")); // back to Today / Depart Now
      form.querySelectorAll("[data-validate]").forEach((input) => delete input.dataset.touched);
      form.querySelectorAll(".is-valid").forEach((el) => el.classList.remove("is-valid"));
      setWhen();
      const checked = form.querySelector('[name="vehicle"]:checked');
      if (checked) vehicleName.textContent = checked.dataset.buttonName;
      closeModal(bookingModal);
      openModal(successModal);
    } catch {
      formError.textContent = "Network error. Please check your connection and try again.";
      formError.hidden = false;
    } finally {
      submitBtn.disabled = false;
    }
  });
});
