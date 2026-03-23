/**
 * sphinx-badges — interactive filter for toctrees and autosummary tables.
 *
 * Data sources (written at build time):
 *   window.SPHINX_BADGES_DATA          — { docname: [badge_id, ...] }
 *   window.SPHINX_BADGES_DEFINITIONS   — { badge_id: { label, color, text_color, group, name, icon, tooltip } }
 *   window.SPHINX_BADGES_STYLE         — "rounded" | "square" | "pill"
 *   window.SPHINX_BADGES_GROUP_LABELS  — { group_key: "Display Label" }
 *
 * Filter modes
 * ────────────
 * Flat (data-grouped="false"):
 *   Uses `data-filter-mode` ("and" / "or") across all selected badges.
 *
 * Grouped (data-grouped="true"):
 *   OR within a group, AND across groups.
 *   Example: selected = { stability: [stable, beta], region: [io] }
 *   → show pages that have (stable OR beta) AND io.
 */

(function () {
  "use strict";

  /* ── Site-root detection ─────────────────────────────────────────────────── */

  // Compute once: the pathname prefix that corresponds to the Sphinx site root.
  // badge-data.js is always deployed at <site-root>/_static/badge-data.js, so
  // we can locate its <script> tag to derive the root reliably without depending
  // on URL_ROOT (removed in Sphinx 7+) or pagename (theme-specific).
  var _siteRoot = (function () {
    var pageDir = window.location.href.slice(0, window.location.href.lastIndexOf("/") + 1);

    // 1. Try URL_ROOT from documentation_options (Sphinx < 7 / some themes).
    var urlRoot = (window.DOCUMENTATION_OPTIONS || {}).URL_ROOT;
    if (urlRoot != null) {
      try { return new URL(urlRoot, pageDir).pathname; } catch (_) {}
    }

    // 2. Find the badge-data.js <script> tag — it lives at _static/badge-data.js
    //    relative to the site root, so we can strip that suffix from its absolute URL.
    var scripts = document.querySelectorAll("script[src]");
    for (var i = 0; i < scripts.length; i++) {
      var src = scripts[i].getAttribute("src") || "";
      if (src.indexOf("badge-data.js") === -1) continue;
      try {
        var abs = new URL(src, pageDir).pathname;
        var marker = "/_static/";
        var idx = abs.indexOf(marker);
        if (idx >= 0) return abs.slice(0, idx + 1);
      } catch (_) {}
    }

    // 3. Last resort: derive depth from pagename (pydata-sphinx-theme sets this).
    var pagename = (window.DOCUMENTATION_OPTIONS || {}).pagename || "";
    var depth = pagename ? pagename.split("/").length - 1 : 0;
    urlRoot = depth > 0 ? new Array(depth + 1).join("../") : "./";
    try { return new URL(urlRoot, pageDir).pathname; } catch (_) { return "/"; }
  }());

  /* ── URL → docname ──────────────────────────────────────────────────────── */

  function hrefToDocname(href) {
    var clean = href.split("#")[0].split("?")[0];
    if (!clean) return "";
    var abs;
    try { abs = new URL(clean, window.location.href).pathname; }
    catch (_) { abs = clean; }

    abs = abs.replace(/\/index\.html$/, "").replace(/\.html$/, "");

    if (abs.startsWith(_siteRoot)) abs = abs.slice(_siteRoot.length);

    var resolved = [];
    abs.split("/").forEach(function (p) {
      if (p === "..") resolved.pop();
      else if (p && p !== ".") resolved.push(p);
    });
    return resolved.join("/");
  }

  /* ── Badge chip factory ─────────────────────────────────────────────────── */

  function makeBadgeChip(badgeId, defn) {
    var styleVal = window.SPHINX_BADGES_STYLE || "rounded";
    var cls = "sphinx-badge sphinx-entry-badge";
    if (styleVal === "square") cls += " sphinx-badge-square";
    else if (styleVal === "pill") cls += " sphinx-badge-pill";

    var icon = defn.icon || "";
    var baseLabel = defn.label != null ? defn.label : badgeId;
    var label = icon && baseLabel
      ? '<span class="sphinx-badge-icon">' + icon + "</span>" +
        '<span class="sphinx-badge-label">' + baseLabel + "</span>"
      : (icon || baseLabel);

    var span = document.createElement("span");
    span.className = cls;
    span.dataset.badgeId = badgeId;
    span.style.backgroundColor = defn.color || "#6c757d";
    span.style.color = defn.text_color || "#fff";
    span.innerHTML = label;
    if (defn.tooltip) span.title = defn.tooltip;
    return span;
  }

  /* ── Collect filterable entries ─────────────────────────────────────────── */

  function collectEntries(contentWrapper) {
    var entries = [];

    contentWrapper.querySelectorAll(".toctree-wrapper li").forEach(function (li) {
      var a = li.querySelector("a[href]");
      if (!a) return;
      var docname = hrefToDocname(a.getAttribute("href"));
      if (docname) { li.dataset.resolvedDocname = docname; entries.push({ element: li, docname: docname, anchor: a, tbody: null }); }
    });

    contentWrapper.querySelectorAll("table.autosummary tbody tr").forEach(function (tr) {
      var a = tr.querySelector("td:first-child a[href]");
      if (!a) return;
      var docname = hrefToDocname(a.getAttribute("href"));
      // Store the tbody so rows can be removed/re-inserted rather than hidden,
      // keeping :nth-child counts accurate.
      if (docname) { tr.dataset.resolvedDocname = docname; entries.push({ element: tr, docname: docname, anchor: a, tbody: tr.parentNode }); }
    });

    return entries;
  }

  /* ── Filter logic ───────────────────────────────────────────────────────── */

  /**
   * Return whether an entry should be visible given the current filters.
   */
  function isEntryVisible(entry, activeFilters, badgeData, isGrouped, filterMode) {
    if (!activeFilters.size) return true;

    var pageBadges = badgeData[entry.docname] || [];

    if (isGrouped) {
      var byGroup = {};
      activeFilters.forEach(function (bid) {
        var colon = bid.indexOf(":");
        var group = colon >= 0 ? bid.slice(0, colon) : "__ungrouped__";
        if (!byGroup[group]) byGroup[group] = [];
        byGroup[group].push(bid);
      });
      return Object.keys(byGroup).every(function (group) {
        return byGroup[group].some(function (bid) { return pageBadges.indexOf(bid) !== -1; });
      });
    }

    return filterMode === "or"
      ? Array.from(activeFilters).some(function (f) { return pageBadges.indexOf(f) !== -1; })
      : Array.from(activeFilters).every(function (f) { return pageBadges.indexOf(f) !== -1; });
  }

  /**
   * Apply the current active filters to the entry list.
   *
   * Table rows (<tr>) are removed from / re-inserted into the DOM so that
   * CSS :nth-child only counts the rows that are actually present.
   * List items (<li>) are hidden with a CSS class as before.
   *
   * @param {Array}  entries       — [{element, docname, tbody}]
   * @param {Set}    activeFilters — set of active badge IDs
   * @param {Object} badgeData     — SPHINX_BADGES_DATA
   * @param {boolean} isGrouped    — use group-aware logic
   * @param {string}  filterMode   — "and" | "or" (flat mode only)
   */
  function applyFilter(entries, activeFilters, badgeData, isGrouped, filterMode) {
    // Non-table entries: toggle a CSS class.
    entries.forEach(function (entry) {
      if (!entry.tbody) {
        entry.element.classList.toggle(
          "sphinx-badge-hidden",
          !isEntryVisible(entry, activeFilters, badgeData, isGrouped, filterMode)
        );
      }
    });

    // Table rows: collect managed rows per tbody (in original document order),
    // then remove ALL of them and re-insert only the visible ones.  This
    // guarantees correct order on every filter/unfilter — appending alone
    // breaks order when some rows were never removed.
    var tbodyRefs = [];   // ordered list of unique tbody references
    var tbodyEntries = []; // parallel array of entry-arrays
    entries.forEach(function (entry) {
      if (!entry.tbody) return;
      var idx = tbodyRefs.indexOf(entry.tbody);
      if (idx === -1) {
        tbodyRefs.push(entry.tbody);
        tbodyEntries.push([]);
        idx = tbodyRefs.length - 1;
      }
      tbodyEntries[idx].push(entry);
    });

    tbodyRefs.forEach(function (tbody, idx) {
      var group = tbodyEntries[idx];

      // Remove every managed row that is currently in this tbody.
      group.forEach(function (entry) {
        if (entry.element.parentNode === tbody) {
          tbody.removeChild(entry.element);
        }
      });

      // Re-append visible rows in original order and update stripe classes.
      var rowIndex = 0;
      group.forEach(function (entry) {
        if (isEntryVisible(entry, activeFilters, badgeData, isGrouped, filterMode)) {
          tbody.appendChild(entry.element);
          entry.element.classList.toggle("row-odd",  rowIndex % 2 === 0);
          entry.element.classList.toggle("row-even", rowIndex % 2 !== 0);
          rowIndex++;
        }
      });
    });
  }

  /* ── Main initialisation ────────────────────────────────────────────────── */

  function init() {
    var badgeData = window.SPHINX_BADGES_DATA || {};
    var badgeDefs = window.SPHINX_BADGES_DEFINITIONS || {};

    document.querySelectorAll(".sphinx-badge-filter").forEach(function (widget) {
      var isGrouped  = widget.dataset.grouped === "true";
      var filterMode = widget.dataset.filterMode || "and";
      var content    = widget.querySelector(".sphinx-badge-filter-content");
      if (!content) return;

      var entries = collectEntries(content);
      if (!entries.length) return;

      // ── Annotate entries with badge chips ──────────────────────────────
      // If the widget declares a canonical badge order via data-badge-order,
      // sort each entry's badges to match that order before rendering chips.
      var badgeOrder = widget.dataset.badgeOrder
        ? widget.dataset.badgeOrder.split(",")
        : null;

      entries.forEach(function (entry) {
        var pageBadges = badgeData[entry.docname] || [];
        if (!pageBadges.length) return;

        if (badgeOrder) {
          pageBadges = pageBadges.slice().sort(function (a, b) {
            var ia = badgeOrder.indexOf(a);
            var ib = badgeOrder.indexOf(b);
            if (ia === -1 && ib === -1) return 0;
            if (ia === -1) return 1;
            if (ib === -1) return -1;
            return ia - ib;
          });
        }

        var target = entry.anchor.closest("td") || entry.anchor.parentNode;
        var wrapper = document.createElement("span");
        wrapper.className = "sphinx-entry-badges";
        pageBadges.forEach(function (bid) {
          var defn = badgeDefs[bid];
          if (!defn) return;
          wrapper.appendChild(makeBadgeChip(bid, defn));
        });
        target.appendChild(wrapper);
      });

      // ── Wire filter buttons ────────────────────────────────────────────
      var activeFilters = new Set();
      var resetRow = widget.querySelector(".sphinx-badge-filter-reset-row");

      function syncUI() {
        // Show/hide "Clear filters" row in grouped mode.
        if (resetRow) {
          resetRow.style.display = activeFilters.size ? "" : "none";
        }

        widget.classList.toggle("sphinx-badge-has-active", activeFilters.size > 0);

        widget.querySelectorAll(".sphinx-badge-filter-btn[data-badge-id]").forEach(function (btn) {
          var bid = btn.dataset.badgeId;
          if (bid === "__all__") {
            btn.setAttribute("aria-pressed", String(activeFilters.size === 0));
          } else {
            btn.setAttribute("aria-pressed", String(activeFilters.has(bid)));
          }
        });
      }

      widget.querySelectorAll("[data-badge-id]").forEach(function (btn) {
        btn.addEventListener("click", function () {
          var bid = btn.dataset.badgeId;

          if (bid === "__all__") {
            activeFilters.clear();
          } else {
            if (activeFilters.has(bid)) activeFilters.delete(bid);
            else activeFilters.add(bid);
          }

          syncUI();
          applyFilter(entries, activeFilters, badgeData, isGrouped, filterMode);
        });
      });
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
