// Generic debounce utility for Vue apps
// - Works with plain functions or Vue refs to functions
// - Delay can be a number or a Vue ref
// - Returns a wrapped function that carries a .cancel() method

import { isRef } from 'vue'

function toVal(v) {
  return isRef(v) ? v.value : v
}

export function useDebounce(fnOrRef, delayOrRef = 300) {
  let timer = null

  function getFn() {
    const fn = toVal(fnOrRef)
    if (typeof fn !== 'function') {
      throw new TypeError('useDebounce: expected a function or a ref to a function')
    }
    return fn
  }

  function getDelay() {
    const d = Number(toVal(delayOrRef))
    return Number.isFinite(d) ? d : 300
  }

  const debounced = function (...args) {
    if (timer) clearTimeout(timer)
    const ms = getDelay()
    return new Promise(resolve => {
      timer = setTimeout(() => {
        timer = null
        resolve(getFn().apply(this, args))
      }, ms)
    })
  }

  debounced.cancel = () => {
    if (timer) {
      clearTimeout(timer)
      timer = null
    }
  }

  return debounced
}

