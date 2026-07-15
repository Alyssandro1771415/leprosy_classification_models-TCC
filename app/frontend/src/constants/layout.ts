export const SAFE_AREA_BOTTOM =
  "max(24px, env(safe-area-inset-bottom, 0px))"

export const FIXED_BOTTOM_OFFSET = `calc(32px + ${SAFE_AREA_BOTTOM})`
