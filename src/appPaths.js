/** Pathname inside the app, without deploy base and without trailing slash. */
export function getAppPath() {
  const base = import.meta.env.BASE_URL;
  let path = window.location.pathname;
  const baseNorm = base.replace(/\/$/, "");
  if (baseNorm && path.startsWith(baseNorm)) {
    path = path.slice(baseNorm.length) || "/";
  }
  return path.replace(/\/$/, "") || "/";
}

/** Absolute URL for client-side navigation (respects Vite `base`). */
export function appHref(pathSegment) {
  const base = import.meta.env.BASE_URL;
  const seg = pathSegment.replace(/^\//, "");
  return `${base}${seg}`;
}
