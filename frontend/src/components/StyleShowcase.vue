<script setup>
import PresetManager from '@/components/PresetManager.vue'
import PrimePTShowcase from '@/components/PrimePTShowcase.vue'


const setLight = () => {
  document.documentElement.dataset.theme = 'light'
  localStorage.setItem('ui.theme', 'light')
  window.dispatchEvent(new Event('themechange'))
}
const setDark = () => {
  document.documentElement.dataset.theme = 'dark'
  localStorage.setItem('ui.theme', 'dark')
  window.dispatchEvent(new Event('themechange'))
}
</script>

<template>
  <div class="card" style="max-width: 960px; margin: var(--sp-6) auto;">
    <div class="card-body stack-md">
      <div class="row-md">
        <button class="btn btn-outline" @click="setLight">Light</button>
        <button class="btn btn-outline" @click="setDark">Dark</button>
        <span class="text-muted">Toggle themes to verify token overrides.</span>
      </div>

      <section class="stack-sm">
        <div class="text-h1">Heading H1 — Railway Failure System</div>
        <div class="text-h2">Heading H2</div>
        <div class="text-h3">Heading H3</div>
        <p class="text-body text-muted">
          Body text uses <code>--font-sans</code> and <code>--fs-md</code>. Change font, size, and colors in <strong>/src/styles/tokens.css</strong>.
        </p>
      </section>

      <section class="stack-sm">
        <div class="row-md">
          <button class="btn btn-primary">Primary Button</button>
          <button class="btn btn-outline">Outline Button</button>
          <button class="btn btn-ghost">Ghost Button</button>
          <span class="chip">Chip</span>
        </div>
      </section>

      <section class="stack-sm">
        <label class="text-muted" for="sc-input">Input</label>
        <input id="sc-input" class="input" placeholder="Type here…" />
      </section>

      <section class="stack-sm">
        <div class="card">
          <div class="card-body">
            <div class="card-title">Card using tokens</div>
            <p class="text-body text-muted">
              Background, border, radius, shadow from tokens. Buttons and inputs inside the card match the theme.
            </p>
            <div class="row-md" style="margin-top: var(--sp-4);">
              <button class="btn btn-primary">Do Action</button>
              <button class="btn btn-outline">Cancel</button>
            </div>
          </div>
        </div>
      </section>

      <section class="stack-sm">
        <div class="text-h3">Sizing demo (global)</div>
        <p class="text-body text-muted">
          Change <code>--scale-text</code> and <code>--scale-control</code> in <strong>/src/styles/tokens.css</strong>.
          All text and buttons below will resize accordingly.
        </p>
        <div class="row-md">
          <button class="btn btn-outline btn-sm">Small</button>
          <button class="btn btn-primary">Default</button>
          <button class="btn btn-outline btn-lg">Large</button>
        </div>
      </section>

      <section class="stack-sm">
        <div class="text-h3">Tailwind mapping demo</div>

        <div class="row-md">
          <div class="rounded-token-md border border-border bg-surface p-token-4 shadow-token-sm">
            <div class="text-token-lg font-sans text-primary">text-primary on bg-surface</div>
            <div class="text-muted text-token-sm">border-border • rounded-token-md • p-token-4 • shadow-token-sm</div>
            <button class="mt-token-3 btn btn-primary transition-fast">Primary (tokens)</button>
          </div>
        </div>
        <div class="text-muted" style="font-family: var(--font-mono); font-size: var(--fs-xs);">
          Tip: Add <code>?style=1</code> to the URL to open this showcase overlay anywhere in dev.
        </div>
      </section>
       <section class="stack-sm">
        <div class="text-h3">Status & Focus demo</div>
        <div class="row-md">
          <span class="badge badge-success">Success</span>
          <span class="badge badge-warning">Warning</span>
          <span class="badge badge-danger">Danger</span>
        </div>
        <div class="row-md">
          <div class="alert alert-success" style="max-width: 28rem;">
            <div class="alert-title">All good</div>
            <div class="alert-desc">This alert uses status tokens and soft background.</div>
          </div>
          <div class="alert alert-warning" style="max-width: 28rem;">
            <div class="alert-title">Heads up</div>
            <div class="alert-desc">Tokenized, theme-aware alert styles.</div>
          </div>
          <div class="alert alert-danger" style="max-width: 28rem;">
            <div class="alert-title">Action needed</div>
            <div class="alert-desc">Colors only come from tokens.</div>
          </div>
        </div>
        <div class="row-md">
          <input class="input" placeholder="Focus me to see ring" />
          <button class="btn btn-primary">Focus me too</button>
        </div>
      </section>
      <!-- PrimeVue PT demo -->
      <section class="stack-sm">
        <div class="text-h3">PrimeVue PT Showcase</div>
        <PrimePTShowcase />
      </section>
     
      <!-- Links & Scrollbar demo -->
      <section class="stack-sm">
        <div class="text-h3">Links & Scrollbar demo</div>
        <p class="text-body">
          This is a <a href="#">sample link</a> with hover/visited colors driven by tokens.
          Try selecting this text to see the tokenized selection colors.
        </p>
        <div class="card max-w-xl" style="max-height: 160px; overflow: auto;">
          <div class="card-body text-body">
            <p>
              Scroll this box to preview themed scrollbars. Lorem ipsum dolor sit amet, consectetur
              adipiscing elit. Vivamus varius, urna sed fermentum hendrerit, lorem leo semper elit,
              nec rhoncus justo massa nec erat. Cras a mi risus. Integer tempus faucibus congue.
            </p>
            <p>
              Proin pharetra, justo sit amet placerat mollis, justo libero aliquet ipsum, vitae
              pretium lorem massa at odio. Suspendisse potenti. Praesent a orci ac diam iaculis
              tristique non quis arcu. Duis lobortis ex nunc, at bibendum orci dictum non.
            </p>
          </div>
        </div>
      </section>
    </div>
  </div>
  <PresetManager />

</template>

<style scoped>
/* Keep the showcase visually separated when mounted as an overlay */
:host, :root { }
</style>
