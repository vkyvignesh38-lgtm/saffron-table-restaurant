/* Saffron Table — site interactions (no dependencies) */
(function () {
  "use strict";

  var $ = function (sel, ctx) { return (ctx || document).querySelector(sel); };
  var $$ = function (sel, ctx) { return Array.prototype.slice.call((ctx || document).querySelectorAll(sel)); };

  /* ---------- Sticky header shadow ---------- */
  var header = $("[data-header]");
  if (header) {
    var onScroll = function () { header.classList.toggle("is-scrolled", window.scrollY > 8); };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  /* ---------- Mobile drawer ---------- */
  var drawer = $("#drawer");
  var openBtn = $("[data-drawer-open]");
  var closeBtn = $("[data-drawer-close]");

  function setDrawer(open) {
    if (!drawer) return;
    drawer.classList.toggle("is-open", open);
    if (open) drawer.removeAttribute("inert"); else drawer.setAttribute("inert", "");
    openBtn && openBtn.setAttribute("aria-expanded", String(open));
    document.documentElement.style.overflow = open ? "hidden" : "";
    if (open) { closeBtn && closeBtn.focus(); } else { openBtn && openBtn.focus(); }
  }
  openBtn && openBtn.addEventListener("click", function () { setDrawer(true); });
  closeBtn && closeBtn.addEventListener("click", function () { setDrawer(false); });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && drawer && drawer.classList.contains("is-open")) setDrawer(false);
  });
  window.addEventListener("resize", function () {
    if (window.innerWidth > 1024 && drawer && drawer.classList.contains("is-open")) setDrawer(false);
  });

  /* ---------- Category filters (menu + gallery) ---------- */
  $$("[data-filter-group]").forEach(function (group) {
    var section = group.parentElement;
    var items = $$("[data-category]", $("[data-filter-items]", section));
    var status = $("[data-filter-status]", section);
    var buttons = $$("[data-filter]", group);
    var noun = group.getAttribute("data-filter-group") === "menu" ? "dishes" : "photos";

    function apply(filter, scroll) {
      var shown = 0;
      buttons.forEach(function (b) { b.setAttribute("aria-pressed", String(b.dataset.filter === filter)); });
      items.forEach(function (item) {
        var match = filter === "all" || item.dataset.category === filter;
        item.hidden = !match;
        if (match) shown++;
      });
      if (status) status.textContent = "Showing " + shown + " " + noun;
      if (scroll) {
        var active = buttons.filter(function (b) { return b.dataset.filter === filter; })[0];
        active && active.scrollIntoView && active.scrollIntoView({ block: "nearest", inline: "center" });
      }
    }

    buttons.forEach(function (b) {
      b.addEventListener("click", function () { apply(b.dataset.filter, false); });
    });

    // Footer "Our Menu" links arrive as menu.html#biryani etc.
    var hash = (location.hash || "").slice(1);
    if (hash && buttons.some(function (b) { return b.dataset.filter === hash; })) {
      apply(hash, true);
      setTimeout(function () { group.scrollIntoView({ behavior: "smooth", block: "start" }); }, 60);
    }
  });

  /* ---------- Gallery lightbox ---------- */
  var lb = $("[data-lightbox]");
  if (lb) {
    var lbImg = $("[data-lb-img]", lb);
    var lbCap = $("[data-lb-caption]", lb);
    var lbLabel = $("[data-lb-label]", lb);
    var lbCount = $("[data-lb-count]", lb);
    var tiles = $$("[data-gallery] .tile");
    var visible = [];
    var current = 0;
    var lastFocus = null;

    var pad = function (n) { return (n < 10 ? "0" : "") + n; };

    function show(i) {
      current = (i + visible.length) % visible.length;
      var t = visible[current];
      lbImg.classList.add("is-swapping");
      var src = t.dataset.src;
      var img = new Image();
      img.onload = img.onerror = function () {
        lbImg.src = src;
        lbImg.alt = t.dataset.caption;
        lbImg.classList.remove("is-swapping");
      };
      img.src = src;
      lbCap.textContent = t.dataset.caption;
      lbLabel.textContent = t.dataset.label;
      lbCount.textContent = pad(current + 1) + " / " + pad(visible.length);
    }

    function open(tile) {
      visible = tiles.filter(function (t) { return !t.hidden; });
      lastFocus = tile;
      lb.removeAttribute("inert");
      lb.classList.add("is-open");
      document.documentElement.style.overflow = "hidden";
      show(visible.indexOf(tile));
      $("[data-lb-close]", lb).focus();
    }

    function close() {
      lb.classList.remove("is-open");
      lb.setAttribute("inert", "");
      document.documentElement.style.overflow = "";
      lastFocus && lastFocus.focus();
    }

    tiles.forEach(function (t) { t.addEventListener("click", function () { open(t); }); });
    $("[data-lb-close]", lb).addEventListener("click", close);
    $("[data-lb-prev]", lb).addEventListener("click", function () { show(current - 1); });
    $("[data-lb-next]", lb).addEventListener("click", function () { show(current + 1); });
    lb.addEventListener("click", function (e) {
      if (e.target === lb || e.target.classList.contains("lightbox__stage")) close();
    });
    document.addEventListener("keydown", function (e) {
      if (!lb.classList.contains("is-open")) return;
      if (e.key === "Escape") close();
      else if (e.key === "ArrowLeft") show(current - 1);
      else if (e.key === "ArrowRight") show(current + 1);
    });

    // Swipe on touch screens
    var startX = null;
    lb.addEventListener("touchstart", function (e) { startX = e.touches[0].clientX; }, { passive: true });
    lb.addEventListener("touchend", function (e) {
      if (startX === null) return;
      var dx = e.changedTouches[0].clientX - startX;
      if (Math.abs(dx) > 50) show(current + (dx < 0 ? 1 : -1));
      startX = null;
    });
  }

  /* ---------- Reservation form (front-end demo only) ---------- */
  var form = $("[data-reserve-form]");
  if (form) {
    var success = $("[data-reserve-success]");
    var summary = $("[data-summary]");
    var dateInput = $("#r-date");
    var timeSelect = $("[data-time-select]");

    var toISO = function (d) {
      return d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" + String(d.getDate()).padStart(2, "0");
    };
    var today = new Date();
    dateInput.min = toISO(today);
    var max = new Date(today); max.setDate(max.getDate() + 60);
    dateInput.max = toISO(max);

    function fmtTime(mins) {
      var h = Math.floor(mins / 60), m = mins % 60;
      var suffix = h >= 12 ? "PM" : "AM";
      var h12 = h % 12 || 12;
      return h12 + ":" + String(m).padStart(2, "0") + " " + suffix;
    }

    // Seatings every 30 min, last seating 30 min before closing.
    function fillTimes() {
      var prev = timeSelect.value;
      timeSelect.innerHTML = "";
      if (!dateInput.value) {
        timeSelect.add(new Option("Select a date first", ""));
        return;
      }
      var d = new Date(dateInput.value + "T00:00:00");
      var weekend = d.getDay() === 0 || d.getDay() === 6;
      var open = weekend ? 10 * 60 : 11 * 60;
      var last = weekend ? 22 * 60 + 30 : 22 * 60;
      var isToday = dateInput.value === toISO(new Date());
      var now = new Date();
      var nowMins = now.getHours() * 60 + now.getMinutes() + 30;
      timeSelect.add(new Option("Select a time", ""));
      var count = 0;
      for (var t = open; t <= last; t += 30) {
        if (isToday && t < nowMins) continue;
        timeSelect.add(new Option(fmtTime(t), fmtTime(t)));
        count++;
      }
      if (!count) {
        timeSelect.innerHTML = "";
        timeSelect.add(new Option("No seatings left today", ""));
      }
      if (prev && Array.prototype.some.call(timeSelect.options, function (o) { return o.value === prev; })) timeSelect.value = prev;
    }
    dateInput.addEventListener("change", fillTimes);

    var rules = {
      name: function (v) { return v.trim().length >= 2 ? "" : "Please enter your full name."; },
      phone: function (v) {
        var digits = v.replace(/\D/g, "");
        return digits.length >= 10 && digits.length <= 13 ? "" : "Please enter a valid phone number (10 digits).";
      },
      guests: function (v) { return v ? "" : "Please choose the number of guests."; },
      date: function (v) {
        if (!v) return "Please choose a date.";
        if (v < dateInput.min) return "Please choose today or a future date.";
        if (v > dateInput.max) return "We take requests up to 60 days ahead.";
        return "";
      },
      time: function (v) { return v ? "" : "Please choose a time."; }
    };

    function check(name) {
      var input = form.elements[name];
      var msg = rules[name](input.value);
      var field = input.closest(".field");
      var err = $("#" + input.id + "-err");
      field.classList.toggle("has-error", !!msg);
      err.textContent = msg;
      if (msg) {
        input.setAttribute("aria-invalid", "true");
        input.setAttribute("aria-describedby", err.id);
      } else {
        input.removeAttribute("aria-invalid");
      }
      return !msg;
    }

    Object.keys(rules).forEach(function (name) {
      var input = form.elements[name];
      input.addEventListener("blur", function () { if (input.value) check(name); });
      input.addEventListener("change", function () {
        if (input.closest(".field").classList.contains("has-error")) check(name);
      });
    });

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var firstBad = null;
      Object.keys(rules).forEach(function (name) {
        if (!check(name) && !firstBad) firstBad = form.elements[name];
      });
      if (firstBad) { firstBad.focus(); return; }

      var d = new Date(form.elements.date.value + "T00:00:00");
      var dateLabel = d.toLocaleDateString("en-IN", { weekday: "short", day: "numeric", month: "short", year: "numeric" });
      var g = form.elements.guests.value;
      var rows = [
        ["Name", form.elements.name.value.trim()],
        ["Phone", form.elements.phone.value.trim()],
        ["Date", dateLabel],
        ["Time", form.elements.time.value],
        ["Guests", g + (g === "1" ? " guest" : " guests")]
      ];
      var notes = form.elements.notes.value.trim();
      if (notes) rows.push(["Special request", notes]);
      summary.innerHTML = "";
      rows.forEach(function (r) {
        var wrap = document.createElement("div");
        var dt = document.createElement("dt"); dt.textContent = r[0];
        var dd = document.createElement("dd"); dd.textContent = r[1];
        wrap.appendChild(dt); wrap.appendChild(dd);
        if (r[0] === "Special request") wrap.style.gridColumn = "1 / -1";
        summary.appendChild(wrap);
      });

      form.hidden = true;
      success.hidden = false;
      success.focus();
      success.scrollIntoView({ behavior: "smooth", block: "center" });
    });

    $("[data-reserve-reset]").addEventListener("click", function () {
      form.reset();
      fillTimes();
      $$(".field", form).forEach(function (f) { f.classList.remove("has-error"); });
      success.hidden = true;
      form.hidden = false;
      form.elements.name.focus();
    });
  }

  /* ---------- Newsletter (front-end demo only) ---------- */
  $$("[data-newsletter]").forEach(function (nf) {
    var msg = $(".newsletter__msg", nf);
    nf.addEventListener("submit", function (e) {
      e.preventDefault();
      var email = nf.elements.email.value.trim();
      var ok = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email);
      msg.classList.toggle("is-error", !ok);
      if (!ok) {
        msg.textContent = "Please enter a valid email address, like name@example.com.";
        nf.elements.email.focus();
        return;
      }
      msg.textContent = "Thanks for subscribing! (Demo only: your email was not sent anywhere.)";
      nf.reset();
    });
  });
})();
