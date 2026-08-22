/**
 * recommendation.js
 * ------------------
 * Drives the questionnaire flow, calls POST /api/recommend, and renders
 * the ranked results. No frontend framework — plain DOM APIs only.
 */

(function () {
  "use strict";

  const GAUGE_CIRCUMFERENCE = 2 * Math.PI * 52; // matches r=52 in the SVG circle

  const STEPS = ["budget", "model_type", "api_required", "technical_level"];
  const TYPE_LABELS = {
    text: "Text / LLM",
    image: "Image Generation",
    audio: "Audio / Speech",
    video: "Video Generation",
    vision: "Vision",
    coding: "Coding",
    embeddings: "Embeddings / Search",
  };

  const state = {
    currentStep: 1,
    answers: {},
  };

  // ---------- Element refs ----------
  const screens = {
    hero: document.getElementById("screen-hero"),
    quiz: document.getElementById("screen-quiz"),
    loading: document.getElementById("screen-loading"),
    results: document.getElementById("screen-results"),
  };

  const btnStart = document.getElementById("btn-start");
  const btnBack = document.getElementById("btn-back");
  const btnSubmit = document.getElementById("btn-submit");
  const btnRestart = document.getElementById("btn-restart");

  const progressFill = document.getElementById("quiz-progress-fill");
  const stepDots = document.querySelectorAll(".step-dot");
  const qCards = document.querySelectorAll(".q-card");

  const resultsList = document.getElementById("results-list");
  const resultsError = document.getElementById("results-error");
  const resultsEmpty = document.getElementById("results-empty");

  const modalBackdrop = document.getElementById("modal-backdrop");
  const modalBody = document.getElementById("modal-body");
  const modalClose = document.getElementById("modal-close");

  const cardTemplate = document.getElementById("tpl-result-card");

  // ---------- Screen switching ----------
  function showScreen(name) {
    Object.values(screens).forEach((el) => el.classList.remove("screen--active"));
    screens[name].classList.add("screen--active");
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  // ---------- Questionnaire navigation ----------
  function renderStep() {
    qCards.forEach((card) => {
      const step = Number(card.dataset.step);
      card.hidden = step !== state.currentStep;
    });

    const pct = (state.currentStep / STEPS.length) * 100;
    progressFill.style.width = pct + "%";

    stepDots.forEach((dot) => {
      const step = Number(dot.dataset.step);
      dot.classList.toggle("is-active", step === state.currentStep);
      dot.classList.toggle("is-done", step < state.currentStep);
    });

    btnBack.hidden = state.currentStep === 1;
    updateSubmitVisibility();
  }

  function currentFieldName() {
    return STEPS[state.currentStep - 1];
  }

  function updateSubmitVisibility() {
    const field = currentFieldName();
    const answered = Boolean(state.answers[field]);
    const isLastStep = state.currentStep === STEPS.length;
    btnSubmit.hidden = !(isLastStep && answered);
  }

  function goToStep(step) {
    state.currentStep = Math.min(Math.max(step, 1), STEPS.length);
    renderStep();
  }

  function advanceIfPossible() {
    if (state.currentStep < STEPS.length) {
      goToStep(state.currentStep + 1);
    } else {
      updateSubmitVisibility();
    }
  }

  // Option selection (event delegation on the whole quiz screen)
  screens.quiz.addEventListener("click", (event) => {
    const optionBtn = event.target.closest(".q-option");
    if (!optionBtn) return;

    const group = optionBtn.closest(".q-options");
    const field = group.dataset.field;
    const value = optionBtn.dataset.value;

    state.answers[field] = value;

    group.querySelectorAll(".q-option").forEach((btn) => {
      btn.classList.toggle("is-selected", btn === optionBtn);
    });

    // small delay so the user sees the selection highlight before advancing
    window.setTimeout(advanceIfPossible, 180);
  });

  btnBack.addEventListener("click", () => goToStep(state.currentStep - 1));

  btnStart.addEventListener("click", () => {
    showScreen("quiz");
    goToStep(1);
  });

  btnRestart.addEventListener("click", () => {
    state.currentStep = 1;
    state.answers = {};
    document.querySelectorAll(".q-option.is-selected").forEach((btn) => {
      btn.classList.remove("is-selected");
    });
    showScreen("hero");
  });

  // ---------- Submit + fetch recommendations ----------
  btnSubmit.addEventListener("click", submitQuestionnaire);

  function validateAnswers() {
    const missing = STEPS.filter((field) => !state.answers[field]);
    return missing;
  }

  async function submitQuestionnaire() {
    const missing = validateAnswers();
    if (missing.length > 0) {
      // Jump back to the first unanswered question instead of guessing.
      const firstMissingIndex = STEPS.indexOf(missing[0]);
      goToStep(firstMissingIndex + 1);
      return;
    }

    showScreen("loading");

    try {
      const response = await fetch("/api/recommend", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(state.answers),
      });

      let payload;
      try {
        payload = await response.json();
      } catch (parseErr) {
        throw new Error("The server sent back something that wasn't valid JSON.");
      }

      if (!response.ok || !payload.success) {
        throw new Error(payload && payload.error ? payload.error : "The server returned an error.");
      }

      renderResults(payload.recommendations || []);
      showScreen("results");
    } catch (err) {
      renderNetworkError(err);
      showScreen("results");
    }
  }

  // ---------- Results rendering ----------
  function renderNetworkError(err) {
    resultsList.innerHTML = "";
    resultsEmpty.hidden = true;
    resultsError.hidden = false;
    resultsError.textContent =
      "We couldn't load recommendations right now (" +
      (err && err.message ? err.message : "network error") +
      "). Please check your connection and try again.";
  }

  function renderResults(models) {
    resultsError.hidden = true;
    resultsList.innerHTML = "";

    if (!models.length) {
      resultsEmpty.hidden = false;
      return;
    }
    resultsEmpty.hidden = true;

    models.forEach((model, index) => {
      resultsList.appendChild(buildResultCard(model, index));
    });
  }

  function buildResultCard(model, index) {
    const node = cardTemplate.content.cloneNode(true);

    const gaugeFill = node.querySelector(".gauge-fill");
    const gaugePct = node.querySelector(".gauge-pct");
    const name = node.querySelector(".result-card__name");
    const provider = node.querySelector(".result-card__provider");
    const typePill = node.querySelector(".pill--type");
    const apiPill = node.querySelector(".pill--api");
    const price = node.querySelector(".result-card__price");
    const reasonsList = node.querySelector(".result-card__reasons");
    const detailsBtn = node.querySelector(".btn-view-details");

    const pct = model.match_percentage;
    const offset = GAUGE_CIRCUMFERENCE * (1 - pct / 100);

    // animate on next frame so the CSS transition actually plays
    requestAnimationFrame(() => {
      gaugeFill.style.strokeDashoffset = String(offset);
    });
    gaugePct.textContent = pct + "%";

    name.textContent = (index + 1) + ". " + model.name;
    provider.textContent = model.provider;
    typePill.textContent = TYPE_LABELS[model.model_type] || model.model_type;

    if (model.api_available) {
      apiPill.textContent = "API available";
      apiPill.classList.add("pill--api-yes");
    } else {
      apiPill.textContent = "No public API";
      apiPill.classList.add("pill--api-no");
    }

    price.textContent = model.price_note;

    reasonsList.innerHTML = "";
    (model.reasons || []).forEach((reason) => {
      const li = document.createElement("li");
      li.textContent = reason;
      reasonsList.appendChild(li);
    });

    detailsBtn.addEventListener("click", () => openModal(model));

    return node;
  }

  // ---------- Modal ----------
  function openModal(model) {
    modalBody.innerHTML = "";

    const title = document.createElement("h3");
    title.className = "modal-title";
    title.id = "modal-title";
    title.textContent = model.name;

    const providerEl = document.createElement("p");
    providerEl.className = "modal-provider";
    providerEl.textContent = model.provider;

    const desc = document.createElement("p");
    desc.className = "modal-desc";
    desc.textContent = model.description;

    const rows = [
      ["Match score", model.match_percentage + "%"],
      ["Type", TYPE_LABELS[model.model_type] || model.model_type],
      ["Pricing", model.price_note],
      ["API access", model.api_available ? "Available" : "Not available"],
      ["Technical level", capitalize(model.technical_level)],
      ["Quality rating", model.quality + " / 5"],
      ["Speed rating", model.speed + " / 5"],
    ];

    modalBody.appendChild(title);
    modalBody.appendChild(providerEl);
    modalBody.appendChild(desc);

    rows.forEach(([label, value]) => {
      const row = document.createElement("div");
      row.className = "modal-row";
      const l = document.createElement("span");
      l.textContent = label;
      const v = document.createElement("span");
      v.textContent = value;
      row.appendChild(l);
      row.appendChild(v);
      modalBody.appendChild(row);
    });

    if (model.use_cases && model.use_cases.length) {
      const ul = document.createElement("ul");
      ul.className = "modal-usecases";
      model.use_cases.forEach((uc) => {
        const li = document.createElement("li");
        li.textContent = uc;
        ul.appendChild(li);
      });
      modalBody.appendChild(ul);
    }

    modalBackdrop.hidden = false;
  }

  function closeModal() {
    modalBackdrop.hidden = true;
  }

  modalClose.addEventListener("click", closeModal);
  modalBackdrop.addEventListener("click", (e) => {
    if (e.target === modalBackdrop) closeModal();
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && !modalBackdrop.hidden) closeModal();
  });

  function capitalize(str) {
    if (!str) return "";
    return str.charAt(0).toUpperCase() + str.slice(1);
  }

  // ---------- Init ----------
  renderStep();
})();
