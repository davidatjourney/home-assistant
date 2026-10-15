// Fit a native card and its overlays together within the remaining viewport.
class ViewportFitCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; width: 100%; }
        #frame { position: relative; margin: 0 auto; overflow: hidden; }
        #content { position: absolute; top: 0; left: 0; transform-origin: top left; }
      </style>
      <div id="frame"><div id="content"></div></div>
    `;
    this._frame = this.shadowRoot.getElementById("frame");
    this._content = this.shadowRoot.getElementById("content");
    this._schedule = () => {
      cancelAnimationFrame(this._raf);
      this._raf = requestAnimationFrame(() => this._fit());
    };
    this._observer = new ResizeObserver(this._schedule);
  }

  async setConfig(config) {
    if (!config.card || !(config.width > 0) || !(config.height > 0)) {
      throw new Error("viewport-fit-card needs a card, width and height");
    }
    this._config = config;
    const helpers = await window.loadCardHelpers();
    // Ignore a previous config if a newer one arrived during loading.
    if (this._config !== config) return;
    this._card = helpers.createCardElement(config.card);
    if (this._hass) this._card.hass = this._hass;
    this._content.style.width = `${config.width}px`;
    this._content.replaceChildren(this._card);
    this._schedule();
  }

  set hass(hass) {
    this._hass = hass;
    if (this._card) this._card.hass = hass;
  }

  connectedCallback() {
    this._observer.observe(this);
    window.addEventListener("resize", this._schedule);
    window.visualViewport?.addEventListener("resize", this._schedule);
    this._schedule();
  }

  disconnectedCallback() {
    this._observer.disconnect();
    window.removeEventListener("resize", this._schedule);
    window.visualViewport?.removeEventListener("resize", this._schedule);
    cancelAnimationFrame(this._raf);
  }

  _fit() {
    if (!this.isConnected || !this._config) return;
    const rect = this.getBoundingClientRect();
    if (!rect.width) return; // Hidden by the responsive conditional card.
    const viewport = window.visualViewport;
    const bottom = viewport ? viewport.offsetTop + viewport.height : window.innerHeight;
    const availableHeight = Math.max(0, bottom - rect.top - 16);
    const { width, height } = this._config;
    const scale = Math.min(rect.width / width, availableHeight / height);
    this._frame.style.width = `${width * scale}px`;
    this._frame.style.height = `${height * scale}px`;
    this._content.style.transform = `scale(${scale})`;
  }

  getCardSize() {
    return Math.ceil((this._frame.clientHeight || 500) / 50);
  }
}

if (!customElements.get("viewport-fit-card")) {
  customElements.define("viewport-fit-card", ViewportFitCard);
}

// A display-only picture element: missing readings use a dash, never zero.
class HomeReading extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._label = document.createElement("span");
    const style = document.createElement("style");
    style.textContent = `
      :host { line-height: 1.2; font-variant-numeric: tabular-nums; }
      :host([role="button"]) { cursor: pointer; }
      :host(:focus-visible) { outline: 2px solid #2563eb; outline-offset: 3px; }
    `;
    this.shadowRoot.append(style, this._label);
    this.addEventListener("click", () => {
      if (this._config?.tap_action?.action === "none") return;
      this.dispatchEvent(new CustomEvent("hass-more-info", {
        detail: { entityId: this._config.entity }, bubbles: true, composed: true,
      }));
    });
    this.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        this.click();
      }
    });
  }

  setConfig(config) {
    if (config.precision !== undefined
      && (!Number.isInteger(config.precision) || config.precision < 0 || config.precision > 6)) {
      throw new Error("home-reading precision must be an integer between 0 and 6");
    }
    this._config = config;
    this.title = config.title || config.entity;
    const interactive = config.tap_action?.action !== "none";
    this.tabIndex = interactive ? 0 : -1;
    this.setAttribute("role", interactive ? "button" : "text");
    this._render();
  }

  set hass(hass) {
    this._hass = hass;
    this._render();
  }

  _render() {
    if (!this._config || !this._hass) return;
    const config = this._config;
    const entity = this._hass.states[config.entity];
    const value = config.attribute ? entity?.attributes[config.attribute] : entity?.state;
    const missing = !entity || ["unknown", "unavailable"].includes(entity.state)
      || value == null || ["", "unknown", "unavailable"].includes(value);
    let reading = missing ? "-" : config.attribute
      ? `${value}${config.suffix || ""}`
      : `${this._hass.formatEntityState(entity)}${config.suffix || ""}`;
    if (!missing && config.precision !== undefined) {
      const numeric = Number(value);
      const unit = config.attribute ? config.suffix : entity.attributes.unit_of_measurement;
      reading = Number.isFinite(numeric) ? new Intl.NumberFormat(
        this._hass.locale?.language || this._hass.language,
        { minimumFractionDigits: config.precision, maximumFractionDigits: config.precision },
      ).format(numeric) + (unit ? `${config.attribute ? "" : " "}${unit}` : "")
        + (config.attribute ? "" : config.suffix || "") : "-";
    }
    this._label.textContent = `${config.prefix || ""}${reading}`;
    this.setAttribute("aria-label", `${this.title}: ${this._label.textContent}`);
  }
}

if (!customElements.get("home-reading")) {
  customElements.define("home-reading", HomeReading);
}

// Embed the native weather card as a picture element, preserving its own UI.
class HomeWeather extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
  }

  async setConfig(config) {
    if (!config.entity?.startsWith("weather.")) {
      throw new Error("home-weather needs a weather entity");
    }
    this._config = config;
    const helpers = await window.loadCardHelpers();
    if (this._config !== config) return;
    this._card = helpers.createCardElement({
      type: "weather-forecast",
      entity: config.entity,
      name: config.name || "Home weather",
      show_current: true,
      show_forecast: false,
      forecast_type: "daily",
      tap_action: { action: "more-info" },
    });
    if (this._hass) this._card.hass = this._hass;
    this.shadowRoot.replaceChildren(this._card);
  }

  set hass(hass) {
    this._hass = hass;
    if (this._card) this._card.hass = hass;
  }
}

if (!customElements.get("home-weather")) {
  customElements.define("home-weather", HomeWeather);
}
