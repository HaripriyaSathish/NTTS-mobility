/* Car photos use Cloudinary's background removal. The very first time a new photo is requested
   Cloudinary may still be processing it, so retry once, then show the original photo instead. */
const carPhotoFailed = (img) => {
  if (!img.dataset.fallback || img.dataset.retried === "fallback") return;
  if (!img.dataset.retried) {
    img.dataset.retried = "1";
    const src = img.src;
    setTimeout(() => { img.src = `${src}${src.includes("?") ? "&" : "?"}r=1`; }, 4000);
  } else {
    img.dataset.retried = "fallback";
    img.src = img.dataset.fallback;
  }
};
document.addEventListener("error", (e) => { if (e.target.tagName === "IMG") carPhotoFailed(e.target); }, true);

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("img[data-fallback]").forEach((img) => {
    if (img.complete && !img.naturalWidth) carPhotoFailed(img);
  });

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

  /* ---------------- Card sliders (Fleet & Rides carousel, Reviews) ----------------
     <div data-slider-track> holds the cards; [data-slider-prev]/[data-slider-next] sit in the same section.
     data-slider-loop        arrows wrap around at the ends.
     data-slider-marquee="40" cards glide continuously at 40 px per second, in an endless loop
     data-slider-direction    "right" (cards move left → right) or "left".
     The glide pauses while the visitor hovers, focuses or touches it, and when it is off screen. */
  const reduceMotionSlider = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  document.querySelectorAll("[data-slider-track]").forEach((track) => {
    const section = track.closest("section") || document;
    const prev = section.querySelector("[data-slider-prev]");
    const next = section.querySelector("[data-slider-next]");
    if (!prev || !next) return;
    const speed = reduceMotionSlider ? 0 : parseFloat(track.dataset.sliderMarquee) || 0;
    const loop = speed > 0 || track.hasAttribute("data-slider-loop");
    const edge = 10; // tolerance: the track has a few px of padding and snapping can land on fractions

    // Endless glide: a hidden copy of the cards follows the real ones, so the row never runs out
    let setWidth = 0;
    if (speed) {
      const originals = [...track.children];
      originals.forEach((card) => {
        const copy = card.cloneNode(true);
        copy.setAttribute("aria-hidden", "true");
        copy.classList.add("is-clone");
        copy.querySelectorAll("a, button, [tabindex]").forEach((el) => el.setAttribute("tabindex", "-1"));
        track.appendChild(copy);
      });
      track.classList.add("is-marquee");
      const measure = () => { setWidth = track.children[originals.length].offsetLeft - originals[0].offsetLeft; };
      measure();
      window.addEventListener("resize", measure);
    }
    // keep the position inside the first copy so the loop is seamless
    const wrap = (x) => (setWidth ? ((x % setWidth) + setWidth) % setWidth : x);

    const maxScroll = () => track.scrollWidth - track.clientWidth;
    const atStart = () => track.scrollLeft <= edge;
    const atEnd = () => track.scrollLeft >= maxScroll() - edge;
    const step = () => {
      const card = track.firstElementChild;
      return card ? card.getBoundingClientRect().width + parseFloat(getComputedStyle(track).columnGap || 0) : track.clientWidth;
    };
    const updateArrows = () => {
      const fits = !speed && maxScroll() <= edge; // everything already visible: nothing to slide
      prev.disabled = fits || (!loop && atStart());
      next.disabled = fits || (!loop && atEnd());
    };

    let pos = 0;
    let busyUntil = 0; // the glide waits while an arrow click is animating
    const move = (dir) => {
      if (speed) {
        pos = wrap(track.scrollLeft);
        if (dir < 0 && pos < step()) pos += setWidth; // room to slide back
        track.scrollLeft = pos; // jump to the matching spot (looks identical), then slide
        busyUntil = performance.now() + 700;
        track.scrollTo({ left: pos + dir * step(), behavior: "smooth" });
      } else if (loop && dir > 0 && atEnd()) track.scrollTo({ left: 0 });
      else if (loop && dir < 0 && atStart()) track.scrollTo({ left: maxScroll() });
      else track.scrollBy({ left: dir * step() });
      setTimeout(updateArrows, 500); // fallback for browsers without "scrollend"
    };
    prev.addEventListener("click", () => move(-1));
    next.addEventListener("click", () => move(1));
    track.addEventListener("keydown", (e) => {
      if (e.key === "ArrowLeft") { e.preventDefault(); prev.click(); }
      if (e.key === "ArrowRight") { e.preventDefault(); next.click(); }
    });
    track.addEventListener("scroll", updateArrows, { passive: true });
    track.addEventListener("scrollend", updateArrows);
    window.addEventListener("resize", updateArrows);
    updateArrows();

    if (!speed) return;
    const direction = track.dataset.sliderDirection === "left" ? 1 : -1; // "right": scroll position goes down
    let paused = false;
    let visible = false;
    let last = 0;
    pos = direction < 0 ? setWidth : 0;
    track.scrollLeft = pos;
    const frame = (now) => {
      const dt = last ? Math.min(now - last, 100) : 0;
      last = now;
      if (!paused && visible && !document.hidden && now > busyUntil) {
        if (Math.abs(track.scrollLeft - pos) > 2) pos = track.scrollLeft; // visitor swiped or clicked an arrow
        pos += direction * speed * dt / 1000;
        if (pos < 0) pos += setWidth; // seamless: the copy looks exactly like the start
        if (pos > setWidth) pos -= setWidth;
        track.scrollLeft = pos;
      }
      requestAnimationFrame(frame);
    };
    requestAnimationFrame(frame);

    const container = track.parentElement;
    ["mouseenter", "focusin", "touchstart"].forEach((type) =>
      container.addEventListener(type, () => { paused = true; }, { passive: true }));
    ["mouseleave", "focusout"].forEach((type) =>
      container.addEventListener(type, () => { paused = false; pos = track.scrollLeft; }));
    track.addEventListener("touchend", () => { setTimeout(() => { paused = false; pos = track.scrollLeft; }, 1200); }, { passive: true });
    if ("IntersectionObserver" in window) {
      new IntersectionObserver(([entry]) => { visible = entry.isIntersecting; }, { threshold: 0.1 }).observe(track);
    } else {
      visible = true;
    }
  });

  /* ---------------- FAQ accordion: one answer open at a time ---------------- */
  document.querySelectorAll(".faq__toggle").forEach((btn) =>
    btn.addEventListener("click", () => {
      const item = btn.closest(".faq__item");
      const opening = !item.classList.contains("is-open");
      item.parentElement.querySelectorAll(".faq__item.is-open").forEach((open) => {
        open.classList.remove("is-open");
        open.querySelector(".faq__toggle").setAttribute("aria-expanded", "false");
      });
      item.classList.toggle("is-open", opening);
      btn.setAttribute("aria-expanded", String(opening));
    })
  );

  /* ---------------- Scroll animations: sections & cards fade/slide in ---------------- */
  // Added by JS only, so without JavaScript everything is simply visible.
  if ("IntersectionObserver" in window && !window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    const groups = [
      // [selector, animation style]
      [".fleet__deck", "up"],
      [".stat", "up"],
      [".rides__head, .how__head, .pricing__head, .reviews__head", "up"],
      [".safety__intro", "left"],
      [".rides__grid:not(.rides__grid--slider) .ride, .step, .sfeature, .pricing__grid:not(.pricing__grid--slider) .plan, .reviews__grid:not(.reviews__grid--slider) .review", "up"],
      // sliders fade in as one block, so cards off to the side are never left hidden
      [".reviews__grid--slider, .rides__grid--slider, .pricing__grid--slider", "up"],
      [".how__banner", "zoom"],
      [".about__intro, .faq__intro", "left"],
      [".about__card, .about__value, .faq__item", "up"],
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
    // Always open at the top (trip tabs first), not where it was last scrolled to
    modal.querySelectorAll(".booking__body").forEach((body) => { body.scrollTop = 0; });
    (modal.querySelector("input:not([type=hidden]):not(.hp)") || modal.querySelector("button"))
      ?.focus({ preventScroll: true });
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

  // Footer links like #privacy-policy open the matching policy popup instead of jumping
  document.querySelectorAll('a[href^="#"]').forEach((link) => {
    const slug = link.getAttribute("href").slice(1);
    const popup = slug && document.getElementById(`legal-${slug}`);
    if (!popup) return;
    link.addEventListener("click", (e) => {
      e.preventDefault();
      openModal(popup);
      popup.querySelector(".legal__body").scrollTop = 0;
    });
  });

  if (!bookingModal) return;
  const form = document.getElementById("bookingForm");
  const submitBtn = document.getElementById("bookingSubmit");
  const vehicleName = document.getElementById("bookingVehicleName");
  const formError = document.getElementById("bookingError");
  const carCount = document.getElementById("bookingCarCount");
  const noCars = document.getElementById("bookingNoCars");
  const carCards = [...form.querySelectorAll(".vehicle[data-trip]")];

  // Booking limits (same numbers as core/forms.py)
  const limits = {
    lead: Number(form.dataset.minLead) || 30,
    daysAhead: Number(form.dataset.maxDaysAhead) || 90,
    tripDays: Number(form.dataset.maxTripDays) || 30,
    pax: Number(form.dataset.maxPax) || 20,
  };
  const currentTrip = () => form.elements.trip_type.value;
  let wantedVehicle = ""; // car the customer picked; kept when switching tab / package

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
  const focusFirstError = (scope) => {
    const field = scope.querySelector(".has-error input");
    if (field) return field.focus();
    scope.querySelector('[data-error-for="rate"]:not(:empty)')?.scrollIntoView({ block: "center", behavior: "smooth" });
  };

  /* ---------------- Checks for every field (same rules as the server) ---------------- */
  const ADDRESS_CHARS = /^[\p{L}\p{M}\p{N} ,.\-/#()&':;+]+$/u;
  const FLIGHT_RE = /^([A-Z]{3}|[A-Z][A-Z0-9]|[0-9][A-Z])(\d{1,4}[A-Z]?)$/;
  const parseDate = (iso) => { const [y, m, d] = iso.split("-").map(Number); return new Date(y, m - 1, d); };
  const lastBookingISO = () => { const d = new Date(); d.setDate(d.getDate() + limits.daysAhead); return isoDate(d); };

  const addressError = (value, label) => {
    const v = value.replace(/\s+/g, " ").trim();
    if (!v) return `Please enter the ${label}.`;
    if (!ADDRESS_CHARS.test(v)) return "Only letters, numbers and , . - / # ( ) & ' are allowed.";
    if ((v.match(/\p{L}/gu) || []).length < 3) return `Please enter a proper ${label}.`;
    if (v.length > 200) return "Address is too long (max 200 characters).";
    return "";
  };
  const numberError = (value, label, high) => {
    const v = value.trim();
    if (!v) return `Please enter the ${label}.`;
    if (!/^\d+$/.test(v)) return `${label[0].toUpperCase()}${label.slice(1)} must be a whole number.`;
    if (Number(v) < 1 || Number(v) > high) return `Please enter between 1 and ${high}.`;
    return "";
  };

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
    address(value, input) {
      const message = addressError(value, input.dataset.label);
      if (message || input.name !== "destination") return message;
      const pickup = form.elements.pickup.value.replace(/\s+/g, " ").trim().toLowerCase();
      const drop = value.replace(/\s+/g, " ").trim().toLowerCase();
      return pickup && pickup === drop ? "Drop address can't be the same as the pickup." : "";
    },
    flight(value) {
      const v = value.replace(/[\s-]/g, "").toUpperCase();
      if (!v) return "Please enter the flight number.";
      return FLIGHT_RE.test(v) ? "" : "Enter a valid flight number, e.g. 6E 2134.";
    },
    date(value) {
      if (!value) return "Please choose a pickup date.";
      if (value < todayISO()) return "Pickup date can't be in the past.";
      if (value > lastBookingISO()) return `You can book up to ${limits.daysAhead} days ahead.`;
      return "";
    },
    time(value) {
      if (!value) return "Please choose a pickup time.";
      const date = form.elements.scheduled_date.value;
      if (!date || rules.date(date)) return "";
      const [h, m] = value.split(":").map(Number);
      const pickupAt = parseDate(date);
      pickupAt.setHours(h, m, 0, 0);
      if (pickupAt < new Date(Date.now() + limits.lead * 60000)) {
        return `Pickup time must be at least ${limits.lead} minutes from now.`;
      }
      return "";
    },
    days: (value) => numberError(value, "no of days", limits.tripDays),
    pax: (value) => numberError(value, "no of pax", limits.pax),
  };

  const isShown = (input) => !input.closest("[hidden]");
  const checkField = (input) => {
    const message = isShown(input) ? rules[input.dataset.validate](input.value, input) : "";
    const label = input.closest("label");
    const slot = form.querySelector(`[data-error-for="${input.name}"]`);
    if (slot) slot.textContent = message;
    label?.classList.toggle("has-error", !!message);
    label?.classList.toggle("is-valid", !message && !!input.value);
    return !message;
  };

  form.querySelectorAll("[data-validate]").forEach((input) => {
    const kind = input.dataset.validate;
    // Block wrong characters while typing
    input.addEventListener("input", () => {
      let value = input.value;
      if (kind === "name") {
        value = value.replace(/[^\p{L}\p{M} .'-]/gu, "").replace(/\s{2,}/g, " ");
      } else if (kind === "phone") {
        let digits = value.replace(/\D/g, "");
        if (digits.length > 10 && digits.startsWith("91")) digits = digits.slice(2); // pasted +91…
        if (digits.length > 10 && digits.startsWith("0")) digits = digits.slice(1);
        value = digits.slice(0, 10);
      } else if (kind === "email") {
        value = value.replace(/\s/g, "");
      } else if (kind === "address") {
        value = value.replace(/[^\p{L}\p{M}\p{N} ,.\-/#()&':;+]/gu, "").replace(/\s{2,}/g, " ");
      } else if (kind === "flight") {
        value = value.toUpperCase().replace(/[^A-Z0-9 -]/g, "");
      } else if (kind === "days" || kind === "pax") {
        value = value.replace(/\D/g, "").slice(0, 2);
      }
      if (value !== input.value) input.value = value;
      // Re-check live once the field has been touched
      if (input.dataset.touched) checkField(input);
      if (kind === "pax") filterCars();
      if (kind === "date" && form.elements.scheduled_time.dataset.touched) checkField(form.elements.scheduled_time);
    });
    input.addEventListener("blur", () => {
      if (kind === "name" || kind === "address") input.value = input.value.replace(/\s+/g, " ").trim();
      if (kind === "email") input.value = input.value.trim().toLowerCase();
      if (kind === "flight") {
        const match = input.value.replace(/[\s-]/g, "").match(FLIGHT_RE);
        if (match) input.value = `${match[1]} ${match[2]}`;
      }
      if (input.value) {
        input.dataset.touched = "1";
        checkField(input);
      }
    });
    // Date and time pickers fire "change" rather than "input" in some browsers
    if (kind === "date" || kind === "time") input.addEventListener("change", () => input.dispatchEvent(new Event("input")));
  });

  /* ---------------- Pickup / Drop suggestions (Chennai places from admin) ----------------
     Typing "tnag", "t nagar" or "airport" lists matching places; ↑/↓ + Enter or a click picks one.
     Names starting with the typed text come first, then names with a word starting with it. */
  const placesData = document.getElementById("locationSuggestions");
  const places = placesData ? JSON.parse(placesData.textContent) : [];
  const squash = (text) => text.toLowerCase().replace(/[^a-z0-9]/g, "");
  const placeIndex = places.map((name) => ({
    name, flat: squash(name), words: name.toLowerCase().split(/[^a-z0-9]+/).filter(Boolean),
  }));
  const findPlaces = (typed) => {
    const flat = squash(typed);
    if (flat.length < 2) return [];
    const word = typed.toLowerCase().trim();
    const scored = [];
    placeIndex.forEach((p) => {
      let score = -1;
      if (p.flat.startsWith(flat)) score = 0;
      else if (p.words.some((w) => w.startsWith(word) || w.startsWith(flat))) score = 1;
      else if (p.flat.includes(flat)) score = 2;
      if (score >= 0) scored.push([score, p.name]);
    });
    return scored.sort((a, b) => a[0] - b[0] || a[1].length - b[1].length).slice(0, 8).map((s) => s[1]);
  };

  form.querySelectorAll("[data-suggest]").forEach((input) => {
    if (!places.length) return;
    const list = document.createElement("ul");
    list.className = "suggest";
    list.id = `${input.name}-suggestions`;
    list.setAttribute("role", "listbox");
    list.hidden = true;
    input.after(list);
    input.setAttribute("role", "combobox");
    input.setAttribute("aria-autocomplete", "list");
    input.setAttribute("aria-controls", list.id);
    input.setAttribute("aria-expanded", "false");
    let active = -1;

    const close = () => {
      list.hidden = true;
      active = -1;
      input.setAttribute("aria-expanded", "false");
    };
    const highlight = (index) => {
      const items = list.children;
      if (!items.length) return;
      active = (index + items.length) % items.length;
      [...items].forEach((li, i) => li.classList.toggle("is-active", i === active));
      items[active].scrollIntoView({ block: "nearest" });
    };
    const pick = (name) => {
      input.value = name;
      close();
      input.dataset.touched = "1";
      input.dispatchEvent(new Event("input")); // runs the address check
    };
    const show = () => {
      const matches = findPlaces(input.value);
      list.replaceChildren(...matches.map((name) => {
        const li = document.createElement("li");
        li.setAttribute("role", "option");
        li.textContent = name;
        // mousedown (not click) so the box doesn't lose focus first
        li.addEventListener("mousedown", (e) => { e.preventDefault(); pick(name); });
        return li;
      }));
      active = -1;
      list.hidden = !matches.length;
      input.setAttribute("aria-expanded", String(!!matches.length));
    };

    input.addEventListener("input", (e) => { if (e.isTrusted) show(); });
    input.addEventListener("focus", show);
    input.addEventListener("blur", close);
    input.addEventListener("keydown", (e) => {
      if (list.hidden) return;
      if (e.key === "ArrowDown") { e.preventDefault(); highlight(active + 1); }
      else if (e.key === "ArrowUp") { e.preventDefault(); highlight(active - 1); }
      else if (e.key === "Enter" && active >= 0) { e.preventDefault(); pick(list.children[active].textContent); }
      else if (e.key === "Escape") { e.stopPropagation(); close(); }
    });
  });

  /* ---------------- Trip tabs, packages and cars ---------------- */
  const pickRate = (input) => {
    input.checked = true;
    wantedVehicle = input.closest(".vehicle").dataset.vehicle;
    vehicleName.textContent = input.dataset.buttonName;
  };

  function filterCars() {
    const trip = currentTrip();
    const pkg = form.querySelector('[name="package_choice"]:checked')?.value || "";
    const paxValue = form.elements.num_pax.value;
    const pax = trip === "outstation" && /^\d+$/.test(paxValue) ? Number(paxValue) : 0;
    let shown = 0;
    carCards.forEach((card) => {
      const input = card.querySelector("input");
      const visible = card.dataset.trip === trip && (trip !== "local" || card.dataset.package === pkg);
      const tooSmall = visible && pax > Number(card.dataset.seats);
      card.hidden = !visible;
      card.classList.toggle("is-disabled", tooSmall);
      input.disabled = !visible || tooSmall;
      if (input.disabled) input.checked = false;
      if (visible) shown += 1;
    });
    // Keep the same car when switching tab or package
    if (!form.querySelector('[name="rate"]:checked') && wantedVehicle) {
      const same = carCards.find((c) => c.dataset.vehicle === wantedVehicle && !c.querySelector("input").disabled);
      if (same) same.querySelector("input").checked = true;
    }
    const checked = form.querySelector('[name="rate"]:checked');
    vehicleName.textContent = checked ? checked.dataset.buttonName : "";
    carCount.textContent = shown;
    noCars.hidden = shown > 0;
  }

  const setTrip = () => {
    const trip = currentTrip();
    form.querySelectorAll("[data-trip-only]").forEach((el) => (el.hidden = !el.dataset.tripOnly.split(" ").includes(trip)));
    // Hidden boxes must not keep showing old errors
    form.querySelectorAll("[data-trip-only] .has-error").forEach((el) => el.classList.remove("has-error"));
    form.querySelectorAll("[data-trip-only] [data-error-for]").forEach((el) => (el.textContent = ""));
    filterCars();
  };

  form.querySelectorAll('[name="trip_type"]').forEach((r) => r.addEventListener("change", setTrip));
  form.querySelectorAll('[name="package_choice"]').forEach((r) => r.addEventListener("change", filterCars));
  form.querySelectorAll('[name="rate"]').forEach((r) => r.addEventListener("change", () => {
    pickRate(r);
    showError(form, "rate", "");
  }));
  setTrip();

  document.querySelectorAll("[data-open-booking]").forEach((btn) =>
    btn.addEventListener("click", (e) => {
      e.preventDefault();
      closeMenu();
      // Buttons on car cards open the popup with that car already picked
      if (btn.dataset.vehicle) {
        wantedVehicle = btn.dataset.vehicle;
        const checked = form.querySelector('[name="rate"]:checked');
        if (checked) checked.checked = false;
        filterCars();
      }
      openModal(bookingModal);
    })
  );

  /* ---------------- Hero card → popup ---------------- */
  // Hero boxes: same address rules as the popup
  const checkRoute = (scope) => {
    let ok = true;
    [["pickup", "pickup address"], ["destination", "destination"]].forEach(([name, label]) => {
      const input = scope.querySelector(`[name="${name}"]`);
      input.value = input.value.replace(/\s+/g, " ").trim();
      const message = addressError(input.value, label);
      if (message) {
        showError(scope, name, message);
        ok = false;
      }
    });
    return ok;
  };

  quick?.addEventListener("submit", (e) => {
    e.preventDefault();
    clearErrors(quick);
    if (!checkRoute(quick)) return focusFirstError(quick);
    ["pickup", "destination"].forEach((name) => {
      form.elements[name].value = quick.elements[name].value;
    });
    // Carry the chosen date / time into the popup ("Depart Now" = earliest allowed time)
    form.elements.date_option.value = heroDateText.textContent;
    form.elements.ride_window.value = heroSlot.options[heroSlot.selectedIndex]?.text || "";
    if (heroSlot.value === "now") {
      const soon = new Date(Date.now() + (limits.lead + 5) * 60000);
      soon.setMinutes(Math.ceil(soon.getMinutes() / 5) * 5, 0, 0);
      form.elements.scheduled_date.value = isoDate(soon);
      form.elements.scheduled_time.value = `${pad(soon.getHours())}:${pad(soon.getMinutes())}`;
    } else {
      form.elements.scheduled_date.value = heroDate.value;
      form.elements.scheduled_time.value = heroSlot.value;
    }
    openModal(bookingModal);
  });
  quick?.addEventListener("input", (e) => {
    e.target.closest("label")?.classList.remove("has-error");
    const slot = quick.querySelector(`[data-error-for="${e.target.name}"]`);
    if (slot) slot.textContent = "";
  });

  /* ---------------- Submit ---------------- */
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    clearErrors(form);

    let ok = true;
    form.querySelectorAll("[data-validate]").forEach((input) => {
      input.dataset.touched = "1";
      if (!checkField(input)) ok = false;
    });
    const rate = form.querySelector('[name="rate"]:checked');
    if (!rate) {
      const pax = form.elements.num_pax.value;
      const allTooSmall = currentTrip() === "outstation" && pax && carCards.some((c) => !c.hidden)
        && carCards.every((c) => c.hidden || c.classList.contains("is-disabled"));
      showError(form, "rate", allTooSmall ? `No car seats ${pax} people. Please call us to book.` : "Please choose a car.");
      ok = false;
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
      wantedVehicle = "";
      setTrip();
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
