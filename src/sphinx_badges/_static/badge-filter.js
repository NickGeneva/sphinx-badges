/**
 * sphinx-badges — interactive filter for toctrees and autosummary tables.
 *
 * Data sources (written at build time):
 *   window.SPHINX_BADGES_DATA          — { docname: [badge_id, ...] }
 *   window.SPHINX_BADGES_DEFINITIONS   — { badge_id: { label, color, text_color, group, name } }
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

  /* ── URL → docname ──────────────────────────────────────────────────────── */

  function hrefToDocname(href) {
    var clean = href.split("#")[0].split("?")[0];
    if (!clean) return "";
    var abs;
    try { abs = new URL(clean, window.location.href).pathname; }
    catch (_) { abs = clean; }

    abs = abs.replace(/\/index\.html$/, "").replace(/\.html$/, "");

    var docname = ((window.DOCUMENTATION_OPTIONS || {}).docname || "").replace(/\/index$/, "");
    if (docname) {
      var currentAbs = window.location.pathname
        .replace(/\/index\.html$/, "")
        .replace(/\.html$/, "");
      var depth = docname.split("/").length;
      var root = currentAbs.split("/").slice(0, -depth).join("/");
      if (abs.startsWith(root + "/")) abs = abs.slice(root.length + 1);
    }

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

    var span = document.createElement("span");
    span.className = cls;
    span.dataset.badgeId = badgeId;
    span.style.backgroundColor = defn.color || "#6c757d";
    span.style.color = defn.text_color || "#fff";
    span.textContent = defn.label || badgeId;
    return span;
  }

  /* ── Collect filterable entries ─────────────────────────────────────────── */

  function collectEntries(contentWrapper) {
    var entries = [];

    contentWrapper.querySelectorAll(".toctree-wrapper li").forEach(function (li) {
      var a = li.querySelector("a[href]");
      if (!a) return;
      var docname = hrefToDocname(a.getAttribute("href"));
      if (docname) { li.dataset.resolvedDocname = docname; entries.push({ element: li, docname: docname, anchor: a }); }
    });

    contentWrapper.querySelectorAll("table.autosummary tbody tr").forEach(function (tr) {
      var a = tr.querySelector("td:first-child a[href]");
      if (!a) return;
      var docname = hrefToDocname(a.getAttribute("href"));
      if (docname) { tr.dataset.resolvedDocname = docname; entries.push({ element: tr, docname: docname, anchor: a }); }
    });

    return entries;
  }

  /* ── Filter logic ───────────────────────────────────────────────────────── */

  /**
   * Apply the current active filters to the entry list.
   *
   * @param {Array}  entries       — [{element, docname}]
   * @param {Set}    activeFilters — set of active badge IDs
   * @param {Object} badgeData     — SPHINX_BADGES_DATA
   * @param {boolean} isGrouped    — use group-aware logic
   * @param {string}  filterMode   — "and" | "or" (flat mode only)
   */
  function applyFilter(entries, activeFilters, badgeData, isGrouped, filterMode) {
    entries.forEach(function (entry) {
      if (!activeFilters.size) {
        entry.element.classList.remove("sphinx-badge-hidden");
        return;
      }

      var pageBadges = badgeData[entry.docname] || [];
      var visible;

      if (isGrouped) {
        // Build { group: [badge_ids] } for the active selection.
        var byGroup = {};
        activeFilters.forEach(function (bid) {
          var colon = bid.indexOf(":");
          var group = colon >= 0 ? bid.slice(0, colon) : "__ungrouped__";
          if (!byGroup[group]) byGroup[group] = [];
          byGroup[group].push(bid);
        });

        // AND across groups, OR within each group.
        visible = Object.keys(byGroup).every(function (group) {
          return byGroup[group].some(function (bid) {
            return pageBadges.indexOf(bid) !== -1;
          });
        });
      } else {
        visible = filterMode === "or"
          ? Array.from(activeFilters).some(function (f) { return pageBadges.indexOf(f) !== -1; })
          : Array.from(activeFilters).every(function (f) { return pageBadges.indexOf(f) !== -1; });
      }

      entry.element.classList.toggle("sphinx-badge-hidden", !visible);
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
      entries.forEach(function (entry) {
        var pageBadges = badgeData[entry.docname] || [];
        pageBadges.forEach(function (bid) {
          var defn = badgeDefs[bid];
          if (!defn) return;
          var target = entry.anchor.closest("td") || entry.anchor.parentNode;
          target.appendChild(makeBadgeChip(bid, defn));
        });
      });

      // ── Wire filter buttons ────────────────────────────────────────────
      var activeFilters = new Set();
      var resetRow = widget.querySelector(".sphinx-badge-filter-reset-row");

      function syncUI() {
        // Show/hide "Clear filters" row in grouped mode.
        if (resetRow) {
          resetRow.style.display = activeFilters.size ? "" : "none";
        }

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
