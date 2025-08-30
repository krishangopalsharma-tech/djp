// PrimeVue Global Pass-Through configuration wired to your tokens/primitives.
// Uses your CSS tokens + Tailwind token utilities from tailwind.config.js.
//
// Important: these are *defaults*; component-level props/class can still override.

const pt = {
  // Buttons: use your .btn primitives by default.
  Button: {
    root: ({ props }) => {
      // Map PrimeVue severities to token-driven variants
      // primary | secondary | success | info | warning | help | danger
      const map = {
        primary: 'btn-primary',
        secondary: 'btn-secondary',
        success: 'btn-success',
        warning: 'btn-warning',
        danger: 'btn-danger',
        info: 'btn-outline', // you can make a dedicated info variant later
        help: 'btn-outline'
      }
      const variant =
        map[props.severity] ??
        // Fallbacks for text/link/outlined modes
        (props.text || props.link ? 'btn-ghost'
         : props.outlined ? 'btn-outline'
         : 'btn-primary')

      return { class: ['btn', variant].join(' ') }
    },
    label: { class: 'text-token-sm' },
    icon: { class: 'text-token-sm' }
  },

  // InputText → your .input primitive
  InputText: {
    root: { class: 'input' }
  },

 // Dropdown (deprecated in v4) → keep styling in case some pages still use it
  Dropdown: {
    root: { class: 'input relative cursor-pointer select-none' },
    trigger: { class: 'px-token-3 text-muted' },
    panel: { class: 'card shadow-token-lg mt-token-2 p-0' },
    items: { class: 'max-h-[18rem] overflow-auto py-token-2' },
    item: ({ context }) => ({
      class: [
        'px-token-4 py-token-2 cursor-pointer',
        context.focused ? 'bg-primary/10' : 'bg-surface',
        context.selected ? 'text-primary font-semibold' : 'text-[var(--text)]'
      ].join(' ')
    }),
    emptyMessage: { class: 'px-token-4 py-token-3 text-muted' }
  },

// Select (replacement for Dropdown in v4)
  Select: {
    root: { class: 'input relative cursor-pointer select-none' },
    trigger: { class: 'px-token-3 text-muted' },
    panel: { class: 'card shadow-token-lg mt-token-2 p-0' },
    list: { class: 'max-h-[18rem] overflow-auto py-token-2' },
    option: ({ context }) => ({
      class: [
        'px-token-4 py-token-2 cursor-pointer',
        context.focused ? 'bg-primary/10' : 'bg-surface',
        context.selected ? 'text-primary font-semibold' : 'text-[var(--text)]'
      ].join(' ')
    }),
    emptyMessage: { class: 'px-token-4 py-token-3 text-muted' }
  },

  // Dialog → surface/border/radius/shadow driven by tokens
  Dialog: {
    mask: { class: 'bg-black/50' },
    root: { class: 'card shadow-token-lg border border-border rounded-token-lg w-[min(90vw,36rem)]' },
    header: { class: 'px-token-5 py-token-4 border-b border-border text-token-lg font-semibold' },
    content: { class: 'px-token-5 py-token-4 text-[var(--text)]' },
    footer: { class: 'px-token-5 py-token-4 border-t border-border flex gap-token-3 justify-end' },
    closeButton: { class: 'btn btn-ghost h-8 px-token-3' }
  },

  // Toast → tokenized container
  Toast: {
    root: { class: 'fixed inset-0 pointer-events-none' },
    container: { class: 'pointer-events-auto w-[min(94vw,28rem)] m-token-4 space-y-token-3' },
    message: ({ props }) => ({
      class: [
        'card border-l-4',
        props.message?.severity === 'warn' ? 'border-warning' :
        props.message?.severity === 'error' ? 'border-danger' :
        props.message?.severity === 'success' ? 'border-success' :
        'border-primary'
      ].join(' ')
    }),
    content: { class: 'card-body py-token-4' },
    summary: { class: 'font-semibold text-token-md' },
    detail: { class: 'text-muted text-token-sm mt-token-2' },
    closeButton: { class: 'btn btn-ghost h-8 px-token-3' }
  },

  // Checkbox & RadioButton → primary color + token radius
  Checkbox: {
    box: ({ context }) => ({
      class: [
        'w-5 h-5 inline-flex items-center justify-center rounded-token-sm border border-border',
        context.checked ? 'bg-primary text-[var(--primary-foreground)]' : 'bg-surface',
        'transition-fast'
      ].join(' ')
    }),
    icon: { class: 'pi pi-check text-[var(--primary-foreground)] text-token-sm' }
  },

  RadioButton: {
    box: ({ context }) => ({
      class: [
        'w-5 h-5 rounded-full border border-border inline-flex items-center justify-center',
        context.checked ? 'bg-primary' : 'bg-surface',
        'transition-fast'
      ].join(' ')
    }),
    icon: { class: 'w-2.5 h-2.5 rounded-full bg-[var(--primary-foreground)]' }
  }
}

export default pt
